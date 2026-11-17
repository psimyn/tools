# call-worker

Optional backend for [`call.html`](../call.html), on Cloudflare Workers (free plan is enough).
It does three things:

- **Signalling rooms.** One Durable Object per call link relays offers, answers and
  ICE candidates between the two people. Sockets use the hibernation API, so
  an idle room costs nothing. Rooms have 2 seats; a reconnecting client
  (same per-tab id) takes over its old seat immediately instead of waiting for the
  server to notice the old socket died.
- **TURN credentials.** `/api/ice` mints short-lived credentials for
  [Cloudflare Realtime TURN](https://developers.cloudflare.com/realtime/turn/):
  anycast, with UDP/TCP on 3478, TCP on 80, and TLS on 443 for strict firewalls.
  1,000 GB/month is free; after that it's $0.05/GB. Without TURN configured
  it returns STUN only.
- **Hosting the page.** `npm run build` copies `../call.html` into `public/`, so the
  Worker serves the page and API from one origin with no config.

Without this Worker, `call.html` falls back to the public PeerJS server and
TURN relay, which are best-effort.

## Deploy

```sh
cd call-worker
npm install
npx wrangler login
npm run deploy            # → https://call.<your-subdomain>.workers.dev
```

Open that URL. The page detects the Worker on its own origin (`/api/ice`) and uses it.

### Turn on Cloudflare TURN (recommended)

In the Cloudflare dashboard, open **Realtime → TURN** and create a TURN key.
That gives a key ID and an API token. Then:

```sh
npx wrangler secret put TURN_KEY_ID
npx wrangler secret put TURN_KEY_API_TOKEN
```

The info panel in a call (tap the timer) shows `server: worker + TURN` when it's active.

### Keep hosting the page elsewhere (e.g. GitHub Pages)

Set `WORKER_URL` near the top of the script in `call.html` to the Worker's URL.
Then lock the API to your page's origin in `wrangler.jsonc`:

```jsonc
"vars": { "ALLOWED_ORIGINS": "https://psimyn.github.io" }
```

The Origin check stops other websites from using your TURN quota from a browser.
It doesn't stop scripts that fake the header. If that matters, add Cloudflare's
rate-limiting binding to `/api/ice`.

## Local development

```sh
npm run dev               # http://127.0.0.1:8787 (page + rooms; TURN only if .dev.vars has the secrets)
```

## API

| | |
|---|---|
| `GET /api/ice` | `{ iceServers: [...], turn: bool }`. Port-53 URLs are filtered out because browsers block them. |
| `GET /api/room/<code>?cid=<client id>` (WebSocket) | Server → client: `welcome {peers}`, `peer-joined {peer}`, `peer-left {peer}`, `signal {from, data}`, `full`. Client → server: `signal {data}`, or the text `ping` (answered with `pong` without waking the room). Close code 4001 = replaced by the same client elsewhere; 4002 = room full. |
