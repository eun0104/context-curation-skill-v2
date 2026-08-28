import importlib.util
import json
import os
import shutil
import subprocess
import tempfile
import time
import types
import unittest
from datetime import date, timedelta
from pathlib import Path


SCRIPT = (Path(__file__).resolve().parents[1]
          / "context-curation" / "scripts" / "docs_inventory.py")
SPEC = importlib.util.spec_from_file_location("docs_inventory", SCRIPT)
inventory = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(inventory)


def args(**overrides):
    values = {
        "l0_budget": 2000,
        "l1_budget": 1500,
        "stale_days": 90,
        "dup_threshold": 0.45,
        "context_window": 200000,
        "bootstrap_sessions": 5,
        "pre_init": None,
    }
    values.update(overrides)
    return types.SimpleNamespace(**values)


def write(root: Path, rel: str, text: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


class InventoryTests(unittest.TestCase):
    def test_canonical_session_path_casing_matches_runtime_skills(self):
        spec = (SCRIPT.parents[1] / "templates" / "handoff-spec.md")
        spec_text = spec.read_text(encoding="utf-8")

        self.assertEqual(("plan.md", "docs/handoff/HANDOFF.md"),
                         inventory.REQUIRED_L1_PATHS)
        self.assertIn("docs/handoff/SESSION_LOG.md", inventory.SESSION_GLOBS)
        self.assertNotIn("docs/handoff/session-log.md", inventory.SESSION_GLOBS)
        self.assertIn("`plan.md`", spec_text)
        self.assertIn("`docs/handoff/HANDOFF.md`", spec_text)
        self.assertIn("`docs/handoff/SESSION_LOG.md`", spec_text)
        self.assertIn("`docs/handoff/DECISIONS.md`", spec_text)

    def test_noncanonical_casing_is_not_accepted_as_the_runtime_contract(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            write(root, "AGENTS.md", "[plan](PLAN.md)\n")
            write(root, "PLAN.md", "# Wrong-case plan\n")
            write(root, "docs/handoff/handoff.md", "# Wrong-case handoff\n")
            write(root, "docs/handoff/session-log.md", "## Session 001\n")

            result = inventory.audit(root, args())
            layers = {record["path"]: record["layer"] for record in result["docs"]}
            missing = {item["path"] for item in result["budget"] if item.get("missing")}

            self.assertEqual("ambiguous", result["mode"])
            self.assertIn("plan.md is missing", result["mode_reason"])
            self.assertEqual("L2", layers["PLAN.md"])
            self.assertEqual({"plan.md", "docs/handoff/HANDOFF.md"}, missing)
            self.assertEqual(0, result["sessions"]["files"])

    def test_only_contract_paths_are_l1_and_all_docs_need_reachability(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            write(root, "AGENTS.md", "[plan](plan.md)\n")
            write(root, "plan.md", "# Plan\n")
            write(root, "docs/handoff/HANDOFF.md", "# Handoff\n")
            write(root, "README.md", "# How to run\n")
            write(root, "docs/subsystem/README.md", "# Subsystem\n")

            result = inventory.audit(root, args())
            layers = {record["path"]: record["layer"] for record in result["docs"]}

            self.assertEqual("L0", layers["AGENTS.md"])
            self.assertEqual("L1", layers["plan.md"])
            self.assertEqual("L1", layers["docs/handoff/HANDOFF.md"])
            self.assertEqual("L2", layers["README.md"])
            self.assertEqual("L2", layers["docs/subsystem/README.md"])
            self.assertIn("docs/handoff/HANDOFF.md", result["orphans"])
            self.assertIn("README.md", result["orphans"])

    def test_missing_required_l1_docs_are_reported(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            write(root, "AGENTS.md", "# Agent instructions\n")

            result = inventory.audit(root, args())
            missing = {item["path"] for item in result["budget"]
                       if item.get("missing")}

            self.assertEqual({"plan.md", "docs/handoff/HANDOFF.md"},
                             missing - {"AGENTS.md"})

    def test_verification_marker_resets_but_does_not_disable_staleness(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            write(root, "AGENTS.md",
                  "[plan](plan.md) [handoff](docs/handoff/HANDOFF.md) "
                  "[old](docs/old.md) [fresh](docs/fresh.md)\n")
            write(root, "plan.md", "# Plan\n")
            write(root, "docs/handoff/HANDOFF.md", "# Handoff\n")
            old_date = (date.today() - timedelta(days=180)).isoformat()
            old_doc = write(root, "docs/old.md", f"<!-- verified: {old_date} -->\n")
            fresh_doc = write(root, "docs/fresh.md",
                              f"<!-- verified: {date.today().isoformat()} -->\n")
            old_epoch = (date.today() - timedelta(days=200)).strftime("%Y-%m-%d")
            old_value = time.mktime(time.strptime(old_epoch, "%Y-%m-%d"))
            os.utime(old_doc, (old_value, old_value))
            os.utime(fresh_doc, (old_value, old_value))

            result = inventory.audit(root, args())
            stale = {item["path"] for item in result["stale"]}

            self.assertIn("docs/old.md", stale)
            self.assertNotIn("docs/fresh.md", stale)

    def test_bootstrap_uses_latest_five_actual_session_entries(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            write(root, "AGENTS.md", "[plan](plan.md) [handoff](docs/handoff/HANDOFF.md)\n")
            write(root, "plan.md", "# Plan\n")
            write(root, "docs/handoff/HANDOFF.md", "# Handoff\n")
            headings = "\n".join(f"## Session {number}" for number in (1, 3, 7, 9, 10, 12))
            write(root, "docs/handoff/SESSION_LOG.md", headings)

            result = inventory.audit(root, args())
            output = inventory.report(result, args())

            self.assertIn("latest 5 session entries (3, 7, 9, 10, 12)", output)

    def test_link_extraction_ignores_examples_globs_and_placeholders(self):
        text = """
`docs/real.md`
`docs/sessions/007-*.md`
`docs/domain/<topic>.md`

```markdown
[example](docs/not-real.md)
`docs/also-not-real.md`
```
"""
        self.assertEqual({"docs/real.md"}, inventory.extract_links(text))

    def test_broken_targets_in_unreachable_docs_do_not_create_noise(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            write(root, "AGENTS.md", "[plan](plan.md) [handoff](docs/handoff/HANDOFF.md)\n")
            write(root, "plan.md", "# Plan\n")
            write(root, "docs/handoff/HANDOFF.md", "# Handoff\n")
            write(root, "docs/orphan.md", "[missing](missing.md)\n")

            result = inventory.audit(root, args())

            self.assertIn("docs/orphan.md", result["orphans"])
            self.assertEqual([], result["broken_links"])

    def test_broken_target_in_reachable_doc_is_reported(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            write(root, "AGENTS.md",
                  "[plan](plan.md) [handoff](docs/handoff/HANDOFF.md) [rules](docs/rules.md)\n")
            write(root, "plan.md", "# Plan\n")
            write(root, "docs/handoff/HANDOFF.md", "# Handoff\n")
            write(root, "docs/rules.md", "[missing](missing.md)\n")

            result = inventory.audit(root, args())

            self.assertEqual([{"from": "docs/rules.md", "link": "missing.md"}],
                             result["broken_links"])

    @unittest.skipUnless(shutil.which("git"), "git is required for commit metadata test")
    def test_git_last_commit_uses_repo_relative_pathspec(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            tracked = write(root, "docs/tracked.md", "# Tracked\n")
            commands = [
                ["git", "init", "-q"],
                ["git", "config", "user.email", "fixture@example.invalid"],
                ["git", "config", "user.name", "Fixture"],
                ["git", "add", "docs/tracked.md"],
            ]
            for command in commands:
                subprocess.run(command, cwd=root, check=True, capture_output=True)
            commit_env = os.environ.copy()
            commit_env["GIT_AUTHOR_DATE"] = "2020-01-02T12:00:00Z"
            commit_env["GIT_COMMITTER_DATE"] = "2020-01-02T12:00:00Z"
            subprocess.run(["git", "commit", "-q", "-m", "fixture"], cwd=root,
                           check=True, capture_output=True, env=commit_env)

            commit_date, sha = inventory.git_last_commit(root, tracked)
            fresh_age, _ = inventory.freshness(
                tracked.read_text(encoding="utf-8"), tracked.stat().st_mtime, commit_date)

            self.assertEqual("2020-01-02", commit_date)
            self.assertRegex(sha or "", r"^[0-9a-f]{7,}$")
            self.assertGreater(fresh_age, 90)

            tracked.write_text("# Tracked\n\nUpdated now.\n", encoding="utf-8")
            self.assertTrue(inventory.git_worktree_changed(root, tracked))
            dirty_age, _ = inventory.freshness(
                tracked.read_text(encoding="utf-8"), tracked.stat().st_mtime, None)
            self.assertLessEqual(dirty_age, 1)

    def test_state_template_is_valid_and_starts_without_fake_rejections(self):
        template = (SCRIPT.parents[1] / "templates" / "curation-state.json")
        state = json.loads(template.read_text(encoding="utf-8"))
        self.assertEqual(1, state["schema_version"])
        self.assertIsNone(state["last_tuned"])
        self.assertEqual([], state["rejected_candidates"])

    def test_state_is_loaded_from_handoff_control_directory(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            write(root, "AGENTS.md", "[plan](plan.md) [handoff](docs/handoff/HANDOFF.md)\n")
            write(root, "plan.md", "# Plan\n")
            write(root, "docs/handoff/HANDOFF.md", "# Handoff\n")
            expected = {"schema_version": 1, "last_tuned": "2026-08-18"}
            write(root, "docs/handoff/.curation-state.json", json.dumps(expected))

            result = inventory.audit(root, args())

            self.assertEqual(expected, result["curation_state"])

    def test_fresh_project_auto_detects_pre_init(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            write(root, "README.md", "# Initial project concept\n")

            result = inventory.audit(root, args())
            output = inventory.report(result, args())

            self.assertEqual("pre-init", result["mode"])
            self.assertIn("no startup files", result["mode_reason"])
            self.assertEqual([], [item for item in result["budget"]
                                  if item.get("missing")])
            self.assertTrue(result["reachability_deferred"])
            self.assertIn("detected automatically", output)
            self.assertIn("No session log expected", output)
            self.assertIn("No orphan judgment is made", output)

    def test_approved_pre_init_state_stays_pre_init_until_init_runs(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            write(root, "docs/handoff/handoff-spec.md", "# Memory contract\n")
            state = {
                "schema_version": 1,
                "last_tuned": "2026-08-20",
                "last_tuned_session": None,
                "harvested_through_session": 0,
            }
            write(root, "docs/handoff/.curation-state.json", json.dumps(state))

            result = inventory.audit(root, args())

            self.assertEqual("pre-init", result["mode"])

    def test_inconsistent_lifecycle_evidence_is_ambiguous(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            write(root, "AGENTS.md", "# Partial initialization\n")

            result = inventory.audit(root, args())
            output = inventory.report(result, args())
            forced = inventory.audit(root, args(pre_init=True))

            self.assertEqual("ambiguous", result["mode"])
            self.assertIn("plan.md is missing", result["mode_reason"])
            self.assertIn("do not continue with curation", output)
            self.assertEqual("pre-init", forced["mode"])
            self.assertIn("explicit", forced["mode_reason"])

    def test_duplication_result_does_not_claim_more_than_it_checked(self):
        # Five-word shingles catch copies, not restatements. A clean run that
        # reads as "no duplication" is the same false confidence this skill
        # warns about for unreachable docs, so the limit is stated either way.
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            write(root, "AGENTS.md", "[plan](plan.md)\n")
            write(root, "plan.md", "# Plan\n")

            output = inventory.report(inventory.audit(root, args()), args())

            self.assertIn("No copied passages above threshold.", output)
            self.assertNotIn("No near-duplicate passages", output)
            self.assertIn("is not detected", output)
            self.assertIn("never as \"no duplication\"", output)

    def test_citation_checking_is_wired_to_the_script_not_left_to_prose(self):
        # The behaviour itself is covered by test_verify_proposal. What matters
        # here is that the workflow actually reaches for the script: an
        # instruction to check citations by hand is the honour system this
        # guardrail exists to replace.
        skill_dir = SCRIPT.parents[1]
        skill = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        proposal = (skill_dir / "templates" / "tuning-proposal.md").read_text(encoding="utf-8")

        self.assertTrue((skill_dir / "scripts" / "verify_proposal.py").is_file())
        self.assertIn("**Evidence:**", proposal)
        self.assertIn("not promotable", proposal)
        self.assertIn("verify_proposal.py", proposal)
        self.assertIn("scripts/verify_proposal.py --root .", skill)
        self.assertIn("verify_proposal.py` exited clean", skill)

    def test_harness_evidence_is_collected_but_never_audited(self):
        # oh-my-openagent writes the plan and its notepads under .omo/. Those are
        # harvest evidence: the agent must be told where they are, but auditing
        # them would report an orphan on every run forever, because AGENTS.md is
        # not supposed to point at another tool's working state.
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            write(root, "AGENTS.md", "[plan](plan.md)\n[handoff](docs/handoff/HANDOFF.md)\n")
            write(root, "plan.md", "# Plan\n")
            write(root, "docs/handoff/HANDOFF.md", "# Handoff\n")
            write(root, ".omo/plans/data-pipeline.md", "# Plan\n\nBuild the collector.\n")
            write(root, ".omo/notepads/data-pipeline/learnings.md", "# Learnings\n- Signatures expire.\n")
            write(root, ".omo/notepads/data-pipeline/decisions.md", "# Decisions\n- CSV over parquet.\n")

            result = inventory.audit(root, args())
            audited = {record["path"] for record in result["docs"]}
            evidence = result["evidence"]

            self.assertEqual([], result["orphans"])
            self.assertEqual([], result["broken_links"])
            self.assertFalse({p for p in audited if p.startswith(".omo/plans")})
            self.assertFalse({p for p in audited if p.startswith(".omo/notepads")})
            self.assertEqual([".omo/plans/data-pipeline.md"],
                             [item["path"] for item in evidence["plans"]])
            self.assertEqual([".omo/notepads/data-pipeline/decisions.md",
                              ".omo/notepads/data-pipeline/learnings.md"],
                             [item["path"] for item in evidence["notepads"]])
            self.assertIn("## 7. Harness evidence", inventory.report(result, args()))

    def test_pre_init_report_points_at_the_omo_plan_as_primary_evidence(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            write(root, ".omo/plans/data-pipeline.md", "# Plan\n\nBuild the collector.\n")

            result = inventory.audit(root, args())
            output = inventory.report(result, args())

            self.assertEqual("pre-init", result["mode"])
            self.assertIn(".omo/plans/data-pipeline.md", output)
            self.assertIn("primary evidence", output)

    def test_projects_without_the_omo_harness_are_unaffected(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            write(root, "AGENTS.md", "[plan](plan.md)\n[handoff](docs/handoff/HANDOFF.md)\n")
            write(root, "plan.md", "# Plan\n")
            write(root, "docs/handoff/HANDOFF.md", "# Handoff\n")

            result = inventory.audit(root, args())

            self.assertEqual({}, result["evidence"])
            self.assertEqual([], result["orphans"])
            self.assertIn("No `.omo/` planning or notepad artefacts found.",
                          inventory.report(result, args()))

    def test_report_survives_a_non_utf8_stdout_encoding(self):
        # An agent harness always captures stdout through a pipe, so Python
        # falls back to the locale encoding rather than the console's UTF-16
        # path. On a cp949/cp932 machine that made every run die on the report's
        # em-dash before it printed anything. In-process tests cannot catch this
        # because unittest captures stdout with an encoding-free StringIO.
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            write(root, "docs/설계-문서.md", "# 설계 문서\n\n한글 본문 — em-dash 포함.\n")

            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "cp949"
            done = subprocess.run(["python", str(SCRIPT), "--root", str(root)],
                                  capture_output=True, env=env)
            stdout = done.stdout.decode("utf-8")

            self.assertNotIn("Traceback", done.stderr.decode("utf-8", "replace"))
            self.assertEqual(0, done.returncode)
            self.assertIn("Mode: **pre-init** —", stdout)
            self.assertIn("docs/설계-문서.md", stdout)


if __name__ == "__main__":
    unittest.main()
