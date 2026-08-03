# WHAT IS ON SCREEN

The visual counterpart to `COMEDY_CRAFT.md`. That file is how a joke is built.
This one is how a joke is SHOWN, and how sixty seconds of animation stops being
a podcast with drawings over it.

## The diagnosis this file exists to fix

The owner, 2026-08-02, on the last episode:

> "the scenes are boring and not actually illustrating anything ... the whole
> story is just like incoherent, like it wasn't planned out to be a funny short
> film, you made it two ppl talking and doing nothing for the most part"

Those read as several complaints. They are one, and the cause is written up in
full in the worklog. Short version, because it is the reason every rule below
exists:

The art library was ported from a daily Alaska publication. It is a shelf of
parkas, snow, spruce, wolves and boreal night. `ASSET_MANIFEST.md` says to cast
from the shelf before drawing anything new, which is a sound engineering rule
that has been doing enormous quiet damage, because the shelf is a PLACE and the
stories are national. So every board dresses an Alaska set for a story that has
nothing to do with Alaska, the set therefore cannot illustrate anything, and once
the set is inert the only thing an episode has left to do is have two people
talk.

"Two people talking and doing nothing" is not a staging failure. It is what
remains after the world has been amputated from the story.

It also explains the standing repeat offenders in `ledger/verdicts.json`.
`carried_by_fact` and `agreement_not_comedy` appear in both runs on file, and
the funny critic blamed the STORY each time. It was half right. The fact was
carrying the episode because nothing else was permitted to: not the set, not the
props, not the world.

---

# THE FIRST LAW: THE WORLD OF THE STORY IS THE SET

**Every episode is staged INSIDE the mechanism it is about.**

Not in a room where two people discuss the mechanism. Inside it. A story about a
Ford engine defect is staged inside a Ford engine, with the cast standing on the
crankshaft while it turns.

Three things follow from that sentence and they are the whole file:

1. The set is BUILT for the story, never shopped for. The shelf supplies parts,
   not places. A world assembled from primitives that has never existed before
   beats a beautiful boreal night that has nothing to do with anything.
   `knowledge/WORLD_KIT.md` is the parts catalogue and the assembly rules; this
   file decides WHAT to build and that one is how it gets built.
2. The world does comedy work the dialogue cannot, which is the only way out of
   `carried_by_fact`. A joke that lives entirely in the dialogue is a joke that
   could have been a tweet, and `AUDIENCE.md` is explicit that this show is
   watched muted more often than not.
3. The cast is dropped into that world at the WRONG SCALE, on purpose.
   `CAST_BIBLE.md` already specifies Ray as "slightly too small for the world he
   is in". The world-as-set is what makes that literal instead of decorative.

## Four worked examples

Read all four. The move is the same every time and the point is how different
the four worlds look.

### A bank fee story

The mechanism: the bank posts the day's transactions largest first instead of in
the order they happened, so one big charge empties the account and the five small
ones behind it each draw a $35 overdraft fee.

| | |
| --- | --- |
| The lazy set | A bank lobby. A teller window. A phone with an app on it. |
| THE WORLD | The inside of the ledger. The day's purchases are physical parcels on a sorting belt, moving in the order they happened. A sorting arm reaches in and pulls the heaviest parcel to the FRONT. The five behind it tip off the end of the belt, one at a time, into a chute stencilled 35. |
| The cast in it | Dee is standing on the belt reading the sort rule off a card. Ray is at the end of the belt catching parcels and cannot catch five. |
| What the set does that the line cannot | Reordering is invisible in prose and obvious as a conveyor. The viewer understands the whole scam from the picture before Dee says a word, and the five separate falls are a free visual rule of three plus two. |

### A health insurance story

The mechanism: the ambulance that was dispatched to you was out of network.

