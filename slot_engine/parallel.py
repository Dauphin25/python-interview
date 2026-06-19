"""Parallel Monte Carlo runner - uses ALL CPU cores via multiprocessing.

This is the concrete answer to "the simulation is CPU-bound, how do you use all
cores?" Threads wouldn't help (GIL); separate processes each get their own GIL
and their own seeded RNG. Each worker returns partial stats, then we combine
the means/variances with the parallel (Chan) variance-merge formula.

    python -m slot_engine.parallel 4000000 4      # total spins, workers

Standard library only. Windows-safe (guarded __main__, top-level worker fn).
"""
from __future__ import annotations

import sys
import time
from multiprocessing import Pool, cpu_count

from .bot import SimulationBot, RunningStats
from .simulate import build_machine


def _run_chunk(args):
    """Top-level (picklable) worker: simulate `n` spins with a unique seed."""
    seed, n = args
    machine = build_machine(seed=seed)          # fresh, independently seeded RNG
    bot = SimulationBot(machine, bet=1)
    stats = RunningStats()
    for payout in bot.play(n):
        stats.update(payout)
    # Return raw moments so the parent can merge exactly.
    return (stats.n, stats.mean, stats.m2, stats.wins, stats.max_win)


def _merge(parts):
    """Combine per-worker (n, mean, m2, wins, max) into global stats (Chan et al.).

    You can't just average the per-worker means if the chunks differ in size, and
    you can't just add the variances. The Chan parallel formula below combines two
    groups' counts/means/M2 exactly - so 4 workers give the SAME result as 1.
    """
    N = 0              # total count so far
    mean = 0.0         # combined mean so far
    M2 = 0.0           # combined sum of squared deviations so far
    wins = 0           # total winning spins
    max_win = 0.0      # overall biggest win
    for n, m, m2, w, mx in parts:               # fold in each worker's partial result
        if n == 0:
            continue
        delta = m - mean                        # gap between this chunk's mean and the combined mean
        new_N = N + n
        # Combined mean = weighted average of the two means by their counts.
        mean = (N * mean + n * m) / new_N
        # Combined M2 adds both chunks' M2 PLUS a correction term for the gap between
        # their means (delta^2 weighted by the two counts). This is the key step.
        M2 = M2 + m2 + delta * delta * N * n / new_N
        N = new_N
        wins += w
        max_win = max(max_win, mx)
    variance = M2 / N if N else 0.0
    return N, mean, variance, wins, max_win


def run_parallel(total_spins: int, workers: int | None = None, bet: float = 1.0) -> dict:
    workers = workers or cpu_count()            # default to one worker per CPU core
    per = total_spins // workers                # base spins per worker (integer division)
    # Each chunk is (seed, n_spins). A distinct seed per worker keeps the random
    # streams independent so we don't simulate the same spins 4 times.
    chunks = [(seed, per) for seed in range(workers)]
    leftover = total_spins - per * workers      # spins lost to integer division...
    if leftover:
        chunks[0] = (chunks[0][0], chunks[0][1] + leftover)   # ...give them to worker 0

    # Pool spins up `workers` separate PROCESSES (own GIL each) and maps the chunks
    # across them in true parallel. `with` ensures the pool is cleaned up afterwards.
    with Pool(workers) as pool:
        parts = pool.map(_run_chunk, chunks)    # blocks until all workers finish

    N, mean, variance, wins, max_win = _merge(parts)   # combine the partial results
    std = variance ** 0.5                       # ** 0.5 is square root
    rtp = mean / bet
    ci = (1.96 * std / (N ** 0.5) / bet) if N else 0.0  # 95% CI half-width (see bot.py)
    return {
        "spins": N,
        "workers": workers,
        "rtp": rtp,
        "rtp_95ci": (rtp - ci, rtp + ci),
        "house_edge": 1 - rtp,
        "hit_rate": wins / N if N else 0.0,
        "volatility_std": std,
        "max_win": max_win,
    }


def main() -> None:
    total = int(sys.argv[1]) if len(sys.argv) > 1 else 2_000_000
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else cpu_count()
    print(f"Running {total:,} spins across {workers} processes...")
    start = time.perf_counter()
    r = run_parallel(total, workers)
    elapsed = time.perf_counter() - start
    lo, hi = r["rtp_95ci"]
    print("-" * 48)
    print(f"Spins:        {r['spins']:,}  on {r['workers']} cores")
    print(f"RTP:          {r['rtp']:.4%}   95% CI [{lo:.4%}, {hi:.4%}]")
    print(f"House edge:   {r['house_edge']:.4%}")
    print(f"Hit rate:     {r['hit_rate']:.4%}")
    print(f"Volatility:   {r['volatility_std']:.4f}")
    print(f"Max win:      {r['max_win']:.0f}x")
    print(f"Wall time:    {elapsed:.2f}s  ({r['spins']/elapsed:,.0f} spins/s)")
    print("-" * 48)


if __name__ == "__main__":
    main()
