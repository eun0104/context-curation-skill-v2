# context-curation

English | [한국어](README.ko.md)

An opencode skill for **managing persistent context layers** in multi-session AI coding
agent projects.

If `session-handoff` carries work across session boundaries, this skill decides *what should
stop being session state and become project state*, then keeps that project state small,
reachable, and internally consistent.

## The problem

As a project grows, AGENTS.md expands, documentation becomes stale or duplicated, and orphaned
documents accumulate. An unreachable document is worse than no document at all because it creates
false confidence.

At setup time, you cannot know which documents the project will eventually need. Those needs
emerge as the project develops. This skill closes that gap.

## Layer model

Documents are classified by **read frequency**, not importance.

| Layer | Documents | When read | Budget |
|---|---|---|---|
| L0 | `AGENTS.md` | Every session | 2,000-token hard cap |
| L1 | root `plan.md`, `docs/handoff/HANDOFF.md` | At session start | ~1,500 each |
| L2 | `decisions` · `architecture` · `domain` · `rules` · `reference` | On demand | Unlimited, but must be linked |
| L3 | `docs/handoff/SESSION_LOG.md`, `docs/archive/` | Never read wholesale; searched only | Append-only |

The L0 cap is not a spending limit. It is a **shape constraint**. If seven non-negotiable rules
compete for attention with paragraphs of ordinary facts, they stop reading like rules.

## How it works

1. Before the first context initialization, turn the initial project concept and rough plan into a
   minimal memory contract without requiring session history.
2. After initialization, audit document budgets, pointers, reachability, duplication, freshness,
   and session-log size.
3. Search the full log for tags and read only the relevant session bodies. If no state file exists,
   use the latest five session entries as the bootstrap scope.
4. Evaluate durable-promotion candidates for recurrence, cost of loss, stability, and
   non-derivability.
5. Write a proposal that adjusts both the read path in `AGENTS.md` and the write path in
   `docs/handoff/handoff-spec.md`, then stop.
6. Apply only the items the user explicitly approves, then rerun the audit to verify the result.

A rejected candidate is not excluded forever. Reconsider it when it recurs or its evidence
changes.

## Installation

Choose one installation scope. OpenCode supports both global and project-local skills.

**Global — reuse one copy across projects:**

```bash
mkdir -p ~/.config/opencode/skills ~/.config/opencode/commands
cp -r context-curation ~/.config/opencode/skills/

# Optional: explicit /tune-docs command in every project
cp context-curation/command/tune-docs.md ~/.config/opencode/commands/
```

**Project-local — pin and review the version with one project:**

```bash
PROJECT_DIR=/path/to/project
mkdir -p "$PROJECT_DIR/.opencode/skills" "$PROJECT_DIR/.opencode/commands"
cp -r context-curation "$PROJECT_DIR/.opencode/skills/"

# Optional: explicit /tune-docs command in this project
cp "$PROJECT_DIR/.opencode/skills/context-curation/command/tune-docs.md" \
   "$PROJECT_DIR/.opencode/commands/tune-docs.md"
```

Copying the skill folder completes installation. Users do not need to open or manually apply files
under `integration/` or `templates/`. The command copy is optional; the skill can always be invoked
by name. Restart OpenCode after installing or changing a skill or command so discovery is refreshed.

If both scopes contain `context-curation`, treat the project-local copy as an intentional override.
Keep the copies version-aligned unless the project is deliberately pinned, and verify the loaded
skill base directory on the first run. If your OpenCode/Oh My OpenCode combination advertises both
copies instead of resolving one, remove the unintended copy rather than relying on ambiguous
selection. A run uses scripts, templates, and references only from the loaded copy.

Regardless of the curation scope, copy `session-context-init` and `session-handoff` into the
project's `.opencode/skills/` directory. After the initial project plan is clear, invoke curation
before `session-context-init`. The skill detects the lifecycle automatically; no `pre-init` prompt
argument is required. It proposes missing contract instruction blocks at the two fixed local paths.
The first approved run installs them and creates `docs/handoff/handoff-spec.md` and
`docs/handoff/.curation-state.json`.

