"""Draw the prototype graph as SVG images for docs/0007-graph-structure.md.

- overview: every node except passages and answer options, in a force-directed layout
- slide 4.1: one topic across all layers, in columns (didactic | source | facts | concepts)

The layout is seeded, so the same graph.json gives the same images.

Usage:
    python prototype/graph/draw_graph.py prototype/graph/output/graph.json docs/images
"""

import json
import math
import random
import sys
from html import escape
from pathlib import Path

# (fill, stroke/text) per node kind; the same colours are used in both images
STYLE = {
    "Document": ("#444441", "#2C2C2A"), "Chapter": ("#534AB7", "#26215C"), "Part": ("#7F77DD", "#3C3489"),
    "Topic": ("#AFA9EC", "#3C3489"), "Slide": ("#CECBF6", "#534AB7"), "Popup": ("#EEEDFE", "#534AB7"),
    "Feedback": ("#F1EFE8", "#888780"), "Passage": ("#F1EFE8", "#5F5E5A"),
    "LearningObjective": ("#F0997B", "#712B13"), "Question": ("#FAC775", "#633806"),
    "Fact": ("#ED93B1", "#72243E"), "Concept": ("#9FE1CB", "#085041"),
}
EDGE_COLOR = {"structure": "#B4B2A9", "didactic": "#D85A30", "fact": "#D4537E", "concept": "#1D9E75"}
DIDACTIC = {"HAS_OBJECTIVE", "HAS_QUESTION", "COVERS", "ASSESSES", "TESTS", "JUSTIFIED_BY", "REFERS_TO"}
FACT = {"SUBJECT", "OBJECT", "CONDITION", "IMPLIES", "RECOMMENDS", "QUALIFIES", "DEPENDS_ON", "SUPPORTED_BY"}
FONT = 'font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="12"'


def kind(node):
    return next(l for l in reversed(node["labels"]) if l in STYLE)


def edge_group(edge):
    if edge["type"] in DIDACTIC:
        return "didactic"
    if edge["type"] in FACT:
        return "fact"
    if edge["type"] in ("HAS_SECTION", "HAS_PASSAGE", "HAS_OPTION"):
        return "structure"
    return "concept"


def short(text, n):
    text = " ".join(str(text).split())
    return text if len(text) <= n else text[: n - 1] + "…"


def svg(width, height, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" {FONT}>\n<rect width="100%" height="100%" fill="#ffffff"/>\n'
            + "\n".join(body) + "\n</svg>\n")


def legend(items, x, y):
    out = []
    for label, color, is_line in items:
        if is_line:
            out.append(f'<line x1="{x}" y1="{y - 4}" x2="{x + 22}" y2="{y - 4}" stroke="{color}" stroke-width="2"/>')
        else:
            out.append(f'<rect x="{x + 5}" y="{y - 10}" width="12" height="12" rx="2" fill="{color}"/>')
        out.append(f'<text x="{x + 28}" y="{y}" fill="#444441">{escape(label)}</text>')
        x += 40 + len(label) * 6.5
    return out


def force_layout(ids, links, width, height, seed=7, iterations=400):
    """Fruchterman-Reingold layout, pure Python (the graphs here have a few hundred nodes)."""
    rnd = random.Random(seed)
    pos = {i: [rnd.uniform(0, width), rnd.uniform(0, height)] for i in ids}
    k = math.sqrt(width * height / len(ids)) * 1.1
    temp = width / 8
    for _ in range(iterations):
        disp = {i: [0.0, 0.0] for i in ids}
        for a_i, a in enumerate(ids):
            ax, ay = pos[a]
            for b in ids[a_i + 1:]:
                dx, dy = ax - pos[b][0], ay - pos[b][1]
                d2 = dx * dx + dy * dy or 0.01
                f = k * k / d2
                disp[a][0] += dx * f; disp[a][1] += dy * f
                disp[b][0] -= dx * f; disp[b][1] -= dy * f
        for a, b in links:
            dx, dy = pos[a][0] - pos[b][0], pos[a][1] - pos[b][1]
            d = math.hypot(dx, dy) or 0.01
            f = d / k
            disp[a][0] -= dx * f; disp[a][1] -= dy * f
            disp[b][0] += dx * f; disp[b][1] += dy * f
        for i in ids:
            dx, dy = disp[i]
            d = math.hypot(dx, dy) or 0.01
            pos[i][0] += dx / d * min(d, temp)
            pos[i][1] += dy / d * min(d, temp)
            # weak pull to the centre keeps unconnected parts on the canvas
            pos[i][0] += (width / 2 - pos[i][0]) * 0.01
            pos[i][1] += (height / 2 - pos[i][1]) * 0.01
        temp *= 0.985
    xs, ys = [p[0] for p in pos.values()], [p[1] for p in pos.values()]
    sx, sy = (width - 40) / (max(xs) - min(xs) or 1), (height - 40) / (max(ys) - min(ys) or 1)
    return {i: (20 + (p[0] - min(xs)) * sx, 20 + (p[1] - min(ys)) * sy) for i, p in pos.items()}


