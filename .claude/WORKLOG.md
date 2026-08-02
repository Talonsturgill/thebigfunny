# WORKLOG — THE SHORT FILM OVERHAUL

Durable plan for a task too large for one context. Resume from the status table.
Delete this file when every wrap task is DONE.

Supersedes the "faces that move" worklog, whose scope shipped (expression engine,
case 0003 rendered). Its three still-open items are carried into "Inherited"
below so nothing is lost by replacing it.

## The owner's diagnosis, 2026-08-02

Verbatim, because paraphrasing loses the diagnosis:

> "no its not funny, kinda cause the speed is slow, kinda cause the scenes are
> boring and not actually illustrating anything, and kinda cause the whole story
> is just like incoherent, like it wasn't planned out to be a funny short film,
> you made it two ppl talking and doing nothing for the most part, and didn't
> really add in the producer room, the director room either"

> "there should be real time spent in the pre-planning room discussing what to
> place on screen and how, that will make ppl genuinely laugh, make agents all
> argue with each other so they can work together to end up with a combined
> amazing flow of on-screen stuff, should be a product that took like 20 minds
> put together"

> "Alaska is rugged (where the chars came from), this show is appeasing... we
> don't have to be people in parkas and cold places, the entire scene can be
> super meta, for example if the topic was about an engine issue on Ford motors,
> u could put the chars inside a Ford engine, point being u can get creative and
> really put the chars inside the world of whatever the topic is"

## THE ROOT CAUSE (this is the important part)

These read as four complaints. They are ONE.

The art library was ported from `alaska-ai-weekly`. It is a shelf of parkas,
snow, spruce, wolves, glaciers and boreal night. `ASSET_MANIFEST.md` says to cast
from the shelf before drawing anything new, which is a good rule that has been
quietly doing enormous damage: the shelf is ALASKA and the stories are national.
So every board casts an Alaska set for a story that has nothing to do with
Alaska, the set therefore cannot illustrate anything, and once the set is inert
the only thing left for an episode to do is HAVE TWO PEOPLE TALK.

"Two people talking and doing nothing" is not a staging failure. It is what is
left over after the world has been amputated from the story.

It also explains the standing repeat offenders. `retro.py` has `carried_by_fact`
and `agreement_not_comedy` in both runs on file, and the funny critic blamed the
STORY both times. It was half right. The fact was carrying the episode because
nothing else was ALLOWED to: not the set, not the props, not the world. A joke
that exists only in the dialogue is a podcast with drawings over it.

## THE FIX, in one sentence

**The world of the story becomes the set.** A Ford engine story is staged INSIDE
a Ford engine. The cast is dropped into whatever world the story is about, and
the world does comedy work the dialogue cannot.

Everything below is downstream of that sentence.

## Approved scope

1. **De-Alaska the library.** The shelf stops being a PLACE and becomes a KIT:
   parametric primitives assembleable into any world in one run, plus a rule that
   every episode BUILDS its world instead of shopping for one. The Alaska assets
   stay (paid-for craft, and one day a story is about Alaska); they stop being
   the default.
2. **The rooms.** A producer room that decides what the episode IS as a short
   film, and a director room that decides what is ON SCREEN every second. Both
   sit UPSTREAM of the writers room, because that is where the decision they own
   actually gets made. This is the standing `retro.py` lesson applied.
3. **Argument, not a pipeline.** Agents with genuinely opposed mandates, run in
   parallel, forced to disagree on the record, then a synthesis that must RESOLVE
   conflicts rather than average them. Averaging N opinions produces the blandest
   member of the set, which is the opposite of the ask.
4. **A gate that refuses talking heads.** Critics downstream of a decision never
   fix that decision, so this is mechanical and runs on the BOARD: before a frame
   is rendered and before a cent of audio is bought.
5. **Silhouettes.** DONE and shipped; kept in the file map.

## The measured reasons (do not re-litigate)

- A downstream critic never fixes an upstream decision. Proven twice: the funny
  critic named the same cause on cases 0002 and 0003 and six rewrites moved the
  score 57 -> 69 -> 63. The ceiling was the STORY and the SET and no amount of
  rewriting reached either. Every new gate here runs at the phase that MAKES the
  decision, not the phase that notices.
