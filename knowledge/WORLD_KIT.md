# THE WORLD KIT

The shelf is a KIT, not a PLACE. Every episode BUILDS the world of its story out
of parts. It does not go shopping for a location that already exists.

## STOP. NOTHING IN THIS KIT IS BUILT YET. (2026-08-02)

Every primitive named below is a PROP-SHAPE SKETCH. Zero of thirteen exist as
`.tsx`. `Volume`, `Passage`, `Rotor`, `Piston`, `Conveyor`, `Flow`, `Stack`,
`Queue`, `Grid`, `Signage`, `Paperwork`, `ScaleFrame` and `WorldRig` are all
absent from `video-engine/src/lib/`, and ASSET_MANIFEST carries no entry for any
of them.

This was buried in one line under the primitives heading, and the first dry run
walked straight into it: the producer budgeted "one new set component and three
props" for a world that in truth was 100 percent new construction wearing the
word "cast". A cost that reads as small and is not is worse than no estimate,
because it converts a two-week decision into an afternoon one.

**So until a build run lands them: a world costs what it costs to BUILD, and
"cast from the kit" is a claim you must check against `lib/` before you make
it.** The designer's adjudication is the required move, and it has a real
answer, because most primitives turn out not to be needed:

- What DOES exist and is genuinely reusable: `lib/draw.ts` (`ribbon`, `band`,
  `bent`, `spline`, `edge`), `lib/stage3d.tsx` (`Stage3D`, `Plane`, `Extrude`,
  `Card`, `Atmosphere`, `CastShadow3D`, `CameraMoves`), `lib/paper.tsx`,
  `lib/kit.tsx`, `lib/props.tsx`, plus lighting, materials, motion and FX.
- `WorldRig` lighting presets are mostly `NightGrade` with different arguments.
- `ScaleFrame`'s only real contract is that a size reference is REQUIRED in
  frame. That is a review rule, enforced at handoff. It is not a component.
- `Signage` and `Paperwork` already have working stand-ins in `kit.BoxLabel`,
  `props.SwingSign`, `paper.Sheet` and `PaperFiber`.
- Note that `stage3d.tsx` has never been wired into the Episode pipeline. First
  use carries an integration cost that is real and must be budgeted once.

A world that needs a true swept tube surface with the camera inside it is a
TWO-WEEK WORLD. A ribbon gives a silhouette, not a surface with a UV. Kill such
a world at the plan, not after a week of building it.

### The ratio ambiguity, resolved

"Ratio 0.06" and "shorter than a postage stamp" are not the same world and the
first dry run tripped on it. Against a human, 0.06 is 105mm and taller than any
stamp; against a #10 envelope's long edge, 241mm, it is 14mm and shorter than a
25mm stamp. **A cast-to-world ratio is measured against the LONG EDGE of the
object the cast is standing on, never against a person.** State the object.

## Why this file exists

The art library was ported from `alaska-ai-weekly`, an educational weekly about
Alaska. It is a genuinely good shelf: eleven biomes, twenty-one animals, three
vehicles, a fish-realism engine. It is also a PLACE, and this show's stories are
national.

`video-engine/src/lib/ASSET_MANIFEST.md` told every run to cast from that shelf
before drawing anything new. That is a good rule and it was doing enormous
damage, because the only sets on the shelf were Alaskan. So a story about an
insurer got staged on a main street, or in a records room, or against a wall,
and the set had nothing to do with the story. A set that has nothing to do with
the story cannot illustrate the story. And once the set is inert, the only thing
left for an episode to do is have two people talk.

"Two people talking and doing nothing" is not a staging failure. It is what is
left over after the world has been amputated from the story. Three separate
complaints (slow, boring, incoherent) and two standing repeat offenders in
`scripts/retro.py` (`carried_by_fact`, `agreement_not_comedy`) are the same one
defect wearing four coats. The fact was carrying every episode because nothing
else was ALLOWED to.

The owner's instruction, standing:

> "the entire scene can be super meta, for example if the topic was about an
> engine issue on Ford motors, u could put the chars inside a Ford engine, point
> being u can get creative and really put the chars inside the world of whatever
> the topic is for said story, and take them into that world and do it in a funny
> way for the viewer"

And: "if its Alaska stuff don't patch it, we are creating a better show that's
more engaging as opposed to educational."

