---
name: bigfunny-dispatch
description: VO synthesis, audio build and voice QC for The Big Funny. Turns a locked script into narration audio plus word timings for forced-aligned captions. Rendering is Remotion (video-engine/ + scripts/render.sh), NOT this skill.
---

# bigfunny-dispatch

The audio half of an episode. Script in, narration audio and word timings out.

**This skill does not render video.** The picture is Remotion:
`video-engine/` plus `scripts/render.sh`. An earlier version of this file
documented a retired PIL frame renderer as the production pipeline at the wrong
aspect ratio, which would have sent a run down a dead path on its first day.

## What is here

| File | What |
| --- | --- |
| `build_vo.py` | Script to narration audio. |
| `vo_backends.py`, `vo_gemini.py` | Synthesis backends. |
| `vo_qc.py` | Voice QC helpers. **Note the gap below.** |
| `vo60.py` | 60 second timing helpers. |
| `audio_build.py` | Mix narration with music and sfx. |
| `dispatch_core.py`, `easing.py`, `craft.py`, `dimensional.py` | Shared helpers. |
| `post_grade.py` | Post-render grade pass. |

## The contract with the rest of the pipeline

Audio work lands in `out/dispatch/`, which is the live scratch dir for the
current run. Downstream, `scripts/align_captions.py` produces word timings and
`scripts/build_scenes.py` turns those into `episode_props.json`, which is what
`scripts/render.sh` feeds to Remotion. Nothing renders until the VO exists.

## Format

1080x1920 vertical, 60 seconds or under. The 60s ceiling is a hard gate, not a
target: `build_scenes.py` refuses to write props for anything longer, and
`scripts/render_gate.py` refuses to pass the finished file.

## KNOWN GAP: one voice, three characters

The ported synthesis path speaks every line in a SINGLE cloned reference voice.
This show has three characters (Ray, Dee, the Institution) and they are the whole
premise, so a single-voice read collapses the cast into a podcast.

This is tracked in `.claude/WORKLOG.md`. Do not paper over it: if a run
synthesises all three in one voice, say so in the run's report rather than
letting a scorer grade it as if the cast were realised.

## Environment

The voice stack needs `scripts/setup_env.sh` (builds `.venv-voice` with
chatterbox / faster-whisper / resemblyzer). Under system python these imports
fail. Run setup before the first VO build.