def overview(graph, width=1600, height=1150):
    all_nodes = {n["id"]: n for n in graph["nodes"]}
    nodes = {i: n for i, n in all_nodes.items() if not {"Passage", "AnswerOption"} & set(n["labels"])}
    edges = [e for e in graph["edges"] if e["from"] in nodes and e["to"] in nodes]
    # Without passages, MENTIONS would vanish; lift it to the slide that holds the passage instead.
    parent = {e["to"]: e["from"] for e in graph["edges"] if e["type"] in ("HAS_SECTION", "HAS_PASSAGE")}

    def slide_of(i):
        while i in parent and not {"Topic", "Slide"} & set(all_nodes[i]["labels"]):
            i = parent[i]
        return i

    lifted = dict.fromkeys((slide_of(e["from"]), e["to"]) for e in graph["edges"] if e["type"] == "MENTIONS")
    edges += [{"type": "MENTIONS", "from": a, "to": b, "props": {"lifted": True}} for a, b in lifted if a in nodes]
    ids = list(nodes)
    pos = force_layout(ids, [(e["from"], e["to"]) for e in edges], width, height - 80)

    body = []
    for e in edges:
        (x1, y1), (x2, y2) = pos[e["from"]], pos[e["to"]]
        if e["props"].get("lifted"):
            style = f'stroke="{EDGE_COLOR["concept"]}" stroke-width="0.6" opacity="0.35" stroke-dasharray="1 2"'
        else:
            dashed = ' stroke-dasharray="3 3"' if e["props"].get("derived") else ""
            style = f'stroke="{EDGE_COLOR[edge_group(e)]}" stroke-width="0.8" opacity="0.7"{dashed}'
        body.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" {style}/>')
    labelled = {"Document", "Chapter", "Part", "Topic", "LearningObjective", "Question", "Concept"}
    size = {"Document": 9, "Chapter": 8, "Part": 6, "Topic": 7, "LearningObjective": 7, "Question": 6, "Concept": 6, "Fact": 5}
    for i in ids:
        n, (x, y) = nodes[i], pos[i]
        k = kind(n)
        fill, stroke = STYLE[k]
        r = size.get(k, 3.5)
        shape = (f'<rect x="{x - r:.1f}" y="{y - r:.1f}" width="{2 * r}" height="{2 * r}" fill="{fill}" stroke="{stroke}" stroke-width="0.6"/>'
                 if k == "Fact" else f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="0.6"/>')
        body.append(shape)
        if k in labelled:
            p = n["props"]
            text = {"Topic": p.get("number"), "LearningObjective": p.get("name"), "Question": p.get("name")}.get(k) or short(p.get("name", ""), 28)
            weight = ' font-weight="600"' if k in ("Document", "Chapter") else ""
            # keep labels near the right edge inside the canvas
            anchor, tx = ("end", x - r - 3) if x > width - 200 else ("start", x + r + 3)
            body.append(f'<text x="{tx:.1f}" y="{y + 4:.1f}" text-anchor="{anchor}" fill="{stroke}"{weight}>{escape(str(text))}</text>')
    counts = {}
    for n in nodes.values():
        counts[kind(n)] = counts.get(kind(n), 0) + 1
    names = [("Chapter", "Chapter"), ("Topic", "Topic"), ("Popup", "Pop-up"), ("Feedback", "Feedback"),
             ("Slide", "Other slide"), ("LearningObjective", "Learning objective"), ("Question", "Question"),
             ("Fact", "Fact"), ("Concept", "Concept")]
    body += legend([(f"{label} ({counts.get(k, 0)})", STYLE[k][0], False) for k, label in names], 20, height - 40)
    body += legend([("structure", EDGE_COLOR["structure"], True), ("didactic", EDGE_COLOR["didactic"], True),
                    ("fact roles", EDGE_COLOR["fact"], True), ("concept (dashed: derived from facts)", EDGE_COLOR["concept"], True),
                    ("slide mentions concept (dotted)", EDGE_COLOR["concept"], True)], 20, height - 16)
    return svg(width, height, body)


def slide_detail(graph, slide_id):
    nodes = {n["id"]: n for n in graph["nodes"]}
    edges = graph["edges"]
    out_of = lambda t, f: [e["to"] for e in edges if e["type"] == t and e["from"] == f]
    into = lambda t, to: [e["from"] for e in edges if e["type"] == t and e["to"] == to]

    topic = f"section:{slide_id}"
    sections = [topic, *out_of("HAS_SECTION", topic)]
    passages = [p for s in sections for p in out_of("HAS_PASSAGE", s)]
    facts = list(dict.fromkeys(f for p in passages for f in into("SUPPORTED_BY", p) if f.startswith("fact:")))
    passages = [p for p in passages if any(f in facts for f in into("SUPPORTED_BY", p))]
    concepts = list(dict.fromkeys(c for f in facts for e in edges if e["from"] == f and e["to"].startswith("concept:")
                                  for c in [e["to"]]))
    questions = list(dict.fromkeys(q for f in facts for q in into("TESTS", f)))
    didactic = [*into("COVERS", topic), *questions]

    def label(i):
        p, k = nodes[i]["props"], kind(nodes[i])
        if k == "Fact":
            return short(p["statement"], 44)
        if k == "Passage":
            return short(p["text"], 36)
        if k == "Topic":
            return f"{p['number']} {p['name']}"
        if k == "Popup":
            return "Pop-up: " + short(p["name"], 26)
        return short(p.get("name", i), 30)

    columns = [("Didactic", didactic, 20, 130), ("Source", [*sections, *passages], 190, 270),
               ("Facts", facts, 520, 320), ("Concepts", concepts, 900, 190)]
    row, top, h = 30, 60, 22
    rows = max(len(c[1]) for c in columns)
    height = top + rows * row + 60
    pos, body = {}, []
    for title, ids, x, w in columns:
        offset = top + (rows - len(ids)) * row / 2
        body.append(f'<text x="{x + w / 2}" y="38" text-anchor="middle" font-size="14" font-weight="600" fill="#2C2C2A">{title}</text>')
        for n, i in enumerate(ids):
            pos[i] = (x, offset + n * row, w)
    for e in edges:
        if e["from"] not in pos or e["to"] not in pos or e["props"].get("derived"):
            continue
        (x1, y1, w1), (x2, y2, w2) = pos[e["from"]], pos[e["to"]]
        y1, y2 = y1 + h / 2, y2 + h / 2
        if x1 == x2:
            d = f"M{x1},{y1} C{x1 - 40},{y1} {x2 - 40},{y2} {x2},{y2}"
        else:
            sx, ex = (x1 + w1, x2) if x1 < x2 else (x1, x2 + w2)
            mx = (sx + ex) / 2
            d = f"M{sx},{y1} C{mx},{y1} {mx},{y2} {ex},{y2}"
        body.append(f'<path d="{d}" fill="none" stroke="{EDGE_COLOR[edge_group(e)]}" stroke-width="1" opacity="0.65"/>')
    for i, (x, y, w) in pos.items():
        fill, stroke = STYLE[kind(nodes[i])]
        body.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{fill}" fill-opacity="0.35" stroke="{stroke}"/>'
                    f'<text x="{x + 7}" y="{y + 15}" fill="{stroke}">{escape(label(i))}</text>')
    body += legend([("structure", EDGE_COLOR["structure"], True), ("didactic", EDGE_COLOR["didactic"], True),
                    ("fact roles (SUBJECT, CONDITION, IMPLIES, …, SUPPORTED_BY)", EDGE_COLOR["fact"], True)], 20, height - 20)
    return svg(1110, height, body)


def main(argv):
    if len(argv) != 3:
        print(__doc__)
        return 1
    graph = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    out = Path(argv[2])
    out.mkdir(parents=True, exist_ok=True)
    (out / "0007-prototype-overview.svg").write_text(overview(graph), encoding="utf-8", newline="\n")
    (out / "0007-prototype-4.1.svg").write_text(slide_detail(graph, "5cxhcjlTRsl"), encoding="utf-8", newline="\n")
    print(f"images -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