| | |
| --- | --- |
| The lazy set | A hospital corridor. A waiting room. A stack of bills. |
| THE WORLD | The network drawn as an actual fenced enclosure on an otherwise dark plain. Inside the fence: lit, mown, tidy, a few approved buildings. Outside: black. The ambulance is parked one tile outside the fence with its lights turning. |
| The cast in it | Ray and Dee are inside the fence, up against it, on the correct side of a rule that is killing them. Ray can touch the ambulance through the fence. |
| What the set does that the line cannot | "Out of network" is a phrase people have heard so often it has stopped meaning anything. Drawn as a fence it means something again in half a second, and the gap between the ambulance and the fence is a distance the viewer can measure with their eye. |

### An airline story

The mechanism: the fare covers the flight and nothing else, and the list of
things it does not cover keeps growing.

| | |
| --- | --- |
| The lazy set | An airport gate. A jet bridge. A departures board. |
| THE WORLD | One row of seats, in a void, with a coin slot bolted to every component. The tray table, the window shade, the recline, the seat belt, the overhead bin, each with its own slot and its own price plate. |
| The cast in it | Ray is belted into the seat. Over the episode the parts LEAVE, one at a time, as their prices go unpaid, until he is belted to a frame in the air. |
| What the set does that the line cannot | This is escalation the dialogue does not have to spend a second on. Each part leaving is a visual event under a line that was going to be said anyway. By the button, the drawing has made an argument the script never had to state, which is the whole point of not being earnest. |

### A software outage story

The mechanism: one cloud region fell over and took down a list of things that had
no obvious reason to depend on it.

| | |
| --- | --- |
| The lazy set | An office. A server room. A laptop with an error on it. |
| THE WORLD | One wall outlet. Every extension cord in the world is daisy-chained into it, and the far end of each cord runs off to a doorbell, a mattress, a litter box, a front door lock, a car. |
| The cast in it | Ray and Dee are standing in the room those cords lead to. The cord is at ankle height and Ray is the reason it is going to come out. |
| What the set does that the line cannot | A dependency graph is a chart, and `ANGLE_TAXONOMY.md` bans anything that needs a chart. One outlet is the same information as a chart and it is funny, because the absurdity is the concentration and concentration is a shape. The lights going out object by object is the escalation, prebuilt. |

## How to find the world, in three questions

1. **Where does the MECHANISM physically happen?** Not where the victim is
   standing. Where the decision gets executed. The victim's kitchen is a place;
   the sorting belt is the mechanism.
2. **What is the smallest space that contains the whole mechanism?** Sixty
   seconds cannot travel. If the world needs two locations to explain itself, it
   is not the world, it is a sequence, and there is no room for one.
3. **Can you OPERATE it, ESCALATE it, and BREAK it on screen?** A world you can
   only look at is a backdrop. A world with a lever, a dial, a belt, a chute or a
   plug is a set, because a set is a thing that can get worse.

If all three answers arrive, that is the world. If question three fails, go back
to question one; you have found a location, not a mechanism.

## The world is not a costume for the Institution

`CAST_BIBLE.md` re-dresses the Institution per episode: an insurer, an airline, a
landlord, a platform, same silhouette, new livery. That is a costume rule and it
stays. It is NOT the world rule. The Institution in an airline livery standing in
a blank room is still a blank room. The livery says who; the world says what they
did.

---

# THE SIX VISUAL MOVES

The same status as the six moves in `COMEDY_CRAFT.md`. Steal the engine.

### 1. THE SIGHT GAG
A joke that exists entirely in the picture and survives the sound being off.

It lands because the platform serves this show muted and because a viewer who
laughs at something nobody said out loud feels like they caught it rather than
were told it. That feeling is the share. `AUDIENCE.md`: "if the joke needs the
audio it does not exist."

Minimum one per episode, and the run is not done until someone can name it.

### 2. VISUAL ESCALATION
The same image, three times, worse each time. The rule of three, in pictures.

It lands for the reason the spoken rule of three lands, two establish a pattern
and the third breaks it, with one enormous advantage: **it costs zero runtime.**
It happens UNDER dialogue that was going to be spoken anyway. In a sixty second
show, free is the only thing there is.

### 3. SCALE REVERSAL
Draw the enormous thing small or the small thing enormous, and let the frame do
the arguing.

