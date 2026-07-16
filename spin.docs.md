# Spin

Add a photo and make it spin. A live preview spins the image around a chosen
centre; controls set the speed (rpm), the spin axis (flat Z spin, Y flip, or
X tumble), the direction, the background, and the output size. Download the
result as a seamlessly looping GIF or as a video.

## Prompt

> spin
> add a photo, app makes it spin. input for speed, axis, centre etc. then download buttons for gif or video or something

## Notes

- **Centre**: drag the photo in the preview to move it relative to the fixed
  crosshair — the crosshair is the rotation centre, and the canvas is always
  sized so a full revolution never clips (off-centre spins orbit). "Reset"
  puts the centre back in the middle.
- **Axes**: Z rotates in the image plane; Y and X are orthographic card-flips
  (horizontal/vertical scale follows `cos θ`, showing a mirrored back face).
- **GIF export** is a from-scratch GIF89a encoder in the page — median-cut
  256-colour palette sampled from the photo, Floyd–Steinberg dithering, LZW
  compression, and an optional 1-bit transparent background. Frame count and
  delay are derived from the rpm so exactly one revolution is encoded and the
  loop is seamless.
- **Video export** records the canvas in real time with
  `canvas.captureStream()` + `MediaRecorder` (MP4 on Safari, WebM elsewhere),
  capturing a whole number of revolutions (at least ~1 s) so it also loops.
- Images are EXIF-orientation corrected via `createImageBitmap` and downscaled
  to at most 1600 px for smooth preview and export.
- No build step, no dependencies — a single `.html` file.
