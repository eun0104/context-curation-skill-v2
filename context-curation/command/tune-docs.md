---
description: Audit and restructure the project's persistent doc layer (AGENTS.md, plan.md, docs/*)
---

Run the `context-curation` skill on this project.

Resolve and read the skill in this order: project-local
`.opencode/skills/context-curation/SKILL.md`, then global
`~/.config/opencode/skills/context-curation/SKILL.md`. If both exist, the project-local copy is the
intentional override. Announce the loaded base directory, follow its run procedure from Step 0,
and use scripts, templates, references, and integration blocks only from that same copy.

Two reminders that matter more than the rest:

- Determine the lifecycle from project evidence as Step 0 requires. The user does not need to
  supply `pre-init`; stop for clarification only when the inventory reports `ambiguous`.
- Step 5 ends with writing `docs/_tuning-proposal.md` and **stopping**. Do not create, edit,
  move, or archive any other file until the user approves item by item.
- Run `scripts/docs_inventory.py` rather than estimating counts by reading files. The numbers
  drive every decision in the run. Resolve the script relative to the SKILL.md that was actually
  loaded, whether the skill is project-local or global.

$ARGUMENTS
