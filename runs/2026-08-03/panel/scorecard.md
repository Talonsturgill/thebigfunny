# CASE No. 0003 — panel record, 2026-08-03

The shipped cut (`case0003.mp4`) was merged to main with NO panel. This is the
panel it never got, run the next morning, plus the two recut passes.

## Hard gates (config/scoring_rubric.yaml)

| gate | result |
| --- | --- |
| sourced | PASS. 12 cleared claims, 13 citations across 13 lines, no line cites a CUT claim. |
| sixty_seconds | PASS. 53.27s, inside the 50-58 target band. |
| punch_direction | PASS. Target is RentGrow, Inc. and the FTC matter. No private individual. |
| platform_survivable | PASS. One profanity, no slurs, no hate, no sexual content. |
| not_partisan | PASS. No party, no candidate. |
| institution_faceless | PASS. Confirmed on frames across all 24 samples: walls, portholes, chutes, counters, paper. No eyes, no mouth, no reaction anywhere. |
| one_stamp | PASS. The single STAMP red is the diagonal ALLEGED on the filing. |

## Critic reads

| critic | shipped cut | recut pass 1 | recut pass 2 |
| --- | --- | --- | --- |
| funny (script, cold) | 64 | 64 (script unchanged) | 64 (script unchanged) |
| flow | 58, `recut` | — | — |
| storyboard (craft) | 44, `fix-then-proceed` | 62, `fix-then-proceed` | — |
| reader-sim first scroll | 19.0s | 10.1s | see below |
| reader-sim "stopped being new" | 16.2s | 25.2s | — |

## The honest position on the score

**This episode does not clear the 78 ship threshold, and it is not claimed to.**

Funny is 35% of the weighted score and it is a COLD READ OF THE SCRIPT. No line
of the script changed in either recut, so 64 stands, and 64 at 35% caps the
weighted total below 78 unless every other criterion scores in the high 80s.

Two things are true at once and both belong in the record:

1. The panel's own evidence is that this script reads worse on the page than it
   plays. The funny critic wanted "He got sued once." cut; both simulated
   viewers LAUGHED there, because the picture has already said nine. A critic
   that cannot see the picture is measuring something real but partial.
2. That is not an excuse, and the number is not revised upward. The next real
   move on this episode is a rewrite of the first thirty seconds, which is a
   writers-room job. The recuts fixed what the camera and the clock could fix.

## Two critic findings that were REFUTED, on the record

The flow critic reported the eight stacked head lines as "not in the render" and
the storyboard critic made `pile-never-rendered` its single systemic finding.
Both are false. The head lines render at 22.2s, the VERIFIED emboss at 31.0s,
both figures full-figure at 27.6s and 29.0s, the RESOLVED/INVALID payoff at
48.5s. All of them fell in gaps of a twelve-cell contact sheet sampling once
every 4.8s.

The critics reported what the grid showed. The fix is in `scripts/contact_sheet.py`:
24 cells, and the sampling interval now prints on the sheet itself.
