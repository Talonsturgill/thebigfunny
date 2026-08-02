# WORKLOG — standing up The Big Funny

Written per the house rule: any task too large for one context gets a durable
plan before code, because a plan that lives only in context does not survive
compaction.

## Approved scope (from the maintainer, 2026-08-01)

Clone the daily-video capability out of `alaska-ai-weekly` and the publication
discipline out of `alaskaaicarousels`, and point them at daily American comedy.

Decisions already locked, do not relitigate:
- **NOT stick figures.** The ported art library is ~7,800 lines with a real
  character rig; stick figures would be a downgrade. Decided after reading
  `ASSET_MANIFEST.md`.
- **Ray is RIGHT**, not a fool. Register is "the only honest voice", not
  "idiot overreacts". This decides every line he ever says.
- **60 seconds, hard gate.** Not 90. The constraint is the training; revisit
  only after a long run of episodes that are genuinely tight at 60.
- **Crude is fine.** Punch at institutions only. Slurs/hate/sexual/harassment
  are bans not demonetizations, and are out.
- **The Institution has no face.** Hardest rule in the show.
- Non-partisan by construction. The villain is an institution, never a voter.

## Status

| # | Task | Status |
| --- | --- | --- |
| 1 | Port video-engine (Remotion + 7.8k line art library) | DONE |
| 2 | Port dispatch skill (render, VO, audio, QC) | DONE |
| 3 | Port pipeline scripts + assets (sfx, voice) | DONE |
| 4 | `CLAUDE.md` constitution incl. 60s law | DONE |
| 5 | `knowledge/CAST_BIBLE.md` | DONE |
| 6 | `knowledge/ANGLE_TAXONOMY.md` | DONE |
| 7 | `knowledge/FIELD_NOTES.md` seeded with upstream scar tissue | DONE |
| 8 | `config/sources.yaml` (7 beats + wildcard) | DONE |
| 9 | `config/scoring_rubric.yaml` incl. the funny gate | DONE |
| 10 | `config/brand.yaml` | DONE |
| 11 | `prompts/BIGFUNNY_ROUTINE.md` master routine | DONE |
| 12 | `prompts/ROUTINE_PROMPT.txt` trigger pointer | DONE |
| 13 | Seed 5 ledgers | DONE |
| 14 | Agents: researcher, fact-checker, angle-room, writer, funny-critic, scorer | DONE |
| 15 | Agents ported + retargeted: storyboard-critic, flow-critic, vo-director, upgrade-engineer | DONE |
| 16 | `video-engine/src/lib/cast.tsx` (Ray, Dee) + manifest registration | DONE |
| 17 | Typecheck the whole ported engine | DONE (tsc exit 0) |
| 18 | README | DONE |
| 19 | Code review of the first commit (15 findings, all valid) | DONE |
| 20 | Delete dangerous/dead ported code (publish_feed, story_gate, 28 one-offs) | DONE |
| 21 | Fix TAIL 60.6s overshoot + scene-count silent fallback, both now hard-fail | DONE |
| 22 | `scripts/render_gate.py` (renders_clean had NO implementation) + self-test | DONE |
| 23 | `scripts/refs_check.py` (largest defect class) + self-test | DONE |
| 24 | Rewrite 4 agents that graded from missing files | DONE |
| 25 | `knowledge/BRAND_BIBLE.md` | DONE |
| 26 | `video-engine/src/lib/brand.tsx` + manifest registration | DONE |
| 27 | `ledger/cases.json` case register | DONE |
| 28 | Case 0001 run: research, fact-check, angle, script, composition, stills | DONE |
| 29 | Fix the SVG mounting contract + font weight (found only by rendering) | DONE |
| 30 | `scripts/vo_cast.py`: three Gemini voices, one per character, + self-test | DONE |
| 31 | `scripts/caption_check.py` + caption and first-comment for case 0001 | DONE |
| 32 | Script approved by the maintainer (2026-08-02) | DONE |

## Not done yet (the honest list)

| # | Task | Note |
| --- | --- | --- |
| A | **Produce episode 1 end to end** | The only real test. Funny is the open question; everything above is scaffolding until one episode exists. |
| B | Look-dev frame for Ray and Dee | `cast.tsx` typechecks but has never been rendered. Wrappers over a proven rig, so low risk, but unrendered is unproven. |
| C | Institution costume system | `MachineShadow` exists; the per-episode re-dressing (insurer/airline/HR livery) is designed, not built. |
| D | `--self-test` for the funny gate | House rule: a gate that cannot fail certifies nothing. The funny gate is a MODEL judgement, so it cannot be self-tested the way render_gate and refs_check are. Open question: feed it a known-unfunny script and require a sub-60. |
| G | Brand components never rendered | brand.tsx typechecks; the stamp overshoot, ink bleed and highlighter overshoot are unproven until a frame exists. |
| E | Trigger config at claude.ai/code/routines | Schedule, model, connectors. Lives outside this repo. |
| F | ~~VO voices for Ray and Dee~~ | DONE. `scripts/vo_cast.py` casts three Gemini voices (Algenib/Schedar/Despina) with per-character delivery direction. Needs `GEMINI_API_KEY` at run time; verified by `--dry-run` and `--self-test` only, never against the live API. |
| H | Synthesize case 0001 for real | The casting layer has never made an API call. First run with a key is the proof. |

