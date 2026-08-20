<!-- context-curation:session-handoff-contract-block:start -->
## Project memory contract

Read `docs/handoff/handoff-spec.md` before writing any session state. Follow its document paths,
cadences, handoff fields, and session-log entry format. It overrides this skill's defaults.

The spec is maintained by `context-curation`. Do not edit it during routine handoff. If it is
missing after initialization, stop and report the broken project setup instead of falling back to
a different path layout.

After all handoff-owned writes finish, follow the spec's `Git checkpoint policy`. If the project is
not a Git work tree, remind the user and ask whether to run `git init`; handoff still completes if
they decline. If changes exist, show the read-only status summary and offer a checkpoint commit.
Never initialize, stage, commit, or change branches without the user's explicit approval.
<!-- context-curation:session-handoff-contract-block:end -->
