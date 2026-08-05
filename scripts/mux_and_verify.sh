#!/usr/bin/env bash
# ============================================================================
# MUX + VERIFY — attach the mixed master audio to the silent render, and FAIL
# loudly if the result is silent.
#
# Why this exists: the 2026-07-17 dispatch shipped SILENT. The mix (master.wav)
# was fine (-16.8 dB), but the final `ffmpeg -i video -i audio` had no `-map`,
# so ffmpeg's default stream selection took the RENDER's empty audio track
# instead of the master. The quality gate checked master60.wav (not the mp4),
# so nothing caught it. This wrapper makes BOTH mistakes impossible:
#   1. explicit `-map 0:v:0 -map 1:a:0` (never guess the audio stream)
#   2. measure the OUTPUT mp4's actual audio and exit non-zero if it is silent
#      (< -60 dB), so a silent mux fails the run instead of shipping.
#
# Usage: scripts/mux_and_verify.sh <silent_video.mp4> <master.wav> <out.mp4> [upstream.wav]
#   upstream.wav: what the PICTURE was cut to, for the staleness check. Defaults
#   to <master.wav>. Pass out/dispatch/vo.wav when the master is a MIX, because a
#   mix is built after the render and is downstream of it.
#        scripts/mux_and_verify.sh --self-test
# ============================================================================
set -uo pipefail
# Prefer a system ffmpeg, then fall back to the one REMOTION ALREADY SHIPS.
# There is no system ffmpeg in every environment this runs in, and a mux that
# cannot run means a silent episode that still passes a render check. Remotion
# vendors a full ffmpeg n7.1 in its linux compositor package, so if the engine
# is installed the mux is always available.
_remotion_ff() {
  for d in "$(dirname "$0")/../video-engine/node_modules/@remotion"/compositor-*/; do
    [ -x "$d/ffmpeg" ] && printf '%s' "$d/ffmpeg" && return 0
  done
  return 1
}
FF="${FFMPEG_BIN:-}"
if [ -z "$FF" ]; then
  if command -v ffmpeg >/dev/null 2>&1; then FF=ffmpeg
  elif FF="$(_remotion_ff)"; then :
  else echo "no ffmpeg: install one, or npm install in video-engine/ (it vendors one)" >&2; exit 1
  fi
fi
SILENCE_FLOOR_DB=-60

# ---------------------------------------------------------------------------
# MEASURING THE OUTPUT, WITHOUT `volumedetect`.
#
# 2026-08-02: the Remotion-vendored ffmpeg is built `--disable-filters` with a
# small whitelist, and `volumedetect` is NOT on it (neither is `astats`). The
# old verify ran `-af volumedetect` and scraped mean_volume, so on any host with
# no system ffmpeg it produced an EMPTY measurement and the script reported
# "has no audio stream at all" — a hard failure on a perfectly good mux. The
# fallback that exists precisely so the mux always works could therefore never
# pass, and the misleading message pointed the run at the wrong thing entirely.
#
# So measure with no filter at all: decode the muxed file's audio to PCM (the
# pcm_s16le encoder and the wav muxer are both enabled in every build we run on)
# and compute RMS directly. One code path, works on system and vendored ffmpeg
# alike, and it measures the SHIPPED FILE rather than something adjacent to it.
# ---------------------------------------------------------------------------
_mean_db() {   # <file> -> prints mean dBFS, or nothing if there is no audio
  local f="$1" tmp
  tmp="$(mktemp -t mux_verify_XXXXXX.wav)"
  if ! "$FF" -y -i "$f" -vn -c:a pcm_s16le -f wav "$tmp" >/dev/null 2>&1; then
    rm -f "$tmp"; return 0
  fi
  python3 - "$tmp" <<'PY'
import math, sys, wave
try:
    with wave.open(sys.argv[1], "rb") as w:
        n = w.getnframes()
        if n == 0:
            sys.exit(0)
        raw = w.readframes(n)
        width, ch = w.getsampwidth(), w.getnchannels()
except Exception:
    sys.exit(0)
if width != 2 or not raw:
    sys.exit(0)
import array
a = array.array("h")
a.frombytes(raw[: len(raw) - (len(raw) % 2)])
if not len(a):
    sys.exit(0)
acc = 0
for s in a:
    acc += s * s
rms = math.sqrt(acc / len(a)) / 32768.0
print(f"{20 * math.log10(rms):.1f}" if rms > 0 else "-999.0")
PY
  rm -f "$tmp"
}

