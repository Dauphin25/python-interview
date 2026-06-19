# 06 — Client-Server Architecture (for a game backend)

The JD requires "understanding of client-server architecture." You know this from Django/support;
here's how to frame it for a *game* backend specifically.

---

## 1. The model

- **Client** requests, **server** responds. Client = the game UI (browser/HTML5 canvas, mobile).
  Server = authoritative game logic, RNG, wallet, state.
- **Golden rule in gambling:** the **server is authoritative**. The client NEVER decides outcomes.
  The client only renders what the server already computed. Why: money + cheating. If the client
  computed the spin, players could tamper with it. Say this — it's a domain-aware, security-aware
  point that impresses.

```
[Game Client]  --spin request-->  [Game Server]
   renders     <--result JSON---   RNG + math + wallet + state  --> [DB]
```

## 2. Request/response flow for one spin

1. Client sends `POST /spin` with `{session_id, bet, lines}`.
2. Server: authenticate → validate bet against balance → debit wallet → call RNG → evaluate board
   via the engine → credit any win → persist the round → return result.
3. Client animates the reels to match the server's already-decided board.

Critical properties: **atomic wallet transaction**, **idempotency** (a retried request must not
double-debit — use an idempotency key / round id), **auditability** (every round logged for
regulators).

## 3. Protocols you should be able to compare

| Protocol | Use | Notes |
|---|---|---|
| HTTP/REST | Standard request/response (spin, balance) | Stateless, cacheable, simple |
| WebSocket | Real-time, bidirectional (live updates, jackpots, multiplayer) | Persistent connection |
| gRPC | Internal service-to-service, high throughput | Binary (protobuf), fast |
| Message queue (RabbitMQ/Kafka) | Async events (stats, audit, analytics) | Decouples producers/consumers |

A slot is mostly **stateless REST per spin**; **WebSockets** appear for live features. The
**simulation bot** typically runs *offline* against the engine directly (no network) — point this out:
the bot doesn't need the server, it imports the engine and hammers it locally/in parallel.

## 4. Statelessness, sessions, scaling

- **Stateless server** = no per-client memory between requests; state lives in DB/cache (Redis).
  Enables horizontal scaling: any server instance can handle any request behind a load balancer.
- Game **session state** (free-spins remaining, current multiplier) is persisted (DB/Redis), keyed by
  session, not held in process memory.
- **Idempotency keys** prevent double-spins on network retries.

## 5. APIs & serialization

- **REST** verbs: GET (read balance), POST (spin), idempotent vs non-idempotent.
- **JSON** is the lingua franca; know `json.dumps/loads`, and that floats/money should be **integer
  cents**, never floats (floating point rounding = real money bugs).
- **Status codes:** 200 ok, 400 bad request (invalid bet), 401 unauth, 409 conflict (duplicate
  round), 422 validation, 500 server error.
- Validate input at the boundary (e.g. `pydantic`); never trust the client.

## 6. Where Python fits / the stack

- Web layer: FastAPI (async, modern) or Django/DRF (you know this) or Flask.
- The **game math engine** is a pure Python library (like `slot_engine/`) the web layer calls.
  Keeping the engine framework-agnostic = reusable by both the live server and the simulation bot.
- Async (`asyncio`) helps the server handle many concurrent I/O-bound requests; the CPU-bound math
  per spin is tiny, so a sync engine called from an async handler is usually fine.

## 7. Reliability & performance words to drop

- **Caching** (Redis) for hot config/paytables.
- **Connection pooling** for the DB.
- **Load balancing** + stateless nodes for horizontal scale.
- **Graceful degradation**, **timeouts**, **retries with backoff** for downstream calls.
- **Observability:** structured logs, metrics (RTP drift alerts!), tracing.

---

### Drill yourself
- Why must the server, not the client, decide the spin outcome? (money, anti-cheat, regulation)
- What makes a server "stateless" and why does it help scaling?
- How do you prevent a double-debit when a client retries a spin? (idempotency key/round id)
- Why store money as integer cents? (float rounding errors)
- Where does the simulation bot sit relative to the client-server system? (offline, calls engine directly)
