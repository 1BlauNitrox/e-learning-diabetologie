"""Build the prototype knowledge graph of one module (docs/0007-graph-structure.md).

The source layer, the questions and the passage-to-concept index are derived from the
extraction output by rules. Names, learning-objective and test mappings, concepts and
facts come from the hand-made prototype/graph/manual.json.

Writes graph.json (nodes and edges) and graph.cypher (loads the same graph into Neo4j).

Usage:
    python prototype/build_graph.py data/extracted/ketonkoerper.json prototype/graph
"""

import json
import re
import sys
from pathlib import Path

MANUAL = Path(__file__).resolve().parent / "graph" / "manual.json"
NAME_LENGTH = 80


class Graph:
    def __init__(self):
        self.nodes, self.edges, self.ids = [], [], set()

    def node(self, id_, labels, **props):
        if id_ in self.ids:
            return
        self.ids.add(id_)
        self.nodes.append({"id": id_, "labels": labels, "props": drop_none(props)})

    def edge(self, type_, from_, to, **props):
        for end in (from_, to):
            if end not in self.ids:
                raise ValueError(f"{type_} edge to unknown node {end}")
        self.edges.append({"type": type_, "from": from_, "to": to, "props": drop_none(props)})


def drop_none(props):
    return {k: v for k, v in props.items() if v is not None}


def short_name(text):
    line = text.strip().split("\n")[0].strip()
    return line if len(line) <= NAME_LENGTH else line[: NAME_LENGTH - 1] + "…"


def concept_id(name):
    return f"concept:{name}"


def mention_pattern(concept):
    # Prefix boundary only, so inflected forms ("SGLT2-Inhibitoren", "Kohlenhydraten") still match.
    terms = sorted([concept["name"], *concept.get("aliases", [])], key=len, reverse=True)
    return re.compile(r"(?<!\w)(?:" + "|".join(re.escape(t) for t in terms) + ")", re.IGNORECASE)


