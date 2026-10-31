# E-Learning Diabetologie

Builds a knowledge graph from German e-learning content on diabetology, as the basis for generating questions. The project is designed so that future contributors can extend it to further modules, courses and websites.

Goal, scope and target users: [`docs/0002-project-scope.md`](docs/0002-project-scope.md).

## Repository structure

| Path | Content |
|---|---|
| `docs/` | Numbered knowledge base: requirements, decisions and findings |
| `prototype/` | Extraction prototype for one Storyline module and its tests, see [`docs/0003-data-analysis.md`](docs/0003-data-analysis.md#46-extraction-prototype) |
| `data/` | Local only and git-ignored: raw data in `data/raw/`, extraction output in `data/extracted/` |
| `.github/` | Issue and pull request templates |
| `AGENTS.md` | Instructions for AI coding agents (`CLAUDE.md` imports it) |

The code structure and tech stack are still to be decided ([#7](https://github.com/1BlauNitrox/e-learning-diabetologie/issues/7)).

## Contributing

We work issue-based with a GitHub Project board, short-lived branches, pull requests and mandatory peer review. AI agents follow the same process. Read [`docs/0001-workflow.md`](docs/0001-workflow.md) before you start.

## Language

Code, comments, issues, PRs and documentation are written in **English**. The source content and any generated learning content are **German**.

## Documentation

`docs/` is a numbered knowledge base (`0001-workflow.md`, `0002-project-scope.md`, …) that records **currently active** requirements, decisions and findings about external systems and data. It is living documentation:

- Docs describe the current state, not its history. When something changes, rewrite the existing doc instead of appending to it.
- Create a new numbered file only for a new decision or finding. If an existing doc covers the topic, update that doc instead.
- Delete docs that are no longer true.
