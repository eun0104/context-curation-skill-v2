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
| L1 | root `PLAN.md`, `docs/handoff/handoff.md` | At session start | ~1,500 each |
| L2 | `decisions` · `architecture` · `domain` · `rules` · `reference` | On demand | Unlimited, but must be linked |
| L3 | `docs/handoff/session-log.md`, `docs/archive/` | Never read wholesale; searched only | Append-only |

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

```bash
# Global installation (recommended)
cp -r context-curation ~/.config/opencode/skills/
cp context-curation/command/tune-docs.md ~/.config/opencode/commands/

# For a project-local installation:
# cp -r context-curation <project>/.opencode/skills/
```

Keep `context-curation` global, but copy `session-context-init` and `session-handoff` into the
project's `.opencode/skills/` directory. Run curation in pre-init mode after the initial project
plan is clear and before running `session-context-init`. It detects missing contract instruction
blocks at the two fixed local paths and proposes their installation; the first approved run
installs them and creates `docs/handoff/handoff-spec.md` and
`docs/handoff/.curation-state.json`.

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
3. Before running context init, invoke curation explicitly:

   ```text
   /tune-docs pre-init
   ```

   Or ask: `Use context-curation in pre-init mode to design this project's memory contract.`
4. Review `docs/_tuning-proposal.md`. Missing or stale session contract blocks appear as blocking
   items.
   Approve or reject items by ID; no persistent project file is changed before approval.
5. After the approved items are applied, run `session-context-init`. It creates root `AGENTS.md`,
   root `PLAN.md`, and the files declared under `docs/handoff/`.

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
│       └── physics-modeling.md    # Profile for physics modeling and data fitting
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

# Before session-context-init
# python context-curation/scripts/docs_inventory.py --root /path/to/project --pre-init

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

All sixteen current regression tests pass, covering the pre-init lifecycle, nested handoff paths,
bootstrap scope, reachability, freshness, curation-state discovery, plural project skill paths,
approved contract-block insertion, legacy-marker migration, and idempotence.

## License

Not yet specified.