## What a WORLD is

**A world is the physical inside of the mechanism the story is about.**

Not the place where the story is discussed. Not a location associated with the
industry. The inside of the thing that did it.

A story about a recalled part is not staged in a dealership. It is staged inside
the engine, standing on the piston. A story about a claim denial is not staged in
a waiting room. It is staged inside the body the claim is about, because that is
what the review is nominally reviewing.

Three tests, and a world has to pass all three:

1. **THE SWAP TEST.** Could this scene play unchanged in a different set? If yes,
   you have a location, not a world. A location is a backdrop; a world is a
   participant.
2. **THE MUTE TEST.** Turn the dialogue off. Does a stranger still know what the
   story is about within about one second of the establishing frame? If not, the
   world is decorative and the dialogue is still doing all the work.
3. **THE WORSE TEST.** Can the world GET WORSE while the episode runs? A world
   that only sits there is a painting. The set must be able to escalate: speed
   up, back up, seize, flood, tilt, narrow, fill. That escalation is the second
   comedy track running under the words, and it is the track this show has never
   had.

A world is also NOT a pun. "Inside the ledger" as a phrase is a pun and it dies
in two seconds. "A mail-sorting floor where the day's transactions arrive in one
order and leave in another, with a fee stamp thunking onto the same small parcel
five times" is a world, because it has a mechanism you can watch and a mechanism
can be funny for sixty seconds.

## HOW TO DERIVE A WORLD, in order

This runs after the fact-check and after the angle is locked, never before. The
design room does not invent the mechanism; it stages the mechanism the documents
already proved. If the world implies a fact the fact-check did not clear, the
world is wrong, not the fact-check.

1. **Name the MECHANISM, not the topic.** Not "airline fees". "The seat pitch
   shrinks one inch per fare class while the sign naming the class gets bigger."
   The mechanism is one sentence with a moving part in it. If you cannot write
   it, go back to the angle room; you have a topic, and a topic cannot be staged.
   `scripts/story_check.py` already gates this at Phase 3.
2. **Find the noun that has an INSIDE.** Every mechanism runs inside something:
   an engine, a body, a warehouse, a shaft, a pipe, a queue, a machine. Pick the
   one the audience already has a picture of. Familiar exterior, unfamiliar
   interior, is the whole trick. Nobody has been inside a cylinder head. Everybody
   knows what an engine is.
3. **Choose the SCALE.** Three options and they are not interchangeable:
   - *Cast tiny inside something ordinary.* The strongest and most expensive.
     Use it when the point is that a huge apparatus exists to move one small
     thing (a clip, a claim, a $4 coffee).
   - *Cast at working scale.* They are employees of the mechanism, or riding it.
     Use it when the point is throughput.
   - *Cast normal, world enormous around them.* Use it when the point is that
     they are outnumbered.
4. **Write the ESTABLISHING IMAGE as one sentence.** One frame, no dialogue, no
   labels. Camera position, what fills the frame, where the light comes from,
   what is moving. If it needs two sentences it is two shots and one of them is
   the real one.
5. **Give the world a JOB the dialogue cannot do.** Pick one: throughput (things
   passing), accumulation (things piling), absence (a thing that should be there
   and is not), or degradation (a thing narrowing, slowing, seizing). This is
   what the world DOES across the sixty seconds. Write its start state and its
   end state.
6. **Find TWO sight gags the world makes possible.** A sight gag is a joke you
   could tell with the sound off. Verify each one: if you can only describe it as
   a line with a picture over it, it is a line, delete it and find a real one.
7. **Cost it.** A world is at most one new set component plus at most three new
   props, assembled from the primitives below. If it cannot be built inside that,
   the world is too literal. Go back to step 2 and pick a smaller inside.

## FIVE WORKED EXAMPLES

These are design exercises across five common story shapes, not five specific
claims. Every number and mechanism in a real episode comes from the cleared
claim set, and the world is built to the mechanism the fact-check actually
licensed.

### 1. Bank overdraft fees

- **World:** THE SORTING FLOOR. Inside the day's posting run: a parcel-sorting
  hall where every transaction arrives as a parcel and a machine re-orders them
  before they are posted.
