# THE COMEDY BIBLE

The show's brain for WRITING. `DIRECTING.md` owns what is on screen; this owns
whether there is a joke on it.

Written 2026-08-03 after the owner watched case 0003 and said "It wasn't funny",
"it made no sense", "there wasn't anything like coherent about it", and asked for
a comedic lane: "raunchy, pushing the boundary, like south park or Dave
chappelle, I also like sophisticated".

Everything here is either sourced to a practitioner or marked as our own
inference. Do not add taste to this file. Add mechanics.

---

## 0. THE LANE

**Smart filth.** Rude enough to earn the click, precise enough to survive the
comments.

The two halves are not a compromise between each other, they are a trade:
- the RUDENESS buys attention, which precision alone never will
- the PRECISION earns the second watch and makes the account unkillable

Case 0003 spent the precision and never bought the attention. It was careful. A
careful show about institutional cruelty is a press release with a cartoon on it.

**What the show is, one sentence, and everything downstream is bound by it:**

> A 60-second animated bit in which a real institution does something genuinely
> insane TO RAY, he cannot get out of it, and the proof is on screen.

It is a BIT, not a report. A report states a true thing with attitude. A bit has
a premise, an escalation, a turn and a tag, and it commits totally.

**The fact is the PREMISE of the bit, not the payload.** That single relocation
is the whole overhaul. Phase 2 does not soften for it and never will.

---

## 0.5 THE POV, AND THE THESIS

**Owner, 2026-08-03, and this is the most load-bearing sentence anyone has
written about this show:**

> "your character arc like pov I think is the average American, and how we are
> going through life and what is happening here in the US, as it gets crazy here,
> and things are painted normal but insane things are happening every day"

Three things in that, and each one settles a question that was open.

### 0.5.1 The POV is THE AVERAGE AMERICAN. Not a commentator.

Ray is not a host, a journalist, a satirist or a guy with a podcast. **He is a
person this is happening TO.** He did not choose the subject; the subject arrived
in his mail.

This kills the failure mode that has produced every weak episode so far. A
commentator has opinions ABOUT a thing and can only ever generate commentary. A
person LIVING it has a want, an obstacle and a stake, which is the difference
between a scene and a segment. It is also Harmon's pity gate: the audience lands
on whoever they can feel sorry for, and you cannot feel sorry for a narrator.

**Ray is never the smartest person in the episode. He is the one being charged
for it.**

### 0.5.2 The arc is ONGOING. This is a series, not 365 sketches.

"How we are going through life" is a continuing condition, not a topic. The show
is not a numbered list of unrelated outrages; it is **one guy's accumulating
experience of living in a country that keeps getting stranger while insisting it
is fine.**

Consequences that are now rules:

- **Ray never wins, and never learns.** Harmon's TV circle beat 8, "I must admit
  the futility of change." If Ray solved it, the condition would end and the show
  would end with it.
- **He does not reset to zero.** He is not surprised in episode 200 the way he was
  in episode 2. The wear accumulates, and that wear IS the character.
- **The Institution is one antagonist wearing different uniforms.** A landlord's
  screening service, an insurer, an airline and a hospital billing department are
  the same entity to Ray, because to a person on hold they are.

### 0.5.3 THE THESIS: painted normal, actually insane

> **Things are painted normal but insane things are happening every day.**

That is the show in one line, and it is not a mood: it is a MECHANISM, and it is
the same mechanism as everything else in this file.

- It is the CONNECTOR (section 10). One thing, two interpretations: the document
  reads as routine and says something deranged.
- It is Carlin's soft language: the paint IS the euphemism.
- It is why the fact gate licenses the crudeness. **We are not claiming the world
  is insane. We are quoting the paint and letting the viewer see through it.**

**THE PAINT IS THE ANTAGONIST.** Not the fee, not the denial, not the number. The
calm, competent, well-designed surface that presents an atrocity as a normal
Tuesday. The hold music. The word "unfortunately." The cheerful onboarding
illustration on the letter that ruins your year.

Which gives every episode a mandatory image:

> **THE PAINT AND WHAT IS UNDER IT MUST BE IN THE SAME FRAME**, with no verb of
> interpretation between them. Never "which means." Never "in other words." Put
> the reassuring sentence and the insane consequence side by side and stop
> talking.

Ray's whole function is to be the only one in the frame who has not agreed to
pretend the paint is the wall.

---

## 1. THE FIRST LAW: BUT / THEREFORE

