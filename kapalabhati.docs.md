# Kapalabhati

A guided 15-minute breathing session built around Kapalabhati ("skull-shining
breath"): rounds of quick belly-driven exhales with a breath hold after each
one, balanced by slower calming practices. Short explanations come up before
each exercise and technique tips change as you go. Four presets (Classic,
Gentle, Energise, Unwind), and you can add, remove, reorder or tune single
exercises in a run.

## Prompt

> khapalbati breathing app, 15 minute interval with different types of breathing and explanations throughout. have some presets for different variations, and allow adding or removing single exercises from a run. after we will add some audio guides that sync up as it goes

## Notes

- **Exercises**: Arrive, Belly breathing, Kapalabhati round (strokes, pace,
  hold length, hold full or empty), Bhastrika, Nadi shodhana, Box, 4-7-8,
  Coherent breathing, Bhramari and Stillness. Each one builds into a flat
  list of *segments* (`inhale`, `exhale`, `hold-in`, `hold-out`, `pump`,
  `bellows`, `intro`, `free`, `rest`). Guided exercises start with a 12 s
  intro that shows the explanation.
- **Run editing**: tap a row to open its settings. ↑/↓ reorders and × removes.
  "Add exercise" opens the library. Any edit makes the run *custom* and you
  can reset it to the preset. **Fit to 15:00** changes (or adds) a closing
  Stillness so the total is exactly 15 minutes. The run is saved in
  `localStorage`.
- **Player**: the orb grows on inhales and shrinks on exhales. During pumps it
  snaps in sharply on each stroke and the count shows strokes done out of the
  total. Tap the timeline to jump to an exercise. Keyboard: space to pause,
  ←/→ for previous/next exercise, Esc to stop. Optional WebAudio pace clicks
  and chimes, optional vibration, and a screen Wake Lock.
- **Timing**: one clock based on `performance.now()` with pause and seek. The
  current segment comes from elapsed time, not from timers, so a throttled
  or backgrounded tab catches up correctly.
- **Audio-guide hook**: `window.breath.on(event, fn)` emits `start`,
  `exercise`, `segment`, `stroke`, `tick`, `play`, `pause`, `seek`, `stop`
  and `end`. Each segment has a stable `cue` key (for example
  `kapalabhati.pump`, `kapalabhati.hold`, `nadi.inhale.left`) plus absolute
  `start`/`end` times. Clips can be mapped by cue, or one long track can be
  synced to `breath.time()` and re-aligned on `seek`.
