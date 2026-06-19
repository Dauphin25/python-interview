"""Tests for the slot engine. Run: python -m pytest  (or python tests/test_engine.py)

Demonstrates the testing ideas from prep/07: deterministic seeded tests,
parametrization, statistical tolerance, and validating the Monte Carlo bot
against an exact analytic RTP. Each test function name starts with `test_` so
pytest discovers it automatically; an `assert` that fails marks the test failed.
"""
import random
from itertools import product                  # builds every combination of reel symbols

# Make the project root importable so `import slot_engine` works no matter where
# pytest is launched from. __file__ is this file; two dirnames up is the repo root.
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from slot_engine.machine import ReelStrip, Paytable, SlotMachine
from slot_engine.bot import SimulationBot, RunningStats


# ---- unit tests -----------------------------------------------------------
# Each checks ONE small behaviour in isolation.

def test_paytable_three_of_a_kind():
    # Three BARs from the left should pay the (BAR, 3) value of 15.
    pt = Paytable({("BAR", 3): 15})
    assert pt.score_line(["BAR", "BAR", "BAR", "CHERRY", "BELL"]) == 15


def test_wild_substitutes():
    # WILD stands in for BAR, so BAR-WILD-BAR still counts as three BARs.
    pt = Paytable({("BAR", 3): 15})
    assert pt.score_line(["BAR", "WILD", "BAR", "CHERRY", "BELL"]) == 15


def test_no_win_returns_zero():
    # No run of 3+ matching symbols from the left -> no payout.
    pt = Paytable({("BAR", 3): 15})
    assert pt.score_line(["CHERRY", "BELL", "7", "BAR", "WILD"]) == 0


def test_reel_window_length():
    # A 3-row window must return exactly 3 visible symbols.
    strip = ReelStrip(["7", "BAR", "CHERRY", "BELL"])
    win = strip.window(random.Random(0), rows=3)
    assert len(win) == 3


# ---- determinism (the payoff of injecting the RNG) ------------------------

def test_seeded_spins_are_reproducible():
    # Same seed must produce the same board - this is why we inject the RNG.
    def build():
        rng = random.Random(123)                # identical seed each time
        reels = [ReelStrip(["7", "BAR", "CHERRY", "WILD", "SCATTER", "BELL"]) for _ in range(5)]
        return SlotMachine(reels, Paytable({("7", 3): 50}), rng=rng)

    seq1 = [build().spin().board for _ in range(1)]  # fresh seeded build
    seq2 = [build().spin().board for _ in range(1)]
    assert seq1 == seq2                          # identical seeds -> identical spins


# ---- property-style invariants -------------------------------------------

def test_payout_never_negative():
    # Invariant: a spin can never pay a negative amount, no matter the board.
    rng = random.Random(7)
    reels = [ReelStrip(["7", "BAR", "CHERRY", "WILD", "SCATTER", "BELL"]) for _ in range(5)]
    m = SlotMachine(reels, Paytable({("7", 3): 50, ("CHERRY", 3): 5}), rng=rng)
    for _ in range(1000):                        # check over many random spins
        assert m.spin().total_win >= 0


# ---- statistical: bot converges to exact analytic RTP ---------------------

def _exact_rtp_3reel(strip, three_pay, bet=1):
    """Brute-force exact RTP for a single-line 3-reel game.

    Because the game is tiny we can enumerate EVERY outcome (strip^3 combos),
    sum the payouts, and divide by the number of combos -> the true RTP with no
    sampling error. This is the "ground truth" we test the simulation against.
    """
    n = len(strip)
    total = 0
    for a, b, c in product(strip, repeat=3):     # every (reel1, reel2, reel3) combination
        if a == b == c:                          # three matching symbols = a win
            total += three_pay.get(a, 0)
    return total / (n ** 3) / bet                # average payout per spin / bet = RTP


def test_bot_matches_analytic_rtp():
    # The headline test: the Monte Carlo bot must agree with the exact math.
    strip = ["7", "BAR", "BAR", "CHERRY", "CHERRY", "CHERRY"]
    three_pay = {"7": 5, "BAR": 2, "CHERRY": 1}  # tuned so RTP < 1
    exact = _exact_rtp_3reel(strip, three_pay)   # the true value, computed analytically

    # Build a 3-reel, single-line machine matching that analytic model exactly.
    reels = [ReelStrip(strip) for _ in range(3)]
    # Rebuild the paytable in (symbol, 3) form the engine expects.
    paytable = Paytable({(s, 3): p for s, p in three_pay.items()})
    rng = random.Random(2024)                    # fixed seed -> reproducible test
    payline = [[(c, 0) for c in range(3)]]       # one horizontal line across 3 reels
    machine = SlotMachine(reels, paytable, rng=rng, paylines=payline, rows=1,
                          scatter_min=99)         # scatter_min=99 effectively disables scatter pay
    bot = SimulationBot(machine, bet=1)
    result = bot.run(300_000)                     # simulate enough spins to converge

    # The exact RTP should fall inside the simulation's 95% confidence interval.
    lo, hi = result["rtp_95ci"]
    assert lo <= exact <= hi, f"exact={exact}, ci=({lo},{hi})"


def test_running_stats_welford():
    # Verify the online mean/variance against a known textbook data set.
    s = RunningStats()
    for x in [2, 4, 4, 4, 5, 5, 7, 9]:
        s.update(x)
    assert abs(s.mean - 5.0) < 1e-9              # known mean is exactly 5
    assert abs(s.variance - 4.0) < 1e-9          # known population variance is exactly 4


# ---- tiny built-in runner (so it works WITHOUT pytest installed) ----------
if __name__ == "__main__":
    import traceback
    # Collect every top-level function whose name starts with "test_".
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    passed = 0
    for fn in fns:
        try:
            fn()                                 # run the test; no exception = pass
            print(f"PASS  {fn.__name__}")
            passed += 1
        except Exception:                        # any assertion/error = fail; show why
            print(f"FAIL  {fn.__name__}")
            traceback.print_exc()
    print(f"\n{passed}/{len(fns)} passed")
