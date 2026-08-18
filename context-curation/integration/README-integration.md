# How the pieces fit

The project keeps two startup files at the root and all handoff-owned state under one directory:

```text
<project>/
├── AGENTS.md
├── PLAN.md
├── .opencode/skill/
│   ├── session-context-init/
│   └── session-handoff/
└── docs/handoff/
    ├── handoff-spec.md
    ├── handoff.md
    ├── session-log.md
    ├── decisions.md
    └── .curation-state.json
```

`AGENTS.md` is the read-path control surface. `docs/handoff/handoff-spec.md` is the write-path
contract consumed by both project-local session skills. Curation tunes both after review.

## Lifecycle

| Phase | Skill | Result |
|---|---|---|
| Initial concept and rough plan | — | Enough evidence to design a minimal memory contract |
| Pre-init curation | `context-curation` | Proposes and, after approval, writes the handoff spec and curation state |
| Session 1 initialization | project-local `session-context-init` | Creates root `AGENTS.md`, root `PLAN.md`, and the initial files listed in the spec |
| Session end | project-local `session-handoff` | Rewrites handoff, appends the session log, and writes on-event records |
| Periodic tuning | `context-curation` | Restructures docs and revises the same spec every ~5 sessions |

Pre-init mode must not treat absent startup files or session logs as defects. It uses the current
conversation, initial plan, repository contents, and explicit project constraints; it does not
pretend that session recurrence evidence already exists.

## Why the session skills are project-local

Keep shared copies as upstream templates, but run pinned copies from `.opencode/skill/` in each
project. This makes path and field changes visible in the project's history and prevents one
project's needs from leaking into another.

Keep `handoff-spec.md` even with local skills. The spec is declarative and shared by init and
handoff; editing both procedural SKILL.md files for every schema change would create two sources
of truth. Edit a local skill only when a requirement cannot be expressed in the spec, and record
generally useful changes for manual upstream review.

## Ownership

| Surface | Owner |
|---|---|
| Root `AGENTS.md` routing and persistent L2 structure | `context-curation`, after approval |
| Root `PLAN.md` initial creation and ongoing project planning | `session-context-init` / project workflow |
| `docs/handoff/handoff-spec.md` | `context-curation`, after approval |
| Files written according to the spec | project-local session skills |
| Shared upstream skill templates | human maintainer |
