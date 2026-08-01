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

## Not done yet (the honest list)

| # | Task | Note |
| --- | --- | --- |
| A | **Produce episode 1 end to end** | The only real test. Funny is the open question; everything above is scaffolding until one episode exists. |
| B | Look-dev frame for Ray and Dee | `cast.tsx` typechecks but has never been rendered. Wrappers over a proven rig, so low risk, but unrendered is unproven. |
| C | Institution costume system | `MachineShadow` exists; the per-episode re-dressing (insurer/airline/HR livery) is designed, not built. |
| D | `--self-test` for the funny gate | House rule: a gate that cannot fail certifies nothing. The funny gate currently has no proof it can go red. |
| E | Trigger config at claude.ai/code/routines | Schedule, model, connectors. Lives outside this repo. |
| F | VO voices for Ray and Dee | Ported synthesis is tuned for a single narrator persona; this show has three. |

## File map

- Master routine: `prompts/BIGFUNNY_ROUTINE.md`
- Voice + cast law: `knowledge/CAST_BIBLE.md`, `config/brand.yaml`
- Angle craft: `knowledge/ANGLE_TAXONOMY.md`
- Gates: `config/scoring_rubric.yaml` (hard gates cannot be averaged away)
- Cast code: `video-engine/src/lib/cast.tsx`, registered in `ASSET_MANIFEST.md`
- Scar tissue: `knowledge/FIELD_NOTES.md`

Delete this file when A through F are done.