- **Establishing image:** low camera under a re-ordering gantry, a fast belt
  running away to a vanishing point, parcels arriving in one order and leaving in
  another, a red-lamped turnstile at the far end.
- **The cast inside it:** Dee rides the belt holding her own small coffee parcel,
  trying to reach the window before the money runs out. Ray stands at the base of
  the sorting arm reading the operating manual bolted to it, out loud.
- **The world's job:** throughput becoming accumulation.
- **Sight gag one:** a mortgage parcel the size of a car goes through first, and
  the arm flicks Dee's coffee parcel to the back of the line. Then again. Then
  again. Same parcel, and each time a fee stamp thunks onto it and the parcel
  gets fractionally heavier and slower.
- **Sight gag two:** the far end is not a chute, it is a turnstile, and it takes
  a coin per rotation whether or not anything goes through.
- **Primitives:** `Volume` + `Conveyor` + `Rotor` (the arm) + `Stack` (the fees) +
  `Signage` + `Paperwork`.

### 2. Health insurance denial

- **World:** THE REVIEW HELD INSIDE THE PATIENT. A hearing room built in a chest
  cavity: ribs as roof beams, a frosted service window in a partition, two bolted
  plastic chairs, a ticket dispenser screwed to a rib.
- **Establishing image:** wide from inside the ribcage, warm wet light coming
  through the rib slats, the service window shut, the heart working away behind
  the partition on a hold-music loop.
- **The cast inside it:** Ray and Dee sitting in the two chairs holding a paper
  ticket, waiting. That is the entire blocking. The world does the rest.
- **The world's job:** degradation, and the reveal that the queue is going
  backwards.
- **Sight gag one:** the ticket number advances one on every heartbeat. The NOW
  SERVING board advances backwards.
- **Sight gag two:** the service shutter is on the same reciprocating linkage as
  the lungs, so it opens and shuts on its own rhythm, and it shuts on Dee mid-word
  every single time.
- **Primitives:** `Volume` (its `ribs` param, literally) + `Piston` (the shutter
  linkage) + `Signage` (split-flap NOW SERVING) + `Queue` + `Paperwork`.

### 3. An airline story

- **World:** THE PITCH SHAFT. A vertical shaft whose every landing is a seat row,
  narrowing one row at a time as it descends toward the cheapest fare.
- **Establishing image:** camera looking straight down the shaft, seat backs
  receding, walls visibly squeezing with depth, a small lit sign at the bottom.
- **The cast inside it:** Ray and Dee climbing DOWN it, hand over hand on tray
  tables, one fare class per landing.
- **The world's job:** degradation, measured against a fixed unit (their own
  bodies) so nobody has to say an inch count.
- **Sight gag one:** the sign naming each fare class gets bigger as the gap gets
  smaller, until the last sign will not fit in the gap it names.
- **Sight gag two:** a duty-free cart crosses the shaft through a side hatch on a
  wide, generously lit aisle they cannot fit through.
- **Primitives:** `Passage` (tapered, axis 'down') + `Signage` + `Grid` (the seat
  map) + `ScaleFrame`.

### 4. A data breach

- **World:** THE WAREHOUSE OF YOU. A records hangar where every shelf bin holds
  one person's file, and the loading dock at the far end is standing open.
- **Establishing image:** down an aisle of bins to a vanishing point, one bin
  pulled halfway out at camera left with a name on it, and at the far end the
  dock door open with rain blowing in.
- **The cast inside it:** Ray and Dee walking the aisle looking for their own
  bins. They find them. Both are empty, and a courtesy notice is taped inside.
- **The world's job:** absence. The single hardest thing to stage and the single
  most valuable, because a viewer who NOTICES an absence has done work and will
  stay for the payoff.
- **Sight gag one:** the notice offers twelve months of a service that watches
  the empty bin.
- **Sight gag two:** the overhead conveyor is still bringing NEW bins in, at
  speed, past the open dock, and nothing about the intake has noticed the outflow.
- **Primitives:** `Volume` + `Grid` (with a `vp`, so it recedes) + `Conveyor` +
  `Paperwork` + `WorldRig` 'interior-fluorescent'.

### 5. A car recall

The owner's own example, honoured literally, so this file cannot be accused of
dodging the thing it was written for.

- **World:** INSIDE THE ENGINE. The cast stands on the crown of a piston at
  bottom dead centre, cylinder walls going up out of frame.
