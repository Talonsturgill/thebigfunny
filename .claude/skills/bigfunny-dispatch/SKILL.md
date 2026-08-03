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

**The entry point is `scripts/vo_cast.py`, which is NOT in this directory.** It
casts every line to Ray, Dee or the Institution, calls `vo_gemini.synth` per
line, caches each take on disk and lays the timeline out from measured
durations. This skill holds what it calls.

| File | What |
| --- | --- |
| `vo_gemini.py` | The Gemini TTS call. Prompt construction, banned-tag guard, per-attempt budget enforcement. |
| `vo_backends.py` | Sample rate and the local backends. |
| `vo_qc.py` | Voice QC helpers. **Note the gap below.** |
| `dispatch_core.py`, `easing.py`, `craft.py`, `dimensional.py` | Shared helpers. |
| `post_grade.py` | Post-render grade pass. |
| `archive/` | **Do not run.** Three hardcoded Alaska episode scripts, kept for reference. See `archive/README.md`. |

This table used to list `build_vo.py`, `vo60.py` and `audio_build.py` as the
live tools. They are 22 hardcoded caribou phrases, 9 permafrost sentences and 5
beluga sentences respectively, with no CLI between them, and `audio_build.py`
mixes neither music nor sfx. A run following the manifest would have synthesized
an Alaska caribou VO for a national story. They are in `archive/` now.

`resume_render.sh` is deleted rather than archived. It `cd`ed to
`/home/user/alaska-ai-weekly`, had no `set -e`, so the failed `cd` left it
launching a retired PIL renderer in the caller's working directory, and it
printed a success line with a PID and exited 0.

## The contract with the rest of the pipeline

Audio work lands in `out/dispatch/`, which is the live scratch dir for the
current run. Downstream, `scripts/align_captions.py` produces word timings and
`scripts/build_scenes.py` turns those into `episode_props.json`, which is what
`scripts/render.sh` feeds to Remotion. Nothing renders until the VO exists.

## Format

1080x1920 vertical, 60 seconds or under. The 60s ceiling is a hard gate, not a
target: `build_scenes.py` refuses to write props for anything longer, and
`scripts/render_gate.py` refuses to pass the finished file.

## CLOSED: one voice, three characters

The ported synthesis path spoke every line in a SINGLE cloned reference voice,
which collapsed Ray, Dee and the Institution into a podcast. `scripts/vo_cast.py`
closed this: three voices, cast per line from a table, and `vo_cast --self-test`
refuses a script that invents a fourth character or casts a human to a voice
whose descriptor is flat.

The casting is settled too: RAY=Algenib, DEE=Pulcherrima, INSTITUTION=Despina,
chosen by the owner and locked in `scripts/vo_cast.py`'s CAST table.

The one thing worth keeping from the audition is the NEGATIVE result, because it
stops a future run from rebuilding a tool that cannot work. The soundcheck
measured all seven candidates between 3.46 and 4.12 semitones of pitch variance,
INCLUDING the one the owner called robotic. Prosody statistics do not measure
"robotic" here; they ran backwards against the ear. `vo_soundcheck.py` prints
those numbers and never fails a take on them, and that is deliberate.

## Environment

The Gemini path needs `GEMINI_API_KEY` and nothing else; it runs under system
python. The LOCAL backends in `vo_backends.py` need `scripts/setup_env.sh`
(builds `.venv-voice` with chatterbox / faster-whisper / resemblyzer), and under
system python those imports fail.

Do not set `SSL_CERT_FILE` in this skill. The two archived scripts forced
`/etc/ssl/certs/ca-certificates.crt`, which overrides the agent proxy's CA
bundle that this environment requires; `vo_gemini` honours the container's
bundle when one is present.
