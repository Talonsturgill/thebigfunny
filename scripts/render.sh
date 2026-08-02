#!/usr/bin/env bash
# Render wrapper — makes the taste loop CHEAP and the final SHIP-GRADE.
#
#   scripts/render.sh draft  [comp] [out.mp4]   half-res, fast-encode preview (~3-4x faster)
#   scripts/render.sh final  [comp] [out.mp4]   full 1080x1920, ship quality
#   scripts/render.sh still  <frame> [comp] [out.png] [--draft]
#   scripts/render.sh --print-comp [comp]       which composition would be rendered
#   scripts/render.sh --self-test               prove the comp resolver can go red
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
SELF="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"
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
#
# AND ONLY WHEN IT BELONGS TO THIS RUN. out/dispatch/ survives across container
# sessions, so the previous episode's episode_props.json at this exact path
# renders a clean, plausible picture of the WRONG cut. scripts/run_guard.py was
# written for precisely this read and nothing in the repo called it.
PROPS_ARG=()
if [[ -f "$PROPS" ]]; then
  if ! python3 ../scripts/run_guard.py check "$PROPS"; then
    echo "render.sh: refusing to render against props that do not belong to this run." >&2
    echo "  Stamp the run in Phase 0:  python3 scripts/run_guard.py init --run-id <date>" >&2
    echo "  Or, for deliberate manual use, BIGFUNNY_NO_FRESHNESS=1." >&2
    [[ "${BIGFUNNY_NO_FRESHNESS:-}" =~ ^(1|true|yes)$ ]] || exit 1
  fi
  PROPS_ARG=(--props="$PROPS")
fi

# ---------------------------------------------------------------------------
# WHICH COMPOSITION.
#
# This used to be `COMP="${2:-${BIGFUNNY_COMP:-Case0001}}"`, a constant that was
# correct for exactly one episode and silently wrong for every episode after it.
# The routine's own documented command is `bash scripts/render.sh draft`, with no
# comp, so following the routine literally on case 0003 would have rendered case
# 0002's picture, muxed this run's VO onto it, and passed render_gate (right
# duration, right size, has audio) and mux_and_verify. The only thing standing
# between that and a shipped wrong episode was a human noticing the frames.
#
# So: the default is now DERIVED. Highest-numbered CaseNNNN registered in
# src/Root.tsx, printed on every invocation so the choice is never invisible.
# Explicit argument beats BIGFUNNY_COMP beats the derived default.
ROOT_TSX="${ROOT_TSX:-src/Root.tsx}"

registered_comps() {   # every composition id registered in Root.tsx
  # Anchored on <Composition ... id="..."> rather than any id= attribute in the
  # file. The loose form would pick up an id on any JSX element or SVG node that
  # happened to live in Root.tsx and offer it as a renderable composition.
  # <Composition and its id= sit on separate lines in Root.tsx, so this reads
  # the id that FOLLOWS a Composition tag rather than any id= in the file.
  awk '/<Composition/ {want=1; next}
       want && match($0, /id="[A-Za-z0-9_]+"/) {
         s = substr($0, RSTART + 4, RLENGTH - 5); print s; want = 0
       }' "$ROOT_TSX" 2>/dev/null || true
}

highest_case_comp() {  # CaseNNNN with the biggest N, or empty. Fixed width, so lexical sort is numeric.
  registered_comps | grep -E '^Case[0-9]{4}$' | sort | tail -n1 || true
}

COMP=""
COMP_SRC=""
pick_comp() {          # $1 = explicit comp from the command line, may be empty
  local c src list
  if [[ -n "${1:-}" ]]; then
    c="$1"; src="named on the command line"
  elif [[ -n "${BIGFUNNY_COMP:-}" ]]; then
    c="$BIGFUNNY_COMP"; src="BIGFUNNY_COMP"
  else
    c="$(highest_case_comp)"; src="default: highest CaseNNNN in $ROOT_TSX"
    if [[ -z "$c" ]]; then
      echo "render.sh: no CaseNNNN composition is registered in $ROOT_TSX, so there is no" >&2
      echo "           default to render. Register this episode's composition in Root.tsx" >&2
      echo "           first, or name one explicitly: render.sh <mode> <Comp>." >&2
      return 1
    fi
  fi
  # Catch a typo or an unregistered comp HERE, with the list, instead of inside
  # a remotion stack trace after node boots.
  list="$(registered_comps)"
  case $'\n'"$list"$'\n' in
    *$'\n'"$c"$'\n'*) : ;;
    *)
      echo "render.sh: composition '$c' is not registered in $ROOT_TSX." >&2
      echo "           registered: $(echo "$list" | tr '\n' ' ')" >&2
      return 1 ;;
  esac
  COMP="$c"; COMP_SRC="$src"
}

