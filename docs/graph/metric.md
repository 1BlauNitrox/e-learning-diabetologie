# Graph metric

**Status:** draft ([#22](https://github.com/1BlauNitrox/e-learning-diabetologie/issues/22)). The metric is applied to graph [v1](v1.md) and [v2](v2.md) in [#25](https://github.com/1BlauNitrox/e-learning-diabetologie/issues/25).

The metric tells whether a graph version serves the uses of the graph, and whether one version serves them better than another. It applies to any version: the questions and reference answers do not depend on a graph model. Only the queries and one adapter are written per version.

## Scope

| Measured | Not measured |
|---|---|
| What a query returns from the graph (retrieval) | An answer that an LLM formulates from the result. It is not deterministic and depends on the LLM and the prompt, not only on the graph |
| Whether the facts of the graph are backed by the source | Readability of the graph, strictness of the model, independence of the layers. These are judged in the review of a version |
| Size of the graph and of a query result, reported without a score | Latency, see [Reported figures](#reported-figures) |

## Parts

| Part | Question | Role in the comparison |
|---|---|---|
| A: Competency questions | Does the graph return what the material says, and nothing else? | Ranking |
| B: Negative questions | Does the graph return nothing where the material says nothing? | Threshold |
| C: Provenance | Is every fact backed by its source? | Threshold |
| Reported figures | How large is the graph, and how much does a question fetch? | None |

A fact is the smallest citable claim a version stores (v1: `Fact`, v2: `Statement`).

## Question set

There is one question set per course. It holds the questions of Parts A and B with their reference answers.

### Uses and levels

| Use | The graph answers |
|---|---|
| Index | Where in the course is a topic covered? |
| Question generation | Which facts can be asked, with which answer and which distractors? |
| Question answering | Which facts answer a user's question, and where are they written? |
| Coverage | Which topics does no quiz question test? See [Open questions](#open-questions) |

| Level | The question needs | Example |
|---|---|---|
| `structure` | Courses, chapters and slides only | Welche Folien hat Kapitel 3? |
| `cross_layer` | Content and structure together | Auf welchen Folien kommen SGLT2-Hemmer vor? |
| `content_direct` | One fact | Worin wird ß-Hydroxybutyrat gemessen? |
| `content_multi_step` | Several facts in sequence | Was folgt aus ß-OHB über 3 mmol/l im Serum? |

Rules:

1. Every use has at least one question.
2. Every level has at least one question.
3. Every type of negative question has at least one question.
4. A course has 20 to 30 questions. Fewer make the means meaningless; more cost two queries each per comparison.

### Entry

| Field | Content |
|---|---|
| `id` | `Q` plus two digits for Part A, `N` plus two digits for Part B. Never reused |
| `use` | `index`, `question_generation`, `question_answering` or `coverage` |
| `level` | One of the four levels |
| `question` | The question in German |
| `negative` | `true` for Part B |
| `negative_type` | 1 to 4, Part B only |
| `twin` | Part B only: the `id` of a Part A question whose query has the same shape |
| `ambiguous` | `true` if the source allows more than one reading |
| `expected.concepts` | Expected concepts: one name each, plus accepted variants |
| `expected.values` | Expected values: `operator`, `value`, `value_max` (for `between` only), `unit` |
| `expected.sources` | Slides that state the answer: the slide number as in the menu, else the Storyline ID of the slide |

```json
{
  "id": "Q04",
  "use": "question_answering",
  "level": "content_direct",
  "question": "Was bedeutet ein ß-OHB-Wert von 2,0 mmol/l im Serum?",
  "negative": false,
  "ambiguous": false,
  "expected": {
    "concepts": [{"name": "schwere Entgleisung", "variants": []}],
    "values": [],
    "sources": ["4.1"]
  }
}
```

### Reference answers

1. Reference answers come from the course text only. They never come from a graph version, because the reference would favour the version it was taken from. They never come from our own medical knowledge.
2. Before the set is written, both team members write reference answers for the same three to five questions independently and compare them. Differences are resolved by sharpening these rules. After that, each member writes part of the set and the other reviews it.
3. A reference answer names concepts, values and slides, not complete facts. A fact with subject, predicate and object is the model of a version, and the metric would depend on it.
4. If the source allows more than one reading, the reference expects every reading, and the question is marked `ambiguous`. A graph should reproduce the source, not resolve it. Example: slide 4.1 assigns 0,6 mmol/l both to the normal finding and to a simple derailment.
5. Quiz questions may serve as a source:
   - a choice question gives its correct options as concepts;
   - a matching question gives one question per pair;
   - a sequence question gives one question per step.

   The set also contains questions taken directly from the text, because the quiz is the test set for coverage.

### Matching

A returned element matches an expected element after normalization:

| List | Normalization | Match |
|---|---|---|
| `concepts` | Unicode NFC, case folding, whitespace collapsed and trimmed | Equal to the name or to a variant |
| `values` | Decimal comma read as decimal point; unit with case folding | `operator` and `unit` equal, numbers equal |
| `sources` | Trimmed | Equal |

Spellings that normalization does not join are listed as variants, for example `ß-Hydroxybutyrat` and `β-Hydroxybutyrat`.

### Adapter

Each version has one adapter that maps a query result to the three lists:

- `concepts`: the names of the concept nodes in the result. Text blocks, titles and structure nodes are not concepts.
- `values`: the value constraints of the facts in the result.
- `sources`: the slide of every source unit in the result.

The adapter does not read the reference answer.

### Queries

- Each question has one query per version. A team member who did not write the reference answer writes it.
- If a version cannot express a question, the question counts as not answerable, with a reason.

## Part A: Competency questions

For each question:

| Symbol | Meaning |
|---|---|
| E | Expected elements of a list |
| R | Returned elements of the same list |
| T | Elements in both E and R |

| Figure | Formula | Answers |
|---|---|---|
| Recall | \|T\| / \|E\| | Is something missing? |
| Precision | \|T\| / \|R\| | Is something returned that was not asked for? |
| F1 | 2 · Precision · Recall / (Precision + Recall) | Both in one number. Returning everything gives a high recall but a low F1 |

Rules:

1. Recall and precision are reported for each list.
2. A list that is empty in the reference is not scored for that question.
3. The F1 of a question is computed over the summed counts of its scored lists.
4. If a query returns nothing, its recall, precision and F1 are 0.
5. A question that is not answerable has F1 0 and is also counted separately.
6. The score of a question set is the mean F1 over its Part A questions. Questions marked `ambiguous` are also listed separately.

## Part B: Negative questions

A negative question asks for something the material does not state. The expected result is empty.

| Type | The material |
|---|---|
| 1 | Does not contain the term |
| 2 | Contains the term, but not the relation asked for |
| 3 | Contains the answer only in an image that is not extracted |
| 4 | Refers to another module for it |

- The query of a negative question has the same shape as the query of its `twin`. A query cannot pass by being narrower than a query for a comparable question that has an answer.
- A result is empty if the adapter returns no element in any of the three lists. If the term is found in the index but the question is about content, the result is still empty, because a content query does not use the index.
- **Score:** the share of negative questions with an empty result.

A graph without content passes every negative question. The score is therefore read only together with Part A.

## Part C: Provenance

Part C checks whether each fact leads to source text that supports it.

| Stage | Check | Facts | By |
|---|---|---|---|
| 1 | The link of the fact leads to an existing source unit | All | Code |
| 2 | The quote of the link occurs verbatim in the text of that unit | All | Code |
| 3 | The quote supports the fact | Sample | Both team members |

Course text is not committed. Stages 2 and 3 run against the local extraction output.

### Sample

- **Size:** 30 facts, or all facts if a version has fewer. If none of 30 facts is unsupported, the share of unsupported facts is below 10 % with 95 % confidence (rule of three).
- **Draw:** for each fact, compute SHA-256 of `graph-metric:<fact id>`. Sort by this value and take the first 30. The draw needs no random generator and gives the same sample for the same graph. Whether a fact is drawn depends only on its own ID.

### Verdict

For each fact, check the quote together with the slide it is on against the parts of the fact: subject, relation, object, every condition, every value, modality.

| Verdict | Rule |
|---|---|
| Supported | Every part is supported |
| Partially supported | Subject, relation and object are supported; at least one condition, value or modality is not |
| Not supported | Subject, relation or object is not supported, or the quote contradicts the fact |

Both team members judge every fact of the sample independently. The share of facts with the same verdict is reported. Differences are discussed, and the agreed verdict is recorded in a file per version. Scores are computed from that file, so they do not change between runs.

## Reported figures

Reported, not scored. They describe size and cost and are compared only within the context of the scores.

| Figure | Definition |
|---|---|
| Graph size | Nodes and edges, also per node type |
| Nodes without function | Nodes that no fact references and no query of the question set returns |
| Unmappable passages | Passages the version logs as not expressible in its model. Not available if the version keeps no log |
| Context size | Distinct nodes a query returns, per question |
| Hops | Edges on the shortest path from the start node of the query to each returned expected element, per question. Not comparable between models, because a model that stores facts as nodes needs more hops for the same relation |

Latency is not measured while there is only one course. At this size it measures the database, not the graph.

## Comparing two versions

1. **Thresholds.** A version qualifies only if:
   - Stages 1 and 2 hold for 100 % of its facts;
   - Stage 3 finds no unsupported fact;
   - Part B reaches the threshold in [Open questions](#open-questions).

   An unsupported medical claim cannot be offset by better coverage.
2. **Ranking.** Qualified versions are ranked by their mean F1 on the common question set.
3. **Per question.** For each question, the versions are compared by F1: better, worse or equal. With a set of this size, a small difference in the mean is not meaningful on its own.

The **common question set** holds the questions whose `sources` lie entirely on slides that both versions cover. The **full question set** holds all questions. Both are reported; only the common set is used for the ranking.

### Scorecard

The scorecard holds every figure, so that no part is hidden behind another. "Measures" tells whether a figure judges the model (can it express the source?) or the content (is it filled correctly?).

| Part | Figure | Measures | Version A | Version B |
|---|---|---|---|---|
| A | Answerable questions | Model | | |
| A | Mean recall, precision and F1 (common set) | Content | | |
| A | Mean recall, precision and F1 (full set) | Content | | |
| B | Negative questions with an empty result | Content | | |
| C | Facts passing Stage 1 / Stage 2 | Content | | |
| C | Sample: supported / partially / not supported; agreement | Content | | |
| Reported | Nodes / edges; nodes without function | Model | | |
| Reported | Unmappable passages | Model | | |
| Reported | Mean context size, mean hops | Model | | |

Results are also reported per question: ID, use, level, recall, precision, F1, context size and hops.

## Determinism

Two runs on the same graph give the same scores, because:

- questions, reference answers, queries and adapters are fixed files;
- matching compares normalized sets, so order does not matter;
- the sample is drawn by hash;
- the verdicts of Stage 3 are recorded once and read from a file.

## Limits

- A wrong fact that no question touches is found only if it is drawn for Stage 3.
- The completeness of a version is measured only as far as the questions reach. A comparison against all statements of annotated slides is not part of the metric.
- The scores reflect the queries as well as the graph. A poor query lowers the score of a good graph.

## Extending

| Change | Work |
|---|---|
| New graph version | One query per question and one adapter |
| New course | A new question set under the same rules |
| Extraction by an LLM | Stability over two runs becomes relevant; it is not defined yet |

## Open questions

- Coverage: answered by the graph together with the quiz as the test set, or removed from the uses?
- Threshold for Part B.
- Whether duplicates are reported. Finding them needs a manual check of candidates.
- Location and format of the question set file. JSON needs no new dependency; YAML would need one.
