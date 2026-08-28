#!/usr/bin/env python3
"""
verify_proposal.py - check that every promotion in a tuning proposal cites a line
that actually exists in the file it names.

Standard library only. No network access. Read-only: never edits the proposal or
any cited file.

A citation is the one part of a proposal a reviewer cannot check by reading the
proposal. Everything else in Pass A shows up in the diff at approval time, so a
fabricated citation is the failure that survives review and lands in the
permanent layer. This script re-reads each cited file and reports whether the
pasted evidence is really there.

It checks that the quoted line EXISTS. Whether that line supports the claim is
still a judgement call for the reviewer - but the invented-citation failure mode
is closed, and that is the one that is otherwise undetectable.

Usage:
    python verify_proposal.py --root .
    python verify_proposal.py --root . --json
    python verify_proposal.py --proposal path/to/_tuning-proposal.md

Exit status: 0 when every promotion verified, 1 when any did not, 2 when the
proposal itself could not be read.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

DEFAULT_PROPOSAL = "docs/_tuning-proposal.md"

SECTION_B_RE = re.compile(r"^##\s+B\.", re.MULTILINE)
NEXT_SECTION_RE = re.compile(r"^##\s+(?!B\.)", re.MULTILINE)
ITEM_RE = re.compile(r"^###\s+(B\d+)\.\s*(.*)$", re.MULTILINE)
SOURCE_RE = re.compile(r"^\s*-\s*\*\*Source:\*\*\s*(.+)$", re.MULTILINE)
EVIDENCE_RE = re.compile(r"^\s*-\s*\*\*Evidence:\*\*", re.MULTILINE)
FENCE_RE = re.compile(r"^(\s*)```[a-zA-Z]*\s*$")
BACKTICK_PATH_RE = re.compile(r"`([^`\s]+\.[A-Za-z0-9]{1,8})`")
# grep -n gives "42:text"; with several files, "path:42:text".
NUMBERED_RE = re.compile(r"^(?:(?P<path>[^:]+):)?(?P<line>\d+):(?P<text>.*)$")
PLACEHOLDER_RE = re.compile(r"<[^>]{3,}>")


def normalize(text: str) -> str:
    """Compare on collapsed whitespace so re-wrapping does not fail a match."""
    return " ".join(text.split())


def read_text(path: Path):
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def section_b(text: str) -> str:
    start = SECTION_B_RE.search(text)
    if not start:
        return ""
    rest = text[start.end():]
    end = NEXT_SECTION_RE.search(rest)
    return rest[:end.start()] if end else rest


def split_items(body: str):
    marks = list(ITEM_RE.finditer(body))
    for index, mark in enumerate(marks):
        stop = marks[index + 1].start() if index + 1 < len(marks) else len(body)
        yield mark.group(1), mark.group(2).strip(), body[mark.end():stop]


def fenced_block_after(body: str, position: int):
    """Return the dedented lines of the first fenced block at or after position."""
    lines = body[position:].splitlines()
    opening = None
    for index, line in enumerate(lines):
        match = FENCE_RE.match(line)
        if match:
            opening = (index, len(match.group(1)))
            break
        # A following bullet means the Evidence field carried no block.
        if opening is None and re.match(r"^\s*-\s*\*\*", line) and index:
            return None
    if opening is None:
        return None
    start, indent = opening
    collected = []
    for line in lines[start + 1:]:
        if FENCE_RE.match(line):
            return collected
        collected.append(line[indent:] if line[:indent].strip() == "" else line.lstrip())
    return None


def cited_paths(source_line: str, evidence_lines):
    """Prefer the path in the pasted command; fall back to the Source field."""
    found = []
    for line in evidence_lines:
        if line.lstrip().startswith("$"):
            for token in reversed(line.split()):
                token = token.strip("\"'")
                if "/" in token or token.endswith(".md"):
                    found.append(token)
                    break
    found.extend(BACKTICK_PATH_RE.findall(source_line))
    seen, ordered = set(), []
    for item in found:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


def check_claim(claim: str, file_lines):
    """Verify one pasted output line against the cited file."""
    match = NUMBERED_RE.match(claim)
    if match:
        number = int(match.group("line"))
        wanted = normalize(match.group("text"))
        if not wanted:
            return True, None
        if 1 <= number <= len(file_lines):
            if normalize(file_lines[number - 1]) == wanted:
                return True, None
            found_at = [i + 1 for i, line in enumerate(file_lines)
                        if normalize(line) == wanted]
            if found_at:
                return False, (f"line {number} does not match; that text is at "
                               f"line {found_at[0]}")
            return False, f"line {number} does not contain the quoted text"
        return False, f"line {number} is past the end of the file"
    wanted = normalize(claim)
    if any(wanted in normalize(line) for line in file_lines):
        return True, None
    return False, "quoted text does not appear in the file"


def verify_item(root: Path, item_id: str, title: str, body: str):
    result = {"id": item_id, "title": title}

    source = SOURCE_RE.search(body)
    if not source:
        return {**result, "status": "no-source",
                "detail": "item has no **Source:** field"}
    source_line = source.group(1).strip()

    evidence = EVIDENCE_RE.search(body)
    if not evidence:
        return {**result, "status": "no-evidence",
                "detail": "item has no **Evidence:** field"}
    block = fenced_block_after(body, evidence.end())
    if block is None:
        return {**result, "status": "no-evidence",
                "detail": "**Evidence:** carries no fenced output block"}

    claims = [line for line in block
              if line.strip() and not line.lstrip().startswith("$")]
    if not claims:
        return {**result, "status": "no-evidence",
                "detail": "evidence block contains no output lines"}
    if any(PLACEHOLDER_RE.search(line) for line in claims):
        return {**result, "status": "placeholder",
                "detail": "evidence still holds template placeholder text"}

    candidates = cited_paths(source_line, block)
    if not candidates:
        return {**result, "status": "no-source",
                "detail": f"no file path found in Source: {source_line}"}

    for candidate in candidates:
        target = root / candidate
        text = read_text(target) if target.is_file() else None
        if text is None:
            continue
        file_lines = text.splitlines()
        failures = []
        for claim in claims:
            ok, why = check_claim(claim, file_lines)
            if not ok:
                failures.append(f"{claim.strip()[:70]} - {why}")
        if failures:
            return {**result, "status": "mismatch", "path": candidate,
                    "detail": "; ".join(failures[:3])}
        return {**result, "status": "verified", "path": candidate,
                "lines_checked": len(claims)}

    return {**result, "status": "file-missing", "path": candidates[0],
            "detail": f"cited file not found: {candidates[0]}"}


def run(root: Path, proposal: Path):
    text = read_text(proposal)
    if text is None:
        return None
    body = section_b(text)
    if not body.strip():
        return []
    return [verify_item(root, *item) for item in split_items(body)]


def print_human(results, proposal: Path) -> None:
    print(f"Citation check: {proposal}")
    if not results:
        print("- no promotions in section B; nothing to verify")
        return
    labels = {
        "verified": "verified",
        "mismatch": "NOT VERIFIED",
        "no-evidence": "NO EVIDENCE",
        "no-source": "NO SOURCE",
        "file-missing": "FILE MISSING",
        "placeholder": "PLACEHOLDER",
    }
    for item in results:
        label = labels.get(item["status"], item["status"])
        where = f" [{item['path']}]" if item.get("path") else ""
        print(f"- {item['id']}: {label}{where}")
        if item.get("detail"):
            print(f"    {item['detail']}")
    bad = [item for item in results if item["status"] != "verified"]
    print()
    print(f"{len(results) - len(bad)} of {len(results)} promotion(s) verified.")
    if bad:
        print("Cut every unverified item or demote it to an open question. "
              "Do not promote a fact whose citation could not be reproduced.")


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", default=".", help="project root (default: .)")
    parser.add_argument("--proposal", default=None,
                        help=f"proposal path (default: <root>/{DEFAULT_PROPOSAL})")
    parser.add_argument("--json", action="store_true", help="emit raw JSON")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    proposal = Path(args.proposal).resolve() if args.proposal else root / DEFAULT_PROPOSAL
    results = run(root, proposal)
    if results is None:
        print(f"error: cannot read proposal: {proposal}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        try:
            print_human(results, proposal)
        except BrokenPipeError:
            os.close(sys.stdout.fileno())
    return 0 if all(item["status"] == "verified" for item in results) else 1


if __name__ == "__main__":
    sys.exit(main())