_verify() {    # <file> -> 0 if it carries real audio, 1 otherwise
  local out="$1" mean
  mean="$(_mean_db "$out")"
  if [ -z "$mean" ]; then
    echo "MUX VERIFY FAIL: $out has no decodable audio stream" >&2
    return 1
  fi
  if awk -v m="$mean" -v f="$SILENCE_FLOOR_DB" 'BEGIN{exit !(m < f)}'; then
    echo "MUX VERIFY FAIL: $out mean_volume ${mean} dB is below the silence floor ${SILENCE_FLOOR_DB} dB (the mux grabbed a silent track)" >&2
    return 1
  fi
  echo "MUX OK: $out  mean_volume ${mean} dB (audio present)"
  return 0
}

# ---------------------------------------------------------------------------
# SELF-TEST. A gate that cannot fail certifies nothing (knowledge/FIELD_NOTES.md),
# so prove BOTH directions: a real track passes, a silent one is caught. The
# silent case is the exact 2026-07-17 shipping bug this wrapper exists to stop.
# ---------------------------------------------------------------------------
if [ "${1:-}" = "--self-test" ]; then
  d="$(mktemp -d)"; ok=0
  # The video fixture is encoded from a generated PNG, NOT from lavfi's nullsrc.
  # The vendored ffmpeg is built --disable-decoders and has no `wrapped_avframe`
  # decoder, so every lavfi VIDEO source fails to encode there; the first cut of
  # this self-test used nullsrc and reported "THE GATE IS WRONG" when the gate
  # was fine and only the fixture was unbuildable. png+image2+libx264 are all
  # enabled in both builds.
  python3 - "$d/f.png" <<'PY'
import struct, sys, zlib
w = h = 64
raw = b"".join(b"\x00" + bytes([32, 32, 40]) * w for _ in range(h))
def ch(t, d):
    c = t + d
    return struct.pack(">I", len(d)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)
