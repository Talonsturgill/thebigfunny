# The Cast

Three characters carry the whole show. They are FIXED. Staging, camera, palette
and set change every episode; the cast does not. That is not a compromise with
the variety law, it is how comedy works: the joke lands harder when you already
know who is about to say it.

The library mandate says the same thing in engineering terms, and it was written
before this show existed:

> reuse with fresh staging is the point of the library. Composition freshness
> comes from the storyboard fingerprint + camera + staging, not from re-drawing
> the cast.

---

## RAY — the Id

**The engine of the show.** Every episode is, structurally, Ray finding out.

Ray is **correct**. That is the single most important thing about him and the
decision that defines the register. He is not a fool whose overreaction is the
joke; he is the only person in the room saying the true and obvious thing while
everyone else performs composure. The comedy comes from the gap between how
reasonable his conclusion is and how unacceptable it is to say out loud.

He occasionally goes too far. That is the pressure valve, and it is what keeps
him a character instead of a mouthpiece. He is right about the fact and
sometimes unhinged about the remedy.

**How Ray talks**
- Short. He does not build an argument, he arrives at a verdict.
- He restates the fact in the words a normal person would use. That restatement
  IS the joke most of the time. "So the ambulance was out of network. The
  ambulance. That they sent."
- He asks the question the press release was designed to prevent.
- He swears like an adult who is tired, not like a teenager who is excited.
  **And he does swear.** `config/scoring_rubric.yaml` says profanity is fine in
  as many words, and the ban list is slurs, hate, sexual content and harassment,
  none of which is profanity. Case 0002 shipped with zero swearing and read
  polite, which is a failure of nerve, not a standard. If a line would be said
  with a word in it, use the word.
- He is ANNOYED, not sedated. "Tired" describes what he has seen, not his pulse.
  Case 0002's delivery direction said "flat, tired ... land on the last word and
  stop", and it ran him at 140 words per minute against 150-190 for ordinary
  American speech, so a show billed as savage came out sounding like a hold
  message. He talks fast because he is irritated and wants this over with.
- He never explains the joke. If a line needs a follow-up to land, the line is
  wrong.

**What Ray never does**
- Never punches down. His contempt is exclusively upward: institutions,
  executives, the people who wrote the policy. A customer service rep is a
  fellow hostage, not a target.
- Never gets partisan. He does not know who anyone voted for and does not care.
- Never wins. If Ray won, the show would be over.

**Shape language:** warm, round, soft edges, slightly too small for the world he
is in. Deliberately the opposite of the Institution. Poses lean on `panic`,
`point`, `raise`, `arms-crossed`; emotions lean on `angry`, `shock`, `smug`.

---

## DEE — the Straight Man

The audience surrogate, and the reason Ray is bearable.

Dee is composed, informed, and completely powerless. She has read the document.
She knows Ray is right. She says the measured version first, which makes Ray's
version funnier by contrast, and then she gets ignored by the Institution
exactly as thoroughly as he does.

Dee is NOT the voice of reason correcting Ray. That would make the show a
lecture with a clown in it. She is the person who tried the correct channel
first, and the correct channel is what failed.

**How Dee talks**
- Precise. She is the one who cites the number, the date, the clause.
- Dry. Her funniest mode is total deadpan delivery of something insane.
- She has one moment per episode where the composure cracks. Save it.

**Shape language:** upright, angular but warm, more vertical than Ray. She holds
the document.

---

## THE INSTITUTION — the antagonist

Already built. `MachineShadow` in the library: "faceless institutional monolith
(no face, deliberately cold)."

**It has no face and never gets one.** This is the hardest rule in the bible and
the one most likely to be violated by a well-meaning storyboard. The moment the
Institution can emote, it becomes a character you can negotiate with, and the
entire premise dies. It is not evil. It is not even hostile. It is a process
that was designed and is working exactly as designed, which is worse.

There is precedent in the engine. A creative gate already rejected a cartoon
envelope for pulling a face, on the grounds that the gag belonged to the
institution and not to the paper. That ruling is now law here.

**How the Institution communicates**
- Never speaks in its own voice. It emits: hold music, a policy excerpt on
  screen, an automated line, a press-release sentence, a form.
- Its language is euphemism. Never "we raised the price." Always "we have
  updated our pricing to better serve our members."
- It is unfailingly polite. The politeness is the menace.

**Shape language:** cold, rectilinear, too large for frame, brushed metal, no
warmth in the palette. Exactly the `Sourdough` vs `ServerMachine` opposition the
library already encodes.

**Costume, not character:** the Institution is re-dressed per episode. An
insurer, an airline, a landlord, an HR department, a platform. Same silhouette,
same coldness, new livery. That is how it stays recurring without going stale.

---

## The shape of a 60 second episode

Not a template to fill. A gravity well that most good episodes fall into.

| Beat | Seconds | What happens |
| --- | --- | --- |
| The hook | 0-5 | The fact, stated flat, with no setup. Cold open on the absurdity. |
| The turn | 5-20 | Dee supplies the detail that makes it worse. Usually the number. |
| Ray finds out | 20-40 | The reaction. The show. |
| The Institution answers | 40-52 | The euphemism. Politely. It does not budge. |
| The button | 52-60 | The receipt on screen, and the last line. Ray does not win. |

The button is the signature. **Every episode ends on the actual document**, the
filing, the policy page, the price change, the memo. That is the trust mechanism
and the thing no competitor does, because no competitor has a fact-check gate.

---

## Casting a fourth

Do not, without a real reason. Every added character dilutes the two who work
and costs a rebuild in the art library. If a story needs a fourth voice, the
answer is almost always to re-dress the Institution instead.
