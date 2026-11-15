"""Build the prototype of graph v2 for one module (docs/graph/v2.md).

The structure layer is derived from the extraction output. The content layer and its evidence come
from the hand-made prototype/graph/v2/statements.json and are checked against the model: closed lists
of concept types, predicates with their signatures, modalities and operators, and every quote verbatim
in its segment. Nothing is written if the check finds a problem.

Writes graph.json (nodes and edges, independent of any graph database) and viewer.html (interactive view).

Usage:
    python prototype/graph/v2/build_graph.py data/extracted/ketonkoerper.json prototype/graph/v2/output
"""

import collections
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STATEMENTS = HERE / "statements.json"
TEMPLATE = HERE / "viewer_template.html"

DOMAIN = "Diabetologie"
# The export does not number chapters. In Ketonkörper they are the scenes 3 to 8, and the first slide
# of a chapter is its start slide, which carries no number.
CHAPTER_SCENES = range(2, 8)

TYPES = ["Substance", "Process", "Condition", "Drug", "Test", "Anatomy", "Finding", "Intervention"]
# predicate -> (category, allowed subject types, allowed object types)
PREDICATES = {
    "IS_A": ("taxonomy", None, None),  # same type on both sides
    "PART_OF": ("taxonomy", ["Process", "Anatomy"], ["Process", "Anatomy"]),
    "CONVERTED_TO": ("metabolism", ["Substance"], ["Substance"]),
    "PRODUCES": ("metabolism", ["Process"], ["Substance"]),
    "CONSUMES": ("metabolism", ["Process"], ["Substance"]),
    "REQUIRES": ("metabolism", ["Process"], ["Substance"]),
    "LOCATED_IN": ("location", ["Process", "Substance"], ["Anatomy"]),
    "USED_IN": ("location", ["Substance"], ["Anatomy"]),
    "EXCRETED_VIA": ("location", ["Substance"], ["Anatomy"]),
    "MEASURES": ("diagnostics", ["Test"], ["Substance"]),
    "MEASURED_IN": ("diagnostics", ["Substance", "Test"], ["Anatomy"]),
    "INDICATES": ("diagnostics", ["Substance", "Test", "Finding"], ["Finding", "Condition"]),
    "INTERFERES_WITH": ("diagnostics", ["Drug", "Substance", "Condition"], ["Test"]),
    "CAUSES": ("causation", ["Condition", "Process", "Drug", "Substance"], ["Condition", "Process", "Finding"]),
    "INCREASES": ("causation", ["Condition", "Process", "Drug", "Substance", "Intervention"], ["Substance", "Test", "Process"]),
    "DECREASES": ("causation", ["Condition", "Process", "Drug", "Substance", "Intervention"], ["Substance", "Test", "Process"]),
    "INDICATION_FOR": ("recommendation", ["Condition", "Finding"], ["Test", "Intervention", "Drug"]),
}
MODALITIES = ["muss", "soll", "sollte", "kann"]
OPERATORS = ["<", "<=", ">", ">=", "=", "between"]
ROLES = ["subject", "object", "condition"]
NOT_MAPPED = ["no_predicate", "signature", "not_a_relation", "not_extracted"]

CONCEPT_KEYS = {"name", "type", "aliases", "unconfirmed_aliases", "normalized_from"}
STATEMENT_KEYS = {"id", "predicate", "subject", "object", "conditions", "modality", "hedged", "timing",
                  "from_context", "text", "note", "evidence"}
CONSTRAINT_KEYS = ["operator", "value", "value_max", "unit", "alt", "approx", "duration", "negated", "qualifier"]


class Graph:
    def __init__(self):
        self.nodes, self.edges, self.ids = [], [], set()

    def node(self, id_, labels, **props):
        if id_ in self.ids:
            raise ValueError(f"duplicate node {id_}")
        self.ids.add(id_)
        self.nodes.append({"id": id_, "labels": labels, "props": drop_none(props)})

    def edge(self, type_, from_, to, **props):
        for end in (from_, to):
            if end not in self.ids:
                raise ValueError(f"{type_} edge to unknown node {end}")
        self.edges.append({"type": type_, "from": from_, "to": to, "props": drop_none(props)})


