"""Core slot engine: reels, paytable, machine, spin result.

Designed to demonstrate the patterns an interviewer wants to see:
  - dependency injection of the RNG (reproducible, testable)
  - immutable value objects via frozen+slots dataclasses
  - composition over inheritance (machine HAS reels, paytable, rng)
  - pure-ish evaluation that is easy to unit test
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field

SYMBOLS = ["7", "BAR", "BELL", "CHERRY", "WILD", "SCATTER"]


# NOTE: we use frozen=True (immutable, hashable) but NOT slots=True, because
# dataclass slots require Python 3.10+. This keeps the project runnable on an
# older work-computer Python (3.8+). For a real high-volume engine you'd add
# __slots__ for memory; mention that trade-off in the interview.
@dataclass(frozen=True)
class SpinResult:
    """Immutable result of a single spin. total_win is in bet-units."""
    board: tuple
    total_win: int
    line_wins: tuple = field(default_factory=tuple)


class ReelStrip:
    """One reel: an ordered list of symbols. A spin picks a random stop."""

    def __init__(self, strip: list[str]):
        if not strip:
            raise ValueError("reel strip cannot be empty")
        self.strip = list(strip)
        self.n = len(self.strip)

    def window(self, rng: random.Random, rows: int = 3) -> tuple:
        """Return the `rows` visible symbols starting at a random stop."""
        stop = rng.randrange(self.n)
        return tuple(self.strip[(stop + i) % self.n] for i in range(rows))


class Paytable:
    """Maps (symbol, count-from-leftmost) -> payout multiplier.

    WILD substitutes for any symbol; SCATTER is handled separately by the machine.
    """

    def __init__(self, table: dict, wild: str = "WILD"):
        self.table = dict(table)
        self.wild = wild

    def score_line(self, line: list[str]) -> int:
        # First non-wild symbol determines what we're matching.
        first = next((s for s in line if s != self.wild), self.wild)
        if first == "SCATTER":
            return 0  # scatters don't pay on lines
        count = 0
        for s in line:
            if s == first or s == self.wild:
                count += 1
            else:
                break
        return self.table.get((first, count), 0)


class SlotMachine:
    """A slot machine composed of reels + a paytable + an injected RNG."""

    def __init__(self, reels, paytable, rng=None, paylines=None, rows=3,
                 scatter_symbol="SCATTER", scatter_min=3, scatter_pay=2):
        self.reels = reels
        self.paytable = paytable
        self.rng = rng or random.Random()
        self.rows = rows
        self.scatter_symbol = scatter_symbol
        self.scatter_min = scatter_min
        self.scatter_pay = scatter_pay
        # Default paylines: the horizontal rows of the board.
        self.paylines = paylines or [
            [(c, r) for c in range(len(reels))] for r in range(rows)
        ]

    def spin(self) -> SpinResult:
        board = tuple(reel.window(self.rng, self.rows) for reel in self.reels)
        total = 0
        line_wins = []
        for idx, line in enumerate(self.paylines):
            symbols = [board[col][row] for (col, row) in line]
            win = self.paytable.score_line(symbols)
            if win:
                total += win
                line_wins.append((idx, win))
        scatters = sum(
            s == self.scatter_symbol for col in board for s in col
        )
        if scatters >= self.scatter_min:
            total += scatters * self.scatter_pay
        return SpinResult(board=board, total_win=total, line_wins=tuple(line_wins))
