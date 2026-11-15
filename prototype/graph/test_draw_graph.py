"""Tests for the graph images.

Run from the repository root: python -m unittest discover -s prototype/graph
"""

import json
import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

import draw_graph

GRAPH = json.loads((Path(__file__).resolve().parent / "output" / "graph.json").read_text(encoding="utf-8"))


class DrawGraphTest(unittest.TestCase):
    def test_overview_shows_all_nodes_except_passages_and_options(self):
        image = draw_graph.overview(GRAPH)
        ET.fromstring(image)
        shown = [n for n in GRAPH["nodes"] if not {"Passage", "AnswerOption"} & set(n["labels"])]
        markers = re.findall(r"<circle |<rect x=\"\d", image)
        legend_markers = 9
        self.assertEqual(len(markers) - legend_markers, len(shown))

    def test_slide_detail_has_every_fact_of_the_slide(self):
        image = draw_graph.slide_detail(GRAPH, "5cxhcjlTRsl")
        ET.fromstring(image)
        facts = [n for n in GRAPH["nodes"] if "Fact" in n["labels"] and n["props"]["name"].startswith("4.1-")]
        for fact in facts:
            self.assertIn(draw_graph.short(fact["props"]["statement"], 44).replace("&", "&amp;"), image)

    def test_layout_is_deterministic(self):
        ids, links = ["a", "b", "c"], [("a", "b"), ("b", "c")]
        self.assertEqual(draw_graph.force_layout(ids, links, 200, 100, iterations=20),
                         draw_graph.force_layout(ids, links, 200, 100, iterations=20))


if __name__ == "__main__":
    unittest.main()
