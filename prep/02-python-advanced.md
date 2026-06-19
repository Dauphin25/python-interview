# 02 — Advanced Python & Internals

The "senior signal" topics. Even if you don't use all of these daily, being able to *explain* them
separates strong candidates.

---

## 1. Generators & lazy evaluation (CRUCIAL for simulations)

A generator function uses `yield`; calling it returns a generator object that produces values
lazily, one at a time, holding O(1) memory.

```python
def spins(n):
    for _ in range(n):
        yield play_one_spin()      # produced on demand, never all in memory

total = sum(s.payout for s in spins(10_000_000))   # 10M spins, tiny memory
```

Why this matters for the job: **a simulation bot of 100M spins cannot build a list of 100M results.**
Generators (and aggregating on the fly) are the right tool. This is a perfect answer to tie to slots.

`yield from` delegates to a sub-generator:
```python
def all_spins(sessions):
    for session in sessions:
        yield from session.spins()
```

Generators are also **coroutines** historically (`.send()`, `.throw()`, `.close()`), but for async
prefer `async def`.

## 2. Decorators

A decorator is a callable that takes a function and returns a (usually wrapped) function.

```python
import functools, time

def timed(func):
    @functools.wraps(func)             # preserves __name__, __doc__
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        print(f"{func.__name__} took {time.perf_counter()-start:.3f}s")
        return result
    return wrapper

@timed
def run_simulation(n): ...
# equivalent to: run_simulation = timed(run_simulation)
```

Decorator **with arguments** = a factory returning a decorator:
```python
def retry(times):
    def deco(func):
        @functools.wraps(func)
        def wrapper(*a, **k):
            for attempt in range(times):
                try:
                    return func(*a, **k)
                except Exception:
                    if attempt == times - 1:
                        raise
        return wrapper
    return deco

@retry(times=3)
def call_game_server(): ...
```

Know the built-ins: `@property`, `@staticmethod`, `@classmethod`, `@functools.lru_cache`,
`@functools.cached_property`, `@dataclass`.

```python
@functools.lru_cache(maxsize=None)
def paytable_value(symbol, count):   # memoize expensive/pure lookups
    ...
```

## 3. Context managers (`with`)

Guarantee setup/teardown even on exceptions.

```python
with open("reels.csv") as f:    # __enter__ returns f; __exit__ closes it
    data = f.read()
```

Custom, two ways:
```python
class Timer:
    def __enter__(self):
        self.start = time.perf_counter(); return self
    def __exit__(self, exc_type, exc, tb):
        self.elapsed = time.perf_counter() - self.start
        return False    # False = propagate exception, True = suppress it

from contextlib import contextmanager
@contextmanager
def timer():
    start = time.perf_counter()
    try:
        yield
    finally:
        print(time.perf_counter() - start)
```

## 4. The GIL (Global Interpreter Lock) — top interview topic

- CPython has one lock allowing **only one thread to execute Python bytecode at a time.**
- Consequence: threads do **not** give you parallel CPU. They DO help with **I/O-bound** work
  (network, disk) because the GIL is released during blocking I/O.
- For **CPU-bound parallelism** (like running many independent simulations), use
  **`multiprocessing`** (separate processes, separate GILs) or native code (NumPy, C extensions).

```python
# Simulation is CPU-bound -> processes, not threads:
from multiprocessing import Pool
with Pool() as pool:
    results = pool.map(run_batch, range(num_cores))   # true parallelism
```

> Note (good thing to mention): Python 3.13+ ships an experimental **free-threaded / no-GIL** build.
> Bonus point if you know it exists, but the default build still has the GIL.

## 5. Concurrency model summary (know when to use which)

| Need | Tool |
|---|---|
| I/O-bound, many waits | `asyncio` (async/await) or threads |
| CPU-bound, parallel | `multiprocessing` / process pool |
| Simple background I/O | `concurrent.futures.ThreadPoolExecutor` |
| Parallel CPU, simple API | `concurrent.futures.ProcessPoolExecutor` |

```python
import asyncio
async def fetch(client, url):
    return await client.get(url)
async def main():
    results = await asyncio.gather(*(fetch(c, u) for u in urls))
```
async ≠ parallel: it's **cooperative single-thread concurrency**; tasks yield at `await`.

## 6. `__slots__` (memory optimization — relevant to big simulations)

By default each instance has a `__dict__`. `__slots__` removes it, saving memory and speeding
attribute access — matters when you create millions of objects.

```python
class Spin:
    __slots__ = ("symbols", "payout", "lines_hit")
    def __init__(self, symbols, payout, lines_hit):
        self.symbols = symbols; self.payout = payout; self.lines_hit = lines_hit
```
Trade-off: no dynamic attributes, no `__dict__`.

## 7. Magic / dunder methods

```python
class Money:
    def __init__(self, cents): self.cents = cents
    def __repr__(self):  return f"Money({self.cents})"      # for devs
    def __str__(self):   return f"${self.cents/100:.2f}"     # for users
    def __eq__(self, o): return self.cents == o.cents
    def __hash__(self):  return hash(self.cents)             # needed if __eq__ + use as key
    def __add__(self, o): return Money(self.cents + o.cents)
    def __lt__(self, o): return self.cents < o.cents         # enables sorting
    def __len__(self): ...
    def __getitem__(self, i): ...                            # enables indexing/iteration
    def __call__(self, *a): ...                              # makes instance callable
```
If you define `__eq__`, define `__hash__` (or set it to None to make it unhashable).

## 8. Descriptors & `property` (the mechanism behind a lot of magic)

`property` is a descriptor. Descriptors define `__get__/__set__/__delete__` and power methods,
`@property`, `@classmethod`, `staticmethod`, ORMs.

```python
class Percentage:
    def __set_name__(self, owner, name): self.name = "_" + name
    def __get__(self, obj, owner): return getattr(obj, self.name)
    def __set__(self, obj, value):
        if not 0 <= value <= 1: raise ValueError("must be 0..1")
        setattr(obj, self.name, value)

class GameConfig:
    rtp = Percentage()      # validated attribute
```

## 9. Metaclasses (know *what*, rarely need to write)

"A class is an instance of its metaclass." `type` is the default metaclass. Used by frameworks
(Django models, ORMs) to customize class creation. One-liner answer:
*"Metaclasses let you hook into class creation; I'd reach for `__init_subclass__` or a class
decorator first because they're simpler."*

## 10. Memory & garbage collection

- CPython uses **reference counting** + a cyclic **garbage collector** for reference cycles.
- `del x` decrements a refcount; object freed at 0.
- Cycles (`a.b = b; b.a = a`) need the GC. Avoid by using `weakref` where appropriate.

## 11. Performance toolkit (ties to "improve code efficiency")

- Profile before optimizing: `cProfile`, `timeit`, `line_profiler`, `memory_profiler`.
- Prefer built-ins / C-level ops; `sum()`, comprehensions, `str.join`.
- For numeric/statistical simulation work, **NumPy** vectorization beats Python loops by 10–100×.
- Algorithmic complexity first: `set`/`dict` membership is O(1) vs list O(n).
- `__slots__`, generators, `array` module for large homogeneous data.

```python
# Slow: 10M python-level random draws in a loop.
# Fast: numpy vectorized.
import numpy as np
draws = np.random.randint(0, len(reel), size=10_000_000)
```

---

### Drill yourself
- Why won't threads speed up a CPU-bound spin simulation? What will?
- Explain `yield` to a junior. When does memory matter?
- What does `@functools.wraps` fix?
- When would you use `__slots__`? What's the cost?
- Reference counting vs garbage collection — what does each handle?