def build(extracted, manual):
    g = Graph()
    chapters = {k: v for k, v in manual["chapters"].items() if not k.startswith("_")}
    topics = {k: v for k, v in manual["topics"].items() if not k.startswith("_")}
    topic_ids = {number: f"section:{slide}" for slide, (number, _) in topics.items()}
    chapter_ids = {f"ch{number}": f"section:{scene}" for scene, (number, _) in chapters.items()}

    # Source layer: module, scenes, slides, layers, text blocks
    doc = "document:" + extracted["source"]
    g.node(doc, ["Document"], name=extracted["source"])
    passages = {}
    for s_order, scene in enumerate(extracted["scenes"], 1):
        scene_id = f"section:{scene['scene_id']}"
        if scene["scene_id"] in chapters:
            number, name = chapters[scene["scene_id"]]
            g.node(scene_id, ["Section", "Chapter"], name=name, number=str(number), source_id=scene["scene_id"])
        else:
            first = next((t["text"] for l in scene["slides"][0]["layers"] for t in l["texts"]), scene["scene_id"])
            g.node(scene_id, ["Section", "Part"], name=scene["menu_title"] or short_name(first), source_id=scene["scene_id"])
        g.edge("HAS_SECTION", doc, scene_id, order=s_order)

        for sl_order, slide in enumerate(scene["slides"], 1):
            slide_id = f"section:{slide['slide_id']}"
            if slide["slide_id"] in topics:
                number, name = topics[slide["slide_id"]]
                g.node(slide_id, ["Section", "Topic"], name=name, number=number, source_id=slide["slide_id"])
            else:
                first = next((t["text"] for l in slide["layers"] for t in l["texts"]), slide["slide_id"])
                g.node(slide_id, ["Section", "Slide"], name=short_name(first), source_id=slide["slide_id"])
            g.edge("HAS_SECTION", scene_id, slide_id, order=sl_order)

            l_order = 0
            for layer in slide["layers"]:
                owner = slide_id
                if layer["kind"] != "base":
                    l_order += 1
                    owner = f"section:{slide['slide_id']}/{layer['layer_id']}"
                    first = layer["texts"][0]["text"] if layer["texts"] else layer["layer_id"]
                    g.node(owner, ["Section", layer["kind"].capitalize()], name=short_name(first),
                           source_id=f"{slide['slide_id']}/{layer['layer_id']}")
                    g.edge("HAS_SECTION", slide_id, owner, order=l_order)
                for p_order, text in enumerate(layer["texts"], 1):
                    pid = f"passage:{text['object_id']}"
                    g.node(pid, ["Passage"], text=text["text"], source_id=text["object_id"])
                    passages.setdefault(text["object_id"], text["text"])
                    g.edge("HAS_PASSAGE", owner, pid, order=p_order)

    # Learning objectives: the objective lines on the objectives slide start with "…"
    objective_slide = next(sl for s in extracted["scenes"] for sl in s["slides"] if sl["slide_id"] == manual["objectives_slide"])
    objective_texts = [t for l in objective_slide["layers"] for t in l["texts"] if t["text"].startswith("…")]
    for number, text in enumerate(objective_texts, 1):
        lo = f"objective:{number}"
        g.node(lo, ["LearningObjective"], name=f"Lernziel {number}", number=number, text=text["text"].lstrip("… ").strip())
        g.edge("HAS_OBJECTIVE", doc, lo, order=number)
        g.edge("SUPPORTED_BY", lo, f"passage:{text['object_id']}")
    for number, topic_numbers in manual["covers"].items():
        if not number.startswith("_"):
            for t in topic_numbers:
                g.edge("COVERS", f"objective:{number}", topic_ids[t], source=manual["covers"]["_source"])

    # Questions and answer options from the extraction
    quiz_ids = {}
    for question in extracted["questions"]:
        qid = f"question:{question['interaction_id']}"
        label = question["prompt"][0]
        number = int(label.split()[1]) if question["in_quiz"] and label.startswith("Frage ") else None
        g.node(qid, ["Question"], name=label if number else "Wissenscheck", number=number, type=question["type"],
               origin="quiz" if question["in_quiz"] else "knowledge-check", points=question["points"],
               text="\n".join(question["prompt"][1:]), source_id=question["interaction_id"])
        g.edge("HAS_QUESTION", f"section:{question['slide_id']}", qid)
        if number:
            quiz_ids[str(number)] = qid
        correct = set(question.get("correct") or [])
        order = question.get("correct_order") or []
        pairs = {p["item"]: p["target"] for p in question.get("correct_pairs") or []}
        for o_order, choice in enumerate(question["choices"], 1):
            oid = f"option:{question['interaction_id']}/{choice['id']}"
            g.node(oid, ["AnswerOption"], text=choice["text"], source_id=choice["id"])
            g.edge("HAS_OPTION", qid, oid, order=o_order,
                   correct=choice["text"] in correct if "correct" in question else None,
                   position=order.index(choice["text"]) + 1 if choice["text"] in order else None,
                   match=pairs.get(choice["text"]))

    for number, objectives in manual["assesses"].items():
        if not number.startswith("_"):
            for lo in objectives:
                g.edge("ASSESSES", quiz_ids[number], f"objective:{lo}", source=manual["assesses"]["_source"])
    for number, topic_numbers in manual["tests"].items():
        if not number.startswith("_"):
            for t in topic_numbers:
                g.edge("TESTS", quiz_ids[number], topic_ids[t], source=manual["tests"]["_source"])
    for from_, to in manual["refers_to"]["references"]:
        target = chapter_ids.get(to) or topic_ids[to]
        g.edge("REFERS_TO", topic_ids[from_], target, source=manual["refers_to"]["_source"])

    # Knowledge layer: concepts, index, taxonomy, facts
    for c in manual["concepts"]:
        g.node(concept_id(c["name"]), ["Concept", c["type"]], name=c["name"], type=c["type"],
               aliases=c.get("aliases") or None, rank=c.get("rank"), normalized=c.get("normalized"))
    for c in manual["concepts"]:
        pattern = mention_pattern(c)
        for object_id, text in passages.items():
            if pattern.search(text):
                g.edge("MENTIONS", f"passage:{object_id}", concept_id(c["name"]), method="string-match")
    for child, parent in manual["is_a"]["pairs"]:
        g.edge("IS_A", concept_id(child), concept_id(parent), source=manual["is_a"]["_source"])

    for f in manual["facts"]:
        fid = f"fact:{f['id']}"
        g.node(fid, ["Fact"], name=f["id"], kind=f["kind"], predicate=f.get("predicate"), statement=f["statement"],
               modality=f.get("modality"), timing=f.get("timing"), review=f.get("review"), method="manual")
        g.edge("SUBJECT", fid, concept_id(f["subject"]))
        if f.get("object"):
            g.edge("OBJECT", fid, concept_id(f["object"]))
        for c in f.get("conditions", []):
            g.edge("CONDITION", fid, concept_id(c["concept"]), **{k: v for k, v in c.items() if k != "concept"})
        if f.get("implies"):
            g.edge("IMPLIES", fid, concept_id(f["implies"]))
        for action in f.get("recommends", []):
            g.edge("RECOMMENDS", fid, concept_id(action))
        if passages.get(f["source"]) is None or f["quote"] not in passages[f["source"]]:
            raise ValueError(f"fact {f['id']}: quote not found in text block {f['source']}")
        g.edge("SUPPORTED_BY", fid, f"passage:{f['source']}", quote=f["quote"])
    for f in manual["facts"]:
        for other in f.get("qualifies", []):
            g.edge("QUALIFIES", f"fact:{f['id']}", f"fact:{other}")
        for other in f.get("depends_on", []):
            g.edge("DEPENDS_ON", f"fact:{f['id']}", f"fact:{other}")

    for number, options in manual["justified_by"].items():
        if number.startswith("_"):
            continue
        qid = quiz_ids[number]
        by_text = {g_node["props"]["text"]: g_node["id"] for g_node in g.nodes
                   if g_node["id"].startswith(f"option:{qid.split(':')[1]}/")}
        tested = []
        for text, fact_ids in options.items():
            for fact in fact_ids:
                g.edge("JUSTIFIED_BY", by_text[text], f"fact:{fact}")
                if fact not in tested:
                    tested.append(fact)
        for fact in tested:
            g.edge("TESTS", qid, f"fact:{fact}", source="answer options")

    # Shortcuts between concepts, derived from facts so the concept view can be browsed directly
    for f in manual["facts"]:
        if f.get("predicate") and f.get("object"):
            g.edge(f["predicate"], concept_id(f["subject"]), concept_id(f["object"]), fact=f["id"], derived=True)
        if f["kind"] == "threshold":
            g.edge("INDICATES", concept_id(f["subject"]), concept_id(f["implies"]), fact=f["id"], derived=True)
    return g


