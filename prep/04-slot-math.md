# 04 — Slot Math: Probability, Combinatorics, RTP & Volatility

This is the differentiator for THIS job and the area you said is weakest. Learn it well — it's also
genuinely interesting and your casino background gives you the vocabulary already.

---

## 1. How a slot actually works (mental model)

- A slot has **reels** (typically 5). Each reel is a **strip**: an ordered list of symbols, e.g.
  `["7", "BAR", "CHERRY", "CHERRY", "WILD", ...]`. A reel strip might have 30–80 positions.
- A **spin** picks a random stop position on each reel. The visible **window** is usually 3 rows ×
  5 reels = a 3×5 **board**.
- **Paylines** are patterns across the board (e.g. top row, middle row, diagonals). Modern games use
  "ways" (243 ways = any matching symbols on adjacent reels) instead of fixed lines.
- A **paytable** maps (symbol, count-in-a-row from leftmost reel) → payout multiplier.
- **RNG** picks the stop on each reel. In real machines it's a certified CSPRNG; in simulation you
  use a seeded PRNG for reproducibility.

> Key insight: the **reel strip composition** (how many of each symbol, and *which symbols sit where*)
> is the lever designers tune to hit a target RTP and volatility. Your job: build the engine and the
> bot that measures whether the math hits target.

## 2. Probability foundations you must know

- **Probability** of an event = favorable outcomes / total outcomes (for equally likely outcomes).
- `0 ≤ P ≤ 1`. P(certain)=1, P(impossible)=0.
- **Complement:** P(not A) = 1 − P(A). Often easier ("at least one" problems).
- **Independent events:** P(A and B) = P(A)·P(B). Reels spin independently.
- **Mutually exclusive (OR):** P(A or B) = P(A) + P(B) when they can't co-occur.
  General: P(A or B) = P(A) + P(B) − P(A and B).
- **Conditional:** P(A|B) = P(A and B) / P(B).

**Example (independent reels):** symbol "7" appears once on a 32-position reel. P(7 on one reel) =
1/32. P(three 7s on reels 1–3) = (1/32)³ ≈ 0.0000305 → about 1 in 32,768.

**"At least one" via complement:** P(at least one WILD on 5 reels), each reel P(wild)=0.1:
P = 1 − (0.9)⁵ = 1 − 0.590 = 0.410.

## 3. Combinatorics you must know

- **Multiplication principle:** independent choices multiply. 32 stops × 32 × 32 × 32 × 32 =
  32⁵ ≈ 33.5M total reel combinations on a 5-reel game with 32-position strips.
