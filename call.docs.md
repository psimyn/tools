# Call

Peer-to-peer video and voice calls. Tap **Video call** or **Voice call**, then send
the link (Share, Copy, or show the QR code). When they open it, you're connected
browser to browser. No accounts, nothing to install. Audio and video go directly between
the two devices whenever the network allows.

## Prompt

> call app - a peer to peer video/voice call app. use public signalling server if available, then people can start call, get a link and send it. this possible¿

## Notes

- **Signalling**: [PeerJS](https://peerjs.com/) (`peerjs@1.5.4` from unpkg) and its
  free public server at `0.peerjs.com`. The server only swaps connection details;
  no media goes through it. PeerJS's default ICE config includes Google STUN plus
  PeerJS's public TURN relays (`eu-0`/`us-0.turn.peerjs.com`). A TURN relay is only used
  when a direct path is impossible, e.g. with symmetric NAT or strict firewalls.
  Media is always DTLS-SRTP encrypted end to end between the browsers.
- **Links are symmetric**: the link is `call.html#<code>`, and the room's peer id is
  `psimyn-call-<code>`. Whoever opens the link first claims that id and waits.
  Whoever comes second gets `unavailable-id`, so they dial it instead. The creator
  can reload, and it doesn't matter who arrives first. The PeerJS server only
  lets an id be re-registered with its original token, so the tab that owns a
  room keeps that token in `sessionStorage`. Without that, a reload or a dropped
  socket on the host would get "ID is taken" for its own room. A guest whose
  call isn't answered within 12 s (e.g. the host's registration is stale) goes
  back to trying to claim the room, up to 6 times. Codes are 10 random characters
  (~49 bits), so links aren't guessable.
- **Two people per call**. A third person who opens the link gets "Call is full".
- When the guest hangs up, the host goes back to waiting and the same link still works.
  A guest gets a Rejoin button.
- Each person picks video or voice-only. If you choose video but have no camera,
  the call falls back to voice. Camera off just disables the track (no renegotiation),
  and the other side is told over a PeerJS data channel, which also carries mute
  state and hang-up.
- In-call: mute, camera on/off, front/back camera flip via `replaceTrack` (shown
  only with multiple cameras), draggable self-view that snaps to corners,
  auto-hiding controls, call timer, a speaking ring when there's no video,
  "Reconnecting…" on ICE `disconnected` (the call is dropped after 15 s), and a
  screen wake lock.
- ICE servers: PeerJS's defaults plus extra Google and Cloudflare STUN servers.
  Until ICE actually connects, the call screen shows a "Connecting…" badge.
  The other side's tracks arrive before any media flows, so without it a
  stalled connection looked like a black, silent call.
- **Connection info**: tap the call timer for a live panel showing ICE state,
  route (direct over the local network / direct via STUN / TURN relay), audio and
  video kbps in each direction, resolution/fps, and whether the player is paused.
  If the browser blocks autoplay, a "Tap to start audio & video" button appears.
- Remote video fills the screen when its orientation matches yours. When it
  doesn't (portrait phone ↔ landscape laptop), it's letterboxed.
- Caveats: the public PeerJS server and TURN relays are best-effort community
  infrastructure with no SLA. If they go away, swap in a self-hosted
  `peer` server and TURN (e.g. coturn) via the `Peer` options.