def drop_none(props):
    return {k: v for k, v in props.items() if v is not None}


def load_structure(extracted, titles):
    """Sections (scenes), slides and segments of the module. A segment is a base layer or a pop-up."""
    sections, segments = [], {}
    for index, scene in enumerate(extracted["scenes"]):
        chapter = index - CHAPTER_SCENES.start + 1 if index in CHAPTER_SCENES else None
        section = {"id": scene["scene_id"], "title": scene["menu_title"], "chapter": chapter, "slides": []}
        for position, slide in enumerate(scene["slides"]):
            base = next(layer for layer in slide["layers"] if layer["kind"] == "base")
            first_line = base["texts"][0]["text"].split("\n")[0].strip() if base["texts"] else None
            title = slide["menu_title"] or first_line
            entry = {"id": slide["slide_id"], "title": title, "segments": [],
                     "number": f"{chapter}.{position}" if chapter and position else None}
            for layer in slide["layers"]:
                if layer["kind"] == "feedback":
                    continue
                segment_id = layer["layer_id"] or f"{slide['slide_id']}:base"
                segments[segment_id] = {"kind": layer["kind"], "blocks": [t["text"] for t in layer["texts"]],
                                        "title": title if layer["kind"] == "base" else titles.get(segment_id)}
                entry["segments"].append(segment_id)
            section["slides"].append(entry)
        sections.append(section)
    return sections, segments


def constraint(role):
    """Readable form of the value constraint on a role edge."""
    number = lambda v: str(v).replace(".", ",") if isinstance(v, float) else str(v)
    parts = ["NOT"] if role.get("negated") else []
    operator = role.get("operator")
    if operator == "between":
        parts.append(f"{number(role['value'])} bis {number(role['value_max'])}")
    elif operator:
        parts.append(("ca. " if role.get("approx") else "") + f"{operator} {number(role['value'])}")
    if operator and role.get("unit"):
        parts.append(role["unit"])
    if role.get("duration"):
        parts.append(f"({role['duration']})")
    if role.get("qualifier"):
        parts.append(role["qualifier"])
    return " ".join(parts)


def identity(statement):
    """Two statements with the same identity are one statement with several evidences."""
    role = lambda r: json.dumps(r, sort_keys=True, ensure_ascii=False)
    return (statement["predicate"], role(statement["subject"]), statement["object"],
            tuple(sorted(role(c) for c in statement.get("conditions", []))),
            statement.get("modality"), statement.get("hedged", False), statement.get("timing"))


def verbatim(quote, segment):
    return any(quote in block for block in segment["blocks"])


