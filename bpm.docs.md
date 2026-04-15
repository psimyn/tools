# BPM

A minimal BPM detector. Tap the big circle to set a tempo, enable the mic to
pick a beat out of audio, or do both at once — taps guide the audio estimate
and snap it to the right harmonic.

## Prompt

> bpm, a bpm detector. can tap button, or listen to mic. if listening to mic and tapping, combine the inputs or use the taps to guide transient detection. very minimal UI. basically just a button and a number

## Notes

- **Tap mode**: rolling median of the last 16 inter-tap intervals, with a 2 s
  reset gap so you can start over cleanly. Median, not mean — so one stray
  tap doesn't poison the estimate. Space bar also taps, for desktop.
- **Mic mode**: spectral-flux onset detection on `getFloatFrequencyData`
  (half-wave-rectified bin-to-bin difference), feeding an onset-strength
  envelope. Autocorrelation of that envelope over lags corresponding to
  50–210 BPM gives the period, with parabolic interpolation around the peak
  for sub-sample precision. The lag-to-BPM conversion uses the *measured*
  `requestAnimationFrame` rate so it's correct on 60, 90, or 120 Hz displays.
- **Combined**: when you tap while listening, the autocorrelation peak is
  snapped to the nearest common harmonic of the tap BPM (`×½, ×1, ×1.5, ×2,
  ×⅓, ×3`), which cheaply fixes the usual "locked on the half-bar" failure.
  The displayed number is a weighted blend (60 % tap, 40 % mic), and turns
  green when the two sources agree within 3 BPM.
- No build step, no dependencies — a single `.html` file.
