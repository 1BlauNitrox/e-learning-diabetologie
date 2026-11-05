"""Tests for the prototype graph (docs/0007-graph-structure.md).

Run from the repository root: python -m unittest discover -s prototype/graph
The committed prototype/graph/output/graph.json is checked always; the rebuild test is
skipped if data/extracted/ketonkoerper.json is not present.
"""

import json
import unittest
from collections import Counter
from pathlib import Path

import build_graph

ROOT = Path(__file__).resolve().parents[2]
GRAPH = ROOT / "prototype" / "graph" / "output" / "graph.json"
EXTRACTED = ROOT / "data" / "extracted" / "ketonkoerper.json"
MANUAL_EDGES = {"COVERS", "ASSESSES", "REFERS_TO", "IS_A"}


class HelpersTest(unittest.TestCase):
    def test_mention_matches_inflections_and_aliases(self):
        pattern = build_graph.mention_pattern({"name": "SGLT2-Inhibitor", "aliases": ["SGLT2-Hemmer"]})
        self.assertTrue(pattern.search("mit SGLT2-Inhibitoren"))
        self.assertTrue(pattern.search("Cave:bei SGLT2-Hemmern!"))

    def test_mention_needs_word_start(self):
        pattern = build_graph.mention_pattern({"name": "Aceton", "aliases": []})
        self.assertFalse(pattern.search("Acetoacetat"))
        self.assertFalse(build_graph.mention_pattern({"name": "BZ", "aliases": []}).search("ABZ"))


class PrototypeGraphTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        graph = json.loads(GRAPH.read_text(encoding="utf-8"))
        cls.nodes = {n["id"]: n for n in graph["nodes"]}
        cls.edges = graph["edges"]

    def with_label(self, label):
        return [n for n in self.nodes.values() if label in n["labels"]]

    def edges_of(self, type_, from_=None):
        return [e for e in self.edges if e["type"] == type_ and (from_ is None or e["from"] == from_)]

    def test_coverage_required_by_issue(self):
        self.assertEqual(len(self.with_label("Topic")), 18)
        self.assertEqual(len(self.with_label("LearningObjective")), 5)
        self.assertEqual(len([q for q in self.with_label("Question") if q["props"]["origin"] == "quiz"]), 10)

    def test_unique_ids_and_known_endpoints(self):
        self.assertEqual(len(self.nodes), len({n for n in self.nodes}))
        for e in self.edges:
            self.assertIn(e["from"], self.nodes, e)
            self.assertIn(e["to"], self.nodes, e)

    def test_manual_edges_name_their_source(self):
        for e in self.edges:
            if e["type"] in MANUAL_EDGES or (e["type"] == "TESTS" and "Topic" in self.nodes[e["to"]]["labels"]):
                self.assertTrue(e["props"].get("source"), e)

    def test_every_fact_has_subject_and_verbatim_quote(self):
        for fact in self.with_label("Fact"):
            self.assertEqual(len(self.edges_of("SUBJECT", fact["id"])), 1, fact["id"])
            support = self.edges_of("SUPPORTED_BY", fact["id"])
            self.assertTrue(support, fact["id"])
            for e in support:
                self.assertIn(e["props"]["quote"], self.nodes[e["to"]]["props"]["text"], fact["id"])

    def test_derived_edges_point_to_existing_facts(self):
        for e in self.edges:
            if e["props"].get("derived"):
                self.assertIn("fact:" + e["props"]["fact"], self.nodes, e)

    def test_untested_topics_match_data_analysis(self):
        tested = {e["to"] for e in self.edges_of("TESTS")}
        untested = sorted(t["props"]["number"] for t in self.with_label("Topic") if t["id"] not in tested)
        self.assertEqual(untested, ["2.1", "2.3", "5.4", "6.1", "6.2", "6.3", "6.4", "6.5"])

    def test_quiz_question_5_options_without_fact(self):
        q5 = next(q for q in self.with_label("Question") if q["props"].get("number") == 5)
        options = [e["to"] for e in self.edges_of("HAS_OPTION", q5["id"])]
        without = sorted(self.nodes[o]["props"]["text"] for o in options if not self.edges_of("JUSTIFIED_BY", o))
        self.assertEqual(without, ["Hauptmetabolit", "Stoffwechsel-zwischenprodukt"])

    def test_umlauts_kept(self):
        names = {n["props"].get("name") for n in self.with_label("Concept")}
        self.assertIn("ß-Hydroxybutyrat", names)
        self.assertIn("Kohlenhydratmenge erhöhen", names)

    def test_edge_types_per_layer(self):
        counts = Counter(e["type"] for e in self.edges)
        for type_ in ["HAS_SECTION", "HAS_PASSAGE", "MENTIONS", "COVERS", "TESTS", "CONDITION", "SUPPORTED_BY"]:
            self.assertGreater(counts[type_], 0, type_)


@unittest.skipUnless(EXTRACTED.exists(), "data/extracted/ketonkoerper.json not present")
class RebuildTest(unittest.TestCase):
    def test_rebuild_reproduces_committed_graph(self):
        extracted = json.loads(EXTRACTED.read_text(encoding="utf-8"))
        manual = json.loads(build_graph.MANUAL.read_text(encoding="utf-8"))
        rebuilt = build_graph.to_json(build_graph.build(extracted, manual))
        self.assertEqual(rebuilt, GRAPH.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
