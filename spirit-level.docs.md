# Spirit Level

A browser-based bullseye + bar spirit level that uses the `DeviceOrientation`
API to show how level your phone (or tablet) is.

## Prompt

> plain html/js spirit level

## Notes

- Works in **both postures**: lay the phone flat to use the bullseye, or hold
  it up (portrait *or* landscape) to check a wall or picture frame against the
  horizontal bar.
- Auto-detects flat vs upright from the gravity vector (|gᵥz| > 0.5 → flat).
  In upright mode only the horizontal roll axis is meaningful, so the bullseye
  slides along its centreline like a single-axis vial.
- All angles are computed from the gravity vector in the *view* frame rather
  than raw β/γ, so it behaves correctly across every `screen.orientation.angle`
  (0 / 90 / 180 / 270).
- iOS 13+ permission prompt surfaced via an "Enable motion sensors" button
  when `DeviceOrientationEvent.requestPermission` exists.
- Exponential smoothing on the device-frame gravity vector, so screen-rotation
  changes don't produce a jump in the smoothing state.
- Bubble turns green when total tilt is within `1.0°` of level.
- Separate calibration offsets per mode, persisted in `localStorage` — zeroing
  the level while flat doesn't affect the upright reading and vice versa.
- No build step, no dependencies — a single `.html` file.

Open the page on a phone, or use the device-orientation emulator in Chrome
DevTools on desktop.
