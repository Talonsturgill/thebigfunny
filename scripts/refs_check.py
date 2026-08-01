#!/usr/bin/env python3
"""refs_check.py — every repo path we point at must actually exist.

WHY THIS EXISTS
A code review of this repo's first commit found fifteen defects, and the single
largest class was not logic: it was PROSE POINTING AT NOTHING. The routine sent
runs to scripts that had been deleted, agents demanded config files that were
never ported, a skill manifest documented a retired renderer, and two of four
panel critics were aimed at four missing docs each. Every one of those would
have produced a confident, wrong answer on the first real run instead of an
error, because a model asked to read a missing file will usually just proceed.

That is exactly the failure knowledge/FIELD_NOTES.md warns about twice, so it
gets a gate rather than a cleanup.

  python scripts/refs_check.py
  python scripts/refs_check.py --self-test    # prove it can go red

Exit 0 pass, 1 fail.
"""

import argparse
import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Prose and config that a run is instructed to follow.
SCAN = [
    "CLAUDE.md", "README.md",
    "prompts/BIGFUNNY_ROUTINE.md", "prompts/ROUTINE_PROMPT.txt",
    "config/brand.yaml", "config/sources.yaml", "config/scoring_rubric.yaml",
    "knowledge/CAST_BIBLE.md", "knowledge/ANGLE_TAXONOMY.md",
    "knowledge/FIELD_NOTES.md",
    "video-engine/src/lib/ASSET_MANIFEST.md",
    ".claude/WORKLOG.md",
    ".claude/skills/bigfunny-dispatch/SKILL.md",
]
SCAN += [os.path.join(".claude/agents", f)
         for f in sorted(os.listdir(os.path.join(REPO, ".claude/agents")))
         if f.endswith(".md")]

# A repo-relative path with a known extension, or a known directory.
PATH_RE = re.compile(
    r"(?<![\w/.-])"
    r"((?:scripts|config|knowledge|prompts|ledger|assets|runs|docs|video-engine|\.claude)"
    r"/[\w./-]+?"
    r"\.(?:py|sh|md|json|yaml|yml|tsx|ts|txt|png|mp4|wav))"
    r"(?![\w/-])")

# Paths a run legitimately CREATES rather than reads. Not defects.
RUNTIME = (
    "out/", "runs/", "video-engine/out/", "node_modules/",
)
# Placeholders, not literal paths.
PLACEHOLDER = re.compile(r"<[^>]+>|\*|\$\{")


def scan_file(rel):
    """Yield (line_no, path) for every repo path referenced that does not exist."""
    p = os.path.join(REPO, rel)
    if not os.path.exists(p):
        yield 0, f"(the scanned file itself is missing: {rel})"
        return
    for n, line in enumerate(open(p, encoding="utf-8", errors="replace"), 1):
        for m in PATH_RE.finditer(line):
            ref = m.group(1)
            if PLACEHOLDER.search(ref) or ref.startswith(RUNTIME):
                continue
            if not os.path.exists(os.path.join(REPO, ref)):
                yield n, ref


def run():
    bad = []
    for rel in SCAN:
        for n, ref in scan_file(rel):
            bad.append((rel, n, ref))
    if bad:
        print(f"BROKEN REFERENCES: {len(bad)}\n")
        for rel, n, ref in bad:
            print(f"  {rel}:{n}  ->  {ref}")
        print("\nA run told to read one of these will not error, it will proceed"
              "\nand answer confidently from nothing. Fix the reference or delete"
              "\nthe claim.")
        return 1
    print(f"refs_check: {len(SCAN)} files scanned, every referenced path exists")
    return 0


def self_test():
    """Prove the gate can go red, and that it does not fire on a real path."""
    import tempfile
    ok = True
    with tempfile.TemporaryDirectory() as d:
        bad = os.path.join(d, "bad.md")
        open(bad, "w").write("Read `scripts/does_not_exist.py` before starting.\n")
        good = os.path.join(d, "good.md")
        open(good, "w").write("Read `scripts/refs_check.py` before starting.\n")

        global SCAN
        keep = SCAN

        SCAN = [os.path.relpath(bad, REPO)]
        red = run() == 1
        print(f"  {'ok  ' if red else 'FAIL'} catches a missing path")
        ok &= red

        SCAN = [os.path.relpath(good, REPO)]
        green = run() == 0
        print(f"  {'ok  ' if green else 'FAIL'} does not fire on a real path")
        ok &= green

        SCAN = keep
    print("\nself-test: " + ("both directions correct, as designed"
                             if ok else "THE GATE IS WRONG"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    return self_test() if a.self_test else run()


if __name__ == "__main__":
    sys.exit(main())