- **Establishing image:** low and centred on the piston crown, cylinder walls
  rising past the top of frame, one shaft of light coming down from the spark
  plug hole far above, carbon crusted on everything.
- **The cast inside it:** Ray reads the recall notice by the light of the plug
  hole. Dee watches the crank throw and times it.
- **The world's job:** degradation on a clock. The cylinder is going to fire.
- **Sight gag one:** the part that failed is a plastic clip. At their scale it is
  a park bench, and it has a moulded date on it that is older than the recall.
- **Sight gag two:** the recall notice arrives by falling in through the plug
  hole and landing on the crown, and the next stroke compresses it into a wafer.
  Delivered, technically.
- **Primitives:** `ScaleFrame` (the entire point) + `Piston` + `Volume` (vertical,
  vanishing point overhead) + `Passage` (the plug hole as a light shaft) +
  `Paperwork` + `WorldRig` 'machine-cavity'.

Note what those five have in common. Not one of them is a room where people
discuss a thing. Every one of them is the inside of the thing. And in four of
five the cast blocking is almost nothing (ride, sit, climb, walk, read) because
once the world is doing the work the cast does not have to mime.

## THE PARAMETRIC PRIMITIVES

A world costs one run, not one week, only if it is assembled rather than drawn.
So the shelf's job is to hold the parts that EVERY world is made of, not the
worlds themselves.

What follows is a prop-shape sketch per primitive: concrete enough that an
engineer can build it without another design pass, and deliberately NOT an
implementation. The `.tsx` is a later run. Anything built here registers in
`video-engine/src/lib/ASSET_MANIFEST.md` in the same commit, same as every other
asset.

Shared vocabulary, from what the library already uses:

```ts
import type {Pt} from './draw';                    // readonly [number, number]
import type {MaterialName} from './materials';     // brushedMetal | corrugated | tarmac | ...

export type VP = {x: number; y: number};           // the world's vanishing point

export interface WorldPalette {
  key: string;      // the lit face
  fill: string;     // the body
  shade: string;    // the turned-away face
  ink: string;      // outline
  accent: string;   // the one saturated colour the world is allowed
}
```

### 1. `Volume`: the interior box and its vanishing point

The most-repeated code in the library and therefore the first primitive.
`MainStreetBG`, `PaperOfficeBG` and `StairwellBG` each hand-rolled the same
one-point recession, including the same foreshortening curve
(`s(t) = (1 - t) ** 1.4`). Three copies of a perspective solver is three chances
to get it wrong, and `StairwellBG` did get it wrong on pass one (the stairs
closed with a flat bottom and read as a jagged mountain).

```ts
export const Volume: React.FC<{
  f: number;
  vp: VP;
  depth: number;                 // 0..1, how far into Z the box runs
  faces: Array<'left' | 'right' | 'floor' | 'ceiling' | 'back'>;
  ribs?: number;                 // structural repeats down the recession
                                 // (beams, rib bones, shelf uprights, seat rows)
  ribPitch?: number;             // 0..1, how fast rib spacing collapses with depth
  aperture?: {w: number; h: number; y?: number};  // a hole in the back face.
                                 // A world with no way out is a coffin; a world
                                 // with a lit exit you cannot reach is a joke.
  material?: MaterialName;
  palette: WorldPalette;
  tilt?: number;                 // deg. Off-axis is how you avoid shipping the
                                 // same symmetrical box twice in a week.
}>;
```

The three surfaces are drawn as separate LIT and SHADED faces. That is the rule
`TaperedCone` had to learn twice: without two distinct faces a form reads flat no
matter how correct the outline is.

### 2. `Passage`: corridor, duct, shaft, bore, chute

The connective tissue. Also the cheapest way to get motion without moving the
camera: scroll the segments toward the lens and the world travels while the shot
holds.

```ts
export const Passage: React.FC<{
  f: number;
  axis: 'in' | 'up' | 'down' | 'across';
  section: 'round' | 'square' | 'ribbed' | 'hex' | 'ductrect';
  length: number;                // in segments
  boreW: number;
  boreH?: number;                // omit for square section
  taper?: number;                // 0..1, far end narrower. The airline shaft.
  bend?: number;                 // lateral offset of the midpoint; uses draw.bent()
                                 // so it curves rather than kinking
  travel?: number;               // px/frame of segment scroll. Motion, no camera move.
  contents?: 'empty' | 'flow' | 'cable' | 'queue' | 'debris';
  endsIn?: 'light' | 'dark' | 'grate' | 'valve' | 'open' | 'wall';
  palette: WorldPalette;
}>;
```