Trey Parker, NYU Tisch guest lecture (Prof. Ken Liotti's "Story-Telling
Strategies", filmed for mtvU's *Stand In*). Note the provenance: this is
routinely misattributed to the documentary *6 Days to Air*. It is the NYU class.
Transcript: https://speakola.com/arts/matt-stone-trey-parker-nyu-writing-class-2014

> "We can take these beats, which are basically the beats of your outline, and
> **if the words 'and then' belong between those beats, you're fucked.**
> Basically. You've got something pretty boring."
>
> "**What should happen between every beat that you've written down, is either
> the word 'therefore' or 'but'.**"
>
> "**Literally we'll sometimes write it out to make sure we're doing it.**"

Matt Stone, same session:

> "it's those two, 'but' 'because', 'therefore' that gives you the causation
> between each beat, and that's a story."

Two operational details that most summaries drop and that we depend on:

1. **It is a written artifact, not a vibe.** "Literally we'll sometimes write it
   out." That is what makes it gateable, and it is why `beats` is now a required
   block on the locked script.
2. **The scene rule is separate and additive.** Parker: "Each individual scene
   has to work as a funny sketch." Every beat must be causally linked to its
   neighbour AND work standalone. A causally perfect chain of unfunny beats
   fails. A sequence of great sketches joined by "and then" also fails.

### 1.1 Why a label is not enough, and the three tests

A writer can label any two beats THEREFORE and nobody can disprove it. So the
connective is checked, not trusted. `scripts/beat_check.py` runs the lint half;
the flow critic runs the judgement half as three yes/no questions.

**Test A, the deletion test.** Delete beat N. Does beat N+1 still make sense?
If yes, the link was "and then." FAIL. A real THEREFORE leaves N+1 impossible or
motiveless.

**Test B, the swap test.** Swap beats N and N+1. Does the script still parse?
If yes, they are not causally linked. FAIL. A true chain is order-rigid.

**Test C, the named-expectation test.** A BUT requires that beat N created an
expectation which beat N+1 violates. Name the expectation in one clause, under
ten words. If you cannot, the BUT is decorative. FAIL.

**Banned connectives, checked as literal strings:** `and then`, `meanwhile`,
`also`, `at the same time`, `later`, `next`, `then`. Allowed: `THEREFORE`, `BUT`.

`meanwhile` is the B-plot connective. It is legitimate in 22 minutes because the
plots converge causally later. **In 60 seconds there is no meanwhile. One plot.**

---

## 2. THE SHAPE OF A 60 SECOND EPISODE

**This replaces the old five-beat shape, which was the problem.**

The retired shape was: hook / the turn / Ray finds out / the Institution answers
/ the button. Run the deletion test on it. Delete "Ray finds out" and the button
still lands. Delete "the turn" and nothing breaks. Nothing in it causes anything
else in it.

That is a REACTION SEQUENCE, and a reaction sequence structurally cannot produce
anything but commentary. Two independent blind funny reads returned "verified
outrage recited with attitude" and "a fact with a tone of voice." The bible was
manufacturing the defect the gate kept catching.

### The causal six

| # | sec | what happens | link in |
| --- | --- | --- | --- |
| 1 | 0-6 | Somebody does the ordinary, correct thing. The premise is normal. The first image is the fact drawn. | — |
| 2 | 6-15 | The mechanism does exactly what it says it does. Literally, immediately, with no malice. | **THEREFORE** |
| 3 | 15-26 | There is an obvious remedy and Ray takes it. The audience believes it will work. | **BUT** |
| 4 | 26-40 | **The remedy IS the mechanism. The escape route is the trap.** The number lands here. | **THEREFORE** |
| 5 | 40-52 | Ray refuses it and escalates, or drops the bit entirely for one plain sentence. | **BUT** |
| 6 | 52-60 | The document, which was true from beat 1. Ray does not win. | **THEREFORE** |

**Beat 4 is load-bearing and the old shape did not have it.** It is the beat
where the argument gets EXECUTED instead of stated. In *HUMANCENTiPAD* the rescue
from the EULA is performed by signing another EULA; nobody says the thesis, the
plot IS the thesis. Our equivalent: the dispute process is the thing that
generates the error, the fee for the fee, the appeal that requires the document
it denied you.

**Alternate the connectives.** Parker's own example alternates. All THEREFOREs is
a ramp and reads mechanical; all BUTs is obstruction and reads like a sketch that
will not end. In six beats: at least two BUTs and at least two THEREFOREs.

**Every one of the six must work as a joke on its own.** A beat with no laugh
line and no sight gag is a connective, and connectives are what "and then" looks
like when it is hiding.

---

## 3. THE TWO-HANDER: THEY MUST WANT DIFFERENT THINGS

**Comic tension comes from two characters who want incompatible things in the
same scene, not from two characters who notice the same thing.**

This is the writing-side answer to "two people talking and doing nothing." The
visual side is in DIRECTING.md and it was only ever half the problem.

**Ray and Dee currently AGREE.** They share an observation, take turns being
appalled, and neither can lose. Two people who agree cannot generate a scene no
matter how well it is drawn. The simulated viewer on case 0003 said it exactly:
"he has been talking constantly, so I do not know what he means by standing
here." Ray had no situation. He had a subject.

The model is *Cartoon Wars*: Kyle and Cartman in one car to one destination, with
opposed objectives, and one of them concealing his real motive. Every line does
work because both are trying to win.

**Required on the locked script, and the gate fails the attempt if the two wants
can be satisfied by the same outcome:**

```
ray_wants:     <one line>
dee_wants:     <one line>
incompatible:  <one line naming why both cannot be satisfied>
```

Legitimate oppositions for this cast:
- Ray wants satisfaction; Dee wants off the phone.
- Ray wants it to be an outrage; Dee has professional pride in the number being
  correct.
- **Strongest:** Ray wants to fight the Institution; Dee has already made peace
  with it and needs Ray to make peace too, so she can stop feeling like a
  coward. This makes Dee DEFEATABLE and gives the Institution an ally in the
  room.

### 3.1 We have no Randy, and that is why nothing escalates

South Park keeps the kids proportionate and lets an adult commit absolutely.
Randy exists structurally so the sane characters do not have to become absurd for
the episode to get somewhere. Parker calls him "the biggest dingbat in the entire
show."

We have two sane characters, so escalation has nowhere to live and the episode
can only get LOUDER, not BIGGER.

**The fix that does not add a fourth voice: the Institution escalates.** Not in
emotion, which is banned and stays banned. In SCALE and in CHEER. It goes from
euphemism to enthusiasm. It gets more helpful as the situation gets worse. That
is exactly what the Margaritaville bank manager does and he never has a face.

`institution_faceless` is untouched: no eyes, no mouth, no reaction, no
negotiation. Escalating volume, scale and cheerfulness are not emotions.

---

## 4. HOW TO ESCALATE: RIGOR, NOT INVENTION

South Park does not escalate by making each beat crazier. It **takes one real
mechanism literally and refuses to stop applying it.** The absurdity is arrived
at by rigor.

- EULAs are real, unread and binding. The show simply enforces one.
- A bank really does convert your deposit into instruments you do not
  understand. The show shortens the interval to zero.

**This means we already own the South Park premise engine: it is the fact-check
gate.** The real mechanism is handed to us by the primary document. What we have
not been doing is following it past the point where it stops being reasonable.

**The escalation question is never "what would be funnier here."** It is:

> **Who has to be right for this to keep going, and what happens if they are?**

That question converts a verified mechanism into a plot instead of a complaint.
It belongs in angle hygiene, not just here.

---

## 4.5 CRAZY SCENES: THE STAGING COMMITS AS HARD AS THE WRITING

**Owner:** *"I also like south park how its not afraid to make crazy scenes and
break boundaries and really make fun of people and things."*

**CRAZY SCENES is the note, and it is one we have been failing quietly.**

Our world-of-the-story law says stage the episode inside the mechanism, and case
0003 obeyed it: a count room, tasteful, apt, legible. It was a good METAPHOR and
it was not an insane IMAGE. South Park does not stop at apt. It builds a giant
robot Barbra Streisand, a human centipede made of an iPad, a town buried in its
own bullshit. The picture is as deranged as the premise.

**The rule: LITERALISE THE MECHANISM UNTIL IT IS PHYSICALLY ABSURD.**

This is section 4's escalation-by-rigor principle applied to the IMAGE instead of
the plot. Do not ask what would be funnier to draw. Ask:

> **If this mechanism were a physical object obeying its own rules in a room with
> a man in it, what would the room look like by the end?**

Worked, against our own shipped episode:

| the mechanism | what we drew | what the rule demands |
| --- | --- | --- |
| the report copies one case nine times | nine cards on a floor, tidy | Ray waist-deep and RISING, the pile lifting him toward the ceiling, only his head showing by the button |
| a dispute returns INVALID | a card comes back stamped | the chute fires it back so fast and so often that it builds a second pile out of refusals |
| a fee compounds | a number on a counter | the counter physically outgrows its housing and cracks the wall |

**Three ways to build a crazy scene, in order of cost:**

1. **SCALE VIOLATION.** The document is furniture-sized. The machine is a
   building. The person is a detail in the corner of his own paperwork. Cheapest
   and most reliable, and it is already native to our kit.
2. **ACCUMULATION.** The thing keeps happening and the evidence PILES UP in
   frame, physically, until it dominates. This one doubles as the motion budget,
   because a growing pile is continuous movement that also does comedy work.
3. **PHYSICAL CONSEQUENCE.** The absurd process moves a body. Ray is lifted,
   buried, carried, sorted, filed. The moment the mechanism touches him
   physically, the episode stops being about a document.

**THE TEST, and it is now a question the director room must answer on the record:**

> **What is the one image from this episode that somebody would describe to a
> friend?**

If the answer is "two people in a room discussing a document", there is no crazy
scene and the board is not finished. Case 0003's honest answer was "a wall of
identical eviction cards", which is why that beat is the only one either
simulated viewer called impressive. **One such image per episode, minimum.**

**The fact gate is not in tension with this and never has been.** Ray buried in a
pile of identical filings asserts nothing false: the record says the case was
duplicated. The PILE is a picture of a true thing. What we may never do is invent
a fact, and drawing a true fact enormous is not inventing it. Being timid with
the picture buys us nothing legally and costs us the show.

---

## 5. THE MOVES

### 5.1 The deadpan functionary says the worst thing
The worst fact in the episode is spoken by the character with the LEAST affect,
in the politest available register, and that character is not upset. The comedy
is entirely in the gap between content and delivery.

> "We can put that check in a money market mutual fund, then we'll re-invest the
> earnings into foreign currency accounts with compounding interest **aaaand
> it's gone.**"

**Our Institution has the voice for this and is not carrying the worst fact.** On
case 0003 it delivered the euphemism while Dee delivered the number. **Swap
them.** The Institution gets the number.

### 5.2 Escalating identical repetition (NOT the rule of three)
These are two different devices and they argue different things.

- **Pattern-break three:** establish, reinforce, SURPRISE. Argues *the world is
  absurd.*
- **Escalating identical three:** the same line, three times, louder and bigger,
  no variation. Argues *the world does not care that you noticed.*

For an institutional-villain show the second is more often right. Shot spec:
**identical framing on all three.** Nothing changes but amplitude and the scale
of the object. The locked frame is what makes it read as a machine.

### 5.3 Sincerity plus crudity
The single strongest anti-punching-down device, and it is a technique rather than
an exception.

*All About Mormons* ridicules a religion for twenty minutes, then the sincere
believer drops the bit and speaks plainly: "All I ever did was try to be your
friend... You've got a lot of growing up to do, buddy. **Suck my balls.**"

Four separable mechanics:
1. **The doctrine is destroyed and the believer is not.** The show proves it can
   tell the difference, and that is what pays for the cruelty.
2. **The target flips onto the mocker in the final beat.** Costs nothing, lands
   harder than the original joke.
3. **Register switch as amplification.** After sustained absurdity, one plain
   declarative sentence is the loudest thing available.
4. **The crudity is punctuation, not content.** Three words at the end. It is
   what stops the speech being a moral.

**ANTI-PATTERN: sincerity that is not undercut within one beat is a SERMON**, and
a sermon is "agreement is not comedy" wearing a serious face. Beat 5 is where Ray
may drop the bit; beat 6 must undercut it.

### 5.4 Reveal in the institution's own frame language
When the absurd object is revealed, shoot it in the visual grammar of whatever
produced it: a product shot, a keynote slide, a rate card, an onboarding
illustration, a compliance poster. **Never a horror reveal.** The frame does the
satire and nobody has to say "and they were proud of it."

The shocked reaction comes SECOND, on a cut, after the wide has held.

### 5.5 One change, then hold
South Park's reaction shots work because they are held and nearly static: one
register change, then nothing, for a beat longer than is comfortable.

**One change, then hold. Not a performance.** A pause needs a face that has
already changed and then stopped, or it reads as dead air rather than as a held
reaction. This is the difference between a 2.5s hold that is funny and one the
flow critic calls dead air.

### 5.6 Let one music change carry the argument
*All About Mormons* delivers the entire editorial position of a twenty-minute
sequence through one verse of a backing vocal changing from "dum dum dum" to
"smart smart smart" and then reverting. Nobody states it.

We own the audio pipeline and have never used this. A cheerful bed under the
worst fifteen seconds, with exactly one change at the moment the argument lands.

---

## 6. NO SACRED COWS

**Owner, 2026-08-03, and this is doctrine, not a mood:**

> "we can cover ANY topic, we are beholden to NO single POV, and we will DUNK on
> everyone, and make fun of ANYTHING that is funny. this is a bold show."

Take that literally. It is also, word for word, what the show we are modelling
on says about itself. Kyle, in *Cartoon Wars Part II*, which is South Park
stating its own constitution in text:

> "If you don't show Muhammad, then you've made a distinction between what is
> okay to poke fun at and what isn't. **Either it's all okay or none of it is.**"

Parker: "Everyone can be made fun of, and everything should be made fun of if you
do it in the right way."

### 6.1 ANY TOPIC. There is no list of subjects we avoid.

Politics, religion, ideology, celebrity, culture war, industry, sport, science,
the media, our own audience, and anything else that is funny. **There is no
subject this show will not go at**, and any run that ducks a story because the
topic is uncomfortable has failed at the job, not protected the channel.

A previous version of this file quietly ruled out "the biggest story of the
week" on the grounds that it was usually political. That was cowardice with a
policy voice, and the owner caught it. It is deleted.

### 6.2 NO SINGLE POV. We are on nobody's team.

Not centrist, which is its own smug position. **Unaligned.** We have no side to
protect, and that is the source of the licence rather than a limit on it: a show
that is not carrying anyone's water can hit everyone, and a partisan show
structurally cannot. It has to keep half the field safe.

Parker's staging, from NPR, and read it as a camera instruction rather than a
disclaimer:

> "we take an issue, and we sort of always have **two sides about to kill each
> other over it and the boys in the middle** going, doing fart jokes and saying,
> who cares?"

Both sides in frame. **Both get hit.** The POV character is the person stuck
between them who did not ask to be there, which is Ray, always.

The test is positive, not negative. Not "did we avoid advantaging a party" but
**"is everyone in this frame taking a hit, and is Ray a hostage rather than a
partisan?"**

### 6.3 The ONE line, and it is craft rather than caution

We punch at **power and self-importance.** Institutions, companies, public
figures acting in public, movements, ideologies, and the certainty of anybody
enjoying being right. All of it, all the time, as hard as we can.

We do not punch at the powerless person inside the system. The clerk, the nurse,
the driver, the applicant, the call-centre worker.

**This is not squeamishness and it is not a hedge. It is that punching down is
the WEAK version.** Anybody can mock somebody with no power; it takes nothing,
it is not brave, and it is not funny. The whole charge of a dunk comes from the
size of what you are dunking on. Aiming at a hostage does not make the show
bolder, it makes it smaller, and it hands anyone who wants us dead the only
weapon that actually works.

There is one diagnostic and it comes free with the fact gate: **punching at the
vulnerable requires exaggeration to work, and punching at power works better
verbatim.** If a line needs the fact stretched to land, it is aimed the wrong
way, because power's actual conduct is always already sufficient.

When the show DOES aim at an ordinary person, it turns the gun around in the last
beat. That is a technique, not an exception. *All About Mormons* ridicules a
religion for twenty minutes and then hands the sincere believer the last word:
"You've got a lot of growing up to do, buddy. **Suck my balls.**" The doctrine is
destroyed and the believer is not, and the person who spent the episode being
smug is the one indicted.

### 6.4 The two bans that stay, and why they cost us nothing

**No slurs. No hate. No sexual content. No harassment of a named private
person.** These are BANS and not preferences. They are not about taste and they
are not about what is funny; they are the four things that end a channel
outright, and a dead channel dunks on nobody.

None of them constrains a single joke worth making. A slur is not an edgy
version of a punchline, it is a substitute for one.

**Everything is sourced.** This is the other half of the boldness and it is the
half people miss. Savage and sourced is unanswerable. **The reason we can dunk
this hard is that nothing we say can be argued with**, and the moment we ship one
thing that is not true, every enemy the show has made gets to dismiss all of it
at once. The fact gate is not a brake on the show. It is the thing that lets the
show be this rude and survive.

### 6.5 The empirical note, for the record

Chappelle's *The Closer* drew a GLAAD statement and a Netflix employee walkout in
2021, and he absorbed it on two decades of accumulated standing. We have none.
That is not an argument for being timid about topics; he was right that the topic
was fair game. It is an argument for being **precise about direction**, because
precision is the only standing a new account has.

## 6.6 FEARLESSNESS IS A CRAFT REQUIREMENT, NOT A RISK POSTURE

**Owner:** *"I like how Dave Chappelle never feared any categories and didn't
fear getting cancelled."*

Take it, and understand WHY it works, because the reason is mechanical and it
makes fearlessness non-optional rather than brave.

**Fear shows up in a script as hedging, winking and pre-apologising, and all
three kill the joke independently of any safety question.**

Dean's model makes it exact. The laugh fires at the moment the AUDIENCE performs
the reinterpretation. A wink is the performer performing it for them. So:

> **A wink pre-spends the laugh.** If the script signals "I know this is edgy,"
> the target assumption never installs, and the punchline has nothing left to
> break.

That is why Chappelle's most dangerous material lands and a nervous version of
the same material dies. Not nerve. **Total commitment to the frame.** Clayton
Bigsby is played entirely straight: the correspondent is earnest, the Klansmen
are sincere, nobody in the sketch acknowledges the premise is absurd. The
absurdity is structural, and the audience does all the work, which is why they
laugh.

**The banned moves, and they are banned for comedy reasons:**

- "I'm just saying..." / "to be fair..." / "obviously not everyone..."
- A character signalling that a line was edgy
- Softening a verb to make a claim feel safer (that is also the move that ends
  channels: soften the CLAIM and you are lying, so kill the claim instead)
- Any line whose job is to reassure the audience that we are nice

**The Institution must never know it is in a comedy.** The moment it is arch,
sardonic or self-aware, it has winked. It is unfailingly polite and completely
sincere, and that is what makes it terrifying and funny at once.

Same for Dee. Her deadpan is not a flat delivery, it is **total commitment to a
frame in which the insane number is a normal number.**

The two bans in 6.4 are not fear and never were. They are the four things that
end a channel outright, and none of them has ever been the difference between a
funny script and a scared one.

---

## 6.7 THE INSTITUTION IS STUPID, NOT EVIL

**Owner:** *"I also like Rick and Morty how it has humor that highlights funny
stupid stuff in a funny way."*

This is a distinct register from satire and we should be running it constantly.
Satire says *look what they did to you.* This says *look how DUMB this is.* The
second one is funnier, it is more accurate, and it is far harder to argue with.

**The absurdity in our stories is almost never malice. It is banality.**

- Someone pressed paste twice.
- A field was the wrong type.
- Nobody owns the form.
- The remedy is under development.
- A number got rounded and a person lost an apartment.

**Nobody is in the room. That is the joke.** A sinister institution implies a
mastermind, which is flattering, arguable, and gives the audience someone to
imagine reasoning with. A STUPID institution is worse, funnier, and unfalsifiable,
because the paperwork proves it.

The Rick technique for delivering it: **be bored by your own mechanism.** The
explainer's attitude instructs the audience how much to care about the
machinery, and the answer is: not much. Contempt for the mechanism, attention on
the consequence. Our Institution's `[extremely fast]` tag is exactly this
instrument and it is underused.

**Where the two registers sit:**

| register | who carries it | the line it produces |
| --- | --- | --- |
| this is STUPID | Dee, and the Institution's own indifference | "It counted the same case nine times." |
| this is CRUEL | Ray, once, late | "So which one of those do I live in?" |

**Run stupid for most of the episode and cruel exactly once, at beat 5.** Stupid
is the engine; cruel is the payload. Leading with cruel is a lecture, and it is
the "agreement is not comedy" failure wearing a serious face. Arriving at cruel
after sixty seconds of stupid is what makes it land, because the viewer got there
first and you only had to stop talking.

---

## 7. ANTI-PATTERNS, the standing list

- **The reaction sequence.** Beats joined by "and then." The defect this file
  exists to kill.
- **Two people who agree.** No opposed want, no scene.
- **The fact as payload.** Delivering the outrage rather than trapping someone
  inside it.
- **Explaining the joke.** The line after the punchline that restates it.
  Mechanically refused by `script_check`'s restatement guard.
- **Sincerity without an undercut.** A sermon.
- **Escalating volume instead of scale.** Louder is not bigger.
- **The horror reveal.** Shoot it in the institution's own grammar instead.
- **A beat with no joke in it.** That is a connective wearing a costume.

---

## 8. THE SPINE: HARMON'S TV CIRCLE (not the film one)

Dan Harmon wrote the story circle in six Channel 101 tutorials.
https://channel101.fandom.com/wiki/Story_Structure_101:_Super_Basic_Shit

The famous eight beats are the FILM circle: "gets what they wanted... having
changed." That is the wrong one for us, because in TV the protagonist cannot
win or the show ends. Harmon wrote a TV variant in 105, and it is our show's
spine, already written, in 2010:

> 1. I
> 2. notice a small problem,
> 3. and make a major decision.
> 4. this changes things
> 5. to some satisfaction, but
> 6. there are consequences
> 7. that must be undone
> 8. **and I must admit the futility of change.**

Beat 8 is literally our law that Ray never wins. Adopt the 105 variant as
canonical. It removes the structural pressure that keeps pushing our buttons
toward a resolution the format forbids.

> "in both the sitcom and dramatic TV version of Star Wars, the Death Star
> stays. If not, the show would end."

**Our Death Star is the Institution. It stays.**

### 8.1 The plant has a timecode now
Harmon, 104: "the opposite of (8) is (4)... Why is this not Deus Ex Machina?
Because we earned it (4)."

We are allowed exactly one plant in sixty seconds. **Plant it at beat 4
(0:22-0:30). Pay it at beat 8 (0:52-0:60).** Geometry, not vibes.

### 8.2 Harmon's own permission to skip
> "Can you skip some of them? Yep. I do it all the time."
> "A confidently hand drawn, vaguely egg-shaped circle can be circular enough."

At 60s the load-bearing beats are 1, 2, 5, 6, 8. **Beat 4 is the first cut.**
Beat 7 compresses to a single shot: a cut back to Ray's face IS a return. Beat 3
can be a hard cut rather than a line.

### 8.3 THE PITY GATE, and it contradicts our old rule
> "The audience is floating freely, like a ghost, until you give them a place to
> land... **When in doubt, they follow their pity.**"
> Bouncing between POVs for "more than 25% of your total story" loses them.

Our retired shape opened on "the fact, stated flat, with no setup." That means
the audience spends the first five seconds with nobody to be, which is 8% of the
runtime as a ghost.

**The first thing on screen is a PERSON, not a document.** Open on Ray already
reacting, or on whoever got hurt. The fact arrives at beat 2. All POV settling
is finished by 0:15.

---

## 9. MAMET: WHY OUR TWO-HANDER IS BROKEN BY DEFAULT

David Mamet's 2005 memo to the writers of *The Unit*.
https://gideonsway.wordpress.com/2010/04/06/david-mamets-letter-to-the-writers-of-the-unit/

Three questions, of every beat:

> 1. WHO WANTS WHAT?
> 2. WHAT HAPPENS IF THEY DON'T GET IT?
> 3. WHY NOW?

> "the answers to these questions are litmus paper"

> "THE AUDIENCE WILL NOT TUNE IN TO WATCH INFORMATION... THE AUDIENCE WILL ONLY
> TUNE IN AND STAY TUNED TO WATCH DRAMA."

> "ANY TIME TWO CHARACTERS ARE TALKING ABOUT A THIRD, THE SCENE IS A CROCK OF
> SHIT."

**That last line is our show's default state.** Ray and Dee stand together and
discuss an absent Institution. By Mamet's rule that is broken before a word is
written, and it is precisely the demonstrated failure mode.

Three fixes, all cheap:

1. **Dee wants something FROM RAY in every beat**, she does not inform him. Not
   "the fee went up 40%." Rather: she needs him to stop, to sign, to shut up, to
   look. Same fact, delivered as a want.
2. **Get the Institution into the frame as the SECOND party, not the third.** Its
   on-screen emissions (the form, the hold music, the clause) are what convert a
   two-hander-about-a-third into a scene with an antagonist present.
3. **The silent-film pass.** Mamet: "THE CAMERA CAN DO THE EXPLAINING FOR YOU."
   Mute all three audio tracks. Would a viewer know who wanted what and who lost?
   If not, the script is doing work the frame should do.

Also banned by name: any line that is implicitly "AS YOU KNOW". On backstory,
Mamet's entire instruction is "FIGURE IT OUT."

---

## 10. IS THERE ACTUALLY A JOKE? (the mechanical test)

Greg Dean's joke anatomy. https://stand-upcomedy.com/glossary/5-joke-mechanisms/

- **Connector** = "1 thing with at least 2 interpretations."
- **Target Assumption** = "The expected interpretation of the Connector,
  established by the Setup to misdirect the audience."
- **Reinterpretation** = "The unexpected interpretation... that makes the Target
  Assumption's expected interpretation wrong."

**Our show has a permanent, free, pre-loaded connector: the document.**

| | |
| --- | --- |
| 1st story | a routine business document |
| target assumption | documents like this are normal, boring, produced in good faith |
| connector | the exact wording |
| reinterpretation | what the exact wording literally says |
| 2nd story | a functioning institution did this on purpose and sent it to you |

**THE CONNECTOR GATE.** Every episode names its Connector, Target Assumption and
Reinterpretation in the script header. **If you cannot name all three, there is
no joke, only a fact.** This is the mechanical answer to "is this funny or is it
just true", and the fact gate is what guarantees the connector is real. That is
why sourcing licenses crudeness: it is load-bearing on the JOKE, not just on the
lawyer.

---

## 11. TAGS, AND WHY WE HAVE ZERO

> A **tag** is "an additional punchline added to the end of a joke without
> requiring a new setup." Structure: setup > punch > tag > tag.

A tag reuses the SETUP. A callback reuses the PUNCHLINE. A tag is immediate; a
callback is delayed. Both hand you a laugh you did not pay setup time for, which
makes them disproportionately valuable at sixty seconds.

**We currently write zero tags.** One tag on the strongest punch costs about two
seconds.

**RULE: after every punchline, write three tags and keep the best one.** At this
length we cannot afford more setups, so tag density is the only lever that raises
laughs-per-second without raising runtime.

---

## 12. QUANTITY IS HOW QUALITY HAPPENS

Scott Dikkers, founding editor of The Onion:
https://blog.hubspot.com/marketing/the-onions-founding-editor-writing-rules

> "The Key to Quality is Quantity." "When you have six high-performing comedy
> writers coming up with 20 ideas each, you're gonna walk away with a dozen
> headlines that are just solid."

> "Concept is King." "Your concept... is the flag you're raising."

> "Only satire that angers or offends people will be remembered."

> "Cutting even a single syllable can make the joke punchier, better."

**The angle room converges far too early.** Require **20 candidate buttons
generated before any is evaluated.** Clown brain first, editor brain second,
never simultaneously.

---

## 13. LINE MECHANICS

### 13.1 The re-frame, five steps (Carlin's "soft language")
https://listeninghard.blogspot.com/2013/01/george-carlin-euphemistic-language.html

1. Quote the euphemism verbatim. Never paraphrase.
2. Say the plain version immediately after, **with no connective tissue.**
3. Escalate through the sequence in order, so the pattern is countable.
4. Land on the harm.
5. **Never state the thesis.** Carlin never says "euphemism enables neglect."

**GATE, regex-checkable:** in a re-frame beat the euphemism and the plain word
are ADJACENT with **no verb of interpretation between them.** Every instance of
"which means", "in other words", "translation:", "read:" is a wink and gets cut.

### 13.2 The punch word goes last
Seinfeld: "you got 'chimps,' 'dirt,' 'playing,' and 'sticks.' Seven words; four
of them are funny." "Text! It's fun to say. It's got that short, tight, got the X
in there, a little bite to it."

Joe Toplyn's analysis: shorter words draw more laughter, and **stop consonants
(B D G K P T)** are funnier because the interrupted airflow creates the surprise.

- **PUNCH WORD LAST.** The final word of a punchline carries the
  reinterpretation. If the sentence continues past it, cut the tail. Flag any
  punchline ending in a preposition, a pronoun, "though", "anyway", "or
  something", or a trailing subordinate clause.
- **PREFER the shorter word ending in a stop.** "Paste" beats "duplicate."
  "Bill" beats "invoice." "Cut" beats "reduction."

### 13.3 Breaking the rule of three
Four documented breaks, and the last is the best fit for us:

1. **THE TWO.** Stop at item two when it is the strongest fact you have. Often
   correct at 60s, where a third item costs seconds we do not have.
2. **THE LONG LIST.** Five or more, where the DURATION is the joke. Excellent
   fit for the Institution's clause read at `[extremely fast]`.
3. **THE FALSE THIRD.** The fourth breaks it. Expensive; rare.
4. **THE MISSING THIRD.** Announce three, deliver two, and **the third is the
   on-screen document.** This makes the button a punchline instead of a
   citation, and it is a rule-of-three, a plant and the mandatory receipt in one
   four-second move.

**ANTI-PATTERN:** three items of the same KIND is a list, not a triple. The break
must change category, not magnitude. Three escalating dollar figures is a
spreadsheet. Two dollar figures and a human consequence is a joke.

---

## 14. THE LAUGH LOCATION TEST

Chappelle walked away from his own show in 2004. The trigger, in his words: a
crew member laughed in a way that made him feel "someone was not laughing with me
but laughing at me," and to Oprah, "I was doing sketches that were funny but
socially irresponsible."
https://www.thefader.com/2016/07/29/skit-that-killed-chappelles-show

> **For every joke, name (a) who is laughing and (b) who they are laughing at.
> If (b) has less power than the viewer, the joke is broken regardless of whether
> the fact is true.**

Our ban list is about CONTENT (slurs, hate, sexual content, harassment). This is
about DIRECTION, and it catches what the ban list cannot see: a technically clean
joke whose laugh lands on a call-centre worker, a debtor, a patient, an
applicant.

Chappelle's own in-room version, from the *Sticks & Stones* epilogue: "if I can't
say in front of her, should I say this shit at all?" Operationalized: **name the
single most vulnerable real human implicated by the story and read the script
imagining they are watching.** Not "would they agree" but "does the show make
them the object."

**And the diagnostic that comes free with our fact gate:** punching at the
vulnerable requires exaggeration to work; **punching at power works better
verbatim.** If you had to embellish the fact to make the line land, you are
probably aimed the wrong way, because power's actual conduct is already
sufficient.

The counterexample, for the record and for FIELD_NOTES: *The Closer* (2021) and
the resulting GLAAD statement and Netflix walkout. Chappelle survived it on two
decades of accumulated standing. **We have none.** The house rule stays exactly
as written, and this is the empirical proof that it is not squeamishness.

---

## 15. WHO SAYS WHAT

- **The Institution gets the CLAUSE**, at `[extremely fast]`, politely,
  indifferent to whether you followed it. It is the correct mouth for mechanism
  because it is bored by its own explanation, which instructs the audience how
  much to care: not much.
- **Dee gets the NUMBER and the DATE.** She is the audience surrogate, and **a
  surrogate who explains is a lecturer.** Move mechanism lines off Dee.
- **Ray gets the reaction and the one plain sentence in beat 5.**

**ONE LAMPSHADE PER EPISODE, MAXIMUM, and never on the joke.** Overused
lampshading is the documented cause of Rick and Morty's weakest season: "almost
everything oversaturated with characters explaining it, leaving viewers with
nothing to ponder." This is the same rule as "never explain the compression."
