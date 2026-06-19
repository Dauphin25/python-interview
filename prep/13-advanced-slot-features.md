# 13 — Advanced Slot Features & Mechanics (domain depth)

Knowing modern slot mechanics by name — and how each affects **RTP and volatility** — makes you
sound like someone who already builds these games. Skim until you can explain each in a sentence.

---

## 1. Win-evaluation models

- **Fixed paylines** — predefined patterns (e.g. 10/20/25 lines). Win = matching symbols left-to-
  right on a line. (What our `slot_engine` does.)
- **Ways-to-win ("243 ways", "1024 ways")** — no fixed lines; any matching symbols on **adjacent
  reels** from the leftmost pay. 3 rows × 5 reels = 3⁵ = **243 ways**; 4 rows = 4⁵ = 1024.
- **Megaways™** — each reel shows a *variable* number of symbols each spin (2–7), so ways change
  every spin, up to **117,649** (7⁵). Big volatility.
- **Cluster pays** — win by groups of ≥N touching same symbols (grid games), not lines.

How to compute ways-to-win payout (interview-ready):
```python
def ways_win(board, symbol, pay_per_count, wild="WILD"):
    """board: list of columns (each a list of symbols). Count matching on
    consecutive reels from reel 0; multiply the per-reel match counts."""
    ways = 1
    matched_reels = 0
    for col in board:
        hits = sum(1 for s in col if s == symbol or s == wild)
        if hits == 0:
            break
        ways *= hits
        matched_reels += 1
    return ways * pay_per_count.get(matched_reels, 0)
```

## 2. Bonus / feature mechanics (and their effect on the math)

| Feature | What it does | Effect on RTP / volatility |
|---|---|---|
| **Free spins** | Scatter trigger awards N spins at no cost, often with extra multipliers | Big chunk of total RTP lives here; raises volatility |
| **Wilds** | Substitute for symbols to complete wins | Raises hit rate & RTP |
| **Expanding wild** | Fills a whole reel | Bigger wins, more volatility |
| **Sticky wild** | Stays for several spins | Higher win potential in features |
| **Multipliers** | ×2/×3/… on wins, esp. in free spins | Directly scales payouts; raises volatility |
| **Scatter** | Pays anywhere / triggers features | Adds wins independent of lines |
| **Cascading / tumbling reels** | Winning symbols removed, new ones drop, chain wins | More wins per paid spin; volatility varies |
| **Hold & Win / respins** | Lock symbols, respin for cash values/jackpots | Concentrated big-win volatility |
| **Progressive jackpot** | A growing pot funded by a slice of each bet | Tiny probability, huge payout; high variance; jackpot contribution is part of total RTP |
| **Buy-feature ("bonus buy")** | Pay e.g. 100× to jump straight to free spins | Has its own RTP, usually validated separately |

**Key talking point:** total game RTP = base-game RTP + feature RTP. Designers **allocate** the RTP
budget between base and features. A "feature-heavy" game puts more RTP into rare big free-spin wins →
high volatility, even at the same 96% total.

## 3. How features change your simulation bot

- The bot must model **state** (in free spins? multiplier active? respins left?). The base `spin()`
  becomes a small **state machine**: `BASE → (trigger) → FREE_SPINS → BASE`.
- You still measure the same outputs (RTP, hit rate, volatility) but now also **per-feature
  contribution** (what % of RTP comes from free spins) and **trigger frequency** (1 in N spins hits
  the bonus).
- Reproducibility (seed) becomes more important because feature sequences are longer and bugs hide in
  rare paths. Record the seed to replay a rare jackpot.

Sketch of a state machine you could describe:
```python
def play_round(machine, rng):
    total = base_spin(machine, rng)
    if triggered_free_spins(machine.last_board):
        spins = award_count(machine.last_board)
        mult = feature_multiplier
        for _ in range(spins):
            total += base_spin(machine, rng) * mult
    return total
```

## 4. Volatility classes & target metrics studios track

- **Volatility index / class:** Low / Medium / High (sometimes a 1–10 scale).
- **Hit frequency:** % of spins with any win (low-vol ~30–45%, high-vol can be <20%).
- **Max win cap:** e.g. 5,000× or 10,000× bet — caps the tail for liability and regulation.
- **Bonus frequency:** e.g. 1 in 150 spins triggers free spins.
- **RTP distribution / percentiles:** what a typical session looks like, not just the mean.

## 5. Fairness, certification & compliance vocabulary

- **RNG certification** by independent labs (e.g. iTech Labs, GLI, BMM) — the RNG and the math model
  are tested and signed off.
- **PAR sheet / math spec:** the document of reel strips, paytable, probabilities, and the proven RTP.
- **Reproducibility:** regulators may require a seedable test mode to replay outcomes.
- **Jurisdictional RTP floors:** some markets mandate minimum RTP (e.g. ≥ 85–92%).
- **Provably fair** (crypto casinos): cryptographic commit-reveal so players can verify a result
  wasn't tampered with — worth knowing the term.

## 6. Run the parallel simulation (uses all cores — the CPU-bound answer made real)

```bash
python -m slot_engine.parallel 4000000 4
```
This splits spins across processes (each with its own seed), then merges the partial means/variances
with the parallel variance formula. Talk through: *"Simulation is CPU-bound and embarrassingly
parallel, so multiprocessing — not threads, because of the GIL — and I merge moments rather than
storing results."*

---

### Drill yourself
- 243 ways vs fixed paylines — how does a win get evaluated?
- Same 96% RTP, one feels boring, one feels wild — explain via RTP allocation/volatility.
- Where in a typical game does most of the RTP live? (often the free-spins / bonus feature)
- What does the simulation bot need that a base-only sim doesn't? (feature state machine, trigger
  frequency, per-feature RTP contribution)
- Name 3 compliance terms. (RNG certification, PAR sheet, RTP floor / reproducibility)
