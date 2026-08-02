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
| A | ~~**Produce episode 1 end to end**~~ | DONE 2026-08-02, case 0002. Shipped at 79.65 against a threshold of 78, merged to main in PR #4. 54.53s, 1080x1920, with audio. Funny scored 76 on the third cold read, carried by FACT, zero explaining lines. |
| B | ~~Look-dev frame for Ray and Dee~~ | DONE 2026-08-02. Both rendered in anger across a whole episode. Worth noting the panel found Dee holds ONE pose in all seven appearances and never holds the document CAST_BIBLE assigns her, so Ray performs and Dee is composited. That is now the standing note for case 0003. |
| C | Institution costume system | `MachineShadow` exists; the per-episode re-dressing (insurer/airline/HR livery) is designed, not built. |
| D | `--self-test` for the funny gate | House rule: a gate that cannot fail certifies nothing. The funny gate is a MODEL judgement, so it cannot be self-tested the way render_gate and refs_check are. Open question: feed it a known-unfunny script and require a sub-60. |
| G | ~~Brand components never rendered~~ | DONE 2026-08-02. All rendered. Rendering them found two real defects: the one-stamp rule was unenforceable because Wordmark and EndCard default to red, and Stamp's hardcoded multiply blend makes a pale wordmark invisible on a night frame. Both now take explicit props. |
| E | Trigger config at claude.ai/code/routines | Schedule, model, connectors. Lives outside this repo. |
| F | ~~VO voices for Ray and Dee~~ | DONE. `scripts/vo_cast.py` casts three Gemini voices (Algenib/Schedar/Despina) with per-character delivery direction. Needs `GEMINI_API_KEY` at run time; verified by `--dry-run` and `--self-test` only, never against the live API. |
| H | ~~Synthesize for real~~ | DONE 2026-08-02. The casting layer made real API calls for the first time, in three distinct voices. It immediately found that the static 3.6 w/s assumption is wrong by roughly 2x and varies per line, which produced `--fit` and the on-disk take cache. |

## RUN 2026-08-02 — CASE No. 0002 (task A, DELIVERED)

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
| 1 | Research, 7 beats + cross-cutting, parallel | DONE |
| 2 | Fact-check hard gate -> claims.json | DONE. Killed google-play (see below). |
| 3 | Pick the story | DONE. ford-28-speakers, cross-cutting beat. |
| 3.5 | Angle room, judge hard | DONE. RATIO survived; precedent and straight-face killed. |
| 4 | Script, art direction, brand moves, the button | DONE |
| 4.5 | Gate 0 storyboard-critic, before any scene code | DONE. FAILED with 6 blockers, all resolved. |
| 5 | VO, scene code, drafts, final, mux, render_gate | DONE. renders_clean PASS at 54.53s. |
| 5b | caption.txt + first_comment.txt, caption_check | DONE, gate PASS |
| 6 | Hard gates + panel, ship threshold 78 | DONE. 79.65, ship true. All 8 hard gates pass. |
| 7 | runs/2026-08-02/, ledgers, commit, push, PR ready, MERGE | DONE. PR #4 merged to main. Gmail draft written. |
| 8 | Retro + upgrades on a SEPARATE branch off fresh main | DONE. PR #5 merged. Three upgrades: render.sh comp resolution, scripts/script_check.py, and the routine's two build paths. |

### The story, and what the gate killed

CHOSEN: NHTSA campaign 26V415000. Ford recalled these hybrid SUVs in October
2025 (43,438) for a pedestrian warning sound the car may not make at certain
speeds, fixed it with a software update, mailed owner letters 5 November. In
June 2026 the same recall came back as an "expansion" covering 66,383, cars
already repaired must be repaired again, the only fix that exists is a hardware
swap for Nautilus Hybrids "equipped with 28 speakers", and for everything else
"the remedy is currently under development". Interim letters mail 3 August 2026,
which is TOMORROW relative to this run.

KILLED at the fact gate: google-play-48-hour-window. The whole angle was that
Google doubled its pre-charge window from 24h to 48h, and that is exactly what
could not be proven. Both texts verify individually, but Google's own archive
page returned a THIRD effective date (2023-03-15), the 2024 page reads as a
stale mirror on the legacy domain rather than the true predecessor, two years
separate the dated pages, and web.archive.org snapshot BODIES are unfetchable
from this environment so the edit could not be dated. No honest hedge exists;
"recently doubled" is the move that ends channels. Binned rather than softened.

