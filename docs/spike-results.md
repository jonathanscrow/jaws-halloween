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

### 2026-08-24 (later) — Mac, real camera via zowiecam
Full ingest chain proven end-to-end:

```
zowiecam (NDI/RTSP, mDNS zowiecam-44361.local) → OBS Media Source (RTSP)
    → OBS Virtual Camera → spike (Camera dropdown = "OBS Virtual Camera")
```

- Tracking runs off the real camera. **Small but perceptible delay** in the
  RTSP→OBS→virtual-cam chain — "tiny, not horrible," but enough that we want to try a
  capture card. This is the network-transport latency the handoff warned about, so the
  "capture card, not NDI/network" call is holding up.
- Getting in was a saga: the camera didn't appear until **NDI was enabled** in its web UI
  (`http://zowiecam-44361.local/#/login`, creds printed on the casing). RTSP ended up the
  path that worked into OBS.
- NOTE the zowiecam is a **network camera** (RTSP/NDI). A capture card needs an **HDMI/SDI**
  source — so the capture-card test only applies if the zowiecam has an HDMI out, OR if it's
  run through a different HDMI camera. Lowest-latency of all would be a **USB-UVC** camera
  straight into the Mac Mini (spike sees it directly, no OBS hop).

**Next:** lower-latency ingest test — capture card (if there's an HDMI source) and/or a
plain USB-UVC webcam, compared against this RTSP baseline using the spike's lag readout.

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

## Ingest chain (how to get a camera into the spike)
- **Best / lowest latency:** USB-UVC camera or capture card (HDMI→USB) straight into the Mac.
  It shows up directly in the spike's Camera dropdown — no OBS, fewest hops.
- **Network camera (zowiecam):** RTSP into OBS (Media Source) → OBS **Start Virtual Camera**
  → spike Camera dropdown = "OBS Virtual Camera". Works, but adds delay. Set OBS canvas to
  720p/30–60 (Settings → Video) since the virtual cam inherits the canvas.

## Anti-misfire recipe (empty walkway must show NO shark)
Raise min-confidence (0.7–0.75) + visibility gate (0.6–0.7) until an empty frame reliably
reads 0 poses, then confirm a real person still locks instantly. This is critical for the
display: a phantom shark on an empty walkway breaks the gag.
