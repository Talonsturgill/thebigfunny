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
#   2. probe the OUTPUT mp4's mean_volume and exit non-zero if it is silent
#      (< -60 dB), so a silent mux fails the run instead of shipping.
#
# Usage: scripts/mux_and_verify.sh <silent_video.mp4> <master.wav> <out.mp4>
# ============================================================================
set -euo pipefail
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

if [ "$#" -ne 3 ]; then
  echo "usage: mux_and_verify.sh <silent_video.mp4> <master.wav> <out.mp4>" >&2
  exit 2
fi
VIDEO="$1"; AUDIO="$2"; OUT="$3"

"$FF" -y -i "$VIDEO" -i "$AUDIO" \
  -map 0:v:0 -map 1:a:0 \
  -c:v copy -c:a aac -b:a 192k -ar 48000 -movflags +faststart -shortest "$OUT" >/dev/null 2>&1

# verify the OUTPUT actually carries audio
mean=$("$FF" -i "$OUT" -af volumedetect -f null - 2>&1 | grep -oE "mean_volume: -?[0-9.]+ dB" | grep -oE "\-?[0-9.]+" | head -1)
if [ -z "$mean" ]; then
  echo "MUX VERIFY FAIL: $OUT has no audio stream at all" >&2
  exit 1
fi
# bash can't do float compare; use awk
if awk -v m="$mean" -v f="$SILENCE_FLOOR_DB" 'BEGIN{exit !(m < f)}'; then
  echo "MUX VERIFY FAIL: $OUT mean_volume ${mean} dB is below the silence floor ${SILENCE_FLOOR_DB} dB (the mux grabbed a silent track)" >&2
  exit 1
fi
echo "MUX OK: $OUT  mean_volume ${mean} dB (audio present)"
