#!/usr/bin/env python3
"""caption_check.py — the hard gate on the post copy.

The upstream publication learned the shape of this the expensive way, on
LinkedIn: sources and credits got pasted INTO the post body and duplicated, and
a credit line sat above the hashtags where it blocked copying the post. The fix
was structural rather than a reminder. The body ends at the hashtags, and every
URL lives in a SEPARATE block the human drops into the first comment.

That structure carries over. The numbers do not. This show is TikTok first, and
a 1,300 character caption is a LinkedIn artifact: on short form the caption is
read in the second before the video starts, or not at all. So the body is short,
the hook carries the angle, and everything else gets out of the way.

  python scripts/caption_check.py out/dispatch/caption.txt
  python scripts/caption_check.py --self-test

Exit 0 pass, 1 fail.
"""

import argparse
import os
import re
import sys

# Short form. The caption is a label on a video, not an essay.
MAX_BODY = 300
MAX_HOOK = 100
MIN_TAGS, MAX_TAGS = 3, 5

URL = re.compile(r"https?://|www\.|\.com\b|\.org\b|\.gov\b", re.I)
EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿️]")
DASHES = re.compile("[—–]")
CLICKBAIT = re.compile(r"!{2,}|\?{2,}|\bYOU WON'?T BELIEVE\b|\bINSANE\b|\bSHOCKING\b", re.I)
SOURCEY = re.compile(r"^\s*(sources?|credits?|music|via)\s*:", re.I | re.M)
TAG = re.compile(r"#\w+")


def check(text):
    rows = []

    def row(n, ok, d):
        rows.append((n, ok, d)); return ok

    lines = [l for l in text.strip().split("\n")]
    nonempty = [l for l in lines if l.strip()]
    if not nonempty:
        row("has content", False, "empty")
        return False, rows
    hook = nonempty[0].strip()
    tags = TAG.findall(text)
    # The body is everything above the hashtag line.
    body = TAG.sub("", text).strip()

    row(f"hook <= {MAX_HOOK} chars", len(hook) <= MAX_HOOK, f"{len(hook)}")
    row(f"body <= {MAX_BODY} chars", len(body) <= MAX_BODY, f"{len(body)}")
    row(f"{MIN_TAGS}-{MAX_TAGS} hashtags", MIN_TAGS <= len(tags) <= MAX_TAGS, f"{len(tags)}")

    # The upstream failure, structurally prevented: no URL and no source or
    # credit line in the body. Those go in the first-comment block.
    row("no URL in the body", not URL.search(body),
        (URL.search(body).group(0) if URL.search(body) else "clean"))
    row("no sources/credits line in the body", not SOURCEY.search(body),
        (SOURCEY.search(body).group(0).strip() if SOURCEY.search(body) else "clean"))

    # House rules.
    row("no emoji", not EMOJI.search(text), "clean" if not EMOJI.search(text) else "found")
    row("no em or en dashes", not DASHES.search(text),
        "clean" if not DASHES.search(text) else "found")
    row("no clickbait punctuation or screaming", not CLICKBAIT.search(text),
        (CLICKBAIT.search(text).group(0) if CLICKBAIT.search(text) else "clean"))

    # Brand: the case number is the archive spine and belongs on every post.
    row("carries the case number", bool(re.search(r"CASE No\. \d{4}", text)),
        "present" if re.search(r"CASE No\. \d{4}", text) else "missing")

    # Hashtags go at the END, so nothing sits above them blocking a copy.
    if tags:
        last = nonempty[-1].strip()
        row("hashtags are the last line", last.startswith("#"), last[:40])
    return all(o for _, o, _ in rows), rows


def check_first_comment(text, body=""):
    """THE OTHER HALF OF THE DELIVERABLE.

    CLAUDE.md: "the deliverable is the mp4 AND the post copy: caption.txt (the
    body) plus first_comment.txt (the sources, which NEVER go in the body). A
    video with no caption is half a deliverable."

    Nothing checked it. `grep -rn first_comment` found it in prose only, so the
    file the body's URL ban PUSHES every source into was the one file in the
    pipeline nobody verified existed, was non-empty, or actually carried the
    sources. The ban and this gate are two halves of one rule: forbidding URLs in
    the body without requiring them here just deletes the sourcing.
    """
    rows = []

    def row(n, ok, d):
        rows.append((n, ok, d)); return ok

    t = (text or "").strip()
    row("first_comment.txt has content", bool(t),
        f"{len(t)} chars" if t else
        "EMPTY. The body is forbidden from carrying URLs, so this is where every "
        "source lives. Empty means the episode ships unsourced.")
    if not t:
        return False, rows

    urls = re.findall(r"https?://\S+", t)
    row("carries at least one source URL", bool(urls),
        f"{len(urls)} url(s)" if urls else
        "no http(s) URL anywhere. `No claim without a source` is the first house "
        "rule and this file is where the audience can check it.")

    # House rules apply to everything a viewer reads.
    row("no emoji", not EMOJI.search(t), "clean" if not EMOJI.search(t) else "found")
    row("no em or en dashes", not DASHES.search(t),
        "clean" if not DASHES.search(t) else "found")

    # It is a SEPARATE block, not a second copy of the post.
    if body.strip():
        shared = {l.strip() for l in t.splitlines() if len(l.strip()) > 30}
        dupe = sorted(shared & {l.strip() for l in body.splitlines() if len(l.strip()) > 30})
        row("is not a duplicate of the caption body", not dupe,
            f"{dupe[:1]} appears in BOTH. The upstream failure was sources pasted "
            f"into the body and duplicated." if dupe else "distinct")
    return all(o for _, o, _ in rows), rows