## RUN 2026-08-02 — CASE No. 0002 (this is task A, in progress)

Appended live so the run survives context compaction. Resume from the table.

### The container started BARE. Minimum deps, not `setup_env.sh`.

`setup_env.sh` also pulls taichi, bpy, kokoro and a torch-based chatterbox venv
that the Gemini VO path does not touch. Installed only what this chain needs:

| Need | Status |
| --- | --- |
| numpy 2.4.6 | installed |
| scipy 1.17.1 | installed. `vo_gemini._resample_to_sr` imports it; without it the API call SUCCEEDS and then dies on resample, i.e. you pay for the take and still get nothing. Fourth instance of the silent-missing-dep class already in FIELD_NOTES three times. |
| node_modules | `npm install` in video-engine/ |
| ffmpeg 6.1.1 | apt was wedged; `dpkg --configure -a` first, then install |
| GEMINI_API_KEY | PRESENT. This is the thing case 0001 lacked. |

**Proved the three things that killed or nearly killed case 0001, BEFORE
committing to a story:** all 3 Gemini voices synthesize live; the render host
draws a real frame (looked at the PNG, not the exit code); mux+verify self-test
green on both ffmpeg builds.

### Machine defect found and FIXED (blocking, not polish)

`scripts/mux_and_verify.sh` measured audio with `-af volumedetect`. The
Remotion-vendored ffmpeg is built `--disable-filters` with a whitelist carrying
NO `volumedetect` and no `astats`. So on any host without a system ffmpeg, the
documented fallback measured NOTHING and the script reported "has no audio
stream at all" — a hard fail on a good mux, aiming the run at the wrong problem
entirely. The fallback that exists so the mux always works could never pass.

Fix: no filter at all. Decode the muxed file's audio to PCM (`pcm_s16le` encoder
and `wav` muxer are enabled in every build we run on) and compute RMS in stdlib
python. One path for both ffmpeg builds, measuring the SHIPPED FILE.

Added `--self-test` proving both directions. Its video fixture is encoded from a
generated PNG, NOT lavfi `nullsrc`: the vendored ffmpeg has no `wrapped_avframe`
decoder so every lavfi VIDEO source fails there. The first cut used nullsrc and
printed "THE GATE IS WRONG" when the gate was fine and only the fixture was
unbuildable. Worth remembering before trusting any future ffmpeg self-test.

### Hard constraints this episode must satisfy

- `topics.json`: case 0001 = `microsoft-365-packaging-and-pricing-update`, beat
  `the-fee`, Microsoft. A beat should not run twice in 3 episodes, so `the-fee`
  is disfavoured.
- `bits.json`: case 0001 used `euphemism`. Legal again (max twice in 7) but
  variety favours another type.
- `artwork.json` divergence is HARD and case 0001 was: hero "interior two-hander
  against filing-cabinet wall", atmosphere "fluorescent records room, dust
  column", palette "manila/carbon", continuity "motif:the drifting sheet",
  camera "locked". **This episode must differ on all five.** Cast is exempt.

### Build path

Self-timed composition like `Case0001.tsx`, NOT the Episode.tsx/build_scenes.py
path: `render.sh` passes `--props` only when `episode_props.json` exists, so a
self-timed comp needs no props and skips the SCENE_START_LINE contract.
Order: script.json -> `vo_cast.py --dry-run` -> `vo_cast.py` (writes vo.wav +
captions.json with MEASURED ends) -> drive the composition's caption timings
FROM captions.json -> draft renders -> final -> mux -> gates.
Mounting contract: `src/lib/` returns SVG and must sit inside
`<svg viewBox="0 0 1080 1920">`; `brand.tsx` is HTML and stays outside it.
Fonts: explicit `fontWeight: 900` plus a stack naming an installed face.

### Run status

| # | Task | Status |
| --- | --- | --- |
| 0 | Preflight, ledgers, branch, env, engine proof | DONE |
| 0b | Fix mux_and_verify.sh volumedetect defect + self-test | DONE |
| 1 | Research, 7 beats + cross-cutting, parallel | IN PROGRESS |
| 2 | Fact-check hard gate -> claims.json | TODO |
| 3 | Pick the story | TODO |
| 3.5 | Angle room, judge hard | TODO |
| 4 | Script, art direction, brand moves, the button | TODO |
| 4.5 | Gate 0 storyboard-critic, before any scene code | TODO |
| 5 | VO, scene code, drafts, final, mux, render_gate | TODO |
| 5b | caption.txt + first_comment.txt, caption_check | TODO |
| 6 | Hard gates + panel, ship threshold 78 | TODO |
| 7 | runs/2026-08-02/, ledgers, commit, push, PR ready, MERGE | TODO |
| 8 | Retro + upgrades on a SEPARATE branch off fresh main | TODO |

## File map

- Master routine: `prompts/BIGFUNNY_ROUTINE.md`
- Voice + cast law: `knowledge/CAST_BIBLE.md`, `config/brand.yaml`
- Angle craft: `knowledge/ANGLE_TAXONOMY.md`
- Gates: `config/scoring_rubric.yaml` (hard gates cannot be averaged away)
- Cast code: `video-engine/src/lib/cast.tsx`, registered in `ASSET_MANIFEST.md`
- Scar tissue: `knowledge/FIELD_NOTES.md`

Delete this file when A through F are done.
