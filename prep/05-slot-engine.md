# 05 — A Real Slot Engine + Monte Carlo Bot

Below is a complete, runnable mini slot engine and simulation bot. The actual code lives in
`../slot_engine/` so you can run it. Study it until you could rebuild it on a whiteboard — it maps
almost 1:1 to the JD responsibilities. Talking through this in the interview is gold.

Run it:
```bash
python -m slot_engine.simulate          # from E:\python-interview
```

## Architecture (explain this out loud)

```
RNG (seedable)  ─┐
ReelStrip(s)     ─┼─►  SlotMachine.spin() ─► SpinResult
Paytable         ─┘                              │
                                                 ▼
                              SimulationBot ──► Stats (RTP, hit rate, volatility)
```

Design choices to defend in the interview:
- **Dependency injection of RNG** → deterministic, reproducible tests (seeded).
- **Pure-ish evaluation** (`evaluate`) → easy to unit test, no hidden state.
- **`@dataclass(frozen, slots)` results** → immutable value objects, memory-light at scale.
- **Generator-based simulation** → run 100M spins in O(1) memory; aggregate on the fly.
- **Composition over inheritance** → machine *has* reels, paytable, rng.
- **Separation of concerns** → engine produces results; bot computes statistics.

## Core engine (annotated)

```python
# slot_engine/machine.py
from dataclasses import dataclass, field
import random

SYMBOLS = ["7", "BAR", "BELL", "CHERRY", "WILD", "SCATTER"]

@dataclass(frozen=True, slots=True)
class SpinResult:
    board: tuple          # tuple of columns (each a tuple of visible symbols)
    total_win: int        # in bet-units (multiplier * 1)
    line_wins: tuple = field(default_factory=tuple)

class ReelStrip:
    """One reel: an ordered list of symbols. A spin picks a random stop."""
    def __init__(self, strip):
        self.strip = strip
        self.n = len(strip)
    def window(self, rng, rows=3):
        stop = rng.randrange(self.n)                 # random stop position
        return tuple(self.strip[(stop + i) % self.n] for i in range(rows))

class Paytable:
    """(symbol, count from leftmost) -> payout multiplier."""
    def __init__(self, table, wild="WILD"):
        self.table = table
        self.wild = wild
    def score_line(self, line):
        first = next((s for s in line if s != self.wild), self.wild)
        if first == "SCATTER":
            return 0  # scatters pay anywhere, handled separately in real games
        count = 0
        for s in line:
            if s == first or s == self.wild:
                count += 1
            else:
                break
        return self.table.get((first, count), 0)

class SlotMachine:
    def __init__(self, reels, paytable, rng=None, paylines=None, rows=3):
        self.reels = reels
        self.paytable = paytable
        self.rng = rng or random.Random()
        self.rows = rows
        # default paylines: the three horizontal rows of a 5x3 board
        self.paylines = paylines or [
            [(c, 0) for c in range(len(reels))],
            [(c, 1) for c in range(len(reels))],
            [(c, 2) for c in range(len(reels))],
        ]

    def spin(self):
        board = tuple(reel.window(self.rng, self.rows) for reel in self.reels)
        total, line_wins = 0, []
        for idx, line in enumerate(self.paylines):
            symbols = [board[col][row] for (col, row) in line]
            win = self.paytable.score_line(symbols)
            if win:
                total += win
                line_wins.append((idx, win))
        # scatter pays: count scatters anywhere on the board
        scatters = sum(s == "SCATTER" for col in board for s in col)
        if scatters >= 3:
            total += scatters * 2
        return SpinResult(board=board, total_win=total, line_wins=tuple(line_wins))
```

## The simulation bot (the core JD task)

```python
# slot_engine/bot.py  (generator-based, O(1) memory, streaming stats)
import math

class RunningStats:
    """Welford's online algorithm: mean + variance without storing all samples."""
    def __init__(self):
        self.n = 0; self.mean = 0.0; self.m2 = 0.0
        self.wins = 0; self.max_win = 0.0
    def update(self, x):
        self.n += 1
        delta = x - self.mean
        self.mean += delta / self.n
        self.m2 += delta * (x - self.mean)
        if x > 0: self.wins += 1
        if x > self.max_win: self.max_win = x
    @property
    def variance(self): return self.m2 / self.n if self.n else 0.0
    @property
    def std(self): return math.sqrt(self.variance)
    @property
    def hit_rate(self): return self.wins / self.n if self.n else 0.0

class SimulationBot:
    """Plays the machine n times, gathering statistics. Bet is 1 unit/spin."""
    def __init__(self, machine, bet=1):
        self.machine = machine; self.bet = bet
    def play(self, n):                       # generator: lazy stream of returns
        for _ in range(n):
            yield self.machine.spin().total_win
    def run(self, n):
        stats = RunningStats()
        for payout in self.play(n):
            stats.update(payout)
        rtp = stats.mean / self.bet          # mean return per unit bet
        # 95% CI half-width for the RTP estimate:
        ci = 1.96 * (stats.std / math.sqrt(stats.n)) / self.bet if stats.n else 0
        return {
            "spins": stats.n,
            "rtp": rtp,
            "rtp_95ci": (rtp - ci, rtp + ci),
            "house_edge": 1 - rtp,
            "hit_rate": stats.hit_rate,
            "volatility_std": stats.std,
            "max_win": stats.max_win,
        }
```

Why `RunningStats` (Welford) and not `statistics.mean(list_of_100M)`? **Memory.** You cannot hold
100M floats (~800MB+) just to average them. Online stats keep it constant-memory. *Say this.*

## Parallelizing (ties to GIL answer)

Simulation is CPU-bound and embarrassingly parallel → use processes, each with its own seed, then
combine. Each worker returns partial sums; you merge means/variances.

```python
from multiprocessing import Pool
def worker(args):
    seed, n = args
    machine = build_machine(seed)           # fresh seeded RNG per process
    bot = SimulationBot(machine)
    return bot.run(n)
# split 100M spins across cores, then aggregate weighted RTPs
```

## The optimization loop (a JD responsibility)

1. Build a candidate config (reel strips + paytable + symbol weights).
2. Run the bot for N spins → measured RTP, hit rate, volatility.
3. Compare to target (e.g. RTP 96% ± 0.1%, target volatility class).
4. Adjust strips/weights/paytable; repeat. (Real studios may use search/optimization here.)

A clean way to put it: *"The bot is the measurement instrument; tuning the reel strips and symbol
weights is the control. I'd build a feedback loop and possibly a parameter search to converge on the
target RTP and volatility."*

---

### Talking points if they ask "how would you verify the bot is correct?"
- For a tiny config, compute the **exact RTP analytically** (sum over all stop combinations) and
  check the simulation converges to it (file 04 §10 worked example).
- Seed the RNG and assert deterministic, repeatable results.
- Property tests: RTP ∈ [0,1] for a losing-config; total_win ≥ 0; with more spins, CI narrows.
