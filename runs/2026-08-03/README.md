# CASE No. 0003 — "One eviction case, counted again"

Shipped 2026-08-03. The first episode produced by the full room: story gate,
producer, devil's advocate, writer, production designer, director, and the
mechanical gates between each of them.

## The story

The FTC sued RentGrow, Inc. over its tenant screening reports. The allegation
this episode is built on: the reports carried DUPLICATE entries for the same
eviction action, so an applicant looked like they had been sued for eviction
more times than they actually had.

The angle, from `story.json`:

> The report wrote the same eviction case out again and again, and counted each
> copy as another time he was sued. It is not wrong about anything. Every copy is
> accurate, and being accurate that many times is what makes the total false.

## The world

THE COUNT ROOM: the inside of the machine that ASSEMBLES the report. Not the
office that sells it, not the counter where you dispute it. The face of the
assembler, with its intake, its count and BOTH of its outputs in one frame, so
the whole allegation is one image and the film never travels.

This is the first set built to the world-of-the-story law rather than shopped off
the ported Alaska shelf, and that change is the reason this episode is not two
people talking. See `video-engine/src/lib/countroom.tsx`.

## What is guarded, and why

- **c10 is CUT.** No number of people affected is stated or implied. The FTC does
  not give one.
- **c11 is CUT.** No named individual was denied a home. Ray is the show's
  everyman reacting, never a case study.
- **c12 is CUT.** This is a SETTLEMENT and a settlement is NOT an admission. The
  button carries the case caption and the word ALLEGED, and the component
  defaults that on so a scene has to work to turn it off.
- **c3 ($2.25M) is CLEARED and deliberately EXCLUDED.** The verdict ledger
  recorded that the number reverses the irony: a settlement figure invites the
  viewer to read the story as resolved, and nothing cleared says the count was
  ever corrected.
- **The odometer only ever displays the number of cards visible in the same
  frame.** That is the ALLEGED guard drawn rather than written down: the wheel
  captions the picture and asserts nothing beyond it.

The caption asserts no count either. An earlier draft said "evicted twice" and
that number is not in the record.

## One line the director refused to illustrate

Line 6, "Somebody got paid to do that." c6 licenses a failure to disclose
SOURCES, not a payment, so drawing the payment would assert an uncleared
transaction. The shot stages the painted-shut panel and the line rides on audio.
Filed as a note to the writers room rather than a rejection: one line, not the
turn, not the button.

## Do not cut, if this is ever recut for pace

- **S7 and S8 are ONE move.** The highest camera in the film and the lowest, back
  to back, with the fall itself as the measurement. Cutting either strands the
  other.
- **S11 lands the punchline BEFORE the euphemism S12 answers.** That order is the
  joke.
- **S5 is the only true-human-size object in the film.** Without Dee's
  letter-size dispute form beside a card 8.2 times its long edge, the scale
  conceit is invisible.
- **S14 is the only still wheel**, in the framing matched exactly to second 2.6.

## Files

| file | what |
| --- | --- |
| `story.json` | the locked angle |
| `claims.json` | the cleared claim set, post fact-check |
| `episode_plan.json` | the producer's plan: logline, the turn, the button |
| `world.json` | the production designer's world |
| `storyboard.json` | the director's board, 18 shots |
| `script.json` | the locked script |
| `caption.txt` | the post body |
| `first_comment.txt` | the sources, which never go in the body |
