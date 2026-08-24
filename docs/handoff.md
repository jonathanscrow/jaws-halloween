# JAWS Halloween Projection — Handoff

## The concept

Front-yard *Jaws* display. Jonathan as Brody, Kirby as Quint, half-eaten boat on the
left, garage door on the right as a projection surface. A camera watches the walkway;
trick-or-treaters see themselves on the garage door as a rigged shark swimming in an
ocean backdrop — arms drive the pectoral fins, mouth drives the jaws, distance drives
the shark's size.

**Key decision:** the camera is input only. Nothing from the camera is composited or
displayed. The output is a clean rendered scene — ocean loop plus a puppeteered shark.
No background segmentation, no masking, no edge artifacts, no lighting sensitivity in
the output.

---

## Settled decisions

| Question | Decision | Why |
|---|---|---|
| Segmentation vs. pure render | Pure render | No mask artifacts; art can be as good as you want |
| Resolution | 1080p out, 720–1080p tracking | Framerate matters far more than resolution at 30ft |
| Machine | Mac Mini M4 | Bolt it to a shelf and forget it; laptop stays free for firefighting |
| Camera transport | Capture card, **not** NDI | NDI adds latency + a decode step; latency kills the illusion |
| Output layer | OBS | Browser source + media source + hotkey to a safe fallback scene |
| Shark orientation | Side profile only, never turns | Iconic silhouette; rotation estimates get noisy and flicker |
| Direction flip | Horizontal sprite flip w/ hysteresis | Flip only after ~0.5s of consistent travel, or it twitches |
| Upper jaw | Does **not** rotate as a hinge | Rotating the head tears a seam against the body |
| Multi-person | Build for 2 from day one | Two kids arrive together constantly; retrofitting in late Oct is misery |

---

## Solved rig numbers

All parts share one **1672 × 941** canvas and are pre-registered. Draw each at 0,0 and
apply only the transforms below. Stacking them untransformed reproduces the shark exactly.

### Draw order (back to front)

1. `Pectoral_Fin_Rear` (far fin)
2. `Tail_Fin`
3. `Blank_Body`
4. `Dorsal_Fin`
5. `Black_part_of_mouth`
6. `Lower_Jaw`
7. `Upper_Jaw`
8. `Pectoral_Fin` (near fin)

### Jaws — solved from open/closed export pairs

| Part | Pivot | Angle at full gape | Fit (IoU) |
|---|---|---|---|
| Lower jaw | (402.2, 563.7) | +25.0° CCW | 0.9942 |
| Upper jaw | (577.1, 115.8) | −6.0° CCW | 0.9990 |

The upper-jaw pivot sits far above the shark, so it's effectively a slight tilt plus a
translation rather than a joint. The numbers interpolate exactly — just don't reason
about that point as a hinge.

**Gape mapping:** dead zone below 0.15 of mouth-open, then ramp fast, clamp at 1.0.
A small mouth-open should give a big satisfying chomp; a slightly-open mouth must not
give a permanently ajar shark.

**Do not exceed t = 1.0.** At ~1.35 the background leaks through the upper tooth gaps
and the rear mouth corner. Enlarge the black mouth blob first if you want more.

### Pectoral fin — bend deform, not rigid rotation

The base stays attached while the fin curves along its length. Implemented as a
progressive rotation: each point rotates by `maxAngle × (root + (1−root) × s^ease)`
where `s` is normalized distance along the base→tip axis.

```
pivot        (571, 556)     midpoint of the attachment edge
tip          (724, 781)
ease         0.75           spreads the bend evenly; higher = whippy + skinny
root         0.20–0.85      how much the shoulder itself swings
hold         0.10           first 10% rigid so the shoulder stays welded
range        −20° to +60°   asymmetric: up-swing is what kids will spam
```

**Why the pivot is at (571, 556):** the attachment edge runs (474, 535) → (668, 578),
about 200px long. An earlier pivot at (505, 545) sat on the *front* corner, so root
rotation swung the rear corner through a 200px arc — ~80px of drop at 40% root, which
read as the fin peeling off the body. Mid-edge halves the radius and splits the travel.

**Far fin:** same treatment, pivot +40 in x → (611, 556). Lag it ~6% of a cycle behind
the near fin. That overlapping-action delay is most of why it reads as alive.

### Tail

Rotate about approximately **(1395, 455)** — *eyeballed, not solved*. ±13–15°.
Do **not** attempt real lateral beat with perspective; every 2D cartoon cheats it as
in-plane rotation and it reads as swimming instantly.

