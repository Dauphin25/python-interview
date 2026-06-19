"""Core slot engine: reels, paytable, machine, spin result.

Designed to demonstrate the patterns an interviewer wants to see:
  - dependency injection of the RNG (reproducible, testable)
  - immutable value objects via frozen dataclasses
  - composition over inheritance (machine HAS reels, paytable, rng)
  - pure-ish evaluation that is easy to unit test

Read this file top to bottom: a spin flows ReelStrip -> board -> Paytable -> SpinResult.
"""
# `from __future__ import annotations` makes all type hints lazy strings, so hints
# like `list[str]` work even on Python 3.8 (where that syntax isn't native yet).
from __future__ import annotations

import random                                   # the seedable pseudo-random generator
from dataclasses import dataclass, field        # for the immutable SpinResult value object

# The symbol "alphabet" of the game. Reel strips are built out of these names.
SYMBOLS = ["7", "BAR", "BELL", "CHERRY", "WILD", "SCATTER"]


# NOTE: we use frozen=True (immutable, hashable) but NOT slots=True, because
# dataclass slots require Python 3.10+. This keeps the project runnable on an
# older work-computer Python (3.8+). For a real high-volume engine you'd add
# __slots__ for memory; mention that trade-off in the interview.
@dataclass(frozen=True)
class SpinResult:
    """Immutable result of a single spin. total_win is in bet-units.

    @dataclass auto-generates __init__/__repr__/__eq__ for us.
    frozen=True makes instances read-only (can't be mutated after creation) and
    hashable - a good fit for a "value object" that just records what happened.
    """
    board: tuple        # the visible symbols: a tuple of columns, each column a tuple of symbols
    total_win: int      # total payout for this spin, in bet-units (0 means no win)
    # line_wins: which paylines won and how much, e.g. ((0, 15), (2, 5)).
    # We use default_factory (not `= ()`) because that's the dataclass-safe way to
    # give a default; it also dodges the classic mutable-default-argument trap.
    line_wins: tuple = field(default_factory=tuple)


class ReelStrip:
    """One reel: an ordered list of symbols. A spin picks a random stop position."""

    def __init__(self, strip: list[str]):
        if not strip:                           # guard: an empty reel makes no sense
            raise ValueError("reel strip cannot be empty")
        self.strip = list(strip)                # copy the list so the caller can't mutate ours
        self.n = len(self.strip)                # cache the length (used a lot)

    def window(self, rng: random.Random, rows: int = 3) -> tuple:
        """Return the `rows` visible symbols starting at a random stop.

        A real reel is a loop, so we pick a random start position and read the next
        few symbols, wrapping around the end with modulo (%). The RNG is passed in
        (dependency injection) so a seeded RNG gives a reproducible window in tests.
        """
        stop = rng.randrange(self.n)            # random start index in [0, n)
        # Read `rows` symbols from `stop`, wrapping with % so the strip behaves as a loop.
        return tuple(self.strip[(stop + i) % self.n] for i in range(rows))


class Paytable:
    """Maps (symbol, count-from-leftmost) -> payout multiplier.

    WILD substitutes for any symbol; SCATTER is handled separately by the machine.
    """

    def __init__(self, table: dict, wild: str = "WILD"):
        self.table = dict(table)                # copy the dict (defensive; caller can't mutate ours)
        self.wild = wild                        # which symbol acts as the wildcard

    def score_line(self, line: list[str]) -> int:
        """Score one payline left-to-right and return its payout multiplier.

        Slot rule: wins are counted from the leftmost reel; the run of matching
        symbols (with WILD substituting) decides the payout.
        """
        # The paying symbol is the first NON-wild symbol on the line. If the line is
        # all wilds, `next(..., default)` falls back to wild itself.
        first = next((s for s in line if s != self.wild), self.wild)
        if first == "SCATTER":
            return 0                            # scatters pay anywhere, not on lines -> handled elsewhere
        count = 0
        for s in line:                          # walk left-to-right counting the matching run
            if s == first or s == self.wild:    # a wild counts as a match too
                count += 1
            else:
                break                           # the run is broken -> stop counting
        # Look up (symbol, run-length) in the paytable; 0 if there's no such payout.
        return self.table.get((first, count), 0)


class SlotMachine:
    """A slot machine composed of reels + a paytable + an injected RNG.

    "Composition over inheritance": the machine HAS-A list of reels, a paytable and
    an RNG, rather than inheriting from them. That makes each part swappable/testable.
    """

    def __init__(self, reels, paytable, rng=None, paylines=None, rows=3,
                 scatter_symbol="SCATTER", scatter_min=3, scatter_pay=2):
        self.reels = reels                      # list[ReelStrip], one per reel column
        self.paytable = paytable                # Paytable used to score each line
        # If no RNG is injected, make a fresh one. Injecting a seeded Random(...) in
        # tests is what makes spins reproducible - the key testability trick here.
        self.rng = rng or random.Random()
        self.rows = rows                        # number of visible rows (board height)
        self.scatter_symbol = scatter_symbol    # symbol that pays "anywhere" on the board
        self.scatter_min = scatter_min          # need at least this many scatters to pay
        self.scatter_pay = scatter_pay          # payout per scatter when triggered
        # Default paylines = the horizontal rows of the board. Each payline is a list
        # of (column, row) coordinates. `paylines or [...]` keeps a caller-supplied one.
        self.paylines = paylines or [
            [(c, r) for c in range(len(reels))] for r in range(rows)
        ]

    def spin(self) -> SpinResult:
        """Play one spin: build the board, score every payline, add scatter pay."""
        # 1) Spin every reel to build the board: a tuple of columns (one per reel).
        board = tuple(reel.window(self.rng, self.rows) for reel in self.reels)
        total = 0                               # running total payout for this spin
        line_wins = []                          # record of (payline index, amount won)
        # 2) Score each payline by reading its symbols off the board.
        for idx, line in enumerate(self.paylines):
            symbols = [board[col][row] for (col, row) in line]   # gather this line's symbols
            win = self.paytable.score_line(symbols)
            if win:                             # only record actual wins
                total += win
                line_wins.append((idx, win))
        # 3) Scatter pays anywhere: count scatters across the whole board.
        #    (booleans are ints in Python, so summing `s == scatter` counts matches.)
        scatters = sum(
            s == self.scatter_symbol for col in board for s in col
        )
        if scatters >= self.scatter_min:
            total += scatters * self.scatter_pay
        # 4) Return an immutable record of what happened this spin.
        return SpinResult(board=board, total_win=total, line_wins=tuple(line_wins))
