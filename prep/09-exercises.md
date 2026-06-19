# 09 — Coding Exercises with Solutions

Do these on paper / in a blank editor first, THEN check. These mirror what a slot-studio interview
(live coding or take-home) tends to ask: probability, data wrangling, a small engine, clean Python.

---

## A. Warmups (language fluency)

**A1. Count symbol frequencies on a reel strip.**
```python
from collections import Counter
def freq(strip): return Counter(strip)
# freq(["7","BAR","7","CHERRY"]) -> Counter({'7':2,'BAR':1,'CHERRY':1})
```

**A2. Group spins by win/lose using one pass.**
```python
from collections import defaultdict
def group(spins):
    g = defaultdict(list)
    for s in spins:
        g["win" if s.total_win > 0 else "lose"].append(s)
    return g
```

**A3. Top-k payouts without sorting everything.**
```python
import heapq
def top_k(payouts, k): return heapq.nlargest(k, payouts)
```

**A4. Flatten a board (list of columns) to a flat list.**
```python
def flatten(board): return [s for col in board for s in col]
```

**A5. Fix the bug.**
```python
def running_totals(values, acc=[]):   # BUG: mutable default
    for v in values: acc.append(v)
    return acc
# FIX:
def running_totals(values, acc=None):
    acc = [] if acc is None else acc
    for v in values: acc.append(v)
    return acc
```

---

## B. Probability & combinatorics

**B1. Probability of three-of-a-kind on a single line.**
Given a reel strip and a symbol, P(symbol on one reel) = count/len. For 3 independent reels:
```python
def p_three(strip, symbol):
    p = strip.count(symbol) / len(strip)
    return p ** 3
```

**B2. P(at least one wild across n reels).**
```python
def p_at_least_one(strip, symbol, n):
    p_none = (1 - strip.count(symbol)/len(strip)) ** n
    return 1 - p_none
```

**B3. Exact EV / RTP of a single-line 3-reel game (analytic, no simulation).**
```python
from itertools import product
def exact_rtp(strip, paytable, bet=1):
    """paytable: dict {symbol: payout_for_three}. Brute force all combos."""
    total_value = 0
    n = len(strip)
    for a, b, c in product(strip, repeat=3):     # n^3 combinations, each equally likely
        if a == b == c:
            total_value += paytable.get(a, 0)
    return total_value / (n ** 3) / bet

strip = ["7","BAR","BAR","CHERRY","CHERRY","CHERRY"]
paytable = {"7":50, "BAR":10, "CHERRY":5}
print(exact_rtp(strip, paytable))   # 1.2268...  matches file 04 worked example!
```
*This is the gold answer: you can compute RTP exactly for small games and use it to validate the
Monte Carlo bot.*

**B4. Combinations: how many 5-symbol lines from a 32-position strip (with order, with repetition)?**
A: 32^5 = 33,554,432 (multiplication principle, order matters, repetition allowed — each reel
independent). `math.comb` is for unordered-without-repetition; here it's just 32**5.

**B5. Birthday-style: probability two of 5 reels stop on the same position (32 positions each)?**
```python
def p_collision(positions=32, reels=5):
    p_all_distinct = 1.0
    for i in range(reels):
        p_all_distinct *= (positions - i) / positions
    return 1 - p_all_distinct
```

---

## C. Build-a-thing (mini engine pieces)

**C1. Weighted random symbol draw (virtual reels).**
```python
import random
def weighted_draw(symbols, weights, rng=random):
    return rng.choices(symbols, weights=weights, k=1)[0]
```

**C2. Score a payline with wilds (left-to-right matching).**
```python
def score(line, paytable, wild="WILD"):
    first = next((s for s in line if s != wild), wild)
    count = 0
    for s in line:
        if s == first or s == wild: count += 1
        else: break
    return paytable.get((first, count), 0)
```

**C3. Monte Carlo RTP estimate (streaming, O(1) memory).**
```python
def estimate_rtp(spin_fn, n, bet=1, seed=None):
    import random
    rng = random.Random(seed)
    total = 0.0
    for _ in range(n):
        total += spin_fn(rng)
    return total / n / bet
```

**C4. Online mean & variance (Welford) — prove you can avoid storing all data.**
```python
def welford(stream):
    n = mean = m2 = 0
    for x in stream:
        n += 1
        d = x - mean
        mean += d / n
        m2 += d * (x - mean)
    variance = m2 / n if n else 0
    return mean, variance
```

**C5. Parallelize the simulation across cores and combine results.**
```python
from multiprocessing import Pool
def run_chunk(args):
    seed, n = args
    return estimate_rtp(my_spin, n, seed=seed) , n
def parallel_rtp(total_spins, workers=4):
    per = total_spins // workers
    with Pool(workers) as pool:
        parts = pool.map(run_chunk, [(s, per) for s in range(workers)])
    # weighted mean of per-chunk RTPs
    return sum(rtp*n for rtp, n in parts) / sum(n for _, n in parts)
```

---

## D. Classic algorithmic warmups (in case they test general coding)

**D1. Two-sum (hash map, O(n)).**
```python
def two_sum(nums, target):
    seen = {}
    for i, x in enumerate(nums):
        if target - x in seen: return (seen[target - x], i)
        seen[x] = i
```

**D2. Is anagram / Counter equality.** `Counter(a) == Counter(b)`

**D3. FizzBuzz, but clean.**
```python
def fizzbuzz(n):
    for i in range(1, n+1):
        out = ("Fizz" if i%3==0 else "") + ("Buzz" if i%5==0 else "")
        print(out or i)
```

**D4. Reverse a linked list / dedupe preserving order.**
```python
def dedupe(seq):
    seen = set(); out = []
    for x in seq:
        if x not in seen: seen.add(x); out.append(x)
    return out
```

**D5. Fibonacci with memoization (shows decorators/closures).**
```python
import functools
@functools.cache
def fib(n): return n if n < 2 else fib(n-1) + fib(n-2)
```

---

## E. Take-home-style prompt (practice end-to-end)

> "Build a 3-reel slot with a configurable paytable. Write a bot that runs 1,000,000 spins and
> reports RTP, hit frequency, and volatility. Make the RTP reproducible with a seed."

You already have the answer pattern in `slot_engine/`. Be able to (1) write it from scratch in ~30
min, (2) explain every design choice, (3) validate it against an analytic RTP (B3), (4) discuss how
you'd parallelize and test it.
