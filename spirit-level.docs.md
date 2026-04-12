# Spirit Level

A browser-based bullseye + bar spirit level that uses the `DeviceOrientation`
API to show how level your phone (or tablet) is.

## Prompt

> plain html/js spirit level

## Notes

- Bullseye vial in the centre plus a horizontal bar for roll only.
- Compensates for screen orientation so "roll" always means left–right of the
  current view, even in landscape.
- iOS 13+ permission prompt is surfaced via an "Enable motion sensors" button
  when `DeviceOrientationEvent.requestPermission` exists.
- Exponential smoothing (`SMOOTH = 0.18`) to stop bubble jitter.
- Bubble turns green when total tilt is within `1.0°` of level.
- Calibrate / Reset buttons with offsets persisted in `localStorage`.
- No build step, no dependencies — a single `.html` file.

Open the page on a phone, or use the device-orientation emulator in Chrome
DevTools on desktop.
