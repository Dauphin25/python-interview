# 11 — One-Page Cheat Sheet (last-minute review)

## Python reflexes
- `is` = identity (only for None/True/False), `==` = value.
- Mutable default arg bug → use `None` sentinel.
- Generator = lazy, O(1) memory → simulations.
- Decorator = func in, wrapped func out; `@functools.wraps`.
- `with` = guaranteed setup/teardown.
- GIL → threads for I/O, **processes for CPU-bound** (simulation).
- `@dataclass(frozen=True, slots=True)` = immutable, memory-light value object.
- `classmethod`=cls/alt-constructor, `staticmethod`=namespaced fn.
- Pure function = same input→same output, no side effects → reproducible + parallel.
- Money = **integer cents**, never float.

## Slot math reflexes
- **RTP** = expected return / bet (long run). 96% RTP → 4% house edge.
- **Volatility** = spread/variance of outcomes. Same RTP can feel very different.
- **EV** = Σ payout·probability.
- Independent reels → multiply probabilities. "At least one" → 1 − P(none).
- **LLN / standard error ∝ 1/√n** → why simulate millions (4× spins = ½ error).
- Tune RTP without touching paytable → **reweight reel strips / virtual reels**.
- Seed RNG in simulation (reproducible); CSPRNG in production (fair/secure).
- Validate the bot → compare to **exact analytic RTP** on a small config.

## Architecture reflexes
- **Server is authoritative** (money + anti-cheat). Client only renders.
- **Idempotency key** prevents double-debit on retry.
- **Stateless** server + state in DB/Redis → horizontal scaling.
- Engine = **pure framework-agnostic library** reused by server AND bot.

## Numbers to know cold
- (1/32)³ ≈ 1/32768 (three rare symbols).
- 1 − 0.9⁵ ≈ 0.41 (at least one, p=0.1, 5 reels).
- 32⁵ ≈ 33.5M combos (5 reels × 32 stops).
- File 04 §10: strip [7,BAR×2,CH×3], pay 50/10/5 → EV 265/216 ≈ 1.227.

## Run the demo
```
python -m slot_engine.simulate 1000000 42   # RTP ~93.3%, reproducible
python tests/test_engine.py                  # 8/8, bot matches analytic RTP
```

## Mindset
- Think out loud. Sanity-check math with EV.
- Tie answers to slots/simulation when natural.
- "I don't know, but here's how I'd reason…" > bluffing.
- Lean on your casino domain edge.
