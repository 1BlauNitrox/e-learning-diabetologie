"""Extraction prototype for an Articulate Storyline 3 HTML5 export.

Extracts the slide text and the questions of one module in reading order and
writes them as JSON. See docs/0003-data-analysis.md for the format.

Usage:
    python prototype/extract.py <export-dir> <output.json>
"""

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROW_TOLERANCE = 10
JS_ESCAPES ={"n": "\n", "r": "\r", "t": "\t", "b": "\b", "f": "\f", "v": "\v", "0": "\0"}

# Texts that repeat on many slides and carry no content: slide header, navigation, image credits.
BOILERPLATE = re.compile(
    r"Diabetologie online lernen [|l] .*|Weiter|Zurück|Zum Schließen klicken|(Alle |Beide )?(Bilder )?© articulate"
)
CLICK_HINT = re.compile(r"\s*-?\s*hier\s+klicken\s*-?\s*", re.IGNORECASE)
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(\.[\w-]+)+")
# Player variables such as %_player.5X8JOp5iKWb.$Score% are filled in at runtime.
PLAYER_VARIABLE = re.compile(r"%_player\.[\w.$]+%")
# Drag items and drop targets carry an LMS label such as "Text-feld 3 - ".
LMS_PREFIX = re.compile(r"^[\w-]+ \d+(?: - |$)")


def load_js(path):
    """Return the JSON payload of a `window.globalProvideData(...)` file."""
    raw = path.read_text(encoding="utf-8-sig")
    match = re.match(r"window\.globalProvideData\('\w+', '(.*)'\);?\s*$", raw, re.DOTALL)
    if not match:
        raise ValueError(f"{path}: not a globalProvideData file")
    # The payload is a JavaScript string literal; escapes such as \' are not valid JSON.
    def unescape(m):
        esc = m.group(1)
        if esc[0] in "ux" and len(esc) > 1:
            return chr(int(esc[1:], 16))
        return JS_ESCAPES.get(esc, esc)

    return json.loads(re.sub(r"\\(u[0-9a-fA-F]{4}|x[0-9a-fA-F]{2}|.)", unescape, match.group(1), flags=re.DOTALL))


def clean(text):
    """Normalize one text and drop it (return "") if it is boilerplate."""
    text = text.replace("^%^", "%").replace("\r\n", "\n").replace("\r", "\n")
    text = EMAIL.sub("", text)
    text = PLAYER_VARIABLE.sub("", text)
    text = CLICK_HINT.sub(" ", text)
    text = re.sub(r"\t+", "\t", text)
    text = re.sub(r"[  ]+", " ", text)
    lines = [line.strip() for line in text.split("\n")]
    text = "\n".join(line for line in lines if line).strip()
    if BOILERPLATE.fullmatch(text) or not any(char.isalnum() for char in text):
        return ""
    return text


def vartext(textdata):
    """Join the spans of a text into lines, one per block."""
    return "\n".join("".join(span["text"] for span in block["spans"]) for block in textdata["vartext"]["blocks"])


def own_texts(obj):
    """Texts stored on the object itself; child objects are handled separately."""
    found = []

    def walk(node):
        if isinstance(node, dict):
            if node.get("vartext"):
                found.append(vartext(node))
            for key, value in node.items():
                if key != "objects":
                    walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk({k: v for k, v in obj.items() if k != "objects"})
    return list(dict.fromkeys(found))


def flatten(objects, x0=0, y0=0):
    """Yield (object, absolute x, absolute y) for all nested objects."""
    for obj in objects:
        x, y = x0 + obj.get("xPos", 0), y0 + obj.get("yPos", 0)
        yield obj, x, y
        yield from flatten(obj.get("objects") or [], x, y)


def find_all(node, kind):
    """Yield all dicts of the given `kind` anywhere below node."""
    if isinstance(node, dict):
        if node.get("kind") == kind:
            yield node
        for value in node.values():
            yield from find_all(value, kind)
    elif isinstance(node, list):
        for item in node:
            yield from find_all(item, kind)