def check(mapping, segments):
    """Problems that make the mapping invalid under the model. An empty list means it is valid."""
    problems = []
    concepts = {c["name"]: c for c in mapping["concepts"]}
    names = collections.Counter()
    for c in mapping["concepts"]:
        names.update([c["name"]] + c.get("aliases", []) + c.get("unconfirmed_aliases", []))
        if set(c) - CONCEPT_KEYS:
            problems.append(f"{c['name']}: unknown property {sorted(set(c) - CONCEPT_KEYS)}")
        if c["type"] not in TYPES:
            problems.append(f"{c['name']}: unknown type {c['type']}")
        source = c.get("normalized_from")
        if source and not any(verbatim(source, segment) for segment in segments.values()):
            problems.append(f"{c['name']}: normalized_from is not verbatim in the module")
    problems += [f"name or alias used twice: {name}" for name, n in names.items() if n > 1]

    used, ids, identities = set(), set(), {}
    for s in mapping["statements"]:
        sid = s["id"]
        if not re.fullmatch(r"S\d{3}", sid) or sid in ids:
            problems.append(f"{sid}: id is malformed or used twice")
        ids.add(sid)
        if set(s) - STATEMENT_KEYS:
            problems.append(f"{sid}: unknown property {sorted(set(s) - STATEMENT_KEYS)}")
        roles = [s["subject"]] + s.get("conditions", [])
        role_names = [r["concept"] for r in roles] + [s["object"]]
        unknown = [name for name in role_names if name not in concepts]
        problems += [f"{sid}: unknown concept {name}" for name in unknown]
        used.update(role_names)
        for r in roles:
            if set(r) - {"concept", *CONSTRAINT_KEYS}:
                problems.append(f"{sid}: unknown role property {sorted(set(r) - {'concept', *CONSTRAINT_KEYS})}")
            if "operator" in r and (r["operator"] not in OPERATORS or "value" not in r):
                problems.append(f"{sid}: operator {r['operator']} is unknown or has no value")
            if ("operator" not in r and "value" in r) or (r.get("operator") == "between") != ("value_max" in r):
                problems.append(f"{sid}: value and operator of {r['concept']} do not fit")
        if s["predicate"] not in PREDICATES:
            problems.append(f"{sid}: unknown predicate {s['predicate']}")
        elif not unknown:
            _, subjects, objects = PREDICATES[s["predicate"]]
            st, ot = concepts[s["subject"]["concept"]]["type"], concepts[s["object"]]["type"]
            if not (st == ot if subjects is None else st in subjects and ot in objects):
                problems.append(f"{sid}: {s['predicate']} does not allow {st} -> {ot}")
        if "modality" in s and s["modality"] not in MODALITIES:
            problems.append(f"{sid}: unknown modality {s['modality']}")
        if s.get("hedged", True) is not True:
            problems.append(f"{sid}: hedged is either true or absent")
        if set(s.get("from_context", [])) - set(ROLES):
            problems.append(f"{sid}: from_context names an unknown role")
        if not s.get("text") or not s.get("evidence"):
            problems.append(f"{sid}: text or evidence is missing")
        for e in s.get("evidence", []):
            if e["segment"] not in segments:
                problems.append(f"{sid}: unknown segment {e['segment']}")
            elif not verbatim(e["quote"], segments[e["segment"]]):
                problems.append(f"{sid}: quote is not verbatim in {e['segment']}: {e['quote']!r}")
        if identity(s) in identities:
            problems.append(f"{sid}: same statement as {identities[identity(s)]}; merge the evidence")
        identities[identity(s)] = sid

    problems += [f"concept without statement: {name}" for name in concepts if name not in used]
    for entry in mapping["not_mapped"]:
        if entry["category"] not in NOT_MAPPED:
            problems.append(f"not_mapped: unknown category {entry['category']}")
        if entry["segment"] not in segments or not verbatim(entry["quote"], segments[entry["segment"]]):
            problems.append(f"not_mapped: quote is not verbatim: {entry['quote']!r}")
    for segment_id in mapping["segment_titles"]:
        if segment_id != "_comment" and segments.get(segment_id, {}).get("kind") != "popup":
            problems.append(f"title for a segment that is not a pop-up: {segment_id}")
    return problems


