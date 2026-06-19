"""Tests for the slot engine. Run: python -m pytest  (or python tests/test_engine.py)

Demonstrates the testing ideas from prep/07: deterministic seeded tests,
parametrization, statistical tolerance, and validating the Monte Carlo bot
against an exact analytic RTP.
"""
import random
from itertools import product

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from slot_engine.machine import ReelStrip, Paytable, SlotMachine
from slot_engine.bot import SimulationBot, RunningStats


# ---- unit tests -----------------------------------------------------------

def test_paytable_three_of_a_kind():
    pt = Paytable({("BAR", 3): 15})
    assert pt.score_line(["BAR", "BAR", "BAR", "CHERRY", "BELL"]) == 15


def test_wild_substitutes():
    pt = Paytable({("BAR", 3): 15})
    assert pt.score_line(["BAR", "WILD", "BAR", "CHERRY", "BELL"]) == 15


def test_no_win_returns_zero():
    pt = Paytable({("BAR", 3): 15})
    assert pt.score_line(["CHERRY", "BELL", "7", "BAR", "WILD"]) == 0


def test_reel_window_length():
    strip = ReelStrip(["7", "BAR", "CHERRY", "BELL"])
    win = strip.window(random.Random(0), rows=3)
    assert len(win) == 3


# ---- determinism (the payoff of injecting the RNG) ------------------------

def test_seeded_spins_are_reproducible():
    def build():
        rng = random.Random(123)
        reels = [ReelStrip(["7", "BAR", "CHERRY", "WILD", "SCATTER", "BELL"]) for _ in range(5)]
        return SlotMachine(reels, Paytable({("7", 3): 50}), rng=rng)

    seq1 = [build().spin().board for _ in range(1)]  # fresh seeded build
    seq2 = [build().spin().board for _ in range(1)]
    assert seq1 == seq2


# ---- property-style invariants -------------------------------------------

def test_payout_never_negative():
    rng = random.Random(7)
    reels = [ReelStrip(["7", "BAR", "CHERRY", "WILD", "SCATTER", "BELL"]) for _ in range(5)]
    m = SlotMachine(reels, Paytable({("7", 3): 50, ("CHERRY", 3): 5}), rng=rng)
    for _ in range(1000):
        assert m.spin().total_win >= 0


# ---- statistical: bot converges to exact analytic RTP ---------------------

def _exact_rtp_3reel(strip, three_pay, bet=1):
    """Brute-force exact RTP for a single-line 3-reel game."""
    n = len(strip)
    total = 0
    for a, b, c in product(strip, repeat=3):
        if a == b == c:
            total += three_pay.get(a, 0)
    return total / (n ** 3) / bet


def test_bot_matches_analytic_rtp():
    strip = ["7", "BAR", "BAR", "CHERRY", "CHERRY", "CHERRY"]
    three_pay = {"7": 5, "BAR": 2, "CHERRY": 1}  # tuned so RTP < 1
    exact = _exact_rtp_3reel(strip, three_pay)

    # Build a 3-reel, single-line machine matching the analytic model.
    reels = [ReelStrip(strip) for _ in range(3)]
    paytable = Paytable({(s, 3): p for s, p in three_pay.items()})
    rng = random.Random(2024)
    payline = [[(c, 0) for c in range(3)]]
    machine = SlotMachine(reels, paytable, rng=rng, paylines=payline, rows=1,
                          scatter_min=99)  # disable scatter
    bot = SimulationBot(machine, bet=1)
    result = bot.run(300_000)

    # Monte Carlo should land within the 95% CI of the exact value.
    lo, hi = result["rtp_95ci"]
    assert lo <= exact <= hi, f"exact={exact}, ci=({lo},{hi})"


def test_running_stats_welford():
    s = RunningStats()
    for x in [2, 4, 4, 4, 5, 5, 7, 9]:
        s.update(x)
    assert abs(s.mean - 5.0) < 1e-9
    assert abs(s.variance - 4.0) < 1e-9  # population variance of this classic set


if __name__ == "__main__":
    import traceback
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    passed = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS  {fn.__name__}")
            passed += 1
        except Exception:
            print(f"FAIL  {fn.__name__}")
            traceback.print_exc()
    print(f"\n{passed}/{len(fns)} passed")