The spec also carries a prompt-only Git checkpoint policy. `session-context-init` detects a
missing repository and offers `git init`; every `session-handoff` checks for uncommitted work and
offers a checkpoint commit. The user must approve the exact operation, paths, and commit message.
The policy never automates branch changes, push, merge, rebase, reset, or stash.

Contract blocks are Markdown instructions, not deterministic runtime hooks. This skill does not
install an OpenCode runtime hook.

See [`context-curation/INSTALL.md`](context-curation/INSTALL.md) for the complete installation and
integration guide (Korean), and [`context-curation/SKILL.md`](context-curation/SKILL.md) for the
agent execution contract.

## Usage

### First project setup

1. Form the initial project concept and a rough plan.
2. Install the project-local `session-context-init` and `session-handoff` copies under
   `.opencode/skills/`.
3. Before running context init, invoke curation explicitly. It detects pre-init from project state:

   ```text
   /tune-docs
   ```

   Or ask: `Run the context-curation skill for this project.`
4. Review `docs/_tuning-proposal.md`. Missing or stale session contract blocks appear as blocking
   items.
   Approve or reject items by ID; no persistent project file is changed before approval.
5. After the approved items are applied, run `session-context-init`. It creates root `AGENTS.md`,
   root `plan.md`, and the files declared under `docs/handoff/`. The spec supplies the required
   curation routing entry and L0 budget marker for AGENTS.md; no separate snippet is applied. If
   the project is not a Git repository, init asks before running `git init`, then offers the first
   checkpoint after its writes.

### Periodic tuning

Run `/tune-docs`, or ask naturally:

```text
The agent keeps forgetting the same constraint. Tune the project docs.
We closed a milestone. Run context-curation before the next session.
```

The skill audits and harvests evidence, writes `docs/_tuning-proposal.md`, and stops. Review the
proposal item by item; only approved items are applied. Typical triggers are five or more sessions
since the last tuning, a closed milestone, documentation drift, an oversized AGENTS.md, or repeated
agent mistakes.

### Session-end Git checkpoint

After writing the handoff, `session-handoff` runs a read-only Git status check. If work remains
uncommitted, it shows staged work separately, proposes exact candidate paths and a message, and
asks whether to commit. It never uses broad staging such as `git add -A`; declining does not block
handoff.

## Scientific modeling projects

The base curation workflow works for any coding project. Scientific support is an optional,
evidence-triggered profile: if the project does not use scientific theories, mechanisms, or
equations, curation does not load the profile or propose its specialized documents and fields.

```text
Any coding project → base context curation
Scientific project → base context curation + scientific profile + optional domain profile
```

When the initial concept applies or combines scientific theories, mechanisms, or equations,
pre-init curation loads `references/profiles/scientific-modeling.md` before designing the memory
contract. More specific profiles, such as physics-based device modeling and fitting, add their
domain requirements without replacing the general scientific contract.

Accepted scientific claims preserve a traceable chain from source or explicit derivation, through
the canonical equation or claim and its implementation, to named verification evidence. The
profile separates hypotheses, adopted and validated models, numerical approximations, fitted
parameters, and rejected alternatives. Missing links remain explicit `[TBD]` items; recurring text
is never treated as scientific validation by itself.