- **Permutations** (order matters): P(n, r) = n! / (n−r)!
- **Combinations** (order doesn't): C(n, r) = n! / (r!·(n−r)!) — `math.comb(n, r)`.
- **Factorial:** n! = n·(n−1)·…·1; `math.factorial(n)`.

```python
import math
math.comb(52, 5)     # 2,598,960  (poker hands)
math.perm(5, 3)      # 60
math.factorial(5)    # 120
```

When *would* you use combinations in slots? Counting how many of the 33.5M stop-combinations produce
a given winning pattern → that count / total = probability of that win. This is the heart of an
**exact RTP calculation** (a "PAR sheet" / math model), as opposed to estimating it by simulation.

## 4. Expected Value (EV) — the single most important concept

EV = Σ (outcome value × its probability).

```
EV = Σ_i  payout_i · P(outcome_i)
```

**Example:** A bet of 1 unit. Outcomes:
- Win 10 with P=0.05, win 2 with P=0.20, win 0 with P=0.75.
EV(return) = 10·0.05 + 2·0.20 + 0·0.75 = 0.5 + 0.4 + 0 = **0.90 per 1 unit bet**.

## 5. RTP and House Edge (define these crisply — you WILL be asked)

- **RTP (Return To Player)** = expected fraction of total wagered money returned to players over the
  long run = EV(return) / bet. In the example above, **RTP = 0.90 = 90%**.
- **House Edge** = 1 − RTP = the operator's expected margin = 10% here.
- Typical online slots: **RTP 94–97%**. Regulators often mandate a floor (e.g. ≥ 85–92%).
- RTP is a **long-run expectation** (Law of Large Numbers). A single session can pay 5000× or 0.
  Don't confuse expectation with any individual result.

**Exact RTP formula for a slot:**
```
RTP = (Σ over all symbol-combinations: probability_of_combo · payout_of_combo) / bet
```
Computed either analytically (sum over the reel strips — "the math model") or estimated by Monte
Carlo simulation (the bot you'll build).

## 6. Volatility / Variance (the other dial designers tune)

- **Volatility (variance)** measures how *spread out* outcomes are around the mean.
- **Low volatility:** frequent small wins (smooth bankroll, e.g. classic fruit machines).
- **High volatility:** rare but huge wins (long dry spells, big jackpots).
- Two games can have the **same 96% RTP** but completely different *feel* due to volatility.

Math:
```
Variance = Σ P(x)·(x − EV)²        Std Dev = √Variance
```
Higher std dev → higher volatility. In simulation you compute it directly from sampled payouts:
```python
import statistics
mean = statistics.mean(payouts)
variance = statistics.pvariance(payouts)     # population variance over all spins
std = statistics.pstdev(payouts)
```

Related metrics the bot should report:
- **Hit frequency / hit rate** = fraction of spins that win anything (e.g. 25%).
- **Max win** (capped, e.g. 5000× bet).
- **RTP** (mean return / bet).
- **Distribution of wins** (histogram of multipliers).

## 7. The Law of Large Numbers & why you simulate millions of spins

- LLN: the sample mean converges to the true expected value as n → ∞.
- The **standard error** of your estimated RTP shrinks like **1/√n**. To halve the error you need
  **4×** the spins. That's why bots run 10M–1B spins: to estimate RTP to ±0.1%.
- This is THE justification for the simulation bot in the JD. Be ready to say it.

**Confidence:** estimated RTP ≈ true RTP ± ~1.96·(σ/√n) for 95% confidence. Large σ (high
volatility) ⇒ need more spins to nail the RTP.

## 8. RNG: pseudo-random vs cryptographic

- `random` module = **Mersenne Twister PRNG**: fast, deterministic given a seed → great for
  *reproducible simulations*, NOT for real-money RNG.
- Real-money / fairness: a **CSPRNG** (`secrets`, `os.urandom`) or certified hardware RNG, often with
  independent certification (e.g. iTech Labs, GLI).
- **Seeding** (`random.seed(42)`) lets you replay an exact sequence of spins — essential for
  debugging "why did this spin pay 5000×" and for regulator-reproducible test runs.

```python
import random
rng = random.Random(42)        # isolated, seeded generator (don't use global state)
stop = rng.randrange(len(strip))
```

## 9. Weighted symbols & virtual reels (important real-world nuance)

Physical/old machines map many **virtual stops** to one physical symbol to control odds beyond what
the visible strip suggests. Equivalent in code: each symbol has a **weight**; you draw proportionally.

```python
import random
symbols = ["7", "BAR", "CHERRY", "WILD"]
weights = [1, 5, 20, 3]                       # CHERRY common, 7 rare
pick = random.choices(symbols, weights=weights, k=1)[0]
```
This is how designers fine-tune RTP without changing the paytable — by reweighting symbol frequency.

## 10. Worked mini-example end-to-end (do this by hand)

3-reel, single payline, each reel strip = `[7, BAR, BAR, CHERRY, CHERRY, CHERRY]` (6 positions).
Paytable: three 7s → 50, three BARs → 10, three CHERRY → 5, any other → 0. Bet = 1.

- P(7 on a reel) = 1/6; P(three 7s) = (1/6)³ = 1/216.
- P(BAR on a reel) = 2/6 = 1/3; P(three BAR) = (1/3)³ = 1/27 = 8/216.
- P(CHERRY) = 3/6 = 1/2; P(three CHERRY) = (1/2)³ = 1/8 = 27/216.
- EV = 50·(1/216) + 10·(8/216) + 5·(27/216)
     = (50 + 80 + 135)/216 = 265/216 ≈ **1.227** → RTP ≈ 122.7%.

That RTP > 100% means *this paytable loses money* — a designer would lower payouts or reweight
symbols. **This is exactly the optimize-based-on-simulation loop in the JD.** Practice tweaking the
numbers to hit 96%.

---

### Drill yourself (answers in your head, then verify with code in file 05)
- Define RTP and house edge. If RTP is 96%, what's the edge? (4%)
- Two 96% RTP games differ how? (volatility/variance)
- Why simulate 50M spins instead of 50k? (standard error ∝ 1/√n; precision)
- P(at least one scatter in 5 reels) if each reel has P=0.08? (1 − 0.92⁵ ≈ 0.341)
- How do designers tune RTP without touching the paytable? (symbol weights / virtual reels)
- Why seed the RNG in simulation but never in production? (reproducibility vs fairness/security)