### 3. Machinery, as three verbs

A machine is not a noun on this shelf. Almost every mechanism in an infuriating
American story is one of three motions: something turns, something reciprocates,
something carries. Build the three verbs and you can build any machine in one
afternoon by composing them.

Every one of them has a named FAILURE parameter, because the comedy is never in
the machine working. It is in the machine working perfectly at the wrong thing,
or failing in exactly one place.

```ts
export const Rotor: React.FC<{
  f: number; x: number; y: number; r: number;
  kind: 'gear' | 'fan' | 'drum' | 'turbine' | 'wheel' | 'reel';
  teeth?: number;
  rpm: number;                   // signed; a meshed neighbour must be opposite
  phase?: number;
  mesh?: Array<{x: number; y: number; r: number}>;  // driven neighbours, auto
                                 // counter-rotated. Two gears turning the same
                                 // way is the single most common cartoon tell.
  seize?: number;                // 0..1: grind, shudder, stop. THE comedy state.
  palette: WorldPalette;
}>;

export const Piston: React.FC<{
  f: number; x: number; y: number;
  boreW: number; stroke: number;
  angleDeg?: number;             // 0 = vertical
  rpm: number; phase?: number;
  linkage?: 'straight' | 'crank' | 'cam';
  deck?: React.ReactNode;        // what is standing ON the crown, moves with it
  misfire?: number;              // 0..1: skips a beat, then over-corrects
  palette: WorldPalette;
}>;

export const Conveyor: React.FC<{
  f: number;
  path: Pt[];                    // a spine. draw.ribbon() gives the belt thickness,
                                 // so a belt can climb, sag and turn without new code.
  beltW: number;
  speed: number;                 // px/frame along the path, signed
  rollers?: number;
  cargo?: Array<{at: number; node: React.ReactNode; mass?: number}>;  // at = 0..1
  jam?: number;                  // 0..1: cargo backs up against the head pulley
                                 // and the belt keeps running underneath it
  palette: WorldPalette;
}>;
```

### 4. `Flow`: fluid, and everything that behaves like fluid

Money, data, sewage, air, claims and callers all move the same way on screen, and
the two states that matter are FULL and DRY. A dry pipe is usually the joke.

```ts
export const Flow: React.FC<{
  f: number;
  path: Pt[]; width: number;
  substance: 'water' | 'oil' | 'money' | 'data' | 'air' | 'sludge' | 'paper';
  rate: number;                  // 0..1. 0 is a dry pipe with a working meter.
  turbulence?: number;
  leak?: Array<{at: number; rate: number}>;        // at = 0..1 along the path
  pool?: {y: number; level: number; capacity?: number};  // where it collects.
                                 // Accumulation is what makes a rate FELT; a
                                 // number on screen never will be.
  palette: WorldPalette;
}>;
```

Reuse `lib/fishcraft.tsx`'s `makeSpine()` for the surface travelling wave rather
than writing a second one. That function is a generic amplitude-grows-along-the-
spine wave generator that happens to have been written for a salmon; nothing in
it knows about fish. This is the clearest example of the whole doctrine: the
Alaska shelf's ENGINES generalize even when its SUBJECTS do not.

### 5. The countable primitives: `Stack`, `Queue`, `Grid`

The show is about quantities that got out of hand. A number on screen is a
caption; a physical count is a joke. These three are how a quantity becomes an
object.