def layer_texts(layer):
    """Texts of one layer in reading order (top to bottom, then left to right)."""
    items = []
    for obj, x, y in flatten(layer.get("objects") or []):
        for text in own_texts(obj):
            text = clean(text)
            if text:
                items.append({"object_id": obj.get("id"), "text": text, "_pos": (y, x)})
    # Objects whose tops differ by at most ROW_TOLERANCE pixels form one row, read left to right.
    items.sort(key=lambda item: item["_pos"])
    row_top = None
    for item in items:
        y, x = item["_pos"]
        if row_top is None or y - row_top > ROW_TOLERANCE:
            row_top = y
        item["_pos"] = (row_top, x)
    items.sort(key=lambda item: item["_pos"])
    # Each drop-down of a sequence question repeats all items; keep the first occurrence.
    seen = set()
    unique = []
    for item in items:
        if item["text"] not in seen:
            seen.add(item["text"])
            del item["_pos"]
            unique.append(item)
    return unique


def classify_layers(slide, interactions):
    """Map each shown layer ID to "popup" or "feedback"; layers missing from the map are never shown.

    Pop-ups are opened by a button on the base layer or on another pop-up. Feedback layers are
    opened by the answer evaluation in data.js, from another feedback layer (e.g. a solution) or
    by slide events (e.g. the quiz result).
    """
    def targets(node):
        return {a["objRef"]["value"].split(".")[-1] for a in find_all(node, "show_slidelayer")}

    from_layer = {}
    for layer in slide["slideLayers"]:
        for target in targets(layer.get("objects") or []):
            from_layer.setdefault(target, set()).add(layer.get("id"))
    from_slide = targets({k: v for k, v in slide.items() if k != "slideLayers"})
    for layer in slide["slideLayers"]:
        from_slide |= targets({k: v for k, v in layer.items() if k != "objects"})

    feedback = targets(interactions) | from_slide
    changed = True
    while changed:
        new = {t for t, sources in from_layer.items() if sources & feedback} - feedback
        feedback |= new
        changed = bool(new)
    kinds = {t: "popup" for t in from_layer}
    kinds.update({t: "feedback" for t in feedback})
    return kinds


def read_menu(frame_xml):
    """Map slide ID to its title in the navigation menu."""
    menu = {}
    for link in ET.parse(frame_xml).iter("slidelink"):
        slide_id = link.get("slideid").split(".")[-1]
        menu[slide_id] = " ".join(link.get("displaytext").split())
    return menu


def reachable_scenes(data, slide_files):
    """Scenes that the learner can reach: the entry scene and every target of a slide jump."""
    targets = set()
    for node in [data] + list(slide_files.values()):
        for action in find_all(node, "gotoplay"):
            parts = action["objRef"]["value"].split(".")
            if len(parts) >= 2:
                targets.add(parts[1])
    entry = data["entryPoint"] if isinstance(data.get("entryPoint"), str) else ""
    targets.update(part for part in entry.split(".")[1:2])
    return targets


def strip_lms(text):
    return LMS_PREFIX.sub("", text).strip()


