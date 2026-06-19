"""Runnable demo. Builds a 5-reel machine and runs a Monte Carlo simulation.

    python -m slot_engine.simulate
    python -m slot_engine.simulate 5000000 7   # spins, seed
"""
from __future__ import annotations

import random
import sys                                       # to read command-line args (spins, seed)

# Relative imports (the leading dot) pull from this same `slot_engine` package.
from .machine import ReelStrip, Paytable, SlotMachine
from .bot import SimulationBot


def build_machine(seed: int | None = None) -> SlotMachine:
    """A deliberately simple, tunable 5x3 machine.

    Tune RTP/volatility by editing the reel strips (symbol frequencies) and the
    paytable. More high-paying symbols on the strips -> higher RTP & volatility.
    The `seed` makes the whole simulation reproducible: same seed => same spins.
    """
    # ~40-position strips. "BLANK" is a non-paying filler that controls how
    # often premium symbols line up - the main lever for lowering RTP.
    # Build one reel strip by repeating symbols. The COUNT of each symbol sets its
    # probability (count / strip_length). "BLANK" pays nothing; adding more blanks
    # makes premium symbols line up less often -> lowers RTP. This list is THE dial
    # designers turn. (`["X"] * 3` makes ["X","X","X"]; `+` concatenates the lists.)
    base_strip = (
        ["BLANK"] * 15          # filler: rarer wins
        + ["CHERRY"] * 8        # common low-pay symbol
        + ["BELL"] * 6
        + ["BAR"] * 4
        + ["7"] * 1             # rare top symbol -> big, infrequent wins (volatility)
        + ["WILD"] * 2          # substitutes to complete wins
        + ["SCATTER"] * 1       # triggers the scatter pay
    )
    # All 5 reels use the same strip here; real games often use a different strip per reel.
    reels = [ReelStrip(base_strip) for _ in range(5)]

    # Paytable: (symbol, how-many-in-a-row-from-the-left) -> payout multiplier.
    # Bigger numbers or longer strips raise RTP; this is the other tuning dial.
    paytable = Paytable({
        ("7", 3): 40, ("7", 4): 150, ("7", 5): 500,
        ("BAR", 3): 15, ("BAR", 4): 40, ("BAR", 5): 120,
        ("BELL", 3): 6, ("BELL", 4): 15, ("BELL", 5): 40,
        ("CHERRY", 3): 3, ("CHERRY", 4): 8, ("CHERRY", 5): 20,
    })

    # random.Random(seed) is an isolated, seeded generator (not the global random
    # state) - good practice and what makes runs reproducible.
    rng = random.Random(seed)
    return SlotMachine(reels, paytable, rng=rng)


def main() -> None:
    # Read optional command-line args: argv[1]=spins, argv[2]=seed; else use defaults.
    spins = int(sys.argv[1]) if len(sys.argv) > 1 else 1_000_000
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 42

    machine = build_machine(seed=seed)          # construct the game
    bot = SimulationBot(machine, bet=1)         # the simulator, wagering 1 unit/spin

    print(f"Running {spins:,} spins (seed={seed})...")
    stats = bot.run(spins)                      # run the Monte Carlo simulation

    # Unpack the confidence interval and print a readable report.
    # `:.4%` formats a fraction as a percentage with 4 decimals (0.96 -> 96.0000%).
    lo, hi = stats["rtp_95ci"]
    print("-" * 48)
    print(f"Spins:           {stats['spins']:,}")
    print(f"RTP:             {stats['rtp']:.4%}")
    print(f"RTP 95% CI:      [{lo:.4%}, {hi:.4%}]")
    print(f"House edge:      {stats['house_edge']:.4%}")
    print(f"Hit rate:        {stats['hit_rate']:.4%}")
    print(f"Volatility (sd): {stats['volatility_std']:.4f}")
    print(f"Max win:         {stats['max_win']:.0f}x")
    print("-" * 48)
    print("Tune build_machine() reel strips / paytable to hit a target RTP.")


if __name__ == "__main__":
    main()
