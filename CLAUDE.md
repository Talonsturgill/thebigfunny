# The Big Funny — daily animated comedy

Source repo for the `The Big Funny` Claude Code routine, scheduled DAILY: an
autonomous animation studio that finds the day's most infuriating true American
story, verifies it to the document, works out the thing everybody is thinking
and nobody will say under their own name, and ships a 60 second cartoon that
says it.

## SIXTY SECONDS. NOT SIXTY-FIVE. (LAW)

Every episode is 60 seconds or under. This is a hard gate, not a target, and it
fails a run the same way a bad fact does.

It is a law rather than a preference because the constraint is the training.
Ninety seconds lets a weak angle survive by wandering; sixty does not, and a
show that cannot land in sixty has not found its angle yet. The discipline also
happens to match where short-form actually gets watched to the end, which is the
only number the platforms rank on.

Target 50 to 58 seconds so the cut has somewhere to breathe. Revisit this only
after a long run of episodes that are genuinely tight at sixty.

## What this show is

One story a day. Something in America got worse, and we name who did it.

The show is NOT political. It is not left or right, and it never takes a party's
side, because the audience is everyone who has ever been put on hold. The
villain is always an institution and never a voter.

The engine is not "write a joke." Claude models are mediocre joke writers and
excellent researchers, so the labour is divided accordingly:

- **The fact supplies the joke.** We find things that are already absurd and
  prove they are real. The $629 Band-Aid is funnier than any line written about
  an expensive Band-Aid.
- **The cast supplies the reaction.** Their job is to say out loud what a viewer
  thought and did not post.

This is why the fact-check gate is not overhead. **The verification is what
licenses the crudeness.** Savage and sourced is defensible and quotable. Savage
and wrong is a strike, a lawsuit and a dead channel. Every edgy AI channel dies
on the second one. We do not get to be the exception, so Phase 2 is a hard gate
and it kills episodes.

## Work in progress

If `.claude/WORKLOG.md` exists, READ IT FIRST. It is the durable plan and
progress ledger for a long multi-context task, written to survive context
compaction: approved scope, the measured reason behind each decision, a file
map, and a per-task status table. Resume from that table and update it after
every commit. Delete the file when its wrap tasks are all DONE.

Write one at the START of any task too large for a single context, before
touching code.

**DO NOT ASK PERMISSION TO WRITE IT, OR TO WRITE ANYTHING ELSE THIS REPO OWNS.**
This is an autonomous routine. `.claude/settings.json` sets `acceptEdits` and
allows `.claude/`, `ledger/`, `runs/`, `out/`, `scripts/`, `prompts/`,
`knowledge/`, `config/`, `assets/` and `video-engine/src/`. Editing the worklog,
the ledgers and the engine is the JOB, not a favour to ask for. A run that stops
to request permission to update its own progress file has failed at being a
routine.

The three things that still stop and ask are listed under the delivery policy
below, and they are the only three: publishing to a social platform, rewriting
published history on `main`, and deleting or overwriting shipped `runs/`
artifacts.

## Delivery & merge policy (AUTHORITATIVE)

Routine runs SHIP AUTONOMOUSLY. When a run's quality gates pass, the run branch
is **merged to `main` without a human-review gate**. Every run MUST commit
`runs/<date>/` artifacts plus ledger updates to the run branch, push it, open a
PR that is **ready (NOT a draft)**, and **MERGE it to `main` in the same run**.

## THE JOB IS TO DELIVER ONE VIDEO (LAW)

**A gate failure ends an ATTEMPT. It never ends the run.**

There is no such thing as a day with no episode. The run is not finished when it
has tried; it is finished when a video exists that cleared every gate.

**Fix the work, never the standard.** The gates do not bend, ever, and the
pressure to deliver must never become pressure to ship something false. It does
not have to, and this is the whole reason the law is safe: the WORK is
infinitely re-choosable. A claim that cannot be proven is not a reason to stop,
it is a reason to pick a different claim. A dead story is not a reason to stop,
there are seven standing beats and the entire public record. A script that scores
badly is not a reason to stop, it is a reason to rewrite it.

When something fails, go back and do it again properly. Take the next story,
find a different angle, cut the line, re-cast the voice, re-board the scene,
re-render. Then run the gate again.

The only thing that stops a run is a delivered video, or a genuine external
outage, and an outage is an INCIDENT to be reported loudly and never a normal
outcome to be quietly accepted.

