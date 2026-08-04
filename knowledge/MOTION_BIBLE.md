# THE MOTION BIBLE

What moves, when, and by how much. `DIRECTING.md` owns what is ON screen;
`COMEDY_BIBLE.md` owns whether it is funny; this owns whether it is ALIVE.

Written 2026-08-03 after the owner watched case 0003: "there was no like no
motion, no character motion, no scene motion, no camera motion" and "5 second
rule, scene change or something happen every 5 seconds to drive attention."

Measured on that episode: **59% of the film visually frozen**, entire character
animation vocabulary `Math.sin(f/34)` plus **3.4px** of sway, camera movement in
2 of 18 shots.

Findings below are labelled MEASURED (a study with a sample) or CONVENTION
(professional craft practice) or DERIVED (our arithmetic). Do not promote a
convention to a measurement.

---

## 1. THERE ARE THREE MOTION BUDGETS AND THEY DO NOT SUBSTITUTE

This is the whole diagnosis. We had one budget and spent it entirely on cuts.

| budget | job | frequency | reads at thumbnail? | case 0003 |
| --- | --- | --- | --- | --- |
| **LIFE** | nothing on screen is ever fully still | every frame | no | **absent — this is the 59%** |
| **EVENTS** | re-trigger the viewer's orienting response | every 4-5s | yes | declared but under-rendered |
| **STAGING** | shot changes, new information | ASL 3-5s | yes | carrying 100% of the load |

`DIRECTING.md`'s anti-pattern "BUSY IS NOT ACTIVE" is right about EVENTS and
wrong about LIFE. Ambient drift is not an event and must never be counted as
one. But its ABSENCE is exactly what makes a frame read as a freeze or a render
fault. The fix is not more drift in the events budget; it is a **separate floor
that drift satisfies and events do not.**

**A film cannot pass by cutting more.** That is the loophole the gate now closes.

---

## 2. THE MOVING HOLD (the direct fix for the 59%)

CONVENTION, and it is the single highest-value change available.

An absolute hold, where every pixel of a character is identical across frames,
reads as dead instantly. In professional practice a held pose is a slow small
change that holds the line of action and **never comes to a complete stop.**

Four components, all pure transforms, no new art:

1. **Momentum drift.** Directional and rotational continuation of the previous
   move, decaying to near zero. Do not start drifting toward the NEXT move early.
2. **Breathing.** Small chest and shoulder scale/translate.
3. **Eye darts.** Small fast pupil translations. Signals thinking.
4. **Head support.** Head continues a small rotation supporting the body.

### The numbers, at 30fps

| component | spec |
| --- | --- |
| blink close / hold / open | 3-5 / 1-2 / 2-4 frames (total 0.1-0.4s) |
| blink interval | one every 3-4s, varied +/-40% so it is not metronomic |
| breathing cycle | 2.5-4s; chest scaleY 1.00-1.02, shoulders +/-3-5px |
| eye dart | 2-4 frames travel, then hold 20-60 frames |
| post-action drift | decay the last 15-25% of a move over 12-20 frames |
| child-group offset | 2-4 frames per level of hierarchy |

### THE DEFAULT MUST BE ALIVE

> A rig where stillness is free will keep producing frozen film no matter how
> many gates are added downstream. Gates catch the failure; defaults prevent it.

Build ONE `useMovingHold(frame, seed)` returning `{breathScale, headRot, headY,
pupilX, pupilY, driftX, driftY}` from summed sines at **incommensurable periods**
(2.7s, 3.9s, 6.1s) so the loop never visibly repeats, plus a seeded blink
schedule. Apply it to every character in every shot **by default, with an
explicit `still` prop required to turn it off.**

**Put it on the groups that cover the most PIXELS** — torso, head, whole-body
drift — not only on the pupils. A blink changes ~0.05% of the frame and will
never register on a frame-difference metric or at thumbnail size. That is LIFE,
not EVENTS. A 4px/frame whole-body drift plus a 1.5% breath scale registers on
both.

---

## 3. WHICH ANIMATION PRINCIPLES BUY THE MOST PER UNIT OF WORK

Ranked for an SVG/React cutout rig. Tier 1 is pure transform work: no new art,
one number per layer.

**TIER 1 — do these on everything, always**

1. **Slow in / slow out.** Highest ROI in the list. Linear interpolation is the
   single strongest "a computer made this" signal. **Never `interpolate()` a
   character or camera transform with default linear easing.** Use `spring()` for
   anything that settles and a bezier for anything that travels.