open(sys.argv[1], "wb").write(
    b"\x89PNG\r\n\x1a\n"
    + ch(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
    + ch(b"IDAT", zlib.compress(raw))
    + ch(b"IEND", b""))
PY
  "$FF" -y -loop 1 -i "$d/f.png" -t 2 -r 30 -c:v libx264 -pix_fmt yuv420p "$d/v.mp4" >/dev/null 2>&1
  "$FF" -y -f lavfi -i "sine=frequency=440:duration=2" -c:a pcm_s16le "$d/tone.wav" >/dev/null 2>&1
  "$FF" -y -f lavfi -i "anullsrc=r=44100:cl=mono:d=2" -c:a pcm_s16le "$d/silent.wav" >/dev/null 2>&1
  # The fixtures are built audio-first, so touch the video AFTER them: in a real
  # run the render happens after the VO, and the staleness rule added 2026-08-02
  # correctly refuses the other order. A self-test whose fixtures could never
  # occur in production is testing the wrong thing.
  sleep 1; touch "$d/v.mp4"
  if [ ! -s "$d/v.mp4" ] || [ ! -s "$d/tone.wav" ] || [ ! -s "$d/silent.wav" ]; then
    echo "  FAIL could not build the self-test fixtures (ffmpeg: $FF)"; rm -rf "$d"; exit 1
  fi

  "$0" "$d/v.mp4" "$d/tone.wav" "$d/tone.mp4" >/dev/null 2>&1
  if [ $? -eq 0 ]; then echo "  ok   accepts: a mux that really carries audio"; else echo "  FAIL accepts: a mux that really carries audio"; ok=1; fi

  "$0" "$d/v.mp4" "$d/silent.wav" "$d/silent.mp4" >/dev/null 2>&1
  if [ $? -ne 0 ]; then echo "  ok   catches: a silent track (the 2026-07-17 bug)"; else echo "  FAIL catches: a silent track (the 2026-07-17 bug)"; ok=1; fi

  # The regression that motivated the rewrite: measurement must not depend on a
  # filter the vendored ffmpeg does not ship.
  if [ -n "$(_mean_db "$d/tone.mp4")" ]; then echo "  ok   measures without volumedetect (vendored-ffmpeg safe)"; else echo "  FAIL measures without volumedetect (vendored-ffmpeg safe)"; ok=1; fi

  # RED on purpose: the failure that shipped a stale picture with fresh audio.
  touch -d "@$(( $(date +%s) + 5 ))" "$d/tone.wav" 2>/dev/null || touch "$d/tone.wav"
  "$0" "$d/v.mp4" "$d/tone.wav" "$d/stale.mp4" >/dev/null 2>&1
  if [ $? -ne 0 ]; then echo "  ok   refuses a video OLDER than its audio (the 2026-08-02 stale mux)"; else echo "  FAIL refuses a video OLDER than its audio (the 2026-08-02 stale mux)"; ok=1; fi

  # RED on purpose, and the reason $OUT is deleted before the mux: point the
  # script at inputs that are not there, WITH A REAL PREVIOUS EPISODE ALREADY AT
  # THE OUTPUT PATH. Before 2026-08-02 both of these printed MUX OK and exited 0
  # while measuring that previous episode, which is how a stale picture would
  # have shipped under a new date. The fixture must carry the stale file, or the
  # case proves nothing: with no file at $OUT, ffmpeg's failure is caught by
  # accident when the measurement finds nothing to measure.
  cp "$d/tone.mp4" "$d/carryover.mp4" 2>/dev/null
  "$0" "$d/does_not_exist.mp4" "$d/tone.wav" "$d/carryover.mp4" >/dev/null 2>&1
  rc=$?
  if [ "$rc" -ne 0 ] && [ -s "$d/carryover.mp4" ]; then
    echo "  ok   refuses a MISSING video and leaves the old output untouched"
  else
    echo "  FAIL refuses a MISSING video and leaves the old output untouched (rc=$rc)"; ok=1
  fi

  cp "$d/tone.mp4" "$d/carryover2.mp4" 2>/dev/null
  "$0" "$d/v.mp4" "$d/does_not_exist.wav" "$d/carryover2.mp4" >/dev/null 2>&1
  if [ $? -ne 0 ]; then echo "  ok   refuses a MISSING audio track"; else echo "  FAIL refuses a MISSING audio track"; ok=1; fi

  # And the layer under that: inputs that EXIST and are not decodable, so the
  # guard above passes and ffmpeg itself is what fails. Nothing may survive at
  # the output path.
  # A FRESH copy of the audio, because the stale-mux case above pushed
  # `tone.wav`'s mtime into the future on purpose. Reusing it here would trip the
  # staleness guard instead, and this case would pass for the wrong reason while
  # ffmpeg never ran at all.
  cp "$d/tone.wav" "$d/tone3.wav"
  printf 'not an mp4' > "$d/junk.mp4"
  cp "$d/tone.mp4" "$d/carryover3.mp4" 2>/dev/null
  "$0" "$d/junk.mp4" "$d/tone3.wav" "$d/carryover3.mp4" >/dev/null 2>&1
  rc=$?
  if [ "$rc" -ne 0 ] && [ ! -f "$d/carryover3.mp4" ]; then
    echo "  ok   a FAILED ffmpeg leaves no output to measure (the carryover bug)"
  else
    echo "  FAIL a FAILED ffmpeg leaves no output to measure (the carryover bug) (rc=$rc)"; ok=1
  fi

  rm -rf "$d"
  echo ""
  [ "$ok" -eq 0 ] && echo "self-test: both directions correct, as designed" || echo "self-test: THE GATE IS WRONG"
  exit "$ok"
fi

if [ "$#" -lt 3 ] || [ "$#" -gt 4 ]; then
  echo "usage: mux_and_verify.sh <silent_video.mp4> <master.wav> <out.mp4> [upstream.wav]" >&2
  echo "       mux_and_verify.sh --self-test" >&2
  exit 2
fi
VIDEO="$1"; AUDIO="$2"; OUT="$3"

# ---------------------------------------------------------------------------
# THE VIDEO MUST BE NEWER THAN THE AUDIO.
#
# 2026-08-02: a render FAILED (a composition threw at module load), and this
# script cheerfully muxed the previous run's silent video onto the new voice
# track. The result parsed, carried both streams, was 1080x1920, and sailed
# through render_gate, because every one of those checks asks about the FILE and
# none of them asks whether the picture belongs to this cut.
#
# A stale picture with fresh audio is the single most expensive failure this
# pipeline can produce: it looks finished. So compare mtimes and refuse.
# BOTH INPUTS MUST EXIST, and this check comes first.
#
# 2026-08-02, found by a repo-wide review: the staleness rule below was written
# `[ -f "$VIDEO" ] && [ -f "$AUDIO" ] && ...`, so a MISSING input skipped the
# guard entirely rather than failing it. The render not existing at all is the
# most common way for the render to fail, which means the guard was absent for
# exactly the case it was written for. An absent input is not a passing input.
for f in "$VIDEO" "$AUDIO"; do
  if [ ! -s "$f" ]; then
    echo "MUX REFUSED: input missing or empty: $f" >&2
    echo "  The step that was supposed to write it did not run, or it failed." >&2
    echo "  Fix that step. Do not mux around it: ffmpeg fails, \$OUT keeps whatever" >&2
    echo "  the LAST run left there, and a previous episode ships under this date." >&2
    exit 1
  fi
done

# AND THE PICTURE MUST BE NEWER THAN THE SOURCE THAT DRAWS IT.
#
# 2026-08-03: the scene file was fixed (a 0.9s hole that rendered black), the
# re-render was still running, and a mux against the PREVIOUS render passed
# every check here. The video was newer than the audio, which is all this file
# knew how to ask, and it was three minutes older than the fix that mattered.
#
# Audio is not the only input to a picture. A self-timed episode is drawn by its
# scene file and its generated sidecars, so those are inputs too, and a render
# older than any of them is a render of code that no longer exists.
_SRC_GLOB="$(dirname "$0")/../video-engine/src"
for src in "$_SRC_GLOB"/Case*.tsx "$_SRC_GLOB"/case*_captions.ts \
           "$_SRC_GLOB"/case*_faces.ts "$_SRC_GLOB"/case*_mouth.ts \
           "$_SRC_GLOB"/lib/countroom.tsx; do
  [ -f "$src" ] || continue
  if [ "$src" -nt "$VIDEO" ]; then
    echo "MUX REFUSED: the picture is OLDER than the source that draws it." >&2
    echo "  video:  $VIDEO  ($(date -r "$VIDEO" '+%H:%M:%S'))" >&2
    echo "  source: $src  ($(date -r "$src" '+%H:%M:%S'))" >&2
    echo "  This render is of code that no longer exists. Re-render." >&2
    echo "  Audio is not the only input to a picture, and comparing only against" >&2
    echo "  the audio is how a fixed scene got muxed against the render that" >&2
    echo "  still had the bug in it." >&2
    exit 1
  fi
done

# THE STALENESS COMPARISON IS AGAINST THE UPSTREAM, NOT AGAINST THE MASTER.
#
# What this guard actually protects is: the picture must not be older than the
# thing that DETERMINED IT. That is the VO, because the word timings drive the
# captions and the scene bounds. It was written when the master WAS the VO, so
# it compared against $AUDIO and that was the same file.
#
# It stopped being the same file the day a mix arrived. The mix is built AFTER
# the render (it needs nothing from the picture, and its cue times come from the
# scene source), so `$AUDIO -nt $VIDEO` is true on every single run and the mux
# refused every time, with a message blaming a render that had just succeeded.
# Adding sound effects to a soundtrack does not invalidate a cut.
#
# So: compare against $UPSTREAM, which callers may pass as a 4th argument and
# which DEFAULTS TO $AUDIO so every existing caller keeps the old behaviour.
UPSTREAM="${4:-$AUDIO}"
if [ ! -f "$UPSTREAM" ]; then
  echo "MUX REFUSED: upstream '$UPSTREAM' does not exist." >&2
  echo "  An absent input is not a passing input." >&2
  exit 1
fi
if [ "$UPSTREAM" -nt "$VIDEO" ]; then
  echo "MUX REFUSED: the video is OLDER than the audio it was cut to." >&2
  echo "  video:    $VIDEO  ($(date -r "$VIDEO" '+%H:%M:%S'))" >&2
  echo "  upstream: $UPSTREAM  ($(date -r "$UPSTREAM" '+%H:%M:%S'))" >&2
  if [ "$UPSTREAM" != "$AUDIO" ]; then
    echo "  master:   $AUDIO (not compared; a mix is downstream of the picture)" >&2
  fi
  echo "  The render did not run, or it failed after the VO was rebuilt." >&2
  echo "  Re-render before muxing; a stale picture with fresh audio passes every" >&2
  echo "  downstream gate, because they all ask about the file and not the cut." >&2
  exit 1
fi

# DELETE THE OUTPUT BEFORE WRITING IT, and CHECK FFMPEG'S EXIT CODE.
#
# The same 2026-08-02 review found the deepest version of the stale-picture bug
# living in these four lines. `set -uo pipefail` has no `-e`, ffmpeg's status was
# discarded, and stderr went to /dev/null. So when the mux failed, the script
# walked straight into `_verify "$OUT"` and measured a file ffmpeg had never
# opened: LAST RUN'S EPISODE, still sitting at that path. It is megabytes, it is
# 1080x1920, it carries audio and it is under 60 seconds, so it printed MUX OK,
# exited 0, and passed render_gate too.
#
# That is the whole failure mode this file was written to make impossible,
# reappearing one layer down. Removing $OUT first means a failed mux leaves
# NOTHING to measure, which is the only honest state for a step that did not run.
rm -f "$OUT"
if ! "$FF" -y -i "$VIDEO" -i "$AUDIO" \
  -map 0:v:0 -map 1:a:0 \
  -c:v copy -c:a aac -b:a 192k -ar 48000 -movflags +faststart -shortest "$OUT" 2>"${OUT}.ffmpeg.log"; then
  echo "MUX FAILED: ffmpeg exited non-zero. $OUT was NOT written." >&2
  echo "  video: $VIDEO" >&2
  echo "  audio: $AUDIO" >&2
  sed -n '$p;x' "${OUT}.ffmpeg.log" 2>/dev/null | sed 's/^/  ffmpeg: /' >&2
  echo "  full ffmpeg stderr: ${OUT}.ffmpeg.log" >&2
  rm -f "$OUT"
  exit 1
fi
rm -f "${OUT}.ffmpeg.log"

_verify "$OUT"
exit $?
