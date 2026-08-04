# WORKLOG — THE 100x OVERHAUL

Durable plan for a task far too large for one context. Resume from the status
table. Delete this file when every wrap task is DONE.

Supersedes the "short film overhaul" worklog, whose scope shipped (the rooms,
the world kit, the gates) and which was NOT ENOUGH. That worklog fixed the SET.
It did not fix the MOTION, the STORY LOGIC or the COMEDY, and the owner watched
case 0003 and said so.

## The owner's verdict on case 0003, 2026-08-03

Verbatim, because paraphrasing loses it:

> good: "nice images", "voices sound better and not robotic"

> bad: "It wasn't funny" / "it made no sense" / "there was no like no motion, no
> character motion, no scene motion, no camera motion" / "there wasn't anything
> like coherent about it"

> "maybe you need to like study rick and morty" / "study south park"

> "its cool that it was automated, but if we don't output a good show, we are
> nothing, so I think you need to get clear on what this is and what it takes to
> make a good and engaging show"

> "5 second rule, scene change or something happen every 5 seconds to drive
> attention"

> "overall we need to find a comedic lane, I like raunchy, pushing the boundary,
> like south park or Dave chappelle, I also like sophisticated, so we need a show
> that people will actually wanna watch, I think u rushed through and just put
> something out. we def need more directors and planners going to plan the whole
> thing out before it starts and discuss with each other like what is a good
> script, maybe study some writer and directors and stuff to learn better"

> "we need this to be 100x better"

He is right on every count, and two of the four are provable in numbers, which
is how we will know when they are fixed.

## THE MEASURED BASELINE (case 0003, the shipped recut)

Do not re-derive these. They are the before-numbers for every later comparison.

| metric | measured | verdict |
| --- | --- | --- |
| frames visually frozen (delta < 3/255 across 0.5s) | **59% of the film** | it is a slideshow |
| longest frozen stretch | 3.0s from 9.0s | dead air with a picture on it |
| total character animation in the rig | `Math.sin(f/34)` breathe + **3.4px** sway | invisible at 1080 wide |
| shots with ANY camera movement | 2 of 18 | the camera is a still tripod |
| funny (cold script read) | 64 / 100 | below the 78 bar |
| what motion exists | almost entirely CUTS between static shots | motion is being faked by editing |

The 3.4px number is the whole story in one figure. `Figure.tsx` line 223 is
`3.4 * idleGain * Math.sin(f / 62)`. That is the entire body movement vocabulary
of this show. Everything else on screen is a still drawing.

## THE ROOT CAUSE, and it is three separate failures wearing one coat

The last overhaul concluded "two people talking is what is left after the world
is amputated from the story", built a world kit, and shipped. The world got
better and the owner's verdict did not, because **the world was only one of
three things missing.** Naming them separately is the point of this document,
because a single fix aimed at all three will miss all three.

### FAILURE 1: NOTHING MOVES (the engine)
The rig can stand, and that is all it can do. There is no gesture, no pose
change within a shot, no head turn, no walk, no weight shift, no reach, no prop
handling, no follow-through, no camera push, no parallax. A shot is a still
drawing held for four seconds while audio plays over it. 59% frozen is not a
pacing problem to be edited around, it is an ENGINE CAPABILITY THAT DOES NOT
EXIST.

### FAILURE 2: THE BEATS ARE A LIST, NOT A CHAIN (the writing)
"It made no sense" and "there wasn't anything coherent about it" are the same
note, and the diagnosis is precise: case 0003's beats are connected by AND THEN.
One eviction case, and then a report goes to a landlord, and then he got sued
once, and then somebody got paid, and then I've been standing here. Nothing
causes anything. Trey Parker's rule is that beats must be joined by BUT or
THEREFORE, and a script that fails it reads as a list of observations no matter
how good each observation is. Ours fails it on nearly every seam.

### FAILURE 3: THERE IS NO COMEDIC LANE (the show)
The show currently has a FORMAT (verified outrage, deadpan reaction) and mistakes
it for a VOICE. It is polite. It is not raunchy, not boundary-pushing, and not
sophisticated either; it is careful. The owner named the lane he wants and it is
a real and coherent one: **smart filth.** South Park and Chappelle are both rude
AND precise, and the rudeness is what buys attention while the precision is what
earns the respect. We have been spending the precision and never buying the
attention.

Note what is NOT on this list: the art and the voices. The owner praised both.
Do not touch the visual identity or the casting. They are the two things working.