It lands because outrage is a size judgement and the eye makes size judgements
faster than the ear makes moral ones. A $35 fee drawn as a building. A quarterly
earnings beat drawn as a coin. The harm drawn at human size next to a cause drawn
at the size of a keystroke, which is also the fix `COMEDY_CRAFT.md` prescribes
for irony pointing the wrong way.

### 4. LITERALIZED METAPHOR
The euphemism, drawn as its literal meaning, played straight.

"Guest experience adjustment" is a hand taking a bag out of another hand.
"Negative patient outcome" is a bed with nobody in it. "We have updated our
pricing to better serve our members" is a hand moving a number up while the
member watches.

**This is the highest-value move the show owns**, because the euphemism is
already sourced, already verbatim, and already the strongest angle in the
taxonomy. It costs no invention. Draw exactly what they said, and the gap between
the words and the picture does everything.

Do not editorialize the drawing. A cackling executive kills it. The politeness is
the menace, on screen exactly as in the voice.

### 5. THE REVEAL
The camera knew something the viewer did not. A pull back, a pan, a door opening,
a light coming on.

It lands because it retroactively rewrites everything already seen, which is the
only way to make second 50 feel like it earned second 5. One per episode, at most.
Two reveals means the first one did not matter.

The button is its natural home: pull back off the document and find what the
document is sitting on.

### 6. WRONG-OBJECT SUBSTITUTION
The prop that should be there is replaced by the thing it actually is.

The ambulance is a taxi with a meter running. The denial letter comes out of a
machine that only has one stamp. The customer service line is a hold-music box
with no wires going anywhere.

It lands because it is the visual form of hyper-specificity: it makes a claim
about what the thing REALLY is, and a claim is funnier than an observation. It
also has a hard constraint. The substitution has to be defensible against the
fact-check, because a picture asserts as loudly as a line. Case 0002 cut a claim
in prose and the board drew a badge that taught the viewer the cut claim anyway.
Draw the rule, not the part.

---

# ILLUSTRATES vs ACCOMPANIES

The single distinction this whole file is built to enforce.

An image that ACCOMPANIES a line sits next to it and is not wrong. An image that
ILLUSTRATES a line carries meaning the line does not, so that removing the image
removes information.

Three tests. Every shot passes all three or it is not a shot, it is wallpaper.

### The swap test (the hard one)
Take the image from shot 4 and put it under line 9. Does the episode break?

If nothing breaks, both images were accompanying. **An illustrating image is not
portable.** This is a mechanical test, it takes ten seconds, and it fails most
boards this show has produced.

### The mute test
Kill the audio and the captions. Can a stranger say what the mechanism was?

Not the topic. The mechanism. "Something about insurance" is a fail. "They
re-sorted his purchases so more of them would bounce" is a pass. The show is
watched muted; this is not a stress test, it is the normal viewing condition.

### The subtraction test
Say out loud what the picture knows that the line does not say.

If the answer is nothing, delete the shot. There is now a hole where it was, and
the hole is the actual assignment. A shot that can be deleted without loss was
never doing work, and it was taking up one of the episode's visual events
the episode is allowed.

---

# WHY TWO PEOPLE TALKING IS A PODCAST WITH DRAWINGS OVER IT

The show has two voices. That is a CASTING decision, not a format. Nothing about
having two characters implies that the picture is those two characters, facing
each other, in a space that is not doing anything.

Four reasons the floating two-shot kills an episode:

1. **Nothing accrues.** The frame at 0:10 and the frame at 0:50 are the same
   drawing. A viewer who cannot see that time has passed has no reason to believe
   anything is coming.
2. **The eye has nothing to do, and the eye leaving is the scroll.** The only
   number the platform ranks on is watch-through. A static frame is a standing
   invitation to check whether the next video is better.
3. **It hands the entire load to the writing**, and `COMEDY_CRAFT.md` opens with
   the admission that the writing is the weakest thing in this machine. Staging
   everything as dialogue is choosing to compete on the one axis where this
   machine is worst.
4. **It makes the show generic.** Two figures against a gradient is every AI
   channel that will be dead by spring. The world is the only thing here that
   cannot be cloned in a weekend.

