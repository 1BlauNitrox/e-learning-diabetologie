// Example queries on the prototype graph (docs/0008-graph-tooling.md). Run them one at a time.

// 1. Index: which topics explain SGLT2 inhibitors?
MATCH (:Concept {name: 'SGLT2-Inhibitor'})<-[:MENTIONS]-(:Passage)<-[:HAS_PASSAGE]-(s:Section)
MATCH (t:Topic)-[:HAS_SECTION*0..1]->(s)
RETURN DISTINCT t.number AS topic, t.name AS name ORDER BY topic;

// 2. Answering: what does ß-OHB 2,0 mmol/l in serum mean, and where does it say so?
WITH 2.0 AS value
MATCH (f:Fact {kind: 'threshold'})-[:SUBJECT]->(c:Concept {name: 'ß-Hydroxybutyrat'}),
      (f)-[cond:CONDITION]->(c), (f)-[:IMPLIES]->(g), (f)-[s:SUPPORTED_BY]->(p)<-[:HAS_PASSAGE]-(sec)
WITH value, f, g, s, sec, collect(cond) AS conds
WHERE all(x IN conds WHERE (x.operator = '>' AND value > x.value) OR (x.operator = '<=' AND value <= x.value))
RETURN g.name AS grade, f.statement AS statement, s.quote AS quote, sec.source_id AS source;

// 3. Coverage: which topics does no question test?
MATCH (t:Topic) WHERE NOT (t)<-[:TESTS]-(:Question)
RETURN t.number AS topic, t.name AS name ORDER BY topic;

// 4. Evaluation: which answer options of quiz question 5 are not backed by a fact?
MATCH (:Question {number: 5})-[:HAS_OPTION]->(o)
WHERE NOT (o)-[:JUSTIFIED_BY]->(:Fact)
RETURN o.text AS option;

// 5. Visualization: slide 4.1 across all layers (switch the result to the graph view)
MATCH p = (t:Topic {number: '4.1'})-[:HAS_SECTION*0..1]->()-[:HAS_PASSAGE]->()<-[:SUPPORTED_BY]-(:Fact)-->(:Concept)
RETURN p;
