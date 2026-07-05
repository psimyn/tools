# drawa7

An A7 page (74 × 105 mm) rendered on screen at actual physical size, filled by
the live camera and overlaid with centre gridlines. Point the camera at a
picture, tap the page to freeze the frame, and tap again for a blank page with
just the gridlines — a reference for copying the picture onto real A7 paper.

## Prompt

> drawa7, app that renders a7 page at actual size, with centre gridlines. It
> activates the camera and then you can tap the camera to pause it and then it
> just shows the grid lines. It's used so that you can then draw stuff based
> on a picture.

## Notes

- Single self-contained HTML file: `getUserMedia` for the camera, inline SVG
  for the gridlines, no build step or dependencies.
- Tapping the page cycles through three states: **Live** (camera feed) →
  **Frozen** (paused frame, grid on top) → **Grid only** (white page with
  graph-paper-blue lines) → back to Live. Freezing is just `video.pause()`,
  so no canvas capture is needed.
- The page is sized in real millimetres via CSS px (`96 / 25.4` px per mm).
  Because screens report their density imperfectly, the **Size** button opens
  a calibration screen: hold a standard bank card (ISO ID-1, 85.6 × 53.98 mm)
  against an outline and drag a slider (80–120 %) until they match. The scale
  factor persists in `localStorage`.
- **Grid** cycles the line density: Centre (the crosshair through the middle),
  Quarters, or Thirds. The centre lines are drawn heavier than the minor ones.
  Over video the lines are yellow with a dark halo for visibility; in
  grid-only mode they turn graph-paper blue on white.
- **Rotate** flips the page between portrait (74 × 105) and landscape
  (105 × 74). **Flip** switches front/rear cameras; the front camera is
  mirrored so it reads like a mirror.
- The video fills the page with `object-fit: cover`, so the picture is cropped
  to the A7 aspect rather than distorted.
- Requires a secure context (HTTPS or `localhost`) for camera access — the
  page surfaces a clear error message if `getUserMedia` is unavailable or
  denied.
