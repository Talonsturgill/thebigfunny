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
    print("\nself-test: " + ("both directions correct, as designed" if ok else "THE GATE IS WRONG"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.path:
        ap.error("give a caption file, or pass --self-test")
    if not os.path.exists(a.path):
        print(f"caption_check: no such file {a.path}", file=sys.stderr)
        return 1
    ok, rows = check(open(a.path, encoding="utf-8").read())
    for n, good, d in rows:
        print(f"  {'ok  ' if good else 'FAIL'} {n:<40} {d}")
    print("\ncaption: " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
