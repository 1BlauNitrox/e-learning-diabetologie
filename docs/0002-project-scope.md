# 0002 – Project Scope

**Status:** agreed within the team; awaiting confirmation by our supervisor (see [Open questions](#open-questions)).

## Problem

The website *Diabetologie online lernen* offers German e-learning modules on diabetology, such as *Ketonkörper* and *Blutzuckermessung in Klinik und Praxis*. They are built with Articulate Storyline. Their knowledge sits in slides: it is not structured, cannot be linked across modules, and cannot be reused automatically, for example to generate new questions. Writing questions by hand does not scale as new modules are added.

## Goal

A pipeline that extracts the content of e-learning modules and builds a **knowledge graph** of their concepts and relations. It works on the given sample and is designed to scale to further modules, courses and websites. The graph is the foundation for **question generation** and **question answering**.

## Target users

| Group | Need |
|---|---|
| Medical professionals and students (physicians, nurses, medical students) | Learn and test diabetology knowledge |
| People with diabetes and their relatives | Understand their condition and its treatment |
| The interested public | Learn about diabetes |
| Future contributors | Extend the pipeline to new content and build applications on top of the graph |

The first three groups use the question generator. Our direct deliverable, the pipeline and the graph, serves future contributors.

## Scope

### Core deliverable

1. **Data analysis and extraction**: extract the text, structure and quiz content of the given modules ([#5](https://github.com/1BlauNitrox/e-learning-diabetologie/issues/5)).
2. **Knowledge graph model**: entities, relations and provenance, so that every fact links back to its source slide ([#6](https://github.com/1BlauNitrox/e-learning-diabetologie/issues/6)).
3. **Construction pipeline**: a reproducible run from the raw module to the graph. A new module in the same format can be added without changing code. A new source format only needs a new extraction step.
4. **Agentic AI**: crewAI agents for the pipeline steps where they add value, e.g. entity and relation extraction ([#8](https://github.com/1BlauNitrox/e-learning-diabetologie/issues/8)).
5. **Documentation** that lets others run, understand and extend the pipeline.

The core is done when the pipeline runs end to end on the given sample, the resulting graph can be inspected and queried, and both are documented.

### Stretch goals

In order of priority:

1. **Question generation** from the graph: German questions with answers and a reference to the source.
2. **Evaluation** of the generated questions against the existing quiz questions in the modules.
3. **Question answering**: a chatbot that answers questions using the graph.
4. **Simple user interface**, e.g. with Streamlit.

### Out of scope

- Production deployment and hosting
- Creating or editing e-learning modules
- Medical validation of generated content (this needs domain experts; we preserve provenance so experts can check it)
- User accounts, progress tracking and LMS integration
- Any patient data

## Constraints

- **Language:** the source content is German, and any generated learning content is German. Code and documentation are English.
- **Data:** we have a small sample: one Storyline HTML5 export with its PDF handout, and two Articulate Review 360 links. Usage rights are unclear and the repository is public, so raw data is not committed.
- **Correctness:** this is medical content. Every graph fact must be traceable to its source.
- **Tools:** the course description suggests Python, crewAI, Streamlit and PostgreSQL. The final stack is decided in [#7](https://github.com/1BlauNitrox/e-learning-diabetologie/issues/7).
- **Deployment:** no target environment is known. Everything must run locally.

## Open questions

To be clarified with our supervisor:

1. Is the core deliverable (the knowledge graph pipeline) the expected result, with question generation as a bonus?
2. Can we get more modules or the full website content, and in which format? Can we access the content of the Review 360 module *Blutzuckermessung in Klinik und Praxis*?
3. May the data, or a graph derived from it, be published in the public repository?
4. Which LLM providers may process the content? Is there a budget, or are there university-hosted models?
5. Should the graph align with an existing medical ontology or terminology (e.g. MeSH, SNOMED CT)?
6. Which question types are expected (e.g. multiple choice, free text)?
