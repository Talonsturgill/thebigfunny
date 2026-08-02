#!/usr/bin/env bash
# Render wrapper — makes the taste loop CHEAP and the final SHIP-GRADE.
#
#   scripts/render.sh draft  [comp] [out.mp4]   half-res, fast-encode preview (~3-4x faster)
#   scripts/render.sh final  [comp] [out.mp4]   full 1080x1920, ship quality
#   scripts/render.sh still  <frame> [comp] [out.png] [--draft]
#
# THE RULE (docs: taste loop / Phase 5): iterate on DRAFT renders and draft
# stills — look, fix, re-render 3-5x at low cost. Only the FINAL gate and the
# judge panel see a full-res render. Draft stills are half-res; critics grading
# COMPOSITION/story can use them, but legibility checks (caption px heights)
# must run on a final-res render.
set -euo pipefail
# CALLER_PWD: captured BEFORE the cd below. A relative OUT path the caller types (e.g.
# "out/dispatch/render/video_mute.mp4" from the repo root) is resolved against THIS
# directory, not video-engine/ -- the 2026-07-22 gotcha that cost a long debugging loop:
# every explicit OUT argument was silently written to video-engine/out/... instead of the
# repo-root out/... the caller expected, so a mux+gate cycle kept re-testing a stale file
# and made real engine fixes look like no-ops. Only the DEFAULT out paths below (relative
# to video-engine, "../out/...") are exempt, since those already resolve correctly as-is.
CALLER_PWD="$PWD"
cd "$(dirname "$0")/../video-engine"
export PLAYWRIGHT_BROWSERS_PATH="${PLAYWRIGHT_BROWSERS_PATH:-/opt/pw-browsers}"
PROPS="${PROPS:-../out/dispatch/episode_props.json}"

# Pass --props ONLY when the file is really there.
#
# Remotion hard-errors on a --props path that does not exist ("neither valid
# JSON nor a file path to a valid JSON file"), which made every render abort for
# a composition that does not take props. Case0001 is self-timed: its Sequences
# carry their own frame numbers, so there is no episode_props.json and never
# will be. A generic Episode built by scripts/build_scenes.py does take props,
# and still gets them. One flag, conditional, instead of two render paths.
PROPS_ARG=()
if [[ -f "$PROPS" ]]; then
  PROPS_ARG=(--props="$PROPS")
fi

resolve_out() {   # abs path -> unchanged; relative path -> resolved against the CALLER's cwd
  local p="$1"
  case "$p" in
    /*) printf '%s' "$p" ;;
    *)  printf '%s' "$CALLER_PWD/$p" ;;
  esac
}

MODE="${1:?usage: render.sh draft|final|still ...}"
case "$MODE" in
  draft)
    COMP="${2:-${BIGFUNNY_COMP:-Case0001}}"; OUT="../out/dispatch/render/draft.mp4"; [[ -n "${3:-}" ]] && OUT="$(resolve_out "$3")"
    exec npx remotion render src/index.ts "$COMP" "$OUT" \
      "${PROPS_ARG[@]}" --codec=h264 --muted --concurrency=2 \
      --scale=0.5 --crf=30 --every-nth-frame=1
    ;;
  final)
    COMP="${2:-${BIGFUNNY_COMP:-Case0001}}"; OUT="../out/dispatch/render/video_mute.mp4"; [[ -n "${3:-}" ]] && OUT="$(resolve_out "$3")"
    exec npx remotion render src/index.ts "$COMP" "$OUT" \
      "${PROPS_ARG[@]}" --codec=h264 --muted --concurrency=2 --crf=19
    ;;
  still)
    FRAME="${2:?frame number}"; COMP="${3:-${BIGFUNNY_COMP:-Case0001}}"
    OUT="../out/dispatch/probe/still_$FRAME.png"; [[ -n "${4:-}" && "${4:-}" != "--draft" ]] && OUT="$(resolve_out "$4")"
    SCALE=1
    if [[ "${5:-}" == "--draft" || "${4:-}" == "--draft" ]]; then SCALE=0.5; fi
    exec npx remotion still src/index.ts "$COMP" "$OUT" --frame="$FRAME" "${PROPS_ARG[@]}" --scale="$SCALE"
    ;;
  *)
    echo "unknown mode: $MODE (draft|final|still)"; exit 2
    ;;
esac
