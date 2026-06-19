# 01 — Modern Python Core (must be fluent)

These are the fundamentals an interviewer assumes a "confident Python" candidate owns. Be able to
*explain the why*, not just recite.

---

## 1. The data model: everything is an object, names are references

```python
a = [1, 2, 3]
b = a          # b and a point to the SAME object
b.append(4)
print(a)       # [1, 2, 3, 4]  <-- surprises juniors
```

- A variable is a **name bound to an object**, not a box holding a value.
- `=` never copies; it rebinds a name.
- `id(x)` is the identity (CPython: memory address). `is` compares identity, `==` compares value.

**Trick question:** `a is b` vs `a == b`. Use `is` only for singletons: `None`, `True`, `False`.
Never `if x is "string"` or `if x is 1000` — that relies on interning and is undefined behavior.

```python
x = 256; y = 256; x is y     # True  (small ints are cached/interned, -5..256)
x = 257; y = 257; x is y     # often False
```

## 2. Mutable vs immutable

- **Immutable:** `int, float, str, tuple, frozenset, bytes, bool`. Hashable → usable as dict keys.
- **Mutable:** `list, dict, set, bytearray`, most custom objects. Not hashable by default.

**The classic mutable-default-argument trap (they LOVE this):**

```python
def add_spin(result, log=[]):     # BUG: default list created ONCE at def time
    log.append(result)
    return log

add_spin(10)   # [10]
add_spin(20)   # [10, 20]  <-- shared across calls!

# Correct:
def add_spin(result, log=None):
    if log is None:
        log = []
    log.append(result)
    return log
```

## 3. Shallow vs deep copy

```python
import copy
reels = [[1,2,3], [4,5,6]]
shallow = copy.copy(reels)     # new outer list, SAME inner lists
deep    = copy.deepcopy(reels) # fully independent
shallow[0].append(99)          # also mutates reels[0]!
```

## 4. Truthiness

Falsy: `0, 0.0, '', [], {}, set(), None, False`. Everything else truthy.
`if my_list:` (pythonic) vs `if len(my_list) > 0:` (verbose).

## 5. Core comprehensions & idioms

```python
squares   = [x*x for x in range(10)]
evens     = [x for x in range(10) if x % 2 == 0]
matrix    = [[r*c for c in range(3)] for r in range(3)]
lookup    = {sym: i for i, sym in enumerate(symbols)}
unique    = {x % 5 for x in data}           # set comp
gen       = (x*x for x in range(10**9))     # generator: lazy, O(1) memory
```

`enumerate`, `zip`, `any`, `all`, `sum`, `min/max(key=...)`, `sorted(key=..., reverse=)` —
know them cold.

```python
# Sort spins by payout desc, then by spin id asc:
sorted(spins, key=lambda s: (-s.payout, s.id))
```

## 6. Args, kwargs, unpacking

```python
def f(a, b, *args, c=10, **kwargs): ...
#      \positional/ \variadic/ \kw-only/ \variadic kw/

reels = [r1, r2, r3]
spin(*reels)                # unpack positionally
config = {"rtp": 0.96}
build(**config)            # unpack as keywords
first, *rest = [1,2,3,4]   # first=1, rest=[2,3,4]
a, *_, last = data         # ignore middle
```

**Positional-only `/` and keyword-only `*`** (modern Python):
```python
def spin(bet, /, *, lines):   # bet must be positional, lines must be keyword
    ...
```

## 7. Strings & f-strings

```python
rtp = 0.9642
f"RTP is {rtp:.2%}"          # 'RTP is 96.42%'
f"{value:>10,.2f}"           # right-align, thousands sep, 2 decimals
f"{name=}"                   # 'name=...'  (debug, Python 3.8+)
```
Strings are immutable → build with `"".join(parts)`, never `s += ...` in a loop (O(n²)).

## 8. Dict mastery (the workhorse)

```python
d.get(key, default)             # no KeyError
d.setdefault(key, []).append(x) # init-and-append
from collections import defaultdict, Counter, deque
counts = Counter(symbols)        # {'cherry': 12, 'bar': 5, ...}
counts.most_common(3)
freq = defaultdict(int)
for s in stream: freq[s] += 1
merged = {**a, **b}              # b wins on conflict
d3 = d1 | d2                     # 3.9+ merge operator
```
Dicts preserve **insertion order** (guaranteed since 3.7).

## 9. Iteration protocol

An object is iterable if it implements `__iter__` returning an iterator; an iterator implements
`__next__` and raises `StopIteration` when exhausted.

```python
it = iter([1,2,3])
next(it)  # 1
# a for-loop is sugar for: call iter(), repeatedly call next() until StopIteration
```

## 10. Exceptions: EAFP over LBYL

Python prefers **"Easier to Ask Forgiveness than Permission"**:
```python
# EAFP (pythonic):
try:
    value = config["rtp"]
except KeyError:
    value = DEFAULT_RTP

# LBYL (less pythonic, race-prone):
if "rtp" in config:
    value = config["rtp"]
```
Know `try/except/else/finally`, exception chaining (`raise X from err`), custom exceptions:
```python
class InvalidBetError(ValueError):
    pass
```
Catch specific exceptions, never bare `except:`.

## 11. The walrus `:=` (assignment expression)

```python
while (spin := bot.next_spin()) is not None:
    process(spin)

if (n := len(results)) > 1_000_000:
    print(f"Large sample: {n}")
```

## 12. Type hints (modern, expected in 2024+ code)

```python
from typing import Optional, Iterable, Callable
def rtp(wins: list[float], bets: list[float]) -> float: ...
def find(xs: list[int], pred: Callable[[int], bool]) -> Optional[int]: ...
sym_map: dict[str, int] = {}
```
Hints are **not enforced at runtime** — they're for tooling (mypy, IDEs, readability).
Know `Optional[X] == X | None`, `Union`, `Any`, `Literal`, and `dataclass`/`Protocol` (file 03).

---

### Drill yourself
- Why does `[]` as a default argument bite you? When is it actually safe to use a mutable default?
- Difference between `is` and `==`? When is `is` correct?
- What does a generator give you over a list? (lazy, memory, infinite streams)
- Walk through what `for x in obj:` does under the hood.
