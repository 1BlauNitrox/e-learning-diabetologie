# 0001 – Workflow

How we plan, build, review and merge work. These rules apply to team members and AI agents alike.

```
Issue → Backlog → Ready → In Progress → In Review → Ready to merge → Done
         (DoR)     (claim + branch)  (PR)     (approved)   (merged, DoD)
```

## GitHub Project board

All work is tracked as issues on the repository's GitHub Project board.

| Column | Meaning |
|---|---|
| `Backlog` | Captured, but not yet fully specified |
| `Ready` | Meets the Definition of Ready and can be picked up |
| `In Progress` | Assigned and being worked on in a branch |
| `In Review` | The PR is open and waiting for review |
| `Ready to merge` | Approved; only the merge is left |
| `Done` | Merged into `main`, issue closed |

| Priority | Meaning |
|---|---|
| `Critical` | Blocks other work or the core deliverable; do first |
| `Important` | Needed for the core deliverable |
| `Nice to Have` | Improves the result but is not required |
| `Deferred` | Consciously postponed and kept for later or for future contributors |

| Label | Use for |
|---|---|
| `documentation` | Docs, README, templates, `AGENTS.md` |
| `planning` | Scoping, design and decisions |
| `data` | Data analysis, extraction and processing |
| `bug` | Something does not work as intended |
| `enhancement` | New functionality |

Labels are added as needed. Whenever a label is added, update this table.

## Issues

Every issue follows the issue template in [`.github/ISSUE_TEMPLATE/task.md`](../.github/ISSUE_TEMPLATE/task.md):

- **Purpose**: the underlying problem or goal, i.e. why the work matters
- **Description**: what is to be done, in a few sentences
- **Outcome**: the concrete deliverables (files, features, decisions)
- **Acceptance criteria**: a checklist that a reviewer can verify

An issue is one reviewable unit of work. Split it if it would produce a PR too large to review in one sitting. An issue moves from `Backlog` to `Ready` only when it meets the Definition of Ready in the issue template.

## Development cycle

1. **Claim**: pick the highest-priority issue from `Ready`, assign yourself and move it to `In Progress`.
2. **Branch** off an up-to-date `main`:
   - `feature/<issue-number>-<short-desc>` (e.g. `feature/5-data-analysis`)
   - `bug/<issue-number>-<short-desc>` (e.g. `bug/12-broken-umlauts`)
3. **Commit** each self-contained unit of work using [Conventional Commits](https://www.conventionalcommits.org/): `<type>(<optional scope>): <summary>` with type `feat`, `fix`, `docs`, `style`, `refactor`, `test` or `chore`.
4. **Open a PR** against `main` using the PR template, with `Closes #<issue-number>` in its body. For larger tasks, open it early as a draft.
5. **Review**: mark the PR as ready, move the issue to `In Review` and request a review from the other team member. The reviewer either approves or requests changes; the author resolves every comment.
6. **Merge**: once the PR is approved and the Definition of Done in the PR template is met, squash-merge it into `main` and delete the branch. The issue closes automatically and moves to `Done`.

Nobody pushes directly to `main`. Mini-fixes such as typos or broken links may be merged without review.

## Agentic AI

We use **Claude Code** as an AI agent throughout the workflow. It works within this workflow, not around it. Its project-specific instructions are in [`AGENTS.md`](../AGENTS.md).

| Step | How the agent helps | What the human does |
|---|---|---|
| Brainstorming and scoping | Explores options, asks questions, points out trade-offs | Makes the decision and records it in `docs/` |
| Issue creation | Drafts a full issue from a short idea, using the template and the project context | Reviews and edits the draft before it is published |
| Planning | Writes an implementation plan before any code is changed | Reviews, corrects and approves the plan |
| Implementation | Writes code, tests and docs on the issue branch, commits, opens the PR | Checks the result before requesting review |
| Review | Can do a first review pass | Gives the approval that counts |

Rules:

- **Humans own every change.** Whoever runs the agent is the author of its output and reviews it before anyone else sees it. Every PR still needs the approval of the other team member.
- **Plan before code.** Any non-trivial issue starts with an agent-written plan that a human approves. Most of our time goes into planning, so implementation can be clear and quick.
- **Context is part of the work.** Agents are only as good as their context. Keeping `README.md`, `AGENTS.md` and `docs/` accurate is part of every issue.
- **Same conventions.** Agents use the same branches, Conventional Commits and PR process, never push to `main` and never merge.
- **No attribution in the history.** Commits, issues and PRs carry no AI attribution lines. Our AI usage is disclosed in one place at the end of the project.

## Communication

- **Team**: we meet regularly to sync progress, plan the next issues and remove blockers. Day-to-day discussion of a task happens in its issue or PR. Decisions with a lasting impact are written into `docs/`.
- **Supervisor**: we update our supervisor regularly on progress, blockers and open questions. Open questions are collected in the relevant issue or doc beforehand, and the answers are recorded there afterwards.
