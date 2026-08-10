# Clip

A video clip editor. Drop a video file in, play it, mark the clip with the
start/end buttons (or drag the amber handles on the timeline), preview it,
and save the clip — all in the browser, nothing uploaded anywhere.

## Prompt

> clip - an app you can drop a video file into and play it, then there is a start clip and end clip button, then you can save the clip

## Notes

- **Trimming**: a custom timeline under the player shows the clip region with
  draggable in/out handles; "Start clip" / "End clip" (or <kbd>I</kbd> /
  <kbd>O</kbd>) mark from the playhead. Space toggles play, arrow keys seek
  (shift for 50 ms nudges), and "Preview clip" plays just the marked region.
- **Saving**: the clip region is played through once and re-encoded with
  `video.captureStream()` + `MediaRecorder`, so it runs entirely on-device
  with no dependencies — the cost is that export takes as long as the clip
  is. Output is MP4 where the browser's recorder supports it, WebM otherwise.
- **Fallbacks**: on browsers whose `captureStream()` has no audio track, the
  element's audio is routed through an `AudioContext` into a
  `MediaStreamDestination`; where the media element can't be captured at all
  (Safari), frames are mirrored onto a canvas and that is captured instead.
- Handles `MediaRecorder`-produced WebM inputs that report `Infinity`
  duration (seek-to-the-end trick before enabling the timeline).
- No build step, no dependencies — a single `.html` file.