def self_test():
    good = ("The FAQ about the price increase has no prices in it.\n"
            "Microsoft called it a packaging and pricing update. CASE No. 0001\n"
            "#microsoft #office365 #pricing #smallbusiness")
    bads = [
        ("URL in the body", good.replace("CASE No. 0001",
                                         "CASE No. 0001 microsoft.com/licensing")),
        ("sources line in the body", "Sources: microsoft\n" + good),
        ("emoji", good.replace("no prices in it.", "no prices in it \U0001F621")),
        ("em dash", good.replace("update.", "update — obviously.")),
        ("clickbait", good.replace("has no prices in it.", "is INSANE!!")),
        ("no case number", good.replace(" CASE No. 0001", "")),
        ("too few hashtags", good.replace(" #pricing #smallbusiness", "")),
        ("hook too long", ("x" * 120) + "\n" + good),
    ]
    ok = True
    for name, t in bads:
        passed = check(t)[0]
        print(f"  {'FAIL' if passed else 'ok  '} rejects: {name}")
        ok &= not passed
    passed, rows = check(good)
    print(f"  {'ok  ' if passed else 'FAIL'} accepts: a clean caption")
    if not passed:
        for n, o, d in rows:
            if not o:
                print(f"        why: {n} -> {d}")
    ok &= passed

    # The first comment, both directions.
    good_fc = ("Sources:\n"
               "FTC v. RentGrow, Inc., No. 1:26-cv-02415 (D.D.C. filed July 9, 2026)\n"
               "https://www.ftc.gov/legal-library/browse/cases-proceedings/222-3002\n")
    fc_bads = [
        ("an empty first comment", ""),
        ("a first comment with no source URL", "Sources: the FTC filing.\n"),
        ("an em dash in the first comment", good_fc.replace("Sources:", "Sources —")),
    ]
    for name, t in fc_bads:
        passed_fc = check_first_comment(t)[0]
        print(f"  {'FAIL' if passed_fc else 'ok  '} rejects: {name}")
        ok &= not passed_fc
    # And a first comment that is just the caption again.
    dupe_body = "The report wrote the same eviction case out again and again.\n"
    passed_fc = check_first_comment(good_fc + dupe_body, dupe_body)[0]
    print(f"  {'FAIL' if passed_fc else 'ok  '} rejects: a first comment that repeats the body")
    ok &= not passed_fc
    passed_fc, fc_rows = check_first_comment(good_fc, dupe_body)
    print(f"  {'ok  ' if passed_fc else 'FAIL'} accepts: a clean first comment")
    if not passed_fc:
        for n, o, d in fc_rows:
            if not o:
                print(f"        why: {n} -> {d}")
    ok &= passed_fc

    print("\nself-test: " + ("both directions correct, as designed" if ok else "THE GATE IS WRONG"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?")
    ap.add_argument("--first-comment",
                    help="default: first_comment.txt beside the caption")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.path:
        ap.error("give a caption file, or pass --self-test")
    if not os.path.exists(a.path):
        print(f"caption_check: no such file {a.path}", file=sys.stderr)
        return 1
    body = open(a.path, encoding="utf-8").read()
    ok, rows = check(body)
    for n, good, d in rows:
        print(f"  {'ok  ' if good else 'FAIL'} {n:<40} {d}")

    # THE OTHER HALF. Checked next to the body by default, because the two files
    # enforce one rule between them and grading only the body means the URL ban
    # quietly deletes the sourcing.
    fc_path = a.first_comment or os.path.join(os.path.dirname(a.path) or ".",
                                              "first_comment.txt")
    print(f"\n  {os.path.basename(fc_path)}")
    if not os.path.exists(fc_path):
        print(f"  FAIL {'first_comment.txt exists':<40} missing at {fc_path}")
        print("       CLAUDE.md: the deliverable is the mp4 AND the post copy. The "
              "body is\n       forbidden from carrying URLs, so with no first "
              "comment the episode\n       ships with nowhere to check it.")
        ok = False
    else:
        fc_ok, fc_rows = check_first_comment(open(fc_path, encoding="utf-8").read(), body)
        for n, good, d in fc_rows:
            print(f"  {'ok  ' if good else 'FAIL'} {n:<40} {d}")
        ok = ok and fc_ok

    print("\npost copy: " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
