// Signalling + TURN credentials for call.html.
//
//   GET /api/ice                 -> { iceServers, turn }   (fresh, short-lived TURN creds)
//   GET /api/room/<code>?cid=<id> -> WebSocket into that call's room
//
// A room is one Durable Object per call code. It only relays offers/answers/
// ICE candidates between the two people in it. Audio and video never touch it.
// Sockets use the hibernation API, so an idle room costs nothing while a call
// is in progress. Client pings ("ping" -> "pong") are answered without waking it.

import { DurableObject } from "cloudflare:workers";

const CODE_RE = /^[a-z0-9]{6,32}$/;
const CID_RE = /^[a-z0-9]{8,40}$/;
const MAX_MSG = 64 * 1024;
const SEATS = 2;

const FALLBACK_ICE = [
  { urls: ["stun:stun.cloudflare.com:3478", "stun:stun.l.google.com:19302"] },
];

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    if (!url.pathname.startsWith("/api/")) return new Response("Not found", { status: 404 });

    const cors = corsHeaders(req, env);
    if (!cors) return new Response("Origin not allowed", { status: 403 });
    if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: cors });

    if (url.pathname === "/api/ice") return iceServers(env, cors);

    const m = url.pathname.match(/^\/api\/room\/([^/]+)$/);
    if (m) {
      if (req.headers.get("Upgrade") !== "websocket") return new Response("Expected WebSocket", { status: 426 });
      const code = m[1].toLowerCase();
      const cid = url.searchParams.get("cid") || "";
      if (!CODE_RE.test(code) || !CID_RE.test(cid)) return new Response("Bad room or client id", { status: 400 });
      return env.ROOMS.get(env.ROOMS.idFromName(code)).fetch(req);
    }
    return new Response("Not found", { status: 404, headers: cors });
  },
};

// Returns CORS headers, or null if the request's Origin isn't allowed.
function corsHeaders(req, env) {
  const origin = req.headers.get("Origin");
  const self = new URL(req.url).origin;
  const allowed = (env.ALLOWED_ORIGINS || "").split(",").map((s) => s.trim()).filter(Boolean);
  if (origin && origin !== self && allowed.length && !allowed.includes(origin)) return null;
  return {
    "Access-Control-Allow-Origin": origin || "*",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Vary": "Origin",
  };
}

// Mint per-call TURN credentials from Cloudflare Realtime TURN, if configured.
// Without the secrets, return STUN only (calls then work wherever a direct
// path exists, which is most, but not all, networks).
async function iceServers(env, cors) {
  const headers = { ...cors, "Content-Type": "application/json", "Cache-Control": "no-store" };
  if (!env.TURN_KEY_ID || !env.TURN_KEY_API_TOKEN) {
    return new Response(JSON.stringify({ iceServers: FALLBACK_ICE, turn: false }), { headers });
  }
  try {
    const r = await fetch(
      `https://rtc.live.cloudflare.com/v1/turn/keys/${env.TURN_KEY_ID}/credentials/generate-ice-servers`,
      {
        method: "POST",
        headers: { Authorization: `Bearer ${env.TURN_KEY_API_TOKEN}`, "Content-Type": "application/json" },
        // Long enough for a long call: credentials are only checked when a
        // TURN allocation is created or refreshed.
        body: JSON.stringify({ ttl: 86400 }),
      },
    );
    if (!r.ok) throw new Error("TURN API " + r.status);
    const data = await r.json();
    let list = Array.isArray(data.iceServers) ? data.iceServers : [data.iceServers];
    // Browsers refuse port 53 and would just stall on those candidates.
    list = list
      .map((s) => ({ ...s, urls: [].concat(s.urls).filter((u) => !/:53(\?|$)/.test(u)) }))
      .filter((s) => s.urls.length);
    return new Response(JSON.stringify({ iceServers: list, turn: true }), { headers });
  } catch (e) {
    console.error("TURN credentials failed", e);
    return new Response(JSON.stringify({ iceServers: FALLBACK_ICE, turn: false }), { headers });
  }
}

export class Room extends DurableObject {
  constructor(ctx, env) {
    super(ctx, env);
    ctx.setWebSocketAutoResponse(new WebSocketRequestResponsePair("ping", "pong"));
  }

  async fetch(req) {
    const cid = new URL(req.url).searchParams.get("cid");
    const { 0: client, 1: server } = new WebSocketPair();

    // Another tab/reconnect of the same client replaces its old socket. This
    // is what lets a reload or a dropped mobile connection rejoin instantly,
    // instead of waiting for the server to notice the old socket is dead.
    for (const ws of this.ctx.getWebSockets(cid)) {
      try { ws.serializeAttachment({ cid, replaced: true }); ws.close(4001, "replaced"); } catch {}
    }
    const others = this.others(cid);

    this.ctx.acceptWebSocket(server, [cid]);
    server.serializeAttachment({ cid });

    // Full when every seat is already taken by someone else.
    const otherIds = [...new Set(others.map((o) => o.cid))];
    if (otherIds.length >= SEATS) {
      server.send(JSON.stringify({ t: "full" }));
      server.serializeAttachment({ cid, full: true });
      server.close(4002, "full");
      return new Response(null, { status: 101, webSocket: client });
    }

    server.send(JSON.stringify({ t: "welcome", peers: otherIds }));
    for (const o of others) o.ws.send(JSON.stringify({ t: "peer-joined", peer: cid }));
    return new Response(null, { status: 101, webSocket: client });
  }

  // Live sockets other than `cid`'s, with their client ids.
  others(cid) {
    const out = [];
    for (const ws of this.ctx.getWebSockets()) {
      const a = ws.deserializeAttachment() || {};
      if (!a.cid || a.cid === cid || a.replaced || a.full) continue;
      if (ws.readyState !== WebSocket.OPEN) continue;
      out.push({ ws, cid: a.cid });
    }
    return out;
  }

  async webSocketMessage(ws, msg) {
    const a = ws.deserializeAttachment() || {};
    if (!a.cid || a.replaced || a.full) return;
    if (typeof msg !== "string" || msg.length > MAX_MSG) return;
    let m;
    try { m = JSON.parse(msg); } catch { return; }
    if (!m || m.t !== "signal") return;
    const out = JSON.stringify({ t: "signal", from: a.cid, data: m.data });
    for (const o of this.others(a.cid)) {
      try { o.ws.send(out); } catch {}
    }
  }

  async webSocketClose(ws, code, reason) {
    // Complete the close handshake. 1005/1006 mean "no code" and can't be
    // sent back; echoing them throws and leaves the client stuck in CLOSING.
    try { ws.close(code === 1005 || code === 1006 || code === 1015 ? 1000 : code, reason); } catch {}
    this.left(ws);
  }

  async webSocketError(ws) {
    this.left(ws);
  }

  left(ws) {
    const a = ws.deserializeAttachment() || {};
    if (!a.cid || a.replaced || a.full) return;
    // Still connected on another socket (reconnected before the old one closed)?
    const still = this.ctx.getWebSockets(a.cid).some((w) => w !== ws && w.readyState === WebSocket.OPEN);
    if (still) return;
    const out = JSON.stringify({ t: "peer-left", peer: a.cid });
    for (const o of this.others(a.cid)) {
      try { o.ws.send(out); } catch {}
    }
  }
}
