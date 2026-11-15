"""Tests for the prototype of graph v2 (docs/graph/v2.md).

Run from the repository root: python -m unittest discover -s prototype/graph/v2
The committed files in prototype/graph/v2/output are checked always; the rebuild test is
skipped if data/extracted/ketonkoerper.json is not present.
"""

import copy
import json
import unittest
from collections import Counter
from pathlib import Path

import build_graph

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "prototype" / "graph" / "v2" / "output"
EXTRACTED = ROOT / "data" / "extracted" / "ketonkoerper.json"

SEGMENTS = {
    "slide:base": {"kind": "base", "title": "Messung", "blocks": ["Acetoacetat (Messung im Urin)"]},
    "popup": {"kind": "popup", "title": "Serum", "blocks": ["Über 3 mmol/l \tmedizinischer Notfall", "sich krank fühlt"]},
}
MAPPING = {
    "segment_titles": {"popup": "Serum"},
    "concepts": [
        {"name": "Acetoacetat", "type": "Substance"},
        {"name": "ß-Hydroxybutyrat", "type": "Substance", "aliases": ["ß-OHB"]},
        {"name": "Urin", "type": "Anatomy"},
        {"name": "Serum", "type": "Anatomy"},
        {"name": "medizinischer Notfall", "type": "Finding"},
    ],
    "statements": [
        {"id": "S001", "predicate": "MEASURED_IN", "subject": {"concept": "Acetoacetat"}, "object": "Urin",
         "text": "Acetoacetat wird im Urin gemessen.",
         "evidence": [{"segment": "slide:base", "quote": "Acetoacetat (Messung im Urin)"}]},
        {"id": "S002", "predicate": "INDICATES", "from_context": ["subject", "condition"],
         "subject": {"concept": "ß-Hydroxybutyrat", "operator": ">", "value": 3, "unit": "mmol/l"},
         "object": "medizinischer Notfall", "conditions": [{"concept": "Serum"}],
         "text": "ß-Hydroxybutyrat im Serum über 3 mmol/l: medizinischer Notfall.",
         "evidence": [{"segment": "popup", "quote": "Über 3 mmol/l \tmedizinischer Notfall"}]},
    ],
    "not_mapped": [{"segment": "popup", "category": "not_a_relation", "quote": "sich krank fühlt", "reason": "Example."}],
}


class ConstraintTest(unittest.TestCase):
    def test_threshold_range_and_approximate_value(self):
        self.assertEqual(build_graph.constraint({"operator": ">", "value": 1.5, "unit": "mmol/l"}), "> 1,5 mmol/l")
        self.assertEqual(build_graph.constraint({"operator": "between", "value": 0.6, "value_max": 1.5, "unit": "mmol/l"}),
                         "0,6 bis 1,5 mmol/l")
        self.assertEqual(build_graph.constraint({"operator": ">=", "approx": True, "value": 200, "unit": "mg/dl"}),
                         "ca. >= 200 mg/dl")

    def test_ordinal_value_negation_and_qualifier(self):
        self.assertEqual(build_graph.constraint({"operator": "=", "value": "++"}), "= ++")
        self.assertEqual(build_graph.constraint({"negated": True, "qualifier": "fehlende"}), "NOT fehlende")
        self.assertEqual(build_graph.constraint({}), "")


class CheckTest(unittest.TestCase):
    def problems(self, change):
        mapping = copy.deepcopy(MAPPING)
        change(mapping)
        return "\n".join(build_graph.check(mapping, SEGMENTS))

    def test_valid_mapping_has_no_problems(self):
        self.assertEqual(build_graph.check(MAPPING, SEGMENTS), [])

    def test_rejects_predicate_outside_the_list(self):
        def change(m): m["statements"][0]["predicate"] = "RELATED_TO"
        self.assertIn("S001: unknown predicate RELATED_TO", self.problems(change))

    def test_rejects_types_outside_the_signature(self):
        def change(m): m["statements"][0]["object"] = "medizinischer Notfall"
        self.assertIn("S001: MEASURED_IN does not allow Substance -> Finding", self.problems(change))

    def test_is_a_needs_the_same_type_on_both_sides(self):
        def change(m): m["statements"][0]["predicate"] = "IS_A"
        self.assertIn("S001: IS_A does not allow Substance -> Anatomy", self.problems(change))

    def test_rejects_unknown_concept_type_and_concept(self):
        def change(m):
            m["concepts"][0]["type"] = "Topic"
            m["statements"][0]["object"] = "Blut"
        problems = self.problems(change)
        self.assertIn("Acetoacetat: unknown type Topic", problems)
        self.assertIn("S001: unknown concept Blut", problems)

    def test_rejects_quote_that_is_not_verbatim(self):
        def change(m): m["statements"][0]["evidence"][0]["quote"] = "Acetoacetat (Messung im Serum)"
        self.assertIn("S001: quote is not verbatim in slide:base", self.problems(change))

    def test_rejects_quote_from_another_segment(self):
        def change(m): m["statements"][0]["evidence"][0]["segment"] = "popup"
        self.assertIn("S001: quote is not verbatim in popup", self.problems(change))

    def test_rejects_free_text_modality_and_unknown_properties(self):
        def change(m):
            m["statements"][0]["modality"] = "In Einzelfällen"
            m["statements"][0]["review"] = "check"
            m["statements"][1]["subject"]["comment"] = "x"
        problems = self.problems(change)
        self.assertIn("S001: unknown modality In Einzelfällen", problems)
        self.assertIn("S001: unknown property ['review']", problems)
        self.assertIn("S002: unknown role property ['comment']", problems)

    def test_rejects_value_without_operator_and_range_without_end(self):
        def no_operator(m): del m["statements"][1]["subject"]["operator"]
        def no_end(m): m["statements"][1]["subject"]["operator"] = "between"
        self.assertIn("S002: value and operator of ß-Hydroxybutyrat do not fit", self.problems(no_operator))
        self.assertIn("S002: value and operator of ß-Hydroxybutyrat do not fit", self.problems(no_end))

    def test_rejects_the_same_statement_twice(self):
        def change(m): m["statements"].append(dict(m["statements"][0], id="S003"))
        self.assertIn("S003: same statement as S001", self.problems(change))

    def test_rejects_concept_without_statement_and_duplicate_alias(self):
        def change(m): m["concepts"].append({"name": "Aceton", "type": "Substance", "aliases": ["ß-OHB"]})
        problems = self.problems(change)
        self.assertIn("concept without statement: Aceton", problems)
        self.assertIn("name or alias used twice: ß-OHB", problems)

    def test_rejects_normalised_concept_whose_source_phrase_is_missing(self):
        def change(m): m["concepts"][0]["normalized_from"] = "sich schlecht fühlt"
        self.assertIn("Acetoacetat: normalized_from is not verbatim", self.problems(change))

    def test_rejects_unknown_category_in_the_log(self):
        def change(m): m["not_mapped"][0]["category"] = "other"
        self.assertIn("not_mapped: unknown category other", self.problems(change))


class PrototypeGraphTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        graph = json.loads((OUTPUT / "graph.json").read_text(encoding="utf-8"))
        cls.nodes = {n["id"]: n for n in graph["nodes"]}
        cls.edges = graph["edges"]

    def label(self, node_id):
        return self.nodes[node_id]["labels"][1]

    def test_node_types_belong_to_exactly_one_layer(self):
        layers = {"Structure": {"Domain", "Course", "Section", "Slide", "Segment"}, "Content": {"Concept", "Statement"}}
        for node in self.nodes.values():
            layer, label = node["labels"]
            self.assertIn(label, layers[layer])

    def test_structure_layer_is_a_tree_of_the_whole_module(self):
        counts = Counter(n["labels"][1] for n in self.nodes.values() if n["labels"][0] == "Structure")
        self.assertEqual(counts, {"Domain": 1, "Course": 1, "Section": 10, "Slide": 43, "Segment": 72})
        parents = Counter(e["to"] for e in self.edges if e["type"] == "CONTAINS")
        for node_id, node in self.nodes.items():
            if node["labels"][0] == "Structure":
                self.assertEqual(parents[node_id], 0 if self.label(node_id) == "Domain" else 1)

    def test_edges_connect_only_the_node_types_of_the_model(self):
        allowed = {"SUBJECT": ("Statement", "Concept"), "OBJECT": ("Statement", "Concept"),
                   "CONDITION": ("Statement", "Concept"), "EVIDENCE": ("Statement", "Segment")}
        order = ["Domain", "Course", "Section", "Slide", "Segment"]
        for e in self.edges:
            ends = (self.label(e["from"]), self.label(e["to"]))
            if e["type"] == "CONTAINS":
                self.assertEqual(order.index(ends[0]) + 1, order.index(ends[1]))
            else:
                self.assertEqual(ends, allowed[e["type"]])

    def test_every_statement_has_one_subject_one_object_and_evidence(self):
        roles = Counter((e["from"], e["type"]) for e in self.edges)
        for node_id, node in self.nodes.items():
            if self.label(node_id) == "Statement":
                self.assertEqual((roles[node_id, "SUBJECT"], roles[node_id, "OBJECT"]), (1, 1))
                self.assertGreaterEqual(roles[node_id, "EVIDENCE"], 1)
                self.assertEqual(node["props"]["category"], build_graph.PREDICATES[node["props"]["predicate"]][0])

    def test_every_concept_is_linked_to_its_source_through_a_statement(self):
        linked = {e["to"] for e in self.edges if e["type"] in ("SUBJECT", "OBJECT", "CONDITION")}
        for node_id in self.nodes:
            if self.label(node_id) == "Concept":
                self.assertIn(node_id, linked)

    def test_threshold_of_slide_4_1(self):
        emergency = [e["from"] for e in self.edges if e["type"] == "OBJECT" and e["to"] == "concept:medizinischer Notfall"]
        subjects = [e for e in self.edges if e["type"] == "SUBJECT" and e["from"] in emergency]
        self.assertEqual([(e["to"], e["props"]) for e in subjects],
                         [("concept:ß-Hydroxybutyrat", {"operator": ">", "value": 3, "unit": "mmol/l"})])

    def test_viewer_contains_every_statement(self):
        viewer = (OUTPUT / "viewer.html").read_text(encoding="utf-8")
        for node_id in self.nodes:
            if self.label(node_id) == "Statement":
                self.assertIn(f'"{node_id}"', viewer)


@unittest.skipUnless(EXTRACTED.exists(), "data/extracted/ketonkoerper.json not present")
class RebuildTest(unittest.TestCase):
    def test_rebuild_reproduces_committed_output(self):
        extracted = json.loads(EXTRACTED.read_text(encoding="utf-8"))
        mapping = json.loads(build_graph.STATEMENTS.read_text(encoding="utf-8"))
        g = build_graph.build(extracted, mapping)
        notes = {s["id"]: s["note"] for s in mapping["statements"] if "note" in s}
        self.assertEqual(build_graph.to_json(g), (OUTPUT / "graph.json").read_text(encoding="utf-8"))
        self.assertEqual(build_graph.viewer(g, notes), (OUTPUT / "viewer.html").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