### The budget, and it is a hard number

**No more than one third of the runtime may be the cast talking to each other in
a space they are not operating.** Twenty seconds of a sixty second episode, and
that is a ceiling and not an allowance.

Never in the first six seconds, because the first second is the whole audition
and a two-shot is the least specific image available. Never on the button,
because the button is the receipt.

A two-hander beat is legal and sometimes correct: a held reaction on a silent Ray
is free runtime and the panel keeps asking for more of it. What is illegal is a
two-hander beat where the SET is doing nothing. Put the conveyor behind them and
the same beat is a shot.

---

# SHOT RHYTHM OF A SIXTY SECOND SHORT FILM

### What counts as a visual event
Something a viewer could describe afterward that was not true a moment before.

- New object enters or leaves the frame. YES.
- A quantity on screen changes. YES.
- A scale change, a reveal, a light going out, a part detaching. YES.
- A face changing register. YES, and it is the cheapest one available.
- A cut. NO, not on its own. Cutting between two shots of nothing is nothing,
  twice.
- A camera push, a parallax layer, an ambient drift. HALF. Motion is not an
  event; the camera has to arrive somewhere.

### The numbers

| | |
| --- | --- |
| Distinct visual events in 60s | **18 minimum, 26 comfortable.** One new thing on screen every 2.3 to 3.3 seconds. |
| Longest any single image may hold | **5.0s** hard ceiling, and **2.5s** inside the first fifteen seconds. Treat 4.0s as the number to aim at. |
| Events before the wordmark stamps at ~2s | **at least one**, and it is the fact drawn. |
| Runtime as a floating two-shot | **20.0s maximum.** |
| Reveals | 1 |
| Escalation ladders running under dialogue | at least 1, of at least 3 steps |

**These numbers were WRONG and they contradicted the gate that enforces them.**
Corrected 2026-08-02, found by the director in the first live Phase 4.4: this
table said 12 to 16 events per 60s and `scripts/visual_check.py` refuses
anything under 18. The two were mutually exclusive, so a director who followed
the doc exactly would have built a board the gate rejects, and a director who
followed the gate would have been amber against the doc no matter what it drew.

The gate is right and the doc was guessing. Case 0002 has about 12 events per 60
seconds and the owner called it two people doing nothing, which means 12 is not
the floor of acceptable, it is a worked example of the failure. A threshold at
12 would have passed the episode this whole phase exists because of.

So: **when a doc and an executable gate disagree, the GATE is the spec.** A
number in prose has never been tested against an episode. A number in a gate has
a self-test and a fixture and has refused something. Fix the doc.

The old ceiling of 16 came from a real worry, and the worry survives even though
the number did not: above some rate nothing is allowed to land and the pauses
`COMEDY_CRAFT.md` calls for have nowhere to sit. That ceiling is a matter of
WHERE the events fall, not how many there are. Eighteen events with three of
them inside one second is frantic; twenty-six spread against the dialogue is a
film. Use the ladder rule below rather than a cap.

The flow critic's 2.5 second dead-air rule is the FLOOR, the absolute worst that
is survivable. Five seconds of a held image is the gate's ceiling and four is
what a director should be aiming at, and the difference between those numbers is
where the craft is.

### The ladder escalates
Order the events so the last third has the largest ones. An episode whose biggest
image is at 0:12 has told the viewer at 0:13 that it is over.

### The first image
The first image is the FACT, drawn. Not a title card, not a logo, not an
establishing wide, not two people about to start talking. `BRAND_BIBLE.md` puts
the wordmark at 2s for exactly this reason, and giving the first two seconds to a
two-shot spends the only guaranteed attention the episode gets on the least
specific frame it contains.

---

# THE ANTI-PATTERNS

### THE PLACE INSTEAD OF THE MECHANISM
A snowfield, a street, an office, a room. Any of them can be beautiful and none
of them illustrates anything. If the set could serve a different story with a
palette swap, it is a place. This is the founding defect and it is the one to
check first.