- A gate that cannot fail certifies nothing. Every gate ships with a
  `--self-test` that must go RED on purpose, and the FIXTURES get checked too:
  three have been wrong on first write (face_check's "good" fixture held one face
  12s, tts_budget's over-budget preview actually fit, vo_soundcheck's short
  fixture was exempt under its own new rule).
- A prop that typechecks and renders can still change nothing on screen. The
  `mouth` prop was dead for a whole episode behind a `talking !== undefined`
  guard while every gate stayed green. Verify a PIXEL.
- Measure geometry, do not reason about it. The Orbit amplitude (96px,
  invisible), the athletic shoulder (+8 units, invisible) and the CastSheet bbox
  (wrong twice from reading the source) each cost a render.
- Iterate the SCRIPT against the free critic; synthesize audio ONCE at the end.
  Six re-synthesis passes in one session is what exhausted the TTS quota.

## File map

| path | state | what it is |
| --- | --- | --- |
| `video-engine/src/lib/Character.tsx` | DONE | `build` prop: broad / hourglass / athletic. Silhouette, clip, belt, jaw, lashes, brow weight, stance. |
| `video-engine/src/lib/cast.tsx` | DONE | Ray athletic, Dee hourglass. |
| `video-engine/src/CastSheet.tsx` | DONE | Proof-of-pixels sheet. `broad` is the control column. |
| `scripts/retro.py` | DONE | Cross-run verdict memory, repeat-offender escalation, phase ownership. |
| `scripts/story_check.py` | DONE | Phase 3 gate: the absurd mechanism, in writing, before anything is paid for. |
| `ledger/verdicts.json` | DONE | Every critic verdict, every run. |
| `knowledge/DIRECTING.md` | TODO | The brain for the director room: world-of-the-story, visual comedy, what separates a short film from two talking heads. |
| `scripts/visual_check.py` | TODO | The gate. Refuses talking heads; refuses a set with nothing to do with the story. |
| `.claude/agents/producer.md` | TODO | Owns the episode AS A FILM. Upstream of the writers room. |
| `.claude/agents/director.md` | TODO | Owns what is on screen, second by second. |
| `.claude/agents/production-designer.md` | TODO | Builds the WORLD of the story. The Ford-engine agent. |
| `.claude/agents/devils-advocate.md` | TODO | Mandated to attack. Defaults to kill. |
| `.claude/agents/asset-upgrader.md` | TODO | De-Alaskas the ported library, one bounded pass per run. |
| `prompts/BIGFUNNY_ROUTINE.md` | TODO | Wire phases 3.7 (producer), 4.2 (world), 4.6 (director), 8 (retro). |
| `video-engine/src/lib/ASSET_MANIFEST.md` | TODO | Kit-not-place mandate. |

## Status

| # | task | state |
| --- | --- | --- |
| 1 | build silhouettes + cast lock + proof sheet | DONE |
| 2 | retro.py cross-run memory + verdict ledger | DONE |
| 3 | story_check.py phase 3 gate | DONE |
| 4 | `button_doesnt_land` closed: the producer room owns the button | DONE |
| 5 | knowledge/DIRECTING.md | DONE |
| 6 | scripts/visual_check.py + self-test | DONE |
| 7 | the room agents (producer, director, designer, devils-advocate, reader-sim) | DONE |
| 8 | asset-upgrader agent + kit mandate | DONE |
| 9 | wire the routine prompt (3.7, 4.2, 4.4, gates, panel, retro) | DONE |
| 10 | GitHub trending research, folded into this file | DONE |
| 11 | ship an episode that clears the new gates | TODO |

## What the GitHub scan actually returned (2026-08-02)

A survey of repos that gained traction May to Aug 2026. Full sourcing is in the
run transcript; what matters here is the short list and the one warning.

**THE WARNING, and it lands directly on the "make agents argue" ask.** The July
2026 multi-agent-debate survey (arXiv 2607.26212) finds the field settled on
fully-connected debate topologies and majority voting BY CONVENTION rather than
by comparison, and that the documented failure modes are conformity, cost and
degeneration. Other 2026 work finds debate UNDERPERFORMS a single strong model
when the agents share a base model, because the panel collapses toward the
majority rather than toward the truth.

