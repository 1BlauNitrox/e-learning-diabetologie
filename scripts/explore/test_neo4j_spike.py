"""Tests for the Neo4j spike script.

Run from the repository root: python -m unittest discover -s scripts/explore
"""

import unittest

import neo4j_spike

GRAPH = {
    "nodes": [
        {"id": "fact:a", "labels": ["Fact"], "props": {"statement": "ß-OHB über 3 mmol/l"}},
        {"id": "concept:b", "labels": ["Concept", "Substance"], "props": {"name": "ß-Hydroxybutyrat", "aliases": ["ß-OHB"]}},
    ],
    "edges": [
        {"type": "CONDITION", "from": "fact:a", "to": "concept:b", "props": {"operator": ">", "value": 3}},
        {"type": "CONDITION", "from": "fact:a", "to": "concept:b", "props": {"operator": "<=", "value": 5}},
    ],
}


class CypherTest(unittest.TestCase):
    def test_value_escaping_and_types(self):
        self.assertEqual(neo4j_spike.cypher_value({"a": "ß \"x\"", "b": [1, True, None]}),
                         '{`a`: "ß \\"x\\"", `b`: [1, true, null]}')

    def test_constraint_per_primary_label(self):
        script = neo4j_spike.to_cypher(GRAPH)
        self.assertIn("FOR (n:Fact) REQUIRE n.id IS UNIQUE", script)
        self.assertIn("FOR (n:Concept) REQUIRE n.id IS UNIQUE", script)
        self.assertNotIn("FOR (n:Substance)", script)

    def test_secondary_labels_and_parallel_edges(self):
        script = neo4j_spike.to_cypher(GRAPH)
        self.assertIn("SET n = row, n:Substance;", script)
        self.assertIn('`key`: 0', script)
        self.assertIn('`key`: 1', script)
        self.assertIn("MERGE (a)-[r:CONDITION {key: row.key}]->(b)", script)


if __name__ == "__main__":
    unittest.main()