```ts
export const Stack: React.FC<{
  f: number; x: number; baseY: number;
  unit: React.ReactNode; unitH: number;
  count: number;                 // ANIMATE THIS. A stack that grows during the
                                 // episode is the cheapest escalation on the shelf.
  lean?: number; sway?: number;
  topple?: number;               // 0..1, the button
  labelEvery?: number;           // tick marks up the side, so it can be read
}>;

export const Queue: React.FC<{
  f: number;
  path: Pt[];
  members: React.ReactNode[];
  advance: number;               // 0..1 along the path
  stalled?: number;              // frames since the head last moved; drives the
                                 // weight-shift, the neck-crane, the shuffle
  head?: 'window' | 'door' | 'wall' | 'sign' | 'nothing';
}>;

export const Grid: React.FC<{
  f: number; x: number; y: number;
  cols: number; rows: number; cellW: number; cellH: number; gap?: number;
  vp?: VP;                       // supplied = the grid RECEDES instead of lying
                                 // flat. A flat grid is a spreadsheet; a receding
                                 // one is a warehouse.
  cell: (i: number, j: number) => {node?: React.ReactNode; tint?: string; on?: number};
  sweep?: {t: number; axis: 'row' | 'col' | 'diag'};   // one cell at a time
  palette: WorldPalette;
}>;
```

### 6. `Signage` and `Paperwork`: the institution's two voices

The Institution has no face, ever. That rule is law and it is not up for
revisiting. So the institution speaks in exactly two registers: what it puts on
a wall, and what it puts in an envelope. These two primitives are the entire
vocabulary of an antagonist that cannot emote, which makes them the highest
leverage parts on this shelf.

```ts
export const Signage: React.FC<{
  f: number; x: number; y: number; scale?: number;
  kind: 'wayfinding' | 'gantry' | 'splitflap' | 'ticket-window' | 'notice'
      | 'exit' | 'nowserving';
  lines: string[];
  authority: 'official' | 'improvised' | 'legal';   // sets plate colour, mounting,
                                 // type weight. A laminated sheet taped over an
                                 // official sign is a whole character beat.
  flip?: number;                 // 0..1 drives split-flap / rolling shutter change
  contradicts?: string[];        // the second sign saying the opposite, mounted
                                 // directly below the first. Free joke, always true.
}>;

export const Paperwork: React.FC<{
  f: number; x: number; y: number; scale?: number;
  sheets: number;
  state: 'crisp' | 'fanned' | 'sprayed' | 'stamped' | 'shredded' | 'wafer';
  headline?: string;             // the ONE legible line
  bodyLines?: number;            // everything else is ruled texture. Real body
                                 // copy is unreadable at 1080x1920 at speed and
                                 // reads as noise, so it IS noise, deliberately.
  stamp?: {text: string; color: string; rot: number};
}>;
```

`Paperwork` composes `paper.tsx`'s existing `Sheet` (which already carries the
numeric shadow contract that makes paper read as a solid) and `PaperFiber`. It
does not replace them.

### 7. `ScaleFrame`: the cast made tiny inside something ordinary

The single most powerful move available to this show, and the one with the
sharpest failure mode: without a size reference in frame, a viewer reads a giant
cylinder as a normal-sized room and the entire gag evaporates silently. So the
reference is a required part of the primitive, not a note in a doc.

```ts
export const ScaleFrame: React.FC<{
  ratio: number;                 // cast height / world unit height.
                                 // 1 = normal, 0.04 = standing on a piston crown
  groundY: number;
  reference: React.ReactNode;    // REQUIRED. The one everyday object at known
                                 // human size in the same frame: a coin, a paper
                                 // cup, a shoe, a pen, a business card.
  children: React.ReactNode;
}>;
```

Second rule, from the same failure family: at small `ratio` the cast must
INTERACT with world geometry (stand on it, hold onto it, be moved by it) within
the first two seconds. A tiny figure floating in front of a big thing reads as a
compositing error.

### 8. `WorldRig`: the lighting each world implies

Every primitive above implies a light. A duct is lit at its two ends and nowhere
else. A machine cavity has one hot practical and no ambient at all. A concourse
is flat overhead daylight with no shadow to hide in, which is exactly why
concourses feel the way they do. Get this wrong and a correctly built world still
reads as a cardboard model.

