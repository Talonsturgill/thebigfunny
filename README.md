# The Big Funny

A daily animated comedy show, produced end to end by an autonomous Claude Code
routine.

One story a day. **Something in America got worse, and we name who did it.**
Sixty seconds, 1080x1920, and it always ends on the actual document.

## How it works

The show runs on an inversion that makes it possible to automate at all:

> **Do not write jokes. Find things that are already absurd and prove they are
> real.** The fact supplies the joke. The cast supplies the reaction.

Claude models are mediocre joke writers and excellent researchers, so the labour
is divided that way. The daily routine goes wide across seven standing beats,
kills everything it cannot trace to a primary document, finds the single
specific detail that does all the work, and hands that to three characters.

The verification is not overhead, it is the license. Savage and sourced is
defensible and quotable. Savage and wrong ends a channel.

## The cast

- **RAY**, the Id. He is right, not a fool. He says the thing you said in the
  car and would not post under your own name.
- **DEE**, the Straight Man. Precise, dry, powerless. She read the document.
- **THE INSTITUTION**. No face, ever. Not evil, just working exactly as
  designed, which is worse. Re-dressed per episode; same silhouette, new livery.

## Repo map

| Path | What |
| --- | --- |
| `prompts/BIGFUNNY_ROUTINE.md` | The master routine. Source of truth for run behavior. |
| `prompts/ROUTINE_PROMPT.txt` | Thin trigger pointer. |
| `knowledge/` | Cast bible, angle taxonomy, field notes. |
| `config/` | Voice, the seven beats and their sources, the scoring rubric. |
| `ledger/` | Dedupe, joke-shape variety, visual variety, instincts, upgrades. |
| `.claude/agents/` | The room: researcher, fact-checker, angle-room, writer, critics, scorer. |
| `video-engine/` | Remotion at 1080x1920 plus `src/lib/`, a ~7,800 line vector art library. |
| `runs/` | Shipped episodes. |

## Quickstart

```
cd video-engine && npm install
bash scripts/render.sh draft      # half-res preview, iterate here
bash scripts/render.sh final      # ship quality
```

## Lineage

Ported from two working daily machines rather than built from scratch:
`alaska-ai-weekly` (the Remotion engine, the art library, VO with
forced-alignment captions, the critic panel) and `alaskaaicarousels` (the ledger
system that enforces variety, the hard fact-check gate, honest scoring, the
self-upgrade retro, the no-empty-runs law).

`knowledge/FIELD_NOTES.md` carries the scar tissue from both. Read it before
deciding a rule here is arbitrary.

## The line

Punch at institutions, companies, and public figures acting in public. Never at
private individuals, never at protected classes. Profanity is fine; slurs, hate,
sexual content and harassment are not, because those are bans rather than
demonetizations.

The routine renders and drafts. **It never posts.** A human posts.
