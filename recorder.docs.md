# Recorder

A voice recorder. Tap the red button to record (pause/resume supported), then
play recordings back and jump around by tapping or dragging on the waveform.
Everything is stored locally in the browser — recordings can be renamed,
downloaded, or deleted, and nothing ever leaves the device.

## Prompt

> new app: recorder
> does voice recording, saves then allows playback or jumping through waveform.
> whatever audiocontext persistence you can do to make it still work in background or when screen is locked. add pwa install if that is needed for better bg behavior but remember this isnt on a subdomain. files are just stored locally, can download or delete. or rename.

## Notes

- **Capture**: `MediaRecorder` with 1 s timeslices; every chunk is written to
  IndexedDB the moment it arrives, so a killed tab or crash loses at most
  about a second. An interrupted session is detected on the next load and
  offered back as a "(recovered)" recording.
- **Background / locked-screen survival**, best-effort per platform:
  - a looping silent `AudioBufferSource` keeps an *output* stream on the
    `AudioContext`, which keeps the audio session alive in the background far
    more reliably than capture alone;
  - Media Session metadata + handlers put recording controls on the lock
    screen (pause/resume/stop) and mark the tab as playing media;
  - a screen Wake Lock is held while recording and re-acquired on
    `visibilitychange`;
  - the context auto-`resume()`s after iOS `interrupted` states (calls, Siri,
    lock) via `statechange`/`visibilitychange`/`pageshow` listeners.
- **PWA**: manifest + service worker so the app can be installed (installed
  apps get better background treatment, especially on iOS). The repo is
  served from a sub-path of github.io, not its own origin, so every URL is
  relative and both the manifest scope and the service worker scope are
  pinned to `./recorder.html` — the worker never controls the other apps on
  this origin. The service worker is network-first with cache fallback, so
  the app also opens offline.
- **Waveform**: blobs are decoded through an 8 kHz `OfflineAudioContext`
  (plenty for peaks; an hour of audio stays ~115 MB in memory instead of
  ~700 MB), min/max peaks per pixel are cached, and pointer events on the
  canvas seek. Chrome's Infinity-duration bug on MediaRecorder webm blobs is
  worked around with the classic seek-past-the-end trick.
- **Storage**: recordings live in IndexedDB; `navigator.storage.persist()` is
  requested once there's something worth keeping. Download filenames get the
  right extension for the recorded container (`.webm`/`.m4a`/`.ogg`).
- Extra files beyond the single HTML page: `recorder.webmanifest`,
  `recorder.sw.js`, `recorder-icon.svg` — a service worker can't be inlined.
