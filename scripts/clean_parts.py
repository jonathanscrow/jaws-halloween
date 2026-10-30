"""Clean the exported shark parts and write them into art/ under rig names.

    python3 scripts/clean_parts.py "<folder with the Photoshop PNG exports>"

Two fixes from docs/handoff.md "Open items", done in code instead of Photoshop:
- Alpha cleanup: ghost alpha (1-19) smeared across the canvas is zeroed.
- Defringe: semi-transparent edge pixels still carrying the magenta key are
  recoloured to the outline colour #1E2A33, so they don't project as halos.
Registration is untouched: every part stays on the shared 1672x941 canvas.
Needs numpy + opencv-python.
"""
import sys
from pathlib import Path

import cv2
import numpy as np

# export name -> rig name (the CLOSED jaws are the rig; open poses come from rotation)
PARTS = {
    "Pectoral Fin Rear": "Pectoral_Fin_Rear",
    "Tail Fin": "Tail_Fin",
    "Blank Body": "Blank_Body",
    "Dorsal Fin": "Dorsal_Fin",
    "Black part of mouth": "Black_part_of_mouth",
    "Lower Jaw Closed": "Lower_Jaw",
    "Upper Jaw Closed": "Upper_Jaw",
    "Pectoral Fin": "Pectoral_Fin",
}
OUTLINE_BGR = (0x33, 0x2A, 0x1E)
GHOST = 20

src = Path(sys.argv[1])
out = Path(__file__).resolve().parent.parent / "art"
for export, rig in PARTS.items():
    im = cv2.imread(str(src / f"{export}.png"), cv2.IMREAD_UNCHANGED)
    assert im is not None and im.shape == (941, 1672, 4), export
    a = im[:, :, 3]
    ghost = (a > 0) & (a < GHOST)
    a[ghost] = 0
    b, g, r = (im[:, :, k].astype(int) for k in range(3))
    fringe = (a > 0) & (a < 255) & (r - g > 40) & (b - g > 40)
    im[fringe, :3] = OUTLINE_BGR
    im[a == 0, :3] = 0
    cv2.imwrite(str(out / f"{rig}.png"), im)
    print(f"{rig:22s} ghost zeroed {ghost.sum():5d}   fringe recoloured {fringe.sum():5d}")
