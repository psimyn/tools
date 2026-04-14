# Protractor

Measure real-world angles through your device's camera. The live video is
shown full-screen with an interactive protractor overlay — drag the vertex and
two arm endpoints to align the green arms with the edges you want to compare,
and the interior angle between them is read off directly.

## Prompt

> webcam with protractor overlay

## Notes

- Single self-contained HTML file: `getUserMedia` for the camera, inline SVG
  for the overlay, no build step or dependencies.
- Three draggable handles: a yellow **vertex** plus two white **arm endpoints**.
  Dragging the vertex translates the whole protractor; dragging an arm endpoint
  only moves that arm.
- The tick ring is a 180° protractor aligned so **0° runs along arm 1** and
  the sweep goes toward arm 2, so the reading is always correct regardless of
  which side of the vertex arm 2 is on. Major ticks every 30° (labelled), minor
  ticks every 10°, fine ticks every 5°.
- Interior angle is computed from `atan2` of each arm and shown to one decimal,
  both at the midpoint of the arc and in the bottom control panel.
- **Flip** toggles between front and rear cameras (`facingMode: user` /
  `environment`); the front camera is mirrored so it reads like a mirror.
- **Reset** recentres the protractor on the viewport.
- Pointer Events (not touch events) so the same code handles mouse, touch and
  stylus; `touch-action: none` on the overlay prevents scroll/zoom from eating
  drags.
- Requires a secure context (HTTPS or `localhost`) for camera access — the
  page surfaces a clear error message if `getUserMedia` is unavailable or
  denied.
