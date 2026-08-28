from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = (Path(__file__).resolve().parents[1]
          / "context-curation" / "scripts" / "verify_proposal.py")
SPEC = importlib.util.spec_from_file_location("verify_proposal", SCRIPT)
verify = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(verify)


LOG = """## Session 001

### Learned
- [gotcha] The vendor signature expires 30s after issue; retries must re-sign.

## Session 002

### Decided
- [decision] CSV over parquet, for in-house tool compatibility.
"""


def write(root: Path, rel: str, text: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def proposal(*items: str) -> str:
    return "# Proposal\n\n## B. Promotions\n\n" + "\n".join(items) + "\n\n## C. Other\n"


def item(number: int, title: str, source: str, evidence: str | None) -> str:
    out = [f"### B{number}. {title}", f"- **Source:** {source}"]
    if evidence is not None:
        out += ["- **Evidence:**", "  ```text", evidence, "  ```"]
    out.append("- **Destination:** `docs/domain/gotchas.md`")
    return "\n".join(out) + "\n"


def statuses(results):
    return {r["id"]: r["status"] for r in results}


class VerifyProposalTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        write(self.root, "docs/handoff/SESSION_LOG.md", LOG)

    def tearDown(self):
        self._tmp.cleanup()

    def run_on(self, text):
        path = write(self.root, "docs/_tuning-proposal.md", text)
        return verify.run(self.root, path)

    def test_a_reproducible_citation_verifies(self):
        results = self.run_on(proposal(item(
            1, "Signatures expire", "`docs/handoff/SESSION_LOG.md`, Session 001, line 4",
            "  $ grep -n \"signature expires\" docs/handoff/SESSION_LOG.md\n"
            "  4:- [gotcha] The vendor signature expires 30s after issue; retries must re-sign.")))

        self.assertEqual({"B1": "verified"}, statuses(results))
        self.assertEqual(1, results[0]["lines_checked"])

    def test_a_fact_that_is_not_in_the_log_is_reported(self):
        # The invented-citation failure mode: plausible text, absent from the file.
        results = self.run_on(proposal(item(
            1, "Vendor rate-limits", "`docs/handoff/SESSION_LOG.md`, Session 002, line 9",
            "  $ grep -n \"rate-limit\" docs/handoff/SESSION_LOG.md\n"
            "  9:- [gotcha] The vendor rate-limits to 100 requests per minute.")))

        self.assertEqual({"B1": "mismatch"}, statuses(results))

    def test_a_real_line_cited_at_the_wrong_number_is_reported_with_the_real_one(self):
        results = self.run_on(proposal(item(
            1, "CSV over parquet", "`docs/handoff/SESSION_LOG.md`, Session 002, line 4",
            "  $ grep -n \"CSV over parquet\" docs/handoff/SESSION_LOG.md\n"
            "  4:- [decision] CSV over parquet, for in-house tool compatibility.")))

        self.assertEqual({"B1": "mismatch"}, statuses(results))
        self.assertIn("at line 9", results[0]["detail"])

    def test_a_promotion_without_evidence_cannot_pass(self):
        results = self.run_on(proposal(
            item(1, "CSV over parquet", "`docs/handoff/SESSION_LOG.md`, Session 002", None)))

        self.assertEqual({"B1": "no-evidence"}, statuses(results))

    def test_harness_notepad_citations_are_checked_the_same_way(self):
        write(self.root, ".omo/notepads/pipe/learnings.md",
              "# Learnings\n- Proxy needs NO_PROXY for the internal registry.\n")
        results = self.run_on(proposal(item(
            1, "Registry needs NO_PROXY", "`.omo/notepads/pipe/learnings.md`",
            "  $ grep -n \"NO_PROXY\" .omo/notepads/pipe/learnings.md\n"
            "  2:- Proxy needs NO_PROXY for the internal registry.")))

        self.assertEqual({"B1": "verified"}, statuses(results))

    def test_template_placeholders_are_not_mistaken_for_evidence(self):
        results = self.run_on(proposal(item(
            1, "Placeholder", "`docs/handoff/SESSION_LOG.md`",
            "  $ grep -n \"x\" docs/handoff/SESSION_LOG.md\n"
            "  42:<the line the fact came from>")))

        self.assertEqual({"B1": "placeholder"}, statuses(results))

    def test_a_missing_cited_file_is_reported_rather_than_passed(self):
        results = self.run_on(proposal(item(
            1, "Gone", "`docs/handoff/GONE.md`",
            "  $ grep -n \"x\" docs/handoff/GONE.md\n  1:- something")))

        self.assertEqual({"B1": "file-missing"}, statuses(results))

    def test_rewrapped_whitespace_still_matches(self):
        results = self.run_on(proposal(item(
            1, "Signatures expire", "`docs/handoff/SESSION_LOG.md`",
            "  $ grep -n \"signature\" docs/handoff/SESSION_LOG.md\n"
            "  4:-   [gotcha]  The vendor signature expires 30s after issue;  "
            "retries must re-sign.")))

        self.assertEqual({"B1": "verified"}, statuses(results))

    def test_a_proposal_with_no_promotions_verifies_vacuously(self):
        self.assertEqual([], self.run_on("# Proposal\n\n## C. Other\n\nNothing.\n"))

    def test_an_unreadable_proposal_is_distinguished_from_a_clean_run(self):
        self.assertIsNone(verify.run(self.root, self.root / "docs/_absent.md"))


if __name__ == "__main__":
    unittest.main()
