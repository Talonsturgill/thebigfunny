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

> **A 60-second animated bit in which a real institution does something
> genuinely insane TO RAY, he cannot get out of it, and the proof is on screen.**

It is a BIT, not a report. The distinction is the whole overhaul:

- A report states a true thing with attitude. Case 0003 is a report.
- A bit has a premise, an escalation, a turn and a tag, and it commits totally to
  an absurd frame. The fact is the PREMISE of the bit, not the payload.

The fact-check gate does not soften for this and never will. Savage and sourced.
What changes is that being sourced stops being mistaken for being funny.

## THE CONTENT DECISION (owner asked, 2026-08-03, and delegated the call)

> "I'm still kind of open on what we wanna use as content, I think the best thing
> to use is the most relevant stuff going on in America, ppl are interested in it
> and already talking about it, we just gotta find funny angles, I also like the
> idea of kind like a show like south park that also incorporated relevant
> current stuff but idk which way to go, want you to do whatever you will be able
> to do best"

**THE CALL: the South Park model, running on the news engine. Not one or the
other.** Both halves matter and the order matters.

### Why not pure news satire, which is what we have been doing

Three episodes of "find a true absurd thing and describe it" produced 57, 69 and
64 on funny and "it made no sense" from the owner. The reason is structural, not
effort: **a fact is not a story.** A fact has no want, no obstacle and no
causality, so a script built directly on one can only ever be a list of
observations joined by AND THEN. That is failure 2 in this document, and it is
caused by the content model, not by the writers room.

The second problem is timing. The genuinely big current-events stories are being
joked about by every account on the platform within hours. Arriving late with a
more accurate version of a joke everyone has heard is the worst place to be.

### Why the South Park model fixes exactly what is broken

South Park's engine is a STABLE CAST that a current event happens TO. The comedy
is people we know reacting in character to something real and insane. That is
why it survives 27 years while topical sketch shows do not.

We already have the fixed cast and have been wasting it. Ray and Dee are
currently NARRATORS WITH NAMES: they comment on a document neither of them has
any stake in. The simulated viewer put it exactly right on case 0003, "he has
been talking constantly, so I do not know what he means by standing here." Ray
had no situation. He had a subject.

The fix is one sentence and it changes everything downstream:

> **The institution does the absurd real thing TO RAY, on screen, and he cannot
> get out of it.**

That single move converts a fact into a premise, an observation into a scene,
and AND THEN into BUT/THEREFORE, because now he WANTS something and each attempt
makes it worse. It is the same engine that makes "Randy tries to fix it and
makes it catastrophically worse" work every week.

### The beat where the news still does the heavy lifting

Research remains this machine's strongest capability and the fact gate remains
the thing that licenses the crudeness. Nothing about that changes. What changes
is WHERE the fact sits:

- before: the fact was the PAYLOAD. The episode delivered it.
- now: the fact is the PREMISE. The episode is what it does to a person.

The document still appears on screen, still verbatim, still sourced in the first
comment. It is now the thing Ray is trapped inside rather than the thing he is
reading out.

### Which current events, given the no-partisan law

This is the part that needs saying plainly rather than discovered later. The
house law bans taking a party's side, and the biggest American news stories are
usually partisan. So we do NOT chase the top of the news. We chase the lane that
is universal by construction:

**The daily indignities of being an American consumer and tenant and patient.**
Fees, denials, hold music, insurance, rent, screening reports, airlines,
subscriptions, medical billing, price changes, and algorithmic decisions made
about you by something with no phone number.

That lane is: genuinely enraging, already being talked about, non-partisan
BECAUSE everyone of every politics has been put on hold, endlessly supplied, and
absolutely full of absurd primary documents. It is also exactly the territory
South Park and Chappelle work when they are at their rudest.

**The honest cost, stated up front:** this rules out the biggest and most
searched stories of any given week, and that costs reach. The trade is a show
that cannot be dismissed as partisan and cannot be argued with on facts. That is
the right trade for an account that has to survive, and it is a trade rather
than a free win.

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
| 2 | craft research: South Park, Harmon/R&M, Chappelle, motion, retention | **DONE.** 3 briefs, all sourced. Headline: our own CAST_BIBLE beat shape fails the deletion test and was manufacturing the defect. |
| 3 | `knowledge/COMEDY_BIBLE.md` — the lane, the bit, but/therefore, the taboo line | **DONE.** 610 lines, every rule sourced to a practitioner. |
| 4 | `knowledge/MOTION_BIBLE.md` — what moves and when, the moving hold, camera language | **DONE.** Three motion budgets, the moving hold with frame numbers, Lang's EDIT-vs-CUT finding, measured retention. |
| 5 | ENGINE: the motion system | **IN PROGRESS.** Landed: the moving hold (default ON, `still` opts out), whole-body drift on the root transform, non-metronomic blink, and a default per-shot camera push (`locked` opts out). STILL MISSING: pose blending / gesture keyframes, parallax layers, smears, hair and coat follow-through. |
| 6 | `scripts/beat_check.py` + self-test — the but/therefore chain, mechanical | **DONE.** Lint half only, and it says so: the deletion/swap/named-expectation tests belong to the flow critic. |
| 7 | `scripts/motion_check.py` + self-test — frozen share, max hold, events/5s, LIFE floor, scene cap | **DONE.** Reads the RENDER, not the board. Fails case 0003 at 59% frozen / 3.0s hold. Mutation-tested on the frozen-share and cut-share guards. Discriminates a slideshow (87% frozen, 100% cuts) from a pan (0%, 0%), so cutting more often cannot game it. |
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

