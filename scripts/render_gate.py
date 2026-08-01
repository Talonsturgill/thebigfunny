#!/usr/bin/env python3
"""render_gate.py — the objective ship/fail check on the finished mp4.

This is the implementation of the `renders_clean` hard gate in
config/scoring_rubric.yaml. Before it existed, that gate had NO implementation:
the upstream repo's quality_gate.py read PIL frame directories that the Remotion
path never produces, so the only thing actually checking the render was the same
model that produced it, describing it in prose.

knowledge/FIELD_NOTES.md forbids exactly that twice over ("the gate that cannot
fail certifies nothing", "verified with the wrong tool is not verified"), so the
gate is a real parser or it is nothing.

NO FFMPEG DEPENDENCY, ON PURPOSE. ffprobe is not installed in every environment
this runs in (it is absent from the current one), and a gate that silently skips
when its binary is missing is worse than no gate, because it reports success.
So this reads the ISO base media container directly: mvhd for duration, tkhd for
dimensions, hdlr for which tracks actually exist. Pure stdlib, works anywhere.

  python scripts/render_gate.py out/dispatch/render/final.mp4
  python scripts/render_gate.py --self-test        # prove the gate can go red

Exit 0 pass, 1 fail.
"""

import argparse
import os
import struct
import sys

# From config/scoring_rubric.yaml and CLAUDE.md. Duplicated nowhere else.
MAX_SECONDS = 60.0
WANT_W, WANT_H = 1080, 1920
# A 60s 1080x1920 h264 render is megabytes. Anything tiny is a broken encode that
# still exited 0, which is a real failure mode worth catching.
MIN_BYTES = 250_000


def _boxes(f, end, depth=0):
    """Walk ISO-BMFF boxes at the current offset. Yields (type, start, size)."""
    while f.tell() < end - 8:
        start = f.tell()
        hdr = f.read(8)
        if len(hdr) < 8:
            return
        size, typ = struct.unpack(">I4s", hdr)
        typ = typ.decode("latin-1")
        if size == 1:                       # 64-bit extended size
            size = struct.unpack(">Q", f.read(8))[0]
        elif size == 0:                     # extends to end of file
            size = end - start
        if size < 8:
            return
        yield typ, start, size
        f.seek(start + size)


CONTAINERS = {"moov", "trak", "mdia", "minf", "stbl"}


def parse(path):
    """Return {duration, tracks:[{kind,w,h}], size}. Raises on unparseable."""
    size = os.path.getsize(path)
    info = {"size": size, "duration": None, "tracks": [], "brand": None}
    with open(path, "rb") as f:
        def walk(end, cur_track=None):
            for typ, start, bsize in _boxes(f, end):
                inner_end = start + bsize
                if typ == "ftyp":
                    f.seek(start + 8)
                    info["brand"] = f.read(4).decode("latin-1", "replace")
                elif typ == "mvhd":
                    f.seek(start + 8)
                    ver = f.read(1)[0]
                    f.read(3)
                    if ver == 1:
                        f.read(16)
                        ts = struct.unpack(">I", f.read(4))[0]
                        dur = struct.unpack(">Q", f.read(8))[0]
                    else:
                        f.read(8)
                        ts = struct.unpack(">I", f.read(4))[0]
                        dur = struct.unpack(">I", f.read(4))[0]
                    if ts:
                        info["duration"] = dur / ts
                elif typ == "trak":
                    t = {"kind": None, "w": None, "h": None}
                    info["tracks"].append(t)
                    walk(inner_end, t)
                elif typ == "tkhd" and cur_track is not None:
                    f.seek(start + 8)
                    ver = f.read(1)[0]
                    f.read(3)
                    f.read(16 if ver == 1 else 8)   # times
                    f.read(4)                        # track id
                    f.read(4)                        # reserved
                    f.read(8 if ver == 1 else 4)     # duration
                    f.read(8 + 2 + 2 + 2 + 2 + 36)   # reserved..matrix
                    w, h = struct.unpack(">II", f.read(8))
                    # cur_track, NOT a local: tkhd is read by the RECURSIVE walk
                    # inside the trak, where the dict from the parent frame is
                    # not in scope. Using a local here raised UnboundLocalError
                    # on every real file, which made the parser throw on
                    # everything, which made all three self-test cases "pass".
                    cur_track["w"], cur_track["h"] = w >> 16, h >> 16  # 16.16 fixed
                elif typ == "hdlr" and cur_track is not None:
                    f.seek(start + 8)
                    f.read(4 + 4)                    # version/flags, predefined
                    cur_track["kind"] = f.read(4).decode("latin-1", "replace")
                elif typ in CONTAINERS:
                    walk(inner_end, cur_track)
        walk(size)
    return info