NOT CHOSEN: subaru (count single-sourced, and its pending-remedy beat duplicates
Ford's), tsa-confirm-id (every quote exact but 8 months stale, no peg).

### The two guards that shape every downstream decision

- **c11 is CUT.** The record never says the 28 speakers FAILED, and the external
  pedestrian emitter is generally not part of the cabin audio array. The episode
  may place the speaker count and the missing sound side by side as two
  separately true facts. It may never assert one caused the other.
- **c8 is a LOW SPEED rule** (FMVSS 141, roughly under 19 mph). Dee may say the
  law requires a noise so people hear the car coming. Never "at any speed".
- **c10: do NOT subtract** 66,383 - 43,438. The populations are not a clean
  superset, so any derived figure is unprovable. State both totals, let the
  viewer do the arithmetic.

### Gate 0 FAILED first pass. Six blockers, and what happened to each

1. **S5 would have taught the wrong fact.** A lone "28 SPEAKERS" badge does not
   read as a window sticker, it reads as a callout on the broken part, so the
   viewer walks away believing exactly the thing c11 forbids. FIXED: the shot now
   draws the SORTING, a two-row eligibility list (NAUTILUS HYBRID, 28 SPEAKERS ->
   module replaced / ALL OTHER -> remedy currently under development), both rows
   straight out of c3 and c4. The picture states the rule instead of pointing at
   a part.
2. **The hook hardened c2.** "a sound they don't make" dropped the "may" and the
   "at certain speeds" and never recovered them, leaving a viewer believing these
   SUVs are silent. FIXED: hook is now "over a warning sound" and Dee immediately
   supplies "It doesn't always play."
3. **One-stamp rule was asserted, not earned.** Wordmark and EndCard both render
   through Stamp, which DEFAULTS to STAMP red, so the episode was spending the
   red token three times. FIXED in brand.tsx with an additive `color` prop
   (defaults unchanged so nothing shipped moves) plus a written audit in the
   composition header. Also needed `blend`, because ink-into-paper is a multiply
   and a pale wordmark on a night frame is invisible under multiply.
4. **Manifest drift on MachineShadow**, the one asset the show cannot ship
   without: registered at Episode.tsx, actually promoted to kit.tsx on 07-22.
   FIXED in ASSET_MANIFEST.md.
5. **Button under-timed and under-sized.** FIXED: type floor lifted, content
   rebalanced, verbatim restored in sentence case, and the button sits OUTSIDE
   NightGrade so PAPER is not dragged to muddy blue-grey on the one frame that
   must look like real paper.
6. **Stale SCENE_START_LINE would drift the picture 15s off the words.** NOT
   APPLICABLE and verified so: Case0002 is a self-timed composition like
   Case0001, it never imports Episode.tsx, and episode_props.json does not exist,
   so render.sh omits --props and build_scenes.py is never invoked.

### The VO fight, and the two tools that came out of it

The static timing check assumes 3.6 words/sec. Real measured delivery on this
cast is 1.85 to 2.81 w/s and VARIES BY LINE, because a full stop mid-line buys a
pause no word count can see. The first synthesis failed with Ray's opening line
needing 7.33s in a 4.20s slot, i.e. after paying for the take.

Two upgrades, both in scripts/vo_cast.py:
- `trim_silence()`: every Gemini take carries ~0.25s lead and ~0.30s tail of dead
  air. Untrimmed that is nearly nine seconds of an episode saying nothing, and
  the padding lands INSIDE the slot so a take that fits fails anyway.
- `--fit` plus an on-disk take CACHE keyed by (voice, style, text): synthesize
  once, measure, lay the timeline out from the REAL durations, and write the
  frozen numbers back. Guess-and-fail does not converge; measure-then-place does.
  The cache means iterating on the script costs nothing after the first take.
- Also added a retry for Gemini answering HTTP 200 with finishReason OTHER and no
  audio, observed live. vo_gemini retries 429/500/503 but not that, so one random
  empty response would kill a run with most takes already paid for.

Final: 12 spoken lines, 55.53s spoken, +1.5s tail = **57.03s**, inside the law
with three seconds to spare.

## File map

- Master routine: `prompts/BIGFUNNY_ROUTINE.md`
- Voice + cast law: `knowledge/CAST_BIBLE.md`, `config/brand.yaml`
- Angle craft: `knowledge/ANGLE_TAXONOMY.md`
- Gates: `config/scoring_rubric.yaml` (hard gates cannot be averaged away)
- Cast code: `video-engine/src/lib/cast.tsx`, registered in `ASSET_MANIFEST.md`
- Scar tissue: `knowledge/FIELD_NOTES.md`

Delete this file when A through F are done. As of 2026-08-02: A, B, G and H are DONE.
Still open: C (Institution costume system, still designed rather than built), D (a
--self-test for the funny gate, which the Phase 8 engineer is looking at), and E
(trigger config, which lives outside this repo).

### How it scored, and the honest read

Weighted **79.65** against a threshold of 78. funny 76, angle 79, ray 83,
craft 81, button 87. All eight hard gates passed on inspection rather than
assertion: the scorer walked every line to a VERIFIED claim, confirmed the CUT
claim c11 appears nowhere in the script or on any card, and confirmed in the
shipped frames that the Institution has no face.

It clears by 1.65, which is thin. The scorer's diagnosis, which two other
critics reached independently from different directions: the episode was built
on the weaker half of its own story. The declared angle type is `ratio`, but the
ratio is the inert half, because claims.json forbids subtracting the two counts,
so the taxonomy's promise that the viewer does the math never cashes out. The
funniest verified fact, that the only fix which exists is for the version with
twenty-eight speakers, arrives as the fourth item in a data block at t=32, and
Ray is consequently off screen for the middle third of a show whose premise is
Ray finding out.

**The lesson for case 0003, now in instincts.json:** pick the spine by asking
which single VERIFIED fact is funniest, then build the episode to arrive at it.
Do not pick an angle TYPE first and fit the facts to it.
