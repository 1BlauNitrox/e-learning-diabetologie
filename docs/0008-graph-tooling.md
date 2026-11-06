# 0008 – Graph Tooling

**Status:** proposed; to be reviewed by the team. The graph structure is in [0007](0007-graph-structure.md); the overall tech stack follows in [#7](https://github.com/1BlauNitrox/e-learning-diabetologie/issues/7).

## Decisions

| Aspect | Choice | Why |
|---|---|---|
| Graph database | **Neo4j** | The established property graph database: rank 1 of 44 graph DBMS in the [DB-Engines ranking](https://db-engines.com/en/ranking/graph+dbms) (November 2026), with more than twice the score of rank 2. Properties on edges carry the values and quotes that [0007](0007-graph-structure.md) needs. Most documentation and examples for future contributors |
| Query language | **Cypher** | Neo4j's language; the ISO standard GQL (ISO/IEC 39075:2024) is based on it, and other databases (ArcadeDB, Apache AGE) accept it too |
| Visualization | **Neo4j Query tool / Browser** | Built in; shows any query result as a graph |
| Exchange format | **`graph.json`** from [0007](0007-graph-structure.md#prototype) | Independent of the database; the Cypher load script is generated from it, so the database can be rebuilt or replaced at any time |

## Cost, licence, local use

| Tool | Cost | Licence | Local |
|---|---|---|---|
| Neo4j Community Edition | Free | GPLv3 | Yes |
| Neo4j Desktop | Free | Its instances run the Enterprise Edition under Neo4j's terms (`LICENSE.txt` in the instance folder) | Yes |

The prototype uses only Community Edition features, so it runs on either. Tested with Neo4j 2026.10.1 in Neo4j Desktop 2.

## Alternatives considered

| Alternative | Licence | Not chosen because |
|---|---|---|
| ArcadeDB (suggested on [#17](https://github.com/1BlauNitrox/e-learning-diabetologie/issues/17)) | Apache 2.0 | Smaller community; Cypher support would need its own tests. Can load the same Cypher script if needed |
| PostgreSQL + Apache AGE | Apache 2.0 | Cypher only inside SQL calls; visualization needs a separate viewer |
| RDF store (e.g. Apache Jena Fuseki), SPARQL | Apache 2.0 | Values and quotes on edges need RDF-star or reification; only worth it if we align with an RDF ontology ([0002](0002-project-scope.md#open-questions), question 4) |
| NetworkX with files | BSD | No persistence and no query language |

## Creation method per node and edge type

| Method | Node and edge types |
|---|---|
| Code, from the export | `Document`, `Section`, `Passage`, `LearningObjective`, `Question`, `AnswerOption`; `HAS_SECTION`, `HAS_PASSAGE`, `HAS_OBJECTIVE`, `HAS_QUESTION`, `HAS_OPTION`, `SUPPORTED_BY` of objectives |
| Code, string match of concept names and aliases | `MENTIONS` |
| Code, derived from facts | Concept shortcuts (`MEASURED_IN`, `INDICATES`, `MAY_FALSIFY`, …) |
| LLM extraction, checked by code (schema, verbatim quote) | `Concept`, `Fact`; `SUBJECT`, `OBJECT`, `CONDITION`, `IMPLIES`, `RECOMMENDS`, `QUALIFIES`, `DEPENDS_ON`, `SUPPORTED_BY` of facts, `IS_A` |
| Mapping (by hand in the prototype; method for the pipeline open) | `COVERS`, `ASSESSES`, `TESTS`, `JUSTIFIED_BY`, `REFERS_TO`, names of chapters and topics |

In the prototype, everything marked LLM is written by hand in `prototype/graph/manual.json`. How the LLM step runs (crewAI) is decided in [#8](https://github.com/1BlauNitrox/e-learning-diabetologie/issues/8).

## Spike

1. Install [Neo4j Desktop](https://neo4j.com/download/), create a local instance and start it.
2. Generate the load script (needs `data/extracted/ketonkoerper.json` only for the first command):
   ```
   python prototype/graph/build_graph.py data/extracted/ketonkoerper.json prototype/graph/output
   python scripts/explore/neo4j_spike.py prototype/graph/output/graph.json scripts/explore/output/graph.cypher
   python -m unittest discover -s scripts/explore
   ```
3. Open **Query** in Neo4j Desktop, connect to the empty instance, paste `scripts/explore/output/graph.cypher` and run it. `MATCH (n) RETURN count(n)` gives 590, `MATCH ()-[r]->() RETURN count(r)` gives 1021.
4. Run the queries in `scripts/explore/queries.cypher` one by one.

| Query | Result |
|---|---|
| 1. Which topics explain SGLT2 inhibitors? | 10 topics: 1.1, 1.2, 3.1, 3.2, 3.3, 4.1, 5.4, 6.2, 6.3, 6.4 (those of [0003 §3.4](0003-data-analysis.md#34-recurring-concepts) plus the knowledge check 1.1) |
| 2. What does ß-OHB 2,0 mmol/l in serum mean? | *schwere Entgleisung*, quote "Über 1,5 mmol/l … schwere Entgleisung", source `5cxhcjlTRsl/6r2GjA03ruM` |
| 3. Which topics does no question test? | 8 topics: 2.1, 2.3, 5.4, 6.1–6.5 (as in [0003 §3.6](0003-data-analysis.md#36-questions)) |
| 4. Which options of quiz question 5 have no fact? | "Hauptmetabolit", "Stoffwechsel-zwischenprodukt" (taught outside slide 4.1) |
| 5. Slide 4.1 across all layers | Graph view as in [0007](0007-graph-structure.md#prototype) |

The generated script contains course text and is git-ignored.