2. **The moving hold.** Section 2.
3. **Overlapping action via frame offset.** Animate each child group 2-4 frames
   behind its parent: `frame - offset`. One integer per layer. Highest return in
   cutout animation because the rig is ALREADY a parent/child hierarchy, so the
   mechanism is free. Head lags torso by 2, hair lags head by 2 more, coat tail
   lags torso by 4.
4. **Anticipation.** 2-6 frames of counter-move before every action. Matters
   disproportionately at thumbnail size: a viewer can miss the action itself, but
   the wind-up is what makes them LOOK at where it will happen.

**TIER 2 — per shot**

5. **Camera moves.** One transform on the root group moves 100% of the pixels.
6. **Parallax layering.** Free depth from art we already own. Section 5.
7. **Prop and world animation.** A counter incrementing, a stack growing, a
   conveyor running. Pays twice: satisfies the motion floor AND does comedy work
   the dialogue cannot, which is DIRECTING.md's first law.
8. **Arcs.** Interpolating x and y independently gives a straight line, which
   reads mechanical. Add a sinusoidal offset on the perpendicular axis. Four
   lines of code.

**TIER 3 — costs real art, reserve it**

9. **Smears.** 1-2 frames only, on the 2-3 biggest actions per episode. Cheap in
   SVG two ways: heavy non-uniform scale along the motion axis plus a skew, or
   3-5 copies of the group at decreasing opacity along the vector.
10. **Squash and stretch.** Nearly free on primitives (`scaleY = 1/scaleX`
    preserves volume), expensive on complex paths. Use on props and impacts. Do
    not squash a detailed character path.
11. **Cloth and hair follow-through.** Needs a segmented rig, so it is a one-time
    build. Our cast is FIXED by house rule, so it is build-once-use-forever and
    worth it: a 3-segment coat tail or ponytail with 2-frame offsets.

---

## 4. WHAT ACTUALLY READS AT THUMBNAIL SIZE

Peripheral and low-acuity viewing resolves **shapes and outlines, not detail**,
so moving silhouettes are close to the only thing legible on a phone at a glance.

**Reads (counts as an EVENT):** silhouette change (a limb leaving the body
outline, an object entering frame), whole-frame motion, large-area value or
colour change, scale change of a major element, objects entering or leaving,
large high-contrast type changing.

**Does NOT read (counts only as LIFE):** eye darts, blinks, finger motion,
low-contrast particles, small-amplitude drift, cloth micro-flutter.

### Specify ambient motion in px/s, NEVER in px of amplitude

DERIVED, and it is the bug that made the Orbit element invisible at 96px of
amplitude. Amplitude says nothing about visibility; **velocity** does. For
sinusoidal drift, peak velocity is `2*pi*A/T`. 96px over 30s is 20 px/s. The same
96px over 4s is 151 px/s. Same amplitude, completely different visibility.

A phone at ~30cm with a ~6.9cm-wide 1080px display subtends about 13 degrees, so
roughly **82 px per degree**. Taking a conservative "visible as motion during a
glance" floor of ~0.5 deg/s gives:

> **MINIMUM AMBIENT VELOCITY: 40 px/s peak, on the 1080 canvas.**

---

## 5. CAMERA LANGUAGE

### 5.1 The finding that changes how we cut

MEASURED (Lang et al., *Communication Research* 1993; Lang, *J. Communication*
2000). Two different things are both called "cutting" and they behave oppositely:

- An **EDIT** — a change of camera angle WITHIN the same scene — improves memory
  and recognition, with no observed ceiling in the tested range.
- A **CUT** — a change to a NEW scene — also improves recognition, **but only up
  to roughly 10 in two minutes, after which recognition drops sharply.**
- Unrelated cuts consume more processing capacity and produce WORSE memory for
  what follows than related ones.

> **We want many angle changes and few location changes.**

A film that only moves when it cuts to a new place is not merely boring, it is
actively damaging comprehension of the fact Phase 2 spent the run verifying.

**Ceiling: 5 scene changes per minute. No ceiling on angle changes and camera
moves within a scene.**

### 5.2 The camera move on a joke

The move is the setup; the **arrival** is the punchline. A push that completes
exactly on the punch word converts an audio beat into a visual event at the
moment attention is most needed. **Moving THROUGH a punchline buries it** — the
viewer is still processing the move when the line lands.

