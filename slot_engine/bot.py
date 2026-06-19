"""Simulation bot: plays a machine many times and gathers statistics.

Uses Welford's online algorithm so memory stays O(1) even for 100M+ spins -
you cannot hold every payout in a list at that scale. This is the heart of the
job: simulate player actions repeatedly and gather statistical data (RTP,
hit-rate, volatility).
"""
from __future__ import annotations

import math


class RunningStats:
    """Online mean + variance (Welford) plus hit-rate and max-win tracking.

    "Online" means we update the statistics one value at a time and never store
    the values themselves - so 100 million spins use the same tiny memory as 100.
    Welford's algorithm is also numerically stable (avoids the precision problems
    of the naive "sum of squares minus square of sum" formula).
    """

    def __init__(self):
        self.n = 0              # how many values we've seen
        self.mean = 0.0         # running average of the payouts
        self.m2 = 0.0           # running sum of squared deviations from the mean (for variance)
        self.wins = 0           # how many spins paid > 0 (for hit-rate)
        self.max_win = 0.0      # biggest single payout seen

    def update(self, x: float) -> None:
        """Fold one new value `x` into the running statistics."""
        self.n += 1
        delta = x - self.mean           # distance from the OLD mean
        self.mean += delta / self.n     # nudge the mean toward the new value
        # m2 accumulates using BOTH the old-mean delta and the new-mean delta;
        # that product is the Welford trick that keeps variance correct online.
        self.m2 += delta * (x - self.mean)
        if x > 0:                       # any payout counts as a "hit"
            self.wins += 1
        if x > self.max_win:            # track the largest win
            self.max_win = x

    @property
    def variance(self) -> float:
        # Population variance = sum of squared deviations / n. (Guard n==0.)
        return self.m2 / self.n if self.n else 0.0

    @property
    def std(self) -> float:
        # Standard deviation = sqrt(variance); our proxy for volatility.
        return math.sqrt(self.variance)

    @property
    def hit_rate(self) -> float:
        # Fraction of spins that won anything.
        return self.wins / self.n if self.n else 0.0


class SimulationBot:
    """Plays the machine n times. Bet is a flat number of units per spin."""

    def __init__(self, machine, bet: float = 1.0):
        self.machine = machine          # the SlotMachine to hammer
        self.bet = bet                  # wager per spin, in the same units as payouts

    def play(self, n: int):
        """Lazy generator of per-spin returns - O(1) memory.

        `yield` makes this a generator: it produces one payout at a time on demand
        instead of building a list of n results. That's why we can simulate
        hundreds of millions of spins without running out of memory.
        """
        for _ in range(n):
            yield self.machine.spin().total_win

    def run(self, n: int) -> dict:
        """Run n spins and return the headline statistics studios care about."""
        stats = RunningStats()
        for payout in self.play(n):     # stream the spins through the online stats
            stats.update(payout)
        # RTP = average return per unit wagered. The Law of Large Numbers says this
        # converges to the game's true RTP as n grows.
        rtp = stats.mean / self.bet
        # 95% confidence half-width for the RTP estimate (~1.96 * standard error).
        # Standard error = std / sqrt(n), so it shrinks like 1/sqrt(n): 4x the spins
        # halves the error. This number tells you how much to trust the RTP estimate.
        ci = (1.96 * stats.std / math.sqrt(stats.n) / self.bet) if stats.n else 0.0
        return {
            "spins": stats.n,
            "rtp": rtp,
            "rtp_95ci": (rtp - ci, rtp + ci),   # estimated RTP is very likely in this range
            "house_edge": 1 - rtp,              # the operator's long-run margin
            "hit_rate": stats.hit_rate,         # how often the player wins anything
            "volatility_std": stats.std,        # spread of outcomes (volatility proxy)
            "max_win": stats.max_win,           # biggest single win observed
        }
