# LAN Speed

Peer-to-peer LAN throughput tester. Open the page on two devices on the same
Wi-Fi / network, copy a short code from one to the other, and measure ping,
download and upload speed between them — over a direct WebRTC data channel,
with no internet, signalling server, STUN or TURN.

## Prompt

> lan speed connection tool that works offline.

## How it works

- Both pages create an `RTCPeerConnection` with `iceServers: []`, so only
  *host* (LAN) ICE candidates are gathered. There's no public-internet
  fall-back — if the two devices can't reach each other on the LAN, the
  connection won't form.
- The SDP offer / answer is gzipped (`CompressionStream("deflate-raw")`)
  then base64-encoded with a 1-byte format flag, and shown as both a
  textarea and a QR code. The QR is rendered with Kazuhiko Arase's
  `qrcode-generator` library (vendored in `public/qrcode.js`). Compression
  roughly halves the payload, which keeps the QR around Version 15
  (~75×75 modules) — well within phone-camera scanning range.
- A "Scan QR" button on each side uses the native `BarcodeDetector` API
  to read the other device's code straight from the camera, no app
  install required. The button stays hidden on browsers without
  `BarcodeDetector` (Firefox today); those users paste the text manually.
- Once connected, an ordered `RTCDataChannel` carries:
  - JSON control messages (`ping`/`pong`, `prep_recv`, `start_send`,
    `end_send`, `result`),
  - and 16 KB binary chunks during the throughput burst.
- The test runs three phases:
  1. **Ping** — 12 round trips, worst sample dropped, average reported.
  2. **Download** — initiator sends a 6 s burst; the peer counts received
     bytes and replies with the result.
  3. **Upload** — initiator asks the peer to send a 6 s burst; initiator
     counts received bytes locally.

## Notes

- 16 KB chunks are the practical max-message size that works across all
  major browser data-channel implementations.
- Backpressure is handled with `bufferedAmountLowThreshold` +
  `bufferedamountlow`, with an 8 MB high-water mark, so a fast sender
  doesn't out-run a slow receiver.
- After a send burst, the sender drains `bufferedAmount` to zero before
  signalling `end_send`, otherwise the receiver would underreport.
- ICE gathering has a 4 s hard cap so the offer / answer codes appear
  quickly even on stacks that never fire `complete`.
- Modern browsers obfuscate host candidates as mDNS `.local` names — both
  devices need to resolve mDNS on the same subnet. Home / office Wi-Fi is
  fine; corporate guest networks with client isolation will block the
  connection.
- No build step, no dependencies, single HTML file.

## Caveats

- Real-world throughput is gated by the slower of the two devices' radios,
  the AP's backplane, and any background traffic on the LAN — this tool
  measures the *path* between two browsers, not the raw link speed of
  either device.
- Wi-Fi rates are highly directional and bursty. Expect noisy numbers if
  one device is at the edge of coverage.
