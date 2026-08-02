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
# Usage: scripts/mux_and_verify.sh <silent_video.mp4> <master.wav> <out.mp4>
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

  rm -rf "$d"
  echo ""
  [ "$ok" -eq 0 ] && echo "self-test: both directions correct, as designed" || echo "self-test: THE GATE IS WRONG"
  exit "$ok"
fi

if [ "$#" -ne 3 ]; then
  echo "usage: mux_and_verify.sh <silent_video.mp4> <master.wav> <out.mp4>" >&2
  echo "       mux_and_verify.sh --self-test" >&2
  exit 2
fi
VIDEO="$1"; AUDIO="$2"; OUT="$3"

"$FF" -y -i "$VIDEO" -i "$AUDIO" \
  -map 0:v:0 -map 1:a:0 \
  -c:v copy -c:a aac -b:a 192k -ar 48000 -movflags +faststart -shortest "$OUT" >/dev/null 2>&1

_verify "$OUT"
exit $?