def check(path):
    """Returns (ok, [(name, ok, detail)])."""
    rows = []

    def row(name, ok, detail):
        rows.append((name, ok, detail))
        return ok

    if not os.path.exists(path):
        row("file exists", False, path)
        return False, rows
    row("file exists", True, path)

    if not row("non-trivial size", os.path.getsize(path) >= MIN_BYTES,
               f"{os.path.getsize(path):,} bytes (min {MIN_BYTES:,})"):
        return False, rows

    try:
        info = parse(path)
    except Exception as e:
        row("parses as mp4", False, f"{type(e).__name__}: {e}")
        return False, rows
    row("parses as mp4", True, f"brand={info['brand']}")

    d = info["duration"]
    row("duration readable", d is not None, f"{d:.2f}s" if d else "no mvhd")
    if d is not None:
        row(f"duration <= {MAX_SECONDS}s (sixty_seconds law)", d <= MAX_SECONDS,
            f"{d:.2f}s")

    kinds = [t["kind"] for t in info["tracks"]]
    row("has a video track", "vide" in kinds, f"tracks={kinds}")
    # A silent episode is a total failure that still renders and still exits 0.
    row("has an audio track", "soun" in kinds, f"tracks={kinds}")

    vid = next((t for t in info["tracks"] if t["kind"] == "vide"), None)
    if vid:
        row(f"is {WANT_W}x{WANT_H} vertical", (vid["w"], vid["h"]) == (WANT_W, WANT_H),
            f"{vid['w']}x{vid['h']}")
    else:
        row(f"is {WANT_W}x{WANT_H} vertical", False, "no video track")

    return all(ok for _, ok, _ in rows), rows


def _synth_mp4(path, w=WANT_W, h=WANT_H, dur_s=57.0, audio=True):
    """A minimal but structurally REAL mp4 container, for testing the parser."""
    def box(t, payload):
        return struct.pack(">I", len(payload) + 8) + t.encode() + payload

    def tkhd(tw, th):
        p = b"\x00" * 4 + b"\x00" * 8 + struct.pack(">I", 1) + b"\x00" * 4 + b"\x00" * 4
        p += b"\x00" * 8 + b"\x00" * 2 * 4 + b"\x00" * 36
        p += struct.pack(">II", tw << 16, th << 16)
        return box("tkhd", p)

    def hdlr(kind):
        return box("hdlr", b"\x00" * 8 + kind.encode() + b"\x00" * 12)

    ts = 1000
    mvhd = box("mvhd", b"\x00" * 4 + b"\x00" * 8 + struct.pack(">I", ts)
               + struct.pack(">I", int(dur_s * ts)) + b"\x00" * 80)
    traks = box("trak", tkhd(w, h) + box("mdia", hdlr("vide")))
    if audio:
        traks += box("trak", tkhd(0, 0) + box("mdia", hdlr("soun")))
    data = box("ftyp", b"isom" + struct.pack(">I", 512) + b"isomavc1")
    data += box("moov", mvhd + traks) + box("mdat", b"\x00" * (MIN_BYTES + 50_000))
    open(path, "wb").write(data)
    return path


def self_test():
    """Prove the gate can go red AND green.

    House rule from FIELD_NOTES.md: a check built only from passing material
    certifies whatever the code does today. The inverse trap is just as real and
    it bit this file during development: a parser bug made every file throw, so
    all three failure cases "passed" and the self-test reported success on a gate
    that rejected everything, including good renders.

    So both directions are required. A gate that never passes is not a gate, it
    is an outage.
    """
    import tempfile
    must_fail, must_pass = [], []
    with tempfile.TemporaryDirectory() as d:
        must_fail.append(("missing file", os.path.join(d, "missing.mp4")))

        p = os.path.join(d, "tiny.mp4"); open(p, "wb").write(b"\x00" * 1000)
        must_fail.append(("truncated/tiny encode", p))

        p = os.path.join(d, "garbage.mp4"); open(p, "wb").write(os.urandom(MIN_BYTES + 10))
        must_fail.append(("unparseable container", p))

        must_fail.append(("over 60 seconds",
                          _synth_mp4(os.path.join(d, "long.mp4"), dur_s=60.6)))
        must_fail.append(("silent, no audio track",
                          _synth_mp4(os.path.join(d, "mute.mp4"), audio=False)))
        must_fail.append(("wrong aspect (landscape)",
                          _synth_mp4(os.path.join(d, "wide.mp4"), w=1920, h=1080)))

        must_pass.append(("a valid 57s 1080x1920 render with audio",
                          _synth_mp4(os.path.join(d, "good.mp4"))))

        bad = []
        for name, p in must_fail:
            passed = check(p)[0]
            print(f"  {'FAIL' if passed else 'ok  '} rejects: {name}")
            if passed:
                bad.append(name)
        for name, p in must_pass:
            passed = check(p)[0]
            print(f"  {'ok  ' if passed else 'FAIL'} accepts: {name}")
            if not passed:
                bad.append(name)

    if bad:
        print(f"\nself-test: gate is WRONG on {len(bad)} case(s): {bad}")
        return 1
    print("\nself-test: rejects every broken render, accepts a good one, as designed")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?", help="the final mp4")
    ap.add_argument("--self-test", action="store_true",
                    help="prove the gate can fail, then exit")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.path:
        ap.error("give a path, or pass --self-test")
    ok, rows = check(a.path)
    for name, good, detail in rows:
        print(f"  {'ok  ' if good else 'FAIL'} {name:<42} {detail}")
    print("\nrenders_clean: " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
