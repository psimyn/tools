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
  Because screens report their density imperfectly, the **Size** button enters
  an in-place calibration mode: a square-cornered bank-card outline (ISO ID-1,
  85.6 × 53.98 mm) is drawn centred over the live page, and the bottom bar
  swaps to a slider (60–140 %, with ± buttons for 0.5 % steps). The page and
  outline resize together, so it can be matched against a real card — or the
  page against a real A7 sheet — while watching the camera. The scale factor
  persists in `localStorage`. Note a bank card is *wider* than A7 (85.6 mm vs
  74 mm), so the outline overhangs the page sides.
- If the page is larger than the viewport (landscape on a narrow phone, or a
  scaled-up calibration), the stage scrolls so it can be panned into view.
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