Drive the swish off horizontal movement speed: faster walk = faster beat, standing
still = slow idle sway.

### Idle animation

Three sine waves at periods that never resync — e.g. 3s, 4.5s, 7s. Slow tail sway,
gentle vertical bob, small rotation so the nose tips a few degrees. Without this a
still kid gets a dead shark and the illusion drops.

### Depth / scale

Shoulder width in pixels is a free depth proxy from the pose skeleton. Wider shoulders =
closer = bigger shark. Scale the whole sprite off that number so the shark fills more of
the door as they approach — the payoff builds right as they reach the boat.

---

## Open items

### Photoshop (needs a laptop)

- [ ] **Trim the black mouth blob** so it hides fully behind the closed jaws. Currently
      it pokes out below the jaw at rest. Worked around in the demo by fading the blob
      in with gape, but that's a patch.
- [ ] **Lock the fin attachment across the three hand-warped poses.** Measured drift:
      backward centroid x=605 (span 479–700), rest x=536 (474–633), forward x=531
      (478–595). The forward pose also sits ~25px high. In motion this reads as the fin
      sliding along the flank rather than pivoting at a joint. Pin the rear corner near
      (668, 578) and the front near (474, 535) in all three.
- [ ] **Alpha cleanup.** `Blank_Body` has ghost alpha (values 1–14) smeared across the
      whole canvas; real content stops at x=1516. Threshold anything under 20 to zero.
- [ ] **Defringe.** ~5,000 semi-transparent pixels on the body, 1,200–2,200 on each
      smaller part — residue from the magenta key. Magenta fringe becomes dark halos
      under a projector.
- [ ] **Normalize outline weights.** Tail and fin outlines are heavier than the body's;
      once each part is scaled the mismatch grows.
- [ ] **Whole-shark fallback frame** for OBS when tracking drops.
- [ ] **Second shark** — same art at ~90% scale with the grey nudged browner or bluer.
      Do NOT regenerate; a second generation reopens the style-matching fight.

### Exports needed

- [ ] **A swished tail position** (same trick as the jaws — one rotated copy on the same
      canvas). That lets the pivot be solved exactly instead of eyeballed.

### Hardware measurements

- [ ] Projector throw distance to the garage door, and door width. Determines whether
      the projector actually fills the door. The one constraint software can't fix.

### The actual build

- [ ] **Run `tracking-spike.html` first.** Grey box, no art. Three numbers decide the
      project: FPS above 24, poses reading 1 without flickering to 0, jitter under
      ~2.5px. Needs https or localhost — `python3 -m http.server 8000`.
- [ ] Ocean loop — seamless stock footage.
- [ ] The real page: MediaPipe Pose + Face Landmarker, the rig above, ocean backdrop.
- [ ] OBS scene with browser source + hotkey fallback.
- [ ] **Test outdoors two weekends before Halloween.**

---

## Lighting

The projector wants darkness on the door; the tracker wants light on the kids. Different
places, so both are achievable. Aim the walkway light low and across, ideally from the
side, so it grazes kids at chest height and never spills onto the projection surface.
Barn doors or cardboard flags on the fixture. Point the camera *at* the lit path rather
than back toward the door.

---

## Art asset generation notes

If more parts are ever needed:

- Generate on **solid magenta #FF00FF**, never ask for transparency — image models paint
  literal checkerboards because they've learned checkerboard *means* transparent.
- Always attach the reference shark and repeat the palette hexes verbatim:
  `#5A6570` dorsal, `#F2EDE4` belly, `#1E2A33` outline, `#14181C` eye, `#47515B` gills,
  `#2A2F35` mouth interior.
- **Never generate head parts in isolation** — they come back internally consistent and
  mutually incompatible. Generate the whole shark in the needed pose, then cut it up.
  Fins and tail are fine in isolation; they're simple shapes with clean attachment edges.
- Shark teeth are broad triangles, packed edge to edge, no gaps, nearly uniform height.
  Asking for irregular heights and missing teeth produces *crocodile* teeth.

---

## Script notes (for the night)

Brody is Jonathan's part, so "You're gonna need a bigger boat" is his — deadpan, as a
small child walks up. "Get out of the water!" while throwing candy. "Smile, you son
of a—" as a closer, for adult audiences only.

Kirby as Quint: the fingernails-on-chalkboard entrance, "This shark, swallow you whole,"
and "Here's to swimmin' with bow-legged women" as a toast with a bottle.