def extract_question(interaction, slide_id, slide, quiz_slides):
    """Question with its choices and solution; item texts come from the slide if possible."""
    objects = {obj.get("id"): obj for layer in slide["slideLayers"] for obj, _, _ in flatten(layer.get("objects") or [])}

    def item_text(item_id, lmstext):
        # The slide object keeps line breaks that lmstext loses. A drop-down slot of a sequence
        # question holds all items, so only an object with exactly one text is used.
        obj = objects.get(item_id.split("_", 1)[1])
        texts = [t for t in (clean(t) for t in own_texts(obj)) if t] if obj else []
        text = texts[0] if len(texts) == 1 else strip_lms(clean(lmstext))
        return text or None

    choices = [{"id": c["id"], "text": item_text(c["id"], c["lmstext"])} for c in interaction.get("choices", [])]
    statements = {s["id"]: item_text(s["id"], s["lmstext"]) for s in interaction.get("statements", [])}
    choice_text = {c["id"]: c["text"] for c in choices}
    correct = next(a for a in interaction["answers"] if a["status"] == "correct")
    rules = correct["evaluate"]["statements"]

    question = {
        "slide_id": slide_id,
        "interaction_id": interaction["id"],
        "in_quiz": slide_id in quiz_slides,
        "type": interaction["type"],
        "points": correct["points"],
        "choices": choices,
    }
    if interaction["type"] == "multipleresponse":
        question["correct"] = [choice_text[r["choiceid"].split(".", 1)[1]] for r in rules]
    elif interaction["type"] == "sequence":
        question["correct_order"] = [choice_text[r["choiceid"].split(".", 1)[1]] for r in rules]
    elif interaction["type"] == "matching":
        # A target of None is an unlabelled box on an image.
        question["correct_pairs"] = [
            {"item": choice_text[r["choiceid"].split(".", 1)[1]], "target": statements[r["statementid"].split(".", 1)[1]]}
            for r in rules
        ]
    else:
        raise ValueError(f"{slide_id}: unsupported question type {interaction['type']}")
    return question


def extract(export_dir):
    export_dir = Path(export_dir)
    js_dir = export_dir / "html5" / "data" / "js"
    data = load_js(js_dir / "data.js")
    menu = read_menu(export_dir / "story_content" / "frame.xml")
    quiz_slides = {ref["id"].split(".")[-1] for quiz in data["quizzes"] for ref in quiz["sliderefs"]}

    # Scene 0 holds player dialogs and has no slide files.
    content_scenes = [scene for scene in data["scenes"] if all((js_dir / f"{s['id']}.js").exists() for s in scene["slides"])]
    slide_files = {s["id"]: load_js(js_dir / f"{s['id']}.js") for scene in content_scenes for s in scene["slides"]}
    reachable = reachable_scenes(data, slide_files)

    result = {"source": export_dir.name, "scenes": [], "questions": [], "excluded": {"scenes": [], "layers": []}}
    for scene in content_scenes:
        if scene["id"] not in reachable:
            result["excluded"]["scenes"].append(scene["id"])
            continue
        scene_out = {"scene_id": scene["id"], "menu_title": menu.get(scene["slides"][0]["id"]), "slides": []}
        for slide_meta in scene["slides"]:
            slide_id = slide_meta["id"]
            slide = slide_files[slide_id]
            interactions = slide_meta.get("interactions", [])
            kinds = classify_layers(slide, interactions)

            layers = []
            for layer in slide["slideLayers"]:
                kind = "base" if layer.get("isBaseLayer") else kinds.get(layer["id"])
                if kind is None:
                    result["excluded"]["layers"].append({"slide_id": slide_id, "layer_id": layer["id"]})
                    continue
                layers.append({"layer_id": layer.get("id"), "kind": kind, "texts": layer_texts(layer)})

            scene_out["slides"].append({"slide_id": slide_id, "menu_title": menu.get(slide_id), "layers": layers})
            for interaction in interactions:
                question = extract_question(interaction, slide_id, slide, quiz_slides)
                # The export does not mark the question text; it is the base-layer text that is not an answer item.
                items = {c["text"] for c in question["choices"]} | {p["target"] for p in question.get("correct_pairs", [])}
                question["prompt"] = [t["text"] for t in layers[0]["texts"] if t["text"] not in items]
                result["questions"].append(question)
        result["scenes"].append(scene_out)
    return result


def main(argv):
    if len(argv) != 3:
        sys.exit(__doc__)
    result = extract(argv[1])
    out = Path(argv[2])
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv)