## WHAT THIS SHOW IS (get clear, per the owner)

One sentence, and every later decision is bound by it:

> **A 60-second animated bit in which two people discover, out loud and with
> escalating disbelief, that a real institution did something genuinely insane,
> and the proof is on screen.**

It is a BIT, not a report. The distinction is the whole overhaul:

- A report states a true thing with attitude. Case 0003 is a report.
- A bit has a premise, an escalation, a turn and a tag, and it commits totally to
  an absurd frame. The fact is the PREMISE of the bit, not the payload.

The fact-check gate does not soften for this and never will. Savage and sourced.
What changes is that being sourced stops being mistaken for being funny.

## Approved scope

1. **A motion system in the engine.** Gesture and pose keyframing, camera moves
   as a first-class property of a shot, parallax layers, moving holds, weight
   shifts, prop handling. Measurable goal: frozen share under 15%, from 59%.
2. **A comedy bible with an actual lane**, built from real craft research rather
   than taste. But/therefore, bit construction (premise, act-out, tag, callback),
   the escalation ladder, and the taboo line drawn where South Park actually
   draws it: cruelty aimed at power, never at the powerless.
3. **A writers room that argues.** Opposed mandates, a real disagreement on the
   record, and a beat sheet that must pass but/therefore BEFORE a line is
   written. Planning before production, which the owner asked for twice.
4. **Mechanical gates for all of it**, because prose rules in this repo have a
   100% historical rate of being violated until something checks them:
   `beat_check` (the but/therefore chain), `motion_check` (measured frozen share
   and max static hold), and an events-per-5s rule from the owner's note.
5. **An episode that proves it**, produced end to end, with the before/after
   motion numbers in the run record.

## Explicitly NOT in scope
- The art style, the palette, the cast design. The owner likes them.
- The voice casting and the TTS stack. Praised; leave alone.
- The fact-check gate. It is not the problem and it never bends.
- The 60-second law. The owner did not complain about length.

## Status

| # | task | state |
| --- | --- | --- |
| 1 | measure the baseline, name the three failures | **DONE** — table above |
| 2 | craft research: South Park, Harmon/R&M, Chappelle, motion, retention | IN FLIGHT (3 agents) |
| 3 | `knowledge/COMEDY_BIBLE.md` — the lane, the bit, but/therefore, the taboo line | TODO |
| 4 | `knowledge/MOTION_BIBLE.md` — what moves and when, the moving hold, camera language | TODO |
| 5 | ENGINE: the motion system (gesture, pose keys, camera moves, parallax) | TODO — biggest single task |
| 6 | `scripts/beat_check.py` + self-test — the but/therefore chain, mechanical | TODO |
| 7 | `scripts/motion_check.py` + self-test — frozen share, max hold, events/5s | TODO |
| 8 | the writers room rebuilt: beat sheet before script, opposed agents, real argument | TODO |
| 9 | rewrite the routine prompt around the new order of operations | TODO |
| 10 | produce an episode that clears every new gate, with before/after numbers | TODO |

## The measured reasons (do not re-litigate)

- **59% frozen, 3.4px of sway.** Motion is not a polish pass, it is missing
  capability. Any plan that treats it as "add some animation at the end" fails.
- **A downstream critic never fixes an upstream decision.** Proven three times.
  The funny critic named the same cause on 0002 and 0003 and six rewrites moved
  57 -> 69 -> 63. Every new gate runs at the phase that MAKES the decision.
- **A prose rule with nothing enforcing it is being violated right now.** True of
  the one-stamp rule, the manifest mandate and the explaining-lines ban. So
  but/therefore and the motion floor ship as CODE or they do not ship.
- **Sampling lies.** A 12-cell contact sheet made two critics report a rendered
  beat as missing. Motion measurement samples at 0.5s and states its interval.

## Inherited from the previous worklog, still open
- **C:** Institution costume system (designed, never built).
- **E:** trigger config (lives outside this repo).
- Dee's voice pick is with the owner. `main` carries Pulcherrima and the owner
  has now called the voices good, so treat this as SETTLED unless he reopens it.

## Wrap
- [ ] frozen share under 15%, measured, on a real episode
- [ ] a script whose every seam is BUT or THEREFORE, checked mechanically
- [ ] the comedy bible names a lane and the writers room is bound to it
- [ ] every new gate self-tests RED on purpose and is mutation-tested
- [ ] an episode the owner watches and does not call a slideshow
- [ ] delete this file