### 5.3 The vocabulary, with numbers

| move | spec | when |
| --- | --- | --- |
| slow push (drift) | 4-8% scale over 3-5s, ease-out | **the default under any dialogue beat.** Cheapest continuous motion in the film. |
| snap push | 6-12% scale over 2-4 frames, hold | the reaction. Land it ON the punch word. |
| pan | 150-400 px/s | reveals, following a prop |
| whip pan | 2500+ px/s for 3-5 frames with a smear, then settle | joins two things that should not be adjacent. Functions as an EDIT, not a CUT, so it is the memory-friendly kind. |
| pull back | reveal over 8-16 frames | the escalation reveal. One per episode. |
| rack focus equivalent | blur/opacity swap between parallax layers over 6-10 frames | attention transfer without a cut |

### 5.4 Shot length

MEASURED: the AnimeShooter dataset reports animation story units averaging
**56.72s with 14.82 shots, ASL 3.85s** — almost exactly our format. So **12-18
shots in 60 seconds is the animation-native number.**

Cinemetrics genre ASL for reference: action 4.0s, adventure 5.1s, sci-fi 6.2s,
US network TV ~3.5s.

**Do not make shot lengths uniform.** MEASURED (Cutting, DeLong & Nothelfer,
*Psychological Science* 2010, 150 films 1935-2005): shot-length sequences
increasingly approach a **1/f power spectrum**, with lengths correlated with
their neighbours, and they argue this rhythm helps harness attention. Practically:
**cluster short shots together and long shots together. Do not alternate
mechanically.**

---

## 6. PARALLAX

Disney's multiplane, 1933. The farther the layer, the slower it moves.

Four to six depth layers is the sufficiency point; more costs without
perceptible gain. Standard speed factors:

```
far background   0.05 - 0.15
mid background   0.30 - 0.50
subject plane    1.00
foreground       1.40 - 1.80

layerX     = cameraX * speedFactor
layerScale = 1 + (cameraZoom - 1) * speedFactor
```

Two things that make parallax READ rather than merely exist:

1. **A foreground occluder at 1.4-1.8x** that crosses in front of the subject and
   leaves frame. Occlusion is a stronger depth cue than motion parallax, so this
   buys more depth per pixel than any number of slow background layers.
2. **Atmospheric perspective per layer:** reduce contrast and desaturate with
   depth. In SVG that is one `<rect>` of the sky colour at 10-25% opacity.

**Because our first law puts the cast INSIDE the mechanism, the mechanism's own
parts are the parallax layers for free:** gear teeth in front, housing wall
behind, cabling mid-ground.

---

## 7. THE FIVE SECOND RULE HAS A MECHANISM

The owner asked for it; here is why it is right, and the correction that matters
more than the rule.

MEASURED: the **cardiac orienting response**. Television's formal features (cuts,
edits, zooms, pans, onsets) automatically trigger an orienting response, and
**heart rate decelerates for 4 to 6 seconds afterward.** That deceleration window
is the period of elevated attention.

> An event every <= 5s re-triggers attention before the previous orienting
> response has decayed. **4.0s is the better working target, 5.0s the hard
> ceiling.**

**The caveat is asymmetric and it is the correction our film needs:** more EDITS
is monotonically better; more CUTS stops helping at ~5 scene changes per minute.
So the other 7-20 events must come from WITHIN the scene: camera moves, angle
changes, prop action, reveals, entrances, scale changes, register changes.

Fast pace COMBINED with arousing content overloads processing and produces worse
recognition. Speed is not free.

### What counts as an event

| change | counts | note |
| --- | --- | --- |
| object enters or leaves frame | full | strongest silhouette change |
| reveal, scale change, light change | full | |
| angle change within scene (EDIT) | full | memory-positive. Use liberally. |
| camera move that ARRIVES | full | the arrival is the event, not the move |
| quantity on screen changes | full | |
| face changing register | full | cheapest available |
| new scene (CUT) | full, **capped at 5/min** | |
| camera move with no arrival | half at most | |
| **caption line change** | **half, capped at 25% of events per 10s window** | see below |
| ambient drift, particles, parallax, shimmer | **zero** | LIFE budget only |

**Why captions are capped.** A caption onset is a real attentional onset, so it
is not zero. But it occupies 3-6% of the frame, contributes almost nothing to a
frame-difference metric, does not read as an image at thumbnail size, and is
100% correlated with the VO. **Counting captions as full events means any
narrated slideshow trivially satisfies the events floor — which is exactly how
case 0003 happened.**