## Measured again after the LIFE floor and scene cap landed

Case 0003 now fails four rows, and the two new ones found something the critics
and I both missed:

| row | measured | ceiling |
| --- | --- | --- |
| frozen share | 59% | 15% |
| longest hold | 3.0s | 2.0s |
| **live share** | **31%** | 40% |
| **scene changes** | **11.4/min** | 5/min |

**It was cutting more than twice the ceiling WHILE being 59% frozen.** That is
the pathology stated exactly: the episode compensated for having no movement by
cutting constantly, and per Lang that trade actively damages recognition of the
fact Phase 2 spent the run verifying. Nobody had noticed, because until today
nothing measured either number.

## Known refinement, with its method, NOT yet done

The motion research recommends sampling every 5 frames (0.167s) instead of 0.5s,
because a blink (0.1-0.4s) and a 4-frame snap push are both invisible at the
current interval. That change REQUIRES recalibrating `FROZEN_DELTA`, which is
currently 3.0 and was calibrated at 0.5s spacing against the owner's own verdict
("no motion" <-> 59% frozen). The same physical motion produces roughly a third
of the per-gap delta at the finer interval, so the new threshold lands near 1.0,
but it must be MEASURED and not assumed.

Deliberately not done on a low context budget, because changing a threshold
without recalibrating it would make the gate worse while looking like progress.
The method is: sample case 0003 at both intervals, sweep the threshold at the
finer one, and take the value that reproduces the verdict the owner already gave.

## Wrap
- [ ] frozen share under 15%, measured, on a real episode
- [ ] a script whose every seam is BUT or THEREFORE, checked mechanically
- [ ] the comedy bible names a lane and the writers room is bound to it
- [ ] every new gate self-tests RED on purpose and is mutation-tested
- [ ] an episode the owner watches and does not call a slideshow
- [ ] delete this file

## Motion system, pass 1: what landed and what is still missing

**Landed.**

- **The moving hold**, replacing the 3.4px sway that was the entire body-movement
  vocabulary. Three summed sines at incommensurable periods (2.7s / 3.9s / 6.1s)
  so the cycle never visibly repeats, per-instance phase derived from `x` so Ray
  and Dee are never in lockstep, and enough amplitude to register on pixels. The
  old idle was a peak velocity of about 10 px/s against a derived ~40 px/s floor
  for ambient motion to be seen at all: it was four times too slow to be visible
  even in principle.
- **Whole-body drift on the root transform.** This is the component that moves
  enough AREA to register on a frame-difference metric. A blink changes about
  0.05% of the frame and never will.
- **A non-metronomic blink**, jittered per instance and per cycle.
- **A default per-shot camera push**, 4.5% over ~4.2s with an ease-out plus a
  small lateral slide. `useCurrentFrame()` inside a `Shot` returns SHOT-relative
  frames, so each push starts when its own shot starts rather than running off
  the episode clock, which is what makes it safe to apply to all 18 shots at
  once.

**Both defaults are opt-OUT, not opt-in** (`still` on the figure, `locked` on the
camera). That is the load-bearing design decision: gates catch the failure,
defaults prevent it, and a rig where stillness is free will keep producing frozen
film no matter how many gates sit downstream.

**Still missing, and none of it is optional for the 100x:**

- **Pose blending and gesture keyframes.** `pose` is still a discrete enum with a
  switch statement, so a figure can hold a pose but cannot TRANSITION between
  two. That means no gesture, no reach, no head turn, no point that arrives. The
  refactor is known: arm poses return polylines of different lengths (3, 4, or a
  `bent()` result), so they must be resampled to a fixed joint count before any
  two can be blended.
- **Parallax layers.** Free depth from art we already own, and because our first
  law puts the cast INSIDE the mechanism, the mechanism's own parts are the
  layers.
- **Smears** on the two or three biggest actions per episode.
- **Follow-through** on hair and coat. A one-time segmented-rig build, and worth
  it because the cast is fixed by house rule.
