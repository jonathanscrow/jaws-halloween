# JAWS Halloween Projection

Front-yard *Jaws* display: trick-or-treaters walk up and see themselves on the garage
door as a rigged shark swimming in an ocean backdrop — arms drive the pectoral fins,
mouth drives the jaws, distance drives the shark's size. The camera is **input only**;
nothing from it is displayed. Output is a clean rendered scene (ocean loop + puppeteered
shark), so there are no masking or edge artifacts.

## What's here

- **`jaws.html`** — the show. 1920×1080 output: procedural ocean (no video file needed)
  plus the rigged shark, one per person (up to 2). See "Running the show" below.
- **`tracking-spike.html`** — the go/no-go harness. Grey box, no art. Answers the three
  numbers that decide the project: tracking **FPS > 24**, **poses steady** (no flicker to
  0), and **jitter < 2.5 px** (smoothed) while holding still. Includes One-Euro smoothing,
  raw/smoothed/lag readouts, and misfire controls (min-confidence + visibility gate).
- **`index.html`** — landing page linking to the spike (so the Pages root isn't a 404).
- **`docs/handoff.md`** — concept, settled decisions, the solved rig numbers (jaw pivots,
  fin bend deform, tail, idle, depth/scale), open items, lighting, and art-gen notes.
- **`docs/spike-results.md`** — run log + tuning-knob reference + the anti-misfire recipe.
- **`art/`** — shark part PNGs (1672×941 shared canvas). See `art/README.md`.
- **`scripts/`** — rig solvers / helpers. See `scripts/README.md`.
  `clean_parts.py` rebuilds `art/` from the Photoshop PNG exports (alpha cleanup + defringe).

## Running the show

Open `https://jonathanscrow.github.io/jaws-halloween/jaws.html` (or `jaws.html?demo` for a
fake visitor with no camera). It starts the camera on its own; allow camera access once.

- **F** fullscreen · **D** settings panel · **H** hide the cursor.
- The settings panel picks the camera, mirrors left/right, and tunes where the shark sits,
  how big it gets near vs far, how long it waits before appearing and holds through
  dropouts, and the jaw sensitivity. Settings save in that browser.
- **Arms** drive the fins (down = tucked, overhead = full lift). **Distance** drives size,
  from torso height, so turning side-on doesn't shrink the shark. **Mouth** drives the jaws
  when the face is close enough to read; farther out the shark chomps on its own every few
  seconds (toggle in settings).
- The shark appears after 12 frames in a row with a person (0.4 s) and holds through gaps
  of up to 10 frames. On the test clips that removed every blink and every phantom.
- Run it in **Chrome fullscreen on the projector**. OBS browser sources don't get camera
  access by default; if OBS is the output layer, window-capture the Chrome window.
- No internet = no tracker (MediaPipe and its models load from a CDN), but the ocean still
  runs. Keep the Mac Mini online on the night.

## Running the spike

The camera needs **https or localhost**. Two ways:

- **GitHub Pages (https, any machine, no server):** enable Pages (Settings → Pages →
  Deploy from a branch → `main` / root), then open
  `https://jonathanscrow.github.io/jaws-halloween/tracking-spike.html`.
- **Locally:** `python3 -m http.server 8000` in the repo, then
  `http://localhost:8000/tracking-spike.html`.

MediaPipe (tasks-vision) loads from a CDN on first run, so the machine needs internet
once; the browser caches it afterward.

## Not in git

The ocean-loop video and any PSD source files are intentionally git-ignored (see
`.gitignore`) — big binaries don't belong in a plain repo. Keep those in Dropbox/Drive
or Git LFS and reference them by path.

## Target machine

The display runs on a **Mac Mini M4**. FPS numbers measured on other machines don't
transfer; jitter and misfire behavior do. Re-run the spike on the Mini before trusting
the frame-rate gate.
