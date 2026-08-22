<!-- context-curation:session-context-init-contract-block:start -->
## Project memory contract

Require `docs/handoff/handoff-spec.md` before initialization and read it first. Keep `AGENTS.md`
and `plan.md` at the project root. Create handoff-owned files only under `docs/handoff/`, using
the paths, initial fields, and cadences declared in the spec. When creating `AGENTS.md`, include
the routing entry and budget marker from the spec's `AGENTS.md initialization` section.

If the spec is missing, ask the user to run `context-curation`. That skill determines the lifecycle
from project evidence. Do not invent a default document layout.

Before creating project files, follow the spec's `Git checkpoint policy`. Check whether the project
is already a Git work tree. If it is not, tell the user and ask whether to run `git init`; continue
initialization if they decline, and never initialize silently. After initialization writes finish,
run the policy's read-only status check and offer a checkpoint commit when changes exist. Do not
stage or commit until the user approves the exact paths and commit message.
<!-- context-curation:session-context-init-contract-block:end -->