```ts
export type WorldLight =
  | 'interior-fluorescent'   // Volume + Grid + Paperwork. Flat, greenish, no mercy.
  | 'machine-cavity'         // Rotor/Piston. One practical, hard falloff, no fill.
  | 'duct-throw'             // Passage. Light at the ends only, black in the middle.
  | 'liquid-caustic'         // Flow. Moving light on every surface above the line.
  | 'concourse-daylight'     // Volume + Signage. Overhead, shadowless, endless.
  | 'server-glow'            // Grid. Edge-lit rows receding, no ambient.
  | 'street-sodium'          // exteriors, the one exterior rig worth keeping
  | 'exam-room';             // the small cold interior with one thing in it

export const WorldRig: React.FC<{
  f: number;
  rig: WorldLight;
  amount?: number;               // 0..1 crossfade, so a world can change state
  sources?: Array<{x: number; y: number; r: number; color: string; intensity: number}>;
  children?: React.ReactNode;
}>;
```

`WorldRig` wraps `lighting.tsx`'s `NightGrade` source model rather than
reimplementing it. That model's best property is that a scene must REGISTER a
light before anything is allowed to glow, which turns a palette convention into a
property of the scene graph that a renderer cannot silently violate. Keep it.

## WHAT OF THE PORTED SHELF IS ACTUALLY REUSABLE

Honest accounting. The Alaska assets are paid-for craft and one day a story will
be about Alaska. They stop being the DEFAULT. They do not stop existing, and
nothing below gets deleted.

### Genuinely generic, use freely, these are the kit

- `lib/draw.ts` - `ribbon`, `spline`, `bent`, `edge`, `rot`, `lerp`. Pure
  geometry that knows nothing about anything. Every primitive above is built on
  it. A belt, a hose, a cable, a queue rope and an arm are all one ribbon.
- `lib/lighting.tsx` - `tones`, `FormGradient`, `RimLight`, `ContactShadow`,
  `GradeLayer`, `MotionBlur`, `NightGrade`, `HazeOverlay`, `IRVision`,
  `WaterColumn`. A light model has no nationality.
- `lib/materials.tsx` - all eight overlays. `brushedMetal`, `corrugated`,
  `tarmac`, `granite`, `planks` are load-bearing for machine and warehouse
  worlds. `bark`, `snowpack`, `ice` are narrower but still just textures.
- `lib/motion.tsx` - `vitals`, `entrance`, `followThrough`, `accentKick`,
  `squashStretch`, `idleSway`, `anticipate`, `holdPayoff`, `staggerDelay`,
  `ChipShadow`. Animation principles, fully portable.
- `lib/stage3d.tsx` - `Stage3D`, `Plane`, `Extrude`, `Atmosphere`, `Solidify`,
  `Card`, `CastShadow3D`. **The most under-used file in the repo and the actual
  backbone of world building.** A shared virtual camera with real perspective
  parallax is exactly what "put the cast inside a thing" needs, and it has been
  sitting unwired since 2026-07-20 because there were only Alaska sets to point it
  at. `Volume` and `Passage` should be authored against it from day one.
- `lib/fishcraft.tsx` `makeSpine()` and `bodyGeom()` - written for a salmon,
  generic in fact. A travelling wave along a spine drives hoses, belts, cables,
  bunting, tubing and anything that snakes. Take the engine, leave the fish.
- `lib/FX.tsx` - `SpeedLines`, `ImpactStar`, `PaperStorm`, `ZoomVignette`,
  `SmellRings`, `ScanReticle`. `PaperStorm` in particular is a bureaucracy asset
  that happened to be born in Alaska.
- `lib/paper.tsx` - `PaperFiber`, `Sheet`, `TaperedCone`, `StateLetter`,
  `FullTapeMachine`. Not Alaskan at all. `TaperedCone` is a real 3/4 cone solver
  and is reusable as a horn, hopper, funnel, nozzle or chute.
- `lib/records.tsx` - `RecordsMachine`, `ThreePipeCutaway`. Generic bureaucracy
  machines. `ThreePipeCutaway`'s idea (a thesis staged as a physical ABSENCE) is
  the template for the data-breach world above.
- `lib/props.tsx` - `StatCard`, `Nameplate`, `SwingSign`, `GearLever`,
  `MeasuringChain`, `PenAndDocument`, `TallyCounter`, `BoundaryReveal`.
  `TallyCounter` is the best generic prop on the shelf: a physical count you can
  hold. `BoundaryReveal` traces any closed path you hand it and is fully
  parametric already.
- `lib/kit.tsx` - `MachineShadow` (the Institution, re-liveried per episode),
  `BoxLabel`, `StatBurst`, `FatArrow`, `Stamp`, `burst()`.
