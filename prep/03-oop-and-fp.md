# 03 — OOP with Functional Elements

The JD says: *"Confident understanding of OOP with functional programming elements."* That exact
phrasing means they want clean class design AND comfort with `map`/`filter`/`lambda`/immutability/
pure functions. Below covers both with slot-flavored examples.

---

# PART A — Object-Oriented Python

## 1. The four pillars (be able to give a one-line + example each)

- **Encapsulation** — bundle data + behavior; hide internals behind an interface.
- **Abstraction** — expose *what*, hide *how* (`abc.ABC`, interfaces).
- **Inheritance** — reuse/extend behavior. Python supports multiple inheritance.
- **Polymorphism** — same interface, different implementations (duck typing).

```python
from abc import ABC, abstractmethod

class Feature(ABC):                  # abstraction
    @abstractmethod
    def trigger(self, board): ...    # subclasses MUST implement

class FreeSpins(Feature):            # inheritance
    def trigger(self, board):        # polymorphism
        return board.count("SCATTER") >= 3

class Wild(Feature):
    def trigger(self, board):
        return "WILD" in board

for f in [FreeSpins(), Wild()]:      # same interface, different behavior
    f.trigger(board)
```

## 2. Encapsulation conventions

```python
class Wallet:
    def __init__(self, balance):
        self.balance = balance        # public
        self._internal = 0            # _ = "protected" by convention (just a hint)
        self.__secret = 0             # __ = name-mangled to _Wallet__secret
```
Python has **no real private**; it's convention + name-mangling. Use `@property` for controlled access.

```python
class Reel:
    def __init__(self, strip): self._strip = strip
    @property
    def length(self):                 # read-only computed attribute
        return len(self._strip)
```

## 3. `classmethod` vs `staticmethod` vs instance method

```python
class Game:
    house_edge = 0.04                          # class attribute (shared)
    def __init__(self, rtp): self.rtp = rtp    # instance attribute

    def play(self): ...                        # instance method (self)

    @classmethod
    def from_rtp(cls, rtp):                     # alternative constructor
        return cls(rtp)                         # cls supports subclassing

    @staticmethod
    def cents_to_dollars(c):                    # no self/cls; just namespaced
        return c / 100
```

## 4. `super()` and MRO (Method Resolution Order)

```python
class Base:
    def __init__(self): self.kind = "base"
class FreeSpinGame(Base):
    def __init__(self):
        super().__init__()        # cooperative init up the chain
        self.feature = "free"
```
Multiple inheritance resolves via **C3 linearization**; inspect with `Cls.__mro__`. Mention the
**diamond problem** and that `super()` follows the MRO, not just the parent.

## 5. Composition over inheritance (senior judgment)

Prefer *has-a* to *is-a* when behavior varies independently.

```python
class SlotMachine:
    def __init__(self, rng, paytable, reels):   # composed of collaborators
        self.rng = rng
        self.paytable = paytable
        self.reels = reels
```
This is also more testable (inject a fake RNG) — a point worth making aloud.

## 6. `@dataclass` (modern, expected)

```python
from dataclasses import dataclass, field

@dataclass(frozen=True, slots=True)     # frozen = immutable + hashable
class SpinResult:
    board: tuple
    total_win: int
    lines_won: tuple = field(default_factory=tuple)

r = SpinResult(board=(...), total_win=50)
# auto __init__, __repr__, __eq__; frozen adds __hash__ and blocks mutation
```
`frozen=True` is great for value objects (results, configs). `slots=True` saves memory at scale.

## 7. Design patterns worth naming for a game engine

- **Strategy** — swap algorithms (different `Feature`/payout strategies). Shown above.
- **Factory** — `Game.from_config(cfg)` build objects without exposing construction.
- **State** — game states (idle → spinning → free-spins → settled).
- **Observer** — notify stats collector on each spin.
- **Singleton** — usually an anti-pattern in Python; a module is already a singleton.

## 8. SOLID (one line each, in slot terms)

- **S**ingle responsibility — RNG class only randomizes; Paytable only scores.
- **O**pen/closed — add a new `Feature` subclass without editing the engine.
- **L**iskov — any `Feature` is substitutable wherever `Feature` is expected.
- **I**nterface segregation — small focused ABCs, not one giant interface.
- **D**ependency inversion — engine depends on a `RNG` abstraction, not a concrete one
  (lets you inject a deterministic RNG in tests).

---

# PART B — Functional Programming elements

## 1. First-class & higher-order functions

Functions are objects: pass them, return them, store them.
```python
def apply(fn, value): return fn(value)
strategies = {"double": lambda x: x*2, "free": grant_free_spins}
strategies["double"](10)
```

## 2. `map`, `filter`, `reduce`, `lambda`

```python
payouts = list(map(lambda s: s.payout, spins))
wins    = list(filter(lambda s: s.payout > 0, spins))

from functools import reduce
total   = reduce(lambda acc, s: acc + s.payout, spins, 0)
```
But **pythonic style prefers comprehensions/generators** over `map`/`filter`:
```python
payouts = [s.payout for s in spins]
total   = sum(s.payout for s in spins)      # clearer than reduce
```
Good answer: *"I know map/filter/reduce, but I reach for comprehensions and `sum`/`any`/`all`
because they're more readable; `reduce` only when there's no built-in."*

## 3. Pure functions & immutability (why FP matters for simulations)

A **pure function**: output depends only on inputs, no side effects. Benefits: trivially testable,
parallelizable, reproducible.

```python
def evaluate_board(board, paytable):      # pure: same board -> same result
    return sum(paytable.score(line) for line in paylines(board))
```
For a **fair, reproducible simulation**, purity + a seeded RNG = you can replay any spin. Huge in
gambling: regulators and QA need reproducibility. Mention this — it's a domain-aware point.

## 4. `functools` toolkit

```python
from functools import partial, reduce, lru_cache, cache

spin_5_lines = partial(spin, lines=5)     # pre-bind arguments
@cache                                     # 3.9+ unbounded memoization
def combinations(n, r): ...
```

## 5. Closures

A function capturing variables from its enclosing scope.
```python
def make_paytable(multiplier):
    def score(count):           # closes over `multiplier`
        return count * multiplier
    return score
triple = make_paytable(3)
```
Watch the **late-binding closure trap**:
```python
funcs = [lambda: i for i in range(3)]
[f() for f in funcs]            # [2, 2, 2]  -- i is looked up at call time!
funcs = [lambda i=i: i for i in range(3)]   # fix: default-arg captures now
```

## 6. Generators as functional pipelines

```python
def pipeline(spins):
    spins = (s for s in spins if s.payout > 0)       # filter
    spins = ((s, s.payout * 2) for s in spins)       # map
    return sum(p for _, p in spins)                  # reduce
```
Lazy, composable, memory-flat — ideal for streaming simulation results.

---

### Drill yourself
- Encapsulation vs abstraction — what's the difference?
- When composition over inheritance? Give a slot example.
- Why are pure functions valuable for a simulation bot? (reproducibility, parallelism, testing)
- Explain the late-binding closure bug and the fix.
- `classmethod` vs `staticmethod` — when each?