def build(extracted, mapping):
    sections, segments = load_structure(extracted, mapping["segment_titles"])
    problems = check(mapping, segments)
    if problems:
        raise ValueError("the mapping does not fit the model:\n" + "\n".join(problems))

    g = Graph()
    domain, course = f"domain:{DOMAIN}", f"course:{extracted['source']}"
    g.node(domain, ["Structure", "Domain"], title=DOMAIN)
    g.node(course, ["Structure", "Course"], title=extracted["source"])
    g.edge("CONTAINS", domain, course, order=1)
    for order, section in enumerate(sections, 1):
        g.node(section["id"], ["Structure", "Section"], title=section["title"], chapter=section["chapter"])
        g.edge("CONTAINS", course, section["id"], order=order)
        for position, slide in enumerate(section["slides"], 1):
            g.node(slide["id"], ["Structure", "Slide"], title=slide["title"], number=slide["number"])
            g.edge("CONTAINS", section["id"], slide["id"], order=position)
            for index, segment_id in enumerate(slide["segments"], 1):
                segment = segments[segment_id]
                g.node(segment_id, ["Structure", "Segment"], kind=segment["kind"], title=segment["title"])
                g.edge("CONTAINS", slide["id"], segment_id, order=index)

    concept_id = lambda name: f"concept:{name}"
    for c in mapping["concepts"]:
        g.node(concept_id(c["name"]), ["Content", "Concept"], name=c["name"], type=c["type"],
               aliases=c.get("aliases"), unconfirmed_aliases=c.get("unconfirmed_aliases"),
               normalized_from=c.get("normalized_from"))
    values = lambda role: {k: role[k] for k in CONSTRAINT_KEYS if k in role}
    for s in mapping["statements"]:
        g.node(s["id"], ["Content", "Statement"], predicate=s["predicate"], category=PREDICATES[s["predicate"]][0],
               label=f"{s['subject']['concept']} {s['predicate']} {s['object']}", text=s["text"],
               modality=s.get("modality"), hedged=s.get("hedged"), timing=s.get("timing"),
               from_context=s.get("from_context"))
        g.edge("SUBJECT", s["id"], concept_id(s["subject"]["concept"]), **values(s["subject"]))
        g.edge("OBJECT", s["id"], concept_id(s["object"]))
        for c in s.get("conditions", []):
            g.edge("CONDITION", s["id"], concept_id(c["concept"]), **values(c))
        for e in s["evidence"]:
            g.edge("EVIDENCE", s["id"], e["segment"], quote=e["quote"])
    return g


def to_json(g):
    """One node or edge per line, so changes show up as small diffs."""
    dump = lambda x: json.dumps(x, ensure_ascii=False)
    return ('{"nodes": [\n' + ",\n".join(dump(n) for n in g.nodes) + '\n],\n"edges": [\n'
            + ",\n".join(dump(e) for e in g.edges) + "\n]}\n")