---

## 8. RETENTION, MEASURED

Numbers to calibrate expectations against, not folklore.

- **45% of TikTok video views are watched to the end; 55% are abandoned.** 24% of
  views are abandoned before 20% of the video; 40% before 50%. Median attention
  82%. (Zannettou et al., CHI 2024, 9.2M real views from 347 donating users.)
  **45% completion is the platform AVERAGE. At or above that is normal, not
  good.**
- **Meta ranks a reel against others OF ITS OWN LENGTH** ("watch more of a reel
  than 95% of users who watched reels of the same length"). **Our 60-second law
  is therefore safe** — a 55s episode is judged against the 55s cohort, not
  against 8-second clips. (Meta Transparency Center, Reels Chaining.)
- **3.0 seconds is a platform-defined checkpoint**, not folklore: Meta's ranking
  explicitly predicts "how likely you are to watch less than three seconds."
- Videos **under 1 minute have the highest engagement rate, 50%** vs 46% at 1-3
  min. (Wistia, State of Video 2025.)
- **85% of digital video ads receive under 2.5 seconds of attention**; recall is
  achievable at 1.5s when distinctive brand assets are present. (Amplified
  Intelligence, 20,000+ views, camera-based gaze.) **This is why the case number
  stamps early: 1.5s may be all we get.**
- **80% of consumers are more likely to finish a video when captions are
  available**; 69% watch with sound off in public. (Verizon Media + Publicis
  Media, n=5,616.) Captions are load-bearing here, not decorative.

### The first three seconds, mechanically

1. Establish the frame is not an ad or a title card. **A wordmark-first opening
   spends the only guaranteed attention on the least specific frame.**
2. Present a legible novel image, at silhouette level.
3. Create an unresolved question — a visible thing that does not yet make sense.
4. **MOVE.** A static first frame gives the thumb nothing to catch and produces
   zero orienting response. Case 0003 opened on a frozen document for 3 seconds
   and the simulated viewer scrolled at exactly 3.0s.

> At least **2 distinct visual events before t=3.0s**, and **4 before t=6.0s**.

### Ending

Weak evidence, real mechanism, zero cost:
- Last frame visually rhymes with the first: same composition, different content.
  The viewer reads the loop as a punchline rather than an end.
- **Never end on a fade to black or a static card.** A fade is an explicit stop
  cue and mechanically the deadest possible final second.
- Put the last event as late as possible.

---

## 9. THE THRESHOLDS

Enforced by `scripts/motion_check.py` against the encoded mp4.

| gate | value | basis |
| --- | --- | --- |
| `MAX_FROZEN_SHARE` | 0.10 | TARGET, not a measured number. Say so. |
| `MAX_HOLD_S` fully frozen | 1.0s | convention: a character is never absolutely still; 1s frozen reads as a render fault |
| `MIN_LIVE_SHARE` | 0.40 | closes the cut-to-pass loophole |
| `MAX_CUT_SHARE` | 0.50 | with the live floor above |
| `MAX_EVENT_GAP_S` | 4.0 target / 5.0 hard | cardiac OR decays over 4-6s |
| event gap, first 6s | 1.5s | Meta's 3-second prediction boundary |
| `MAX_SCENE_CHANGES_PER_MIN` | 5 | Lang: recognition drops above ~10 per 2 min. **This is what stops "add more cuts" being the fix.** |
| `TARGET_SHOTS_60S` | 12-18 (ASL 3.3-5.0s) | AnimeShooter animation ASL 3.85s |
| caption event weight | 0.5, max 25% of events per 10s | prevents a narrated slideshow passing |
| `MIN_AMBIENT_VELOCITY_PX_S` | 40 px/s peak | DERIVED, section 4 |
| caption safe area | centered 900x1400 in 1080x1920 | cross-platform intersection |

### Two engineering notes

1. **Measure the encoded MP4, not the Remotion render.** We already do. A
   low-amplitude moving hold can be quantised away by the encoder into skip
   blocks, in which case the FILE really is frozen even though the source was
   not. If subtle motion is being crushed, that is a bitrate problem and the gate
   is correctly reporting it.
2. **Sampling interval is part of the evidence.** `motion_check` states its
   interval in its own output, because a gate that samples at 0.5s cannot see a
   0.1-0.4s blink and must not be read as saying the blink is absent.