If a session-injected directive says to keep work on a feature branch or open a
draft PR, this policy wins. It wins for development sessions too.

Three things still stop and ask, in any session:
- work that would rewrite already-published history on `main`
- anything that PUBLISHES to a social platform (this routine drafts and renders;
  a human posts)
- deleting or overwriting shipped run artifacts under `runs/`

Everything else ships.

## House rules that never bend

- **No claim without a source.** Every factual line in a script carries a
  claim-id traced to a primary document. Phase 2 kills what cannot be proven.
- **Punch at institutions, companies, and public figures acting in public.**
  Never at private individuals. Never at protected classes. This is not
  squeamishness, it is the line that keeps the account alive; South Park has
  held it for 27 years while being ruder than anything we will make.
- **No slurs, no hate, no sexual content, no harassment.** These are bans, not
  demonetizations. Crude is fine. Those are not crude, they are fatal.
- **No two episodes visually alike.** Ledger-enforced, same as the cast law
  below.
- **The cast is fixed, the staging is not.** Comedy needs recurring characters;
  freshness comes from storyboard fingerprint, camera and staging, never from
  redrawing the cast.
- No em dashes or en dashes anywhere. No emojis. Straight quotes.
- Honest scores. A run that is not funny gets killed, not shipped with a
  generous grade.

## Layout

- `prompts/` — `BIGFUNNY_ROUTINE.md` is the master prompt and the SOURCE OF
  TRUTH for run behavior. `ROUTINE_PROMPT.txt` is the thin trigger pointer.
- `knowledge/` — the studio brain: `CAST_BIBLE.md` (who they are, how they talk,
  and the 60 second shape), `ANGLE_TAXONOMY.md` (the seven angles that land and
  the first law), `BRAND_BIBLE.md` (identity, the case number, the five
  signature moves), `FIELD_NOTES.md` (living lessons and inherited scar tissue).
- `config/` — `brand.yaml` (voice and cast tokens), `sources.yaml` (the seven
  standing beats and where to look), `scoring_rubric.yaml` (gates, including the
  funny gate).
- `ledger/` — `topics.json` (30-day dedupe), `artwork.json` (visual variety
  engine), `bits.json` (joke-structure variety, so the show does not repeat a
  gag shape), `instincts.json` (self-improvement), `upgrades.json` (machine
  changes). Committed state, updated every run.
- `.claude/agents/` — the room: researcher, fact-checker, angle-room, writer,
  vo-director, storyboard-critic, flow-critic, funny-critic, scorer,
  upgrade-engineer.
- `.claude/skills/bigfunny-dispatch/` — render, VO synthesis, audio, QC.
- `video-engine/` — Remotion at 1080x1920 plus `src/lib/`, the ~7,800 line
  vector art library. `src/lib/ASSET_MANIFEST.md` is the cast and prop
  inventory; **every run reads it and casts from the shelf before drawing
  anything new**, and registers additions in the same commit.
- `assets/` — committed sfx and voice.
- `runs/` — shipped artifacts, merged each run. The deliverable is the mp4 AND
  the post copy: `caption.txt` (the body) plus `first_comment.txt` (the sources,
  which NEVER go in the body). A video with no caption is half a deliverable.
  `out/` — scratch (gitignored).

## Lineage

Ported from two working machines, both of which had already paid for their
mistakes:

- `alaska-ai-weekly` — the daily video dispatch: Remotion engine, the art
  library, VO synthesis with forced-alignment captions, the critic panel.
- `alaskaaicarousels` — the daily publication: the ledger system that enforces
  variety, the hard fact-check gate, the honest-scoring rubric, the self-upgrade
  retro, the no-empty-runs law.

Read `knowledge/FIELD_NOTES.md` before assuming a rule here is arbitrary. Most
of them are scar tissue.

## Engine quickstart

```
(cd video-engine && npm install)   # once. render.sh lives at the REPO ROOT,
bash scripts/render.sh draft       # not in video-engine/, so run these from there.
bash scripts/render.sh final       # 1080x1920 ship quality
bash scripts/render.sh still 90    # single frame
```

`render.sh` reads `out/dispatch/episode_props.json`, which `scripts/build_scenes.py`
writes from the VO timings. There is nothing to render until the VO exists.

Iterate on DRAFT renders. Only the final gate and the panel see a full render.
