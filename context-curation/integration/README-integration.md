# How the pieces fit

The project keeps two startup files at the root and all handoff-owned state under one directory:

```text
<project>/
├── AGENTS.md
├── PLAN.md
├── .opencode/skills/
│   ├── context-curation/            # only when project-local
│   ├── session-context-init/
│   └── session-handoff/
└── docs/handoff/
    ├── handoff-spec.md
    ├── handoff.md
    ├── session-log.md
    ├── decisions.md
    └── .curation-state.json
```

`AGENTS.md` is the read-path control surface. `docs/handoff/handoff-spec.md` is the project memory
contract consumed by both project-local session skills. It declares both the write path and the
required AGENTS.md initialization entries. Curation tunes both after review.

`context-curation` itself may be installed globally or under the project's `.opencode/skills/`.
Each run resolves its base from the `SKILL.md` actually loaded and uses scripts, templates,
references, and integration blocks only from that copy. When both scopes contain the same skill
name, the project-local copy is an intentional override; verify the resolved base and remove an
unintended duplicate if the installed OpenCode/Oh My OpenCode versions expose both copies.

## Lifecycle

| Phase | Skill | Result |
|---|---|---|
| Initial concept and rough plan | — | Enough evidence to design a minimal memory contract |
| Automatic lifecycle check | `context-curation` | Selects pre-init or normal from startup files and session evidence; stops if ambiguous |
| Pre-init curation | `context-curation` | Proposes and, after approval, writes the memory spec and curation state |
| Session 1 initialization | project-local `session-context-init` | Offers Git initialization when absent; creates root `AGENTS.md`, root `PLAN.md`, and the initial files and routing entries listed in the spec |
| Session end | project-local `session-handoff` | Rewrites handoff, appends the session log, writes on-event records, and offers a Git checkpoint when dirty |
| Periodic tuning | `context-curation` | Restructures docs and revises the same spec every ~5 sessions |

The user invokes curation without a mode argument. Pre-init must not treat absent startup files or
session logs as defects. It uses the current conversation, initial plan, repository contents, and
explicit project constraints; it does not pretend that session recurrence evidence already exists.
Partial startup files or initialized-session evidence without startup files produce `ambiguous`
instead of silently choosing a mode.

## Why the session skills are project-local

Keep shared copies as upstream templates, but run pinned copies from `.opencode/skills/` in each
project. This makes path and field changes visible in the project's history and prevents one
project's needs from leaking into another.

`scripts/session_contract_blocks.py` checks these exact paths without writing. During the approved
apply pass, run it with `--apply` to install or refresh the marked blocks from the two contract-block
files. Repeated application is idempotent, legacy `hook` markers are migrated, and the script never
falls back to a global skill. These are Markdown instruction blocks, not OpenCode runtime hooks.

Keep `handoff-spec.md` even with local skills. The spec is declarative and shared by init and
handoff; editing both procedural SKILL.md files for every schema change would create two sources
of truth. Edit a local skill only when a requirement cannot be expressed in the spec, and record
generally useful changes for manual upstream review.

The spec's `AGENTS.md initialization` section is the single source for the curation routing entry
and L0 budget marker. `session-context-init` applies it while creating AGENTS.md. No integration
snippet needs to be read or copied by the user.

## Git checkpoint policy

The spec carries one project-local policy shared by init, handoff, and normal-mode curation apply.
It is deliberately smaller than Git Flow:

- Detect a missing repository and ask before `git init`.
- At init completion and every handoff, show read-only status and offer a checkpoint when dirty.
- Keep pre-existing staged work separate and stage only user-approved literal paths.
- Require approval of the operation, exact paths, and commit message.
- Never automate branch changes, push, merge, rebase, reset, stash, or amend.

Declining Git initialization or a checkpoint does not fail the session operation. The agent reports
the remaining uncommitted paths so the next session does not mistake them for a clean baseline.

## Ownership

| Surface | Owner |
|---|---|
| Root `AGENTS.md` routing and persistent L2 structure | `context-curation`, after approval |
| Root `PLAN.md` initial creation and ongoing project planning | `session-context-init` / project workflow |
| `docs/handoff/handoff-spec.md` | `context-curation`, after approval |
| Files written according to the spec | project-local session skills |
| Shared upstream skill templates | human maintainer |