def viewer_data(g, notes):
    """Nodes and edges for the viewer. Every node lists the views it appears in and its detail rows."""
    node = {n["id"]: n for n in g.nodes}
    kind = lambda n: n["labels"][1].lower()
    short = lambda text, n=30: text if len(text) <= n else text[: n - 1].rstrip() + "…"
    parent = {e["to"]: e["from"] for e in g.edges if e["type"] == "CONTAINS"}
    outgoing = collections.defaultdict(list)
    for e in g.edges:
        outgoing[e["from"]].append(e)
    number = lambda segment_id: node[parent[segment_id]]["props"].get("number")
    evidence = collections.Counter(e["to"] for e in g.edges if e["type"] == "EVIDENCE")
    mapped_slides = sorted({number(segment_id) for segment_id in evidence})

    nodes, edges, compact = [], [], []
    concept_views = collections.defaultdict(set)
    for n in g.nodes:
        p = n["props"]
        if kind(n) == "statement":
            roles = [e for e in outgoing[n["id"]] if e["type"] != "EVIDENCE"]
            quotes = [e for e in outgoing[n["id"]] if e["type"] == "EVIDENCE"]
            slides = sorted({number(e["to"]) for e in quotes})
            info = [["Statement", p["label"]], ["Id", n["id"]], ["Category", p["category"]], ["Text", p["text"]]]
            info += [[key.capitalize(), p[key]] for key in ("modality", "timing") if key in p]
            if p.get("hedged"):
                info.append(["Hedged", "the source limits the statement (ggf., meistens, in Einzelfällen, …)"])
            info += [[f"Quote ({number(e['to'])})", e["props"]["quote"].replace("\t", " | ").replace("\n", " / ")]
                     for e in quotes]
            if p.get("from_context"):
                info.append(["From context", ", ".join(p["from_context"]) + " not named in the quote"])
            if n["id"] in notes:
                info.append(["Note", notes[n["id"]]])
            nodes.append({"id": n["id"], "label": p["predicate"], "kind": "statement",
                          "views": ["content"] + slides, "info": info})
            for e in roles:
                extra = constraint(e["props"])
                edges.append({"from": n["id"], "to": e["to"], "kind": "role",
                              "label": e["type"] + (f"\n{extra}" if extra else "")})
                concept_views[e["to"]].update(slides)
            edges += [{"from": n["id"], "to": e["to"], "label": "EVIDENCE", "kind": "evidence"} for e in quotes]
            ends = {e["type"]: e["to"] for e in roles}
            compact.append({"from": ends["SUBJECT"], "to": ends["OBJECT"], "label": p["predicate"], "statement": n["id"]})
        elif kind(n) != "concept":
            slide = n["id"] if kind(n) == "slide" else parent[n["id"]] if kind(n) == "segment" else None
            views = ["structure"] + ([node[slide]["props"]["number"]] if slide and node[slide]["props"].get("number") in mapped_slides else [])
            title = p.get("title") or ""
            if kind(n) == "section":
                title = (f"{p['chapter']} " if "chapter" in p else "") + (title or "(no menu title)")
            if kind(n) == "slide":
                title = (f"{p['number']} " if "number" in p else "") + title
            if kind(n) == "segment":
                where = node[slide]["props"].get("number") or short(node[slide]["props"].get("title", ""), 20)
                title = f"{where} base" if p["kind"] == "base" else f"{where} pop-up {p.get('title', '')}".rstrip()
            info = [[n["labels"][1], title], ["Layer", "structure"]]
            entry = {"id": n["id"], "kind": kind(n), "views": views, "info": info, "label": short(title, 34)}
            if kind(n) == "slide":
                entry.update(short=short(title, 26), label=f"Slide {p['number']}" if len(views) > 1 else short(title, 26))
            if kind(n) == "segment":
                info.append(["Statements", str(evidence[n["id"]]) if len(views) > 1 else "slide not mapped yet"])
                entry.update(short=p["kind"].replace("popup", "pop-up"), label=title.replace(" pop-up ", "\npop-up "),
                             mapped=n["id"] in evidence)
            nodes.append(entry)
    edges += [{"from": e["from"], "to": e["to"], "label": "CONTAINS", "kind": "contains"}
              for e in g.edges if e["type"] == "CONTAINS"]
    for n in g.nodes:
        if kind(n) == "concept":
            p = n["props"]
            info = [["Concept", p["name"]], ["Type", p["type"]]]
            info += [[label, ", ".join(p[key])] for key, label in
                     (("aliases", "Aliases"), ("unconfirmed_aliases", "Aliases to confirm")) if key in p]
            if "normalized_from" in p:
                info.append(["Normalised from", p["normalized_from"]])
            info.append(["Slides", ", ".join(sorted(concept_views[n["id"]]))])
            nodes.append({"id": n["id"], "label": p["name"], "kind": "concept",
                          "views": ["content"] + sorted(concept_views[n["id"]]), "info": info})
    return {"nodes": nodes, "edges": edges, "compact": compact, "slides": mapped_slides}


def viewer(g, notes):
    data = json.dumps(viewer_data(g, notes), ensure_ascii=False, separators=(",", ":"))
    return TEMPLATE.read_text(encoding="utf-8").replace("__DATA__", data.replace("</", "<\\/"))


def main(argv):
    if len(argv) != 3:
        print(__doc__)
        return 1
    extracted = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    mapping = json.loads(STATEMENTS.read_text(encoding="utf-8"))
    try:
        g = build(extracted, mapping)
    except ValueError as error:
        print(error)
        return 1
    notes = {s["id"]: s["note"] for s in mapping["statements"] if "note" in s}
    out = Path(argv[2])
    out.mkdir(parents=True, exist_ok=True)
    (out / "graph.json").write_text(to_json(g), encoding="utf-8", newline="\n")
    (out / "viewer.html").write_text(viewer(g, notes), encoding="utf-8", newline="\n")
    print(f"{len(g.nodes)} nodes, {len(g.edges)} edges -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
