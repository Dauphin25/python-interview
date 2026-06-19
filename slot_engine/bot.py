"""Simulation bot: plays a machine many times and gathers statistics.

Uses Welford's online algorithm so memory stays O(1) even for 100M+ spins -
you cannot hold every payout in a list at that scale.
"""
from __future__ import annotations

import math


class RunningStats:
    """Online mean + variance (Welford) plus hit-rate and max-win tracking."""

    def __init__(self):
        self.n = 0
        self.mean = 0.0
        self.m2 = 0.0
        self.wins = 0
        self.max_win = 0.0

    def update(self, x: float) -> None:
        self.n += 1
        delta = x - self.mean
        self.mean += delta / self.n
        self.m2 += delta * (x - self.mean)
        if x > 0:
            self.wins += 1
        if x > self.max_win:
            self.max_win = x

    @property
    def variance(self) -> float:
        return self.m2 / self.n if self.n else 0.0

    @property
    def std(self) -> float:
        return math.sqrt(self.variance)

    @property
    def hit_rate(self) -> float:
        return self.wins / self.n if self.n else 0.0


class SimulationBot:
    """Plays the machine n times. Bet is a flat number of units per spin."""

    def __init__(self, machine, bet: float = 1.0):
        self.machine = machine
        self.bet = bet

    def play(self, n: int):
        """Lazy generator of per-spin returns - O(1) memory."""
        for _ in range(n):
            yield self.machine.spin().total_win

    def run(self, n: int) -> dict:
        stats = RunningStats()
        for payout in self.play(n):
            stats.update(payout)
        rtp = stats.mean / self.bet
        # 95% confidence half-width for the RTP estimate (~1.96 * SE).
        ci = (1.96 * stats.std / math.sqrt(stats.n) / self.bet) if stats.n else 0.0
        return {
            "spins": stats.n,
            "rtp": rtp,
            "rtp_95ci": (rtp - ci, rtp + ci),
            "house_edge": 1 - rtp,
            "hit_rate": stats.hit_rate,
            "volatility_std": stats.std,
            "max_win": stats.max_win,
        }
