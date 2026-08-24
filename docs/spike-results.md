# Tracking-spike results & tuning notes

## Run log

### 2026-08-24 — JCROW-ROZ (ROG Strix, Windows, strong GPU) — NOT the target machine
First run, lite model, 720p, no smoothing:

| Gate | Reading | Verdict |
|---|---|---|
| Frame rate | 207 fps render | PASS (bar 24) — but that's render-loop; tracking runs at webcam rate |
| Poses locked | 1 · steady | PASS |
| Jitter (raw) | 37.44 px (3s peak 51.11) | FAIL (bar 2.5) — raw, unsmoothed lite-model noise |

Supporting: detect 9.3 ms, shoulder 561 px (close range).

Observations:
- Flicker is worse at close range, better further away → tracker likes full-body framing
  (close range crops the lower body and destabilizes the pose). Lines up with the depth-scale
  design where the shark grows as they approach.
- With **no person in frame** the detector misfires (phantom poses) on the default 0.5
  confidence thresholds.

Decision: raw jitter of 37 px is expected for the lite model with no smoothing — the fix is
smoothing, not chasing a lower raw number. Added One-Euro smoothing + confidence/visibility
controls to the spike (v2).

**Still owed:** re-run on the **Mac Mini M4** (the actual display machine). FPS does NOT
transfer from the ROZ; jitter and misfire behavior do.

## The spike controls (v2)

- **Model** — lite / full / heavy. Default full. Heavy is steadiest (lowest raw jitter),
  lite is fastest. On a machine with FPS headroom, prefer full/heavy.
- **Smoothing** (One-Euro) — on by default. This is the number that matters for the real shark.
  - **min-cutoff** (Hz): lower = smoother but more lag. Start ~1.0.
  - **beta**: higher = less lag on fast motion (fin swings, chomps). Start ~0.007, raise if
    the "lag when moving" number feels too high during quick moves.
  - Watch the **raw vs smoothed vs lag** subline: tune smoothed under 2.5 px while keeping
    lag-when-moving low enough that the fins/jaws feel responsive.
- **min-confidence** (rebuilds landmarker): raises detection/presence/tracking thresholds off
  the permissive 0.5 default. Higher = fewer phantom detections. Start 0.6, raise toward
  0.75 if empty-frame misfires persist.
- **visibility gate** (live): drops any pose whose key landmarks (nose, shoulders, hips)
  average below the gate. Second line of defense against phantoms. Start 0.5.
- **Frame rate** gate now evaluates **tracking fps** (actual pose-update rate), shown next to
  the render fps.

## Anti-misfire recipe (empty walkway must show NO shark)
Raise min-confidence (0.7–0.75) + visibility gate (0.6–0.7) until an empty frame reliably
reads 0 poses, then confirm a real person still locks instantly. This is critical for the
display: a phantom shark on an empty walkway breaks the gag.