resolve_out() {   # abs path -> unchanged; relative path -> resolved against the CALLER's cwd
  local p="$1"
  case "$p" in
    /*) printf '%s' "$p" ;;
    *)  printf '%s' "$CALLER_PWD/$p" ;;
  esac
}

self_test() {
  # Prove the resolver picks the CURRENT episode, that overrides win, and that
  # the failure modes are loud. Every case below is a deliberate reintroduction
  # of the constant-default bug or one of its neighbours: restore
  # `COMP=Case0001` and case 1 goes red.
  local d ok=0 got rc
  d="$(mktemp -d)"
  trap 'rm -rf "$d"' RETURN

  cat > "$d/three.tsx" <<'EOF'
      <Composition id="Case0002" component={C} />
      <Composition id="Case0001" component={C} />
      <Composition id="Case0003" component={C} />
      <Composition id="Dispatch" component={E} />
EOF
  cat > "$d/one.tsx" <<'EOF'
      <Composition id="Case0001" component={C} />
      <Composition id="Standoff" component={S} />
EOF
  cat > "$d/none.tsx" <<'EOF'
      <Composition id="Standoff" component={S} />
EOF

  check() {  # name, expected ("" = expect failure), env/args...
    local name="$1" want="$2"; shift 2
    set +e
    got="$("$@" 2>/dev/null)"; rc=$?
    set -e
    if [[ -z "$want" ]]; then
      [[ $rc -ne 0 ]] && { echo "  ok   $name"; return 0; }
      echo "  FAIL $name   <- expected a loud failure, got '$got' (rc=$rc)"; ok=1; return 0
    fi
    if [[ $rc -eq 0 && "$got" == "$want" ]]; then echo "  ok   $name"; return 0; fi
    echo "  FAIL $name   <- wanted '$want', got '$got' (rc=$rc)"; ok=1
  }

  check "picks the NEWEST case, not the first (the 2026-08-02 bug)" "Case0003" \
        env ROOT_TSX="$d/three.tsx" BIGFUNNY_COMP= "$SELF" --print-comp
  check "picks the only case when there is one" "Case0001" \
        env ROOT_TSX="$d/one.tsx" BIGFUNNY_COMP= "$SELF" --print-comp
  check "BIGFUNNY_COMP overrides the default" "Dispatch" \
        env ROOT_TSX="$d/three.tsx" BIGFUNNY_COMP=Dispatch "$SELF" --print-comp
  check "an explicit argument overrides BIGFUNNY_COMP" "Case0002" \
        env ROOT_TSX="$d/three.tsx" BIGFUNNY_COMP=Dispatch "$SELF" --print-comp Case0002
  check "fails loudly when no case is registered" "" \
        env ROOT_TSX="$d/none.tsx" BIGFUNNY_COMP= "$SELF" --print-comp
  check "fails loudly on a comp that is not registered" "" \
        env ROOT_TSX="$d/three.tsx" BIGFUNNY_COMP= "$SELF" --print-comp Case9999

  # And against the real Root.tsx, because a fixture is not the thing that ships.
  set +e
  got="$(env BIGFUNNY_COMP= "$SELF" --print-comp 2>/dev/null)"; rc=$?
  set -e
  if [[ $rc -eq 0 && "$got" =~ ^Case[0-9]{4}$ ]]; then
    echo "  ok   resolves a real registered case against src/Root.tsx ($got)"
  else
    echo "  FAIL resolves a real registered case against src/Root.tsx   <- got '$got' (rc=$rc)"; ok=1
  fi

  if [[ $ok -eq 0 ]]; then
    echo ""; echo "self-test: both directions correct, as designed"; return 0
  fi
  echo ""; echo "self-test: THE GATE IS WRONG"; return 1
}

MODE="${1:?usage: render.sh draft|final|still|--print-comp|--self-test ...}"
case "$MODE" in
  --self-test) self_test; exit $? ;;
  --print-comp)
    pick_comp "${2:-}" || exit 2
    printf '%s\n' "$COMP"; exit 0 ;;
  draft|final) pick_comp "${2:-}" || exit 2 ;;
  still)       FRAME="${2:?frame number}"; pick_comp "${3:-}" || exit 2 ;;
  *) echo "unknown mode: $MODE (draft|final|still|--print-comp|--self-test)"; exit 2 ;;
esac
# Never silent about which episode is being rendered.
echo "render.sh: composition $COMP  [$COMP_SRC]" >&2

case "$MODE" in
  draft)
    OUT="../out/dispatch/render/draft.mp4"; [[ -n "${3:-}" ]] && OUT="$(resolve_out "$3")"
    exec npx remotion render src/index.ts "$COMP" "$OUT" \
      "${PROPS_ARG[@]}" --codec=h264 --muted --concurrency=2 \
      --scale=0.5 --crf=30 --every-nth-frame=1
    ;;
  final)
    # THE CUE FILE MUST MATCH THE TAKES. A ship render is the last place this can
    # be caught, and it is invisible everywhere else: a stale caseNNNN_captions.ts
    # is internally consistent, so the render succeeds and the picture simply cuts
    # on the wrong word with last cut's captions burned over this cut's audio.
    # Draft renders skip it on purpose, because iterating on the board before the
    # VO is re-fitted is a normal thing to do.
    if [[ "$COMP" =~ ^Case([0-9]{4})$ ]]; then
      n="$((10#${BASH_REMATCH[1]}))"
      # A GENERATED SIDECAR WITHOUT ITS SOURCE IS THE STALE CASE, NOT AN EXEMPT
      # ONE. All three checks below were written `[[ -f <generated> && -f
      # <source> ]]`, so a cleaned scratch dir or a run resumed in a fresh
      # container skipped every one of them and shipped the committed track. The
      # generated file existing IS the claim that a source produced it; if the
      # source is gone, nothing can say whether the claim is still true.
      _need_source() {   # $1 generated, $2 source it was generated from
        if [[ -f "$1" && ! -f "$2" ]]; then
          echo "render.sh: $1 is committed and $2 is MISSING, so nothing can tell" >&2
          echo "  whether it still matches this cut. That is the stale case, not an" >&2
          echo "  exempt one. Re-run the VO, or delete the generated file." >&2
          exit 1
        fi
      }
      _need_source "src/case$(printf '%04d' "$n")_captions.ts" "../out/dispatch/vo_lines.json"
      _need_source "src/case$(printf '%04d' "$n")_mouth.ts"    "../out/dispatch/vo.wav"
      _need_source "src/case$(printf '%04d' "$n")_faces.ts"    "../out/dispatch/script.json"

      if [[ -f "src/case$(printf '%04d' "$n")_captions.ts" && -f "../out/dispatch/vo_lines.json" ]]; then
        if ! python3 ../scripts/gen_captions_ts.py --case "$n" --check; then
          echo "render.sh: refusing to ship a final render against stale captions." >&2
          exit 1
        fi
      fi
      # Same check for the mouth track, same reason: a stale envelope renders
      # clean and the mouths move to the PREVIOUS cut's audio, which is the exact
      # defect the owner caught by eye on 2026-08-02.
      if [[ -f "src/case$(printf '%04d' "$n")_mouth.ts" && -f "../out/dispatch/vo.wav" ]]; then
        if ! python3 ../scripts/vo_envelope.py --case "$n" --check; then
          echo "render.sh: refusing to ship a final render against a stale mouth track." >&2
          exit 1
        fi
      fi
      # And the face track. Same class again: stale means the episode wears the
      # PREVIOUS cut's expressions, which renders clean and is invisible to
      # everything except a person watching.
      if [[ -f "src/case$(printf '%04d' "$n")_faces.ts" && -f "../out/dispatch/script.json" ]]; then
        if ! python3 ../scripts/gen_faces_ts.py --case "$n" --check; then
          echo "render.sh: refusing to ship a final render against a stale face track." >&2
          exit 1
        fi
      fi
    fi
    OUT="../out/dispatch/render/video_mute.mp4"; [[ -n "${3:-}" ]] && OUT="$(resolve_out "$3")"
    exec npx remotion render src/index.ts "$COMP" "$OUT" \
      "${PROPS_ARG[@]}" --codec=h264 --muted --concurrency=2 --crf=19
    ;;
  still)
    OUT="../out/dispatch/probe/still_$FRAME.png"; [[ -n "${4:-}" && "${4:-}" != "--draft" ]] && OUT="$(resolve_out "$4")"
    SCALE=1
    if [[ "${5:-}" == "--draft" || "${4:-}" == "--draft" ]]; then SCALE=0.5; fi
    exec npx remotion still src/index.ts "$COMP" "$OUT" --frame="$FRAME" "${PROPS_ARG[@]}" --scale="$SCALE"
    ;;
esac