- `lib/brand.tsx` - the whole file. It is the show, not the place.
- `biomes.tsx` `StairwellBG` - built 2026-08-02 for a housing story and the only
  ported set with nothing Alaskan in it. It is the model for what a set on this
  shelf should look like.

### Place-locked or subject-locked. Kept, never the default

- `lib/fauna.tsx`, all twenty-one species plus `SledDogTeam`. The best craft in
  the repo and almost never castable in a national story. **Do not generalize
  these and do not delete them.** A moose in a story that is not about a moose is
  the exact failure this file exists to end.
- `lib/vehicles.tsx` - `Snowmachine` is hard-locked. `BushPlane` and
  `FishingBoat` are regionally strong but usable when a story is genuinely about
  small aviation or commercial fishing.
- `biomes.tsx` - `AuroraNightBG`, `TundraBG`, `FjordBG`, `GlacierBG`, `RiverBG`,
  `OilfieldBG` are Alaskan exteriors. `AnchorageSkylineBG` is the hardest-locked
  asset in the library and carries its own usage rules.
  **Generalization direction:** `MainStreetBG` and `OilfieldBG` both contain a
  correct one-point recession solver buried in episode-specific art. Lift the
  solver into `Volume`; leave the art where it is.
- `lib/kit.tsx` - `AlaskaMini` (locked by name and shape), `Sourdough`, `Cell`,
  `Vale`, `SatelliteEye`, `Petrel`, `PetrelDock`. Not all Alaskan, but all
  story-locked heroes from the weekly. **Generalization direction:** the
  characterized-object pattern they share (one expressive camera eye as the
  entire emotional tell, an `emotion` enum, `accent` for VO reactivity, built
  against `vitals()`) is a genuinely reusable authoring recipe and should be
  documented as one. The specific machines are not.
- `lib/sensors.tsx` - `ListeningMooring`, `SeismicStation`, the duplicate
  `SatelliteEye`. Subject-locked instruments. The `SeismicStation` gramophone
  horn is a `TaperedCone` in a hat, which is the reuse worth remembering.
- `lib/props.tsx` - `SurveyStake`, `TrailPost`, `VideoWeir`. Land and fisheries.
- `lib/Character.tsx` - superseded as the CAST rig by `Figure.tsx` and
  `cast.tsx`, still serving crowd figures and the back catalogue. Its outfit list
  (parka, trapper, hood) is where the Alaska default is most likely to sneak back
  in through a background extra.

## THE RULE THAT REPLACES "CAST FROM THE SHELF"

Old rule, still true and still load-bearing for the CAST: the cast is a lock, not
a redraw. Ray and Dee never change. That has not moved.

New rule for everything else:

> **Cast the PRIMITIVES from the shelf. Build the WORLD fresh, every episode.**

A run that reuses a whole biome unchanged has almost certainly skipped the
derivation procedure, because the odds that today's mechanism has the same inside
as last week's are low. `ledger/artwork.json` already enforces divergence on hero
structure, atmosphere, palette, continuity device and camera language; the world
is now the sixth axis and the most important one.

## ANTI-PATTERNS, each of which has already cost this show an episode

- **The world is a backdrop.** Nobody touches it, nothing in it moves, it could
  be swapped for a grey wall. Fails the swap test. This is what shipped in cases
  0001 and 0002.
- **The world is a location.** An office where two people discuss the mechanism,
  rather than the inside of the mechanism. The most common near-miss, and the
  most seductive because it is easy to build.
- **The world is a pun.** The gag is the name of the set. It lands at second two
  and there are fifty-eight left.
- **The world is a diagram.** Labels, arrows and callouts explaining the
  mechanism. That is the educational show we are deliberately not making. If the
  world needs a label to be understood, build a clearer world.
- **Scale reversal with no reference object.** The viewer reads a normal room and
  the whole conceit is invisible. Covered by making `reference` required.
- **Nine shots at one camera height on one set.** Flagged by the 2026-07-26
  panel. A built world with a locked camera is a diorama; move the camera THROUGH
  it, because that is the payoff for having built an inside at all.
- **The world contradicts a cleared claim.** The most dangerous one, because it
  is funny and wrong. The world stages what the fact-check licensed and not one
  inch further. Savage and sourced is defensible; savage and wrong is a dead
  channel.
