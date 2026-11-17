# Call

Peer-to-peer video and voice calls. Tap **Video call** or **Voice call**, then send
the link (Share, Copy, or show the QR code). When they open it, you're connected
browser to browser. No accounts, nothing to install. Audio and video go directly between
the two devices whenever the network allows.

## Prompt

> call app - a peer to peer video/voice call app. use public signalling server if available, then people can start call, get a link and send it. this possible¿

Follow-ups: fix "ID is taken"; couldn't see/hear the other person; then
"improvements, preferably perf and stability and reliability… if app needs to
be hosted differently we can do that, cloudflare hosted static site peer to
peer should be decent".

## How it connects

- **Signalling** (only connection setup goes through a server; media never does):
  - **Preferred: the Cloudflare Worker in [`call-worker/`](call-worker/README.md).**
    One Durable Object room per link, plus Cloudflare TURN credentials. The page
    finds it automatically when the Worker serves it (`/api/ice` on its own
    origin), or via `WORKER_URL` at the top of the script.
  - **Fallback, zero setup: the public PeerJS server (`0.peerjs.com`)**, used
    as a plain message relay by speaking its WebSocket protocol directly. The
    PeerJS library isn't loaded. Whoever registers `psimyn-call-<code>` first
    holds the room; others register their own id and say hello. The holder's token
    is kept per tab, so a reload reclaims the room instead of getting "ID is taken".
    If the old socket is still registered, the server silently re-attaches the new
    one without sending `OPEN`, so silence after connecting is treated as success.
- **One `RTCPeerConnection`** carries audio, video and a negotiated control data
  channel (mute/camera state, hang-up). Negotiation follows the **perfect
  negotiation** pattern (fixed polite/impolite roles), so either side can
  renegotiate at any time. The newcomer makes the *first* offer, though: having
  both sides offer at once and rolling one back trips a Chrome bug ("Failed to
  start SCTP transport") when the two offers' m-lines differ (video vs voice-only).
- **Every signalling message carries the sender's connection id and the id it's
  addressed to**. After a reload on either side, messages for the old connection
  are dropped, and a fresh offer from the other side starts a fresh connection.
- Codes are 10 random characters (~49 bits), so links aren't guessable. Two people
  per call; a third gets "Call is full". When someone hangs up, whoever is
  left keeps the room and the same link still works.

## Reliability

- **ICE restart** (`pc.restartIce()`) when the connection goes `disconnected`
  (after 2 s / 4 s, staggered by role so both sides rarely restart at once) or
  `failed`. It also runs immediately on `online` / Network Information `change`
  events (Wi-Fi ↔ mobile data) and when the tab becomes visible again. The call
  is only given up after 45 s without recovery (30 s for a first connection).
- **A signalling outage doesn't end the call.** The socket reconnects with
  backoff, and queued messages (e.g. an ICE-restart offer) are sent once it's
  back. The Worker room answers `ping` with `pong` without waking. No pong in
  10 s (3 s right after a network change) means the socket is dead even though
  it looks open, so it's replaced.
- **Capture tracks that die are replaced**: iOS ends camera/mic tracks in
  the background, and unplugging a headset ends the mic. A new track is fetched
  and swapped in with `replaceTrack`, with no renegotiation.
- Leaving is detected three ways: a `bye` over the data channel, a `bye` over
  signalling, and the server noticing the socket closed. The last one only
  ends the call if media is down as well.

## Media quality

- **Opus + RED** (RFC 2198 redundant audio): RED is put first with
  `setCodecPreferences`, so each packet also carries the previous audio frame.
  A single lost packet then costs nothing audible. Chrome only uses RED when
  it's the preferred codec. getStats still reports the codec as "opus", which
  is why the info panel shows opus.
- **Audio send priority `high`** (`priority` and `networkPriority`): voice wins
  over video locally, and DSCP-marked for networks that honour it.
- 720p / 30 fps capture cap, with echo cancellation, noise suppression and AGC.
  Bitrate adaptation is left to the browser's congestion control (GCC).
- `navigator.audioSession.type = "play-and-record"` on Safari, so audio routes like a call.
- `bundlePolicy: "max-bundle"` puts everything on one transport, so there's
  one ICE negotiation instead of several.

## UI

- Mute, camera on/off, front/back camera flip (when there's more than one camera),
  draggable self-view that snaps to corners, auto-hiding controls, call timer, a
  speaking ring when there's no video, a "Connecting…/Reconnecting…" badge, and a
  screen wake lock.
- **Quality bars** (top right) from live stats: round-trip time and audio packet loss.
- **Connection info**: tap the call timer for a live panel. It shows the server
  (Worker / public PeerJS) and whether TURN is available, ICE state and restart
  count, route (local network / internet via STUN / TURN relay), RTT and loss,
  kbps and codec each way, the browser's bandwidth estimate, and whether
  playback is paused.
- `?debug` exposes the call state as `window.__call` in the console.

## Research notes

- About 15–25% of calls can't connect directly and need a TURN relay. The
  most-cited figure is callstats.io's ~22%; [fippo's analysis](https://medium.com/@fippo/67b185e49765)
  of ~100k calls disputes how "failure" is counted. Mobile carriers' CGNAT is a
  big contributor. Hence Cloudflare TURN with TLS on 443, not just UDP 3478.
- ICE restart and perfect negotiation: [Mozilla's write-up](https://blog.mozilla.org/webrtc/perfect-negotiation-in-webrtc/),
  [bloggeek on ICE restarts](https://bloggeek.me/webrtcglossary/ice-restart/).
- Consent freshness (RFC 7675) is why a dead path takes ~30 s to reach
  `failed`. Restarting on `disconnected` is much faster.
- RED: [webrtcHacks](https://webrtchacks.com/red-improving-audio-quality-with-redundancy/),
  [Chrome M96 PSA](https://groups.google.com/g/discuss-webrtc/c/5761etCrSuA).
- Congestion control: Carlucci et al., *Analysis and design of the Google
  congestion control for WebRTC* (MMSys 2016). Delay-based, so the app doesn't
  hard-cap bitrates.
- iOS capture tracks ending in the background: WebKit bugs
  [208516](https://bugs.webkit.org/show_bug.cgi?id=208516) and
  [259337](https://bugs.webkit.org/show_bug.cgi?id=259337).

## Testing

Playwright with fake camera/mic, two to four browsers, run against both backends:
`wrangler dev` for the Worker, and a local `peer` server for the PeerJS
fallback. Checks: media flows both ways; RED negotiated; audio priority; mute
and camera-off propagate; ICE restart mid-call; signalling socket dropped mid-call;
third person gets "full"; reload mid-call; hang-up → waiting → voice-only rejoin;
the original creator leaves and a newcomer joins whoever stayed. Not tested:
real network handoffs, real TURN credentials, real iOS devices.