For standalone audit commands, see [Audit script](#audit-script). For detailed installation,
operating settings, and troubleshooting, see
[`context-curation/INSTALL.md`](context-curation/INSTALL.md).

## Repository layout

```text
context-curation/
├── SKILL.md                       # Layer model, seven-step workflow, and guardrails
├── INSTALL.md                     # Installation and integration guide (Korean)
├── command/tune-docs.md           # Slash command for explicit invocation
├── scripts/docs_inventory.py      # Structural audit; standard library only, no network
├── scripts/session_contract_blocks.py  # Check/install project-local contract blocks
├── references/
│   ├── promotion-test.md          # Four promotion criteria and examples
│   ├── routing-table.md           # Destination selection and document formats
│   ├── audit-checks.md            # Responses for each audit finding
│   ├── agents-md-contract.md      # What belongs in L0 and what does not
│   └── profiles/
│       ├── scientific-modeling.md # Theory/equation traceability and verification
│       └── physics-modeling.md    # Device-modeling and data-fitting refinements
├── templates/                     # Templates for new documents
└── integration/                   # Project-local init and handoff integration blocks

tests/
├── test_docs_inventory.py         # Standard-library regression tests
├── test_session_contract_blocks.py  # Contract-block regression tests
└── fixtures/bootstrap-project/    # Anonymous forward-test project
```

## Design principles

**Propose, then stop.** At Step 5, write `docs/_tuning-proposal.md` and stop. Do not change any
project documentation before approval. Documentation restructuring is difficult to review after
the fact.

**Keep runtime session skills project-local.** Shared skills are upstream templates; pinned local
copies make each project's path and field contract reviewable. Keep the declarative handoff spec
even when the procedural skills are local so init and handoff cannot drift apart.

**Prompt for Git checkpoints, never automate Git workflow.** Init can offer repository
initialization, and handoff can offer a narrow checkpoint commit. Both require explicit approval;
branch and remote operations remain separate user requests.

**Do not delete durable documentation.** Move it to `docs/archive/` and record what replaced it.
Only the temporary review artifact `docs/_tuning-proposal.md` is removed after approved changes
are applied.

**Keep one source of truth.** State each fact in one place and point to it everywhere else. Copying
content into AGENTS.md is where drift begins.

**Keep change sets small.** Create at most two new durable L2 knowledge documents in one run. The
review proposal, curation state, and handoff control spec do not count toward this limit.

**Use two passes.** Pass A audits, harvests, and proposes; review happens at the approval boundary;
Pass B applies and verifies. This preserves context for the quality-critical final stage without
adding an artificial split.

## Audit script

To inspect a project without invoking the skill:

```bash
# From this repository
python context-curation/scripts/docs_inventory.py --root /path/to/project

# Lifecycle is detected automatically; flags are only ambiguity overrides
# python context-curation/scripts/docs_inventory.py --root /path/to/project --pre-init
# python context-curation/scripts/docs_inventory.py --root /path/to/project --normal

# Check fixed project-local session skill contract blocks (read-only by default)
# python context-curation/scripts/session_contract_blocks.py --root /path/to/project

# From a global installation
# python ~/.config/opencode/skills/context-curation/scripts/docs_inventory.py --root /path/to/project
```

The audit reports:

- L0/L1 token budgets and missing required startup documents
- documents unreachable from AGENTS.md and broken pointers in reachable documents
- freshness based on the last Git commit or file mtime together with
  `<!-- verified: YYYY-MM-DD -->`
- paragraph duplication, session-log size, and unharvested sessions
- the recent-session bootstrap scope when no state file exists

README files are conditional L2 documents; their filename alone does not add them to the
always-read cost. The script uses only the Python standard library and makes no network requests.
Python 3.8+ is required.

## Validation

Anonymous synthetic projects provide regression coverage for layer classification, reachability,
verification dates, first-run harvest scope, Git dates, and working-tree changes.

```bash
python -m unittest discover -s tests -v
```

All thirty-one current regression tests pass, covering citation-evidence and duplication-scope
contracts, harness evidence collection, non-UTF-8
stdout encodings, scientific
pre-init profile and traceability contracts, strict canonical session-file casing, automatic
lifecycle detection, ambiguous startup evidence, AGENTS.md initialization routing, nested handoff
paths, bootstrap scope, reachability, freshness, curation-state discovery, plural project skill
paths, approved contract-block insertion, prompt-only Git checkpoint contracts, legacy-marker
migration, outdated-block upgrades, and idempotence.

## License

Not yet specified.