So: **a debate between five Claude subagents with different system prompts is
theatre.** Five voices that agree politely is not twenty minds, it is one mind
billed five times. The value is entirely in (a) heterogeneity and (b)
ANTI-CONFORMITY ENFORCEMENT. The room we build has to reject a round in which
everyone agreed immediately, or it is worse than the single agent it replaced.

Adoption order, cheapest and highest-leverage first:

1. **Remotion `--frames=0,10,20` contact sheets** (landed 2026-07-30, a flag on a
   tool already in the stack). One render call produces a strip across the whole
   episode; stitch it into a grid and give the storyboard and flow critics EYES.
   They currently grade JSON. This is why "the scenes are boring" was invisible
   to every gate: nothing in the machine ever LOOKED at the episode.
2. **Deterministic detectors before LLM critics** (Impeccable). Claim-id
   resolution, verbatim numeral matching, the 58-second law, screen-side
   continuity and staging-fingerprint distance are all RULES. Zero model calls,
   zero grade inflation, and they cannot be talked out of a verdict.
3. **Slideshow / motion-energy risk score** (OpenMontage). A measure of WITHIN
   episode staticness. This is exactly "two people talking and doing nothing",
   made mechanical, and it is the core of `visual_check.py`.
4. **Reader-sim agent** (creative-writing-skills). Reports a second-by-second
   experiential timeline ("at 14 I was waiting, at 31 I laughed, at 44 I would
   have scrolled") instead of a holistic score. A 60-second show needs a
   TIMELINE, not a grade.
5. **Side-swapped, reference-anchored scoring** (lechmazur/debate). Never an
   absolute 1-10 in isolation: rank today's script against two fixed prior
   episodes, one good and one marginal, presented in BOTH orders, and only trust
   a result that survives the swap. Fixes both drift and position bias.
6. **Anti-conformity check + kill criteria + FACT/INFERENCE/ASSUMPTION tags**
   (council-of-high-intelligence). Reject any round where everyone agreed on the
   first pass. Every approved angle ships with the condition that would
   INVALIDATE it, so Phase 2 knows what to hunt.
7. **Layered fact-check cascade + numeral sanitizer** (AutoResearchClaw).
   Cheapest verification first, LLM last; any figure not appearing verbatim in a
   source is stripped mechanically before a critic ever reads the draft. Also:
   their skills DECAY after 30 days, which is what stops `instincts.json` from
   becoming a superstition ledger.
8. **Tiered duration rescue** (ai-shortVideo-pipeline). At 63 seconds the options
   are not "rewrite" or "ship long": trim gaps, then nudge rate under 4%
   (inaudible), then cut the weakest sourced line, then rewrite.
9. **Rhubarb Lip Sync** with `--dialogFile`. Boring, correct, a decade old, and
   nothing from 2026 beats it for 2D with pre-locked dialogue. We have the
   advantage most users do not: the script is locked before synthesis.

Explicitly NOT adopting: the Chinese short-drama cluster (six near-identical
repos in eight weeks, aimed at diffusion video, a gold rush), HyperFrames (a
lateral move from Remotion), any framework dependency at all.

## Inherited from the previous worklog, still open

- **C:** Institution costume system (designed, never built).
- **E:** trigger config (lives outside this repo).
- **Dee's voice pick is still with the owner.** An audition of seven candidates
  went out; `main` carries Pulcherrima. The soundcheck measured every candidate
  between 3.46 and 4.12 semitones of pitch variance INCLUDING the one the owner
  called robotic, so the machine cannot rank them and does not pretend to.
- **TTS model:** temporarily overridden to 2.5-flash by env var after the daily
  quota exhausted on 3.1. This reverts by itself; the override is not in code.

## Wrap

- [x] every gate self-tests RED on purpose, fixtures checked
- [x] `retro --check` exits 0
- [x] routine prompt is the source of truth and matches the code
- [x] FIELD_NOTES gets the root-cause paragraph above, in short form
- [ ] delete this file