def cypher_value(value):
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, list):
        return "[" + ", ".join(cypher_value(v) for v in value) + "]"
    if isinstance(value, dict):
        return "{" + ", ".join(f"`{k}`: {cypher_value(v)}" for k, v in value.items()) + "}"
    return json.dumps(value, ensure_ascii=False)


def to_cypher(g):
    """MERGE statements, so loading twice gives the same graph. Edges carry a key to keep parallel edges apart."""
    labels = {n["id"]: n["labels"][0] for n in g.nodes}
    lines = ["// Generated by prototype/build_graph.py. Load into Neo4j (Browser or Query tool)."]
    for label in dict.fromkeys(n["labels"][0] for n in g.nodes):
        lines.append(f"CREATE CONSTRAINT {label.lower()}_id IF NOT EXISTS FOR (n:{label}) REQUIRE n.id IS UNIQUE;")
    groups = {}
    for n in g.nodes:
        groups.setdefault(tuple(n["labels"]), []).append({"id": n["id"], **n["props"]})
    for node_labels, rows in groups.items():
        lines.append(f"UNWIND {cypher_value(rows)} AS row\nMERGE (n:{node_labels[0]} {{id: row.id}})\n"
                     f"SET n = row" + "".join(f", n:{l}" for l in node_labels[1:]) + ";")
    edge_groups = {}
    for i, e in enumerate(g.edges):
        key = (e["type"], labels[e["from"]], labels[e["to"]])
        edge_groups.setdefault(key, []).append({"from": e["from"], "to": e["to"], "key": i, "props": e["props"]})
    for (type_, a, b), rows in edge_groups.items():
        lines.append(f"UNWIND {cypher_value(rows)} AS row\nMATCH (a:{a} {{id: row.from}}), (b:{b} {{id: row.to}})\n"
                     f"MERGE (a)-[r:{type_} {{key: row.key}}]->(b)\nSET r += row.props;")
    return "\n".join(lines) + "\n"


def to_json(g):
    """One node or edge per line, so changes show up as small diffs."""
    dump = lambda x: json.dumps(x, ensure_ascii=False)
    return ('{"nodes": [\n' + ",\n".join(dump(n) for n in g.nodes) + '\n],\n"edges": [\n'
            + ",\n".join(dump(e) for e in g.edges) + "\n]}\n")


def main(argv):
    if len(argv) != 3:
        print(__doc__)
        return 1
    extracted = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    manual = json.loads(MANUAL.read_text(encoding="utf-8"))
    g = build(extracted, manual)
    out = Path(argv[2])
    out.mkdir(parents=True, exist_ok=True)
    (out / "graph.json").write_text(to_json(g), encoding="utf-8", newline="\n")
    (out / "graph.cypher").write_text(to_cypher(g), encoding="utf-8", newline="\n")
    print(f"{len(g.nodes)} nodes, {len(g.edges)} edges -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
