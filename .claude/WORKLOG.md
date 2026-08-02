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

## File map

- Master routine: `prompts/BIGFUNNY_ROUTINE.md`
- Voice + cast law: `knowledge/CAST_BIBLE.md`, `config/brand.yaml`
- Angle craft: `knowledge/ANGLE_TAXONOMY.md`
- Gates: `config/scoring_rubric.yaml` (hard gates cannot be averaged away)
- Cast code: `video-engine/src/lib/cast.tsx`, registered in `ASSET_MANIFEST.md`
- Scar tissue: `knowledge/FIELD_NOTES.md`

Delete this file when A through F are done.