### THE ILLUSTRATED NOUN
The line says airline, the picture draws an airplane. The line says bank, the
picture draws a bank.

This is the visual form of explaining the joke, and it is banned for the same
reason: the audience is faster than the board. Drawing the noun that was just
spoken adds zero information and consumes an event that could have been
something. Draw what
the noun DID.

### THE FLOATING TWO-SHOT
Covered above. It is listed again here because it is the failure that shows up
when a board runs out of ideas at second 30, and knowing that is when it happens
is most of the defence.

### THE UI SCREENSHOT
Drawing a phone, a chat window or an app screen, and putting the joke in text
inside it. The joke is then a caption inside a picture of a caption, the frame is
unreadable at thumbnail size, and the show has burned-in captions already.

The exception is the button, where the real document is the point and legibility
at 1080x1920 is a gate.

### BUSY IS NOT ACTIVE
Parallax, drifting particles, a slow push, a shimmer. All of it can run for sixty
seconds while nothing happens. Case 0003's Orbit ran at an amplitude of 96px and
was simply invisible; it cost a render and changed no pixel a viewer could name.
Motion that cannot be described afterward is not an event, and adding more of it
is how a board convinces itself a static episode is moving.

### THE PICTURE THAT ASSERTS A CUT CLAIM
A prose guard does not bind a storyboard. If the fact-checker cut it, the board
cannot draw it, imply it, badge it or label it. This has already happened once.

### THE INSTITUTION WITH A FACE
The hardest rule in the show and the one a well-meaning board violates most,
because a face is the easiest way to make a shot legible. No expression, no eyes,
no reaction, nothing to negotiate with. It emits: policy text, hold music, an
automated line, a form. The moment it can emote it becomes a villain with
opinions instead of a process working as designed, and the process is the point.

---

# THE ROOM PROTOCOL

Every room in this show, the producer room and the director room included,
follows this. It exists because of a specific finding and not because argument
sounds impressive.

**The finding.** The July 2026 multi-agent-debate survey (arXiv 2607.26212) finds
that the field settled on fully-connected debate and majority voting by
convention rather than by comparison, and that the documented failure modes are
conformity, cost and degeneration. Other 2026 work finds debate UNDERPERFORMS a
single strong model when the agents share a base model, because the panel
collapses toward the majority rather than toward the truth.

So five Claude subagents with different system prompts, agreeing politely, is not
twenty minds. It is one mind billed five times, and it is WORSE than the single
agent it replaced, because the agreement reads as corroboration.

The value of a room is not the number of voices. It is anti-conformity
enforcement and genuine opposition of MANDATE. Design rooms where the producer
wants a film, the director wants a picture, the writer wants a line and the
devil's advocate wants it dead, and none of them can get what they want by
agreeing.

Four rules. Every room agent implements all four, and returns them in its output.

1. **A round in which everyone agreed on the first pass is REJECTED.** It is
   re-run with the positions made explicit and the devil's advocate forced to a
   KILL-level objection. First-pass consensus is evidence of conformity, not
   evidence of quality.
2. **Every position is tagged FACT, INFERENCE, ASSUMPTION or UNKNOWN.**
   FACT resolves to a claim-id in `claims.json` or to a file in this repo.
   INFERENCE follows from a FACT and names which one. ASSUMPTION is a judgement
   call held with no support, and most creative positions are these; saying so is
   the point. UNKNOWN is an admission and is more useful than a confident guess.
3. **Every verdict ships with its KILL CRITERIA**: the condition that would
   invalidate it. "This plan is wrong if the fence reads as a prison instead of a
   network." A verdict with no kill criteria is a preference wearing a verdict's
   clothes, and it gives the next phase nothing to test.
4. **Return a SPLIT rather than manufacturing consensus.** When a room does not
   converge, it says so, names both positions and hands the decision up. An
   averaged verdict is the blandest member of the set, which is the exact
   opposite of what a room is for.

Unresolved dissent travels DOWNSTREAM. It is not deleted when the decision is
made. The board should know what the devil's advocate still thinks, because that
is the fastest place to look when the render turns out flat.
