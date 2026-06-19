"""Runnable demo. Builds a 5-reel machine and runs a Monte Carlo simulation.

    python -m slot_engine.simulate
    python -m slot_engine.simulate 5000000 7   # spins, seed
"""
from __future__ import annotations

import random
import sys

from .machine import ReelStrip, Paytable, SlotMachine
from .bot import SimulationBot


def build_machine(seed: int | None = None) -> SlotMachine:
    """A deliberately simple, tunable 5x3 machine.

    Tune RTP/volatility by editing the reel strips (symbol frequencies) and the
    paytable. More high-paying symbols on the strips -> higher RTP & volatility.
    """
    # ~40-position strips. "BLANK" is a non-paying filler that controls how
    # often premium symbols line up - the main lever for lowering RTP.
    base_strip = (
        ["BLANK"] * 15
        + ["CHERRY"] * 8
        + ["BELL"] * 6
        + ["BAR"] * 4
        + ["7"] * 1
        + ["WILD"] * 2
        + ["SCATTER"] * 1
    )
    reels = [ReelStrip(base_strip) for _ in range(5)]

    paytable = Paytable({
        ("7", 3): 40, ("7", 4): 150, ("7", 5): 500,
        ("BAR", 3): 15, ("BAR", 4): 40, ("BAR", 5): 120,
        ("BELL", 3): 6, ("BELL", 4): 15, ("BELL", 5): 40,
        ("CHERRY", 3): 3, ("CHERRY", 4): 8, ("CHERRY", 5): 20,
    })

    rng = random.Random(seed)
    return SlotMachine(reels, paytable, rng=rng)


def main() -> None:
    spins = int(sys.argv[1]) if len(sys.argv) > 1 else 1_000_000
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 42

    machine = build_machine(seed=seed)
    bot = SimulationBot(machine, bet=1)

    print(f"Running {spins:,} spins (seed={seed})...")
    stats = bot.run(spins)

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
