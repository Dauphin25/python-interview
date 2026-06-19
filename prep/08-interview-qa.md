# 08 — Tricky Interview Questions & Strong Answers

Practice saying these *out loud*. The model answer is in **A:**. The parenthetical is the trap or the
signal the interviewer is checking.

---

## Python language

**Q: Difference between a list and a tuple? When use which?**
A: List is mutable, tuple is immutable and hashable. Use a tuple for fixed records / dict keys / when
you want to signal "don't change this" (e.g. an immutable board); a list for collections that grow or
change. Tuples are slightly lighter/faster. *(Signal: do you know hashability matters for dict keys.)*

**Q: `is` vs `==`?**
A: `==` compares value, `is` compares identity (same object in memory). Use `is` only for `None`,
`True`, `False`. Relying on `is` for ints/strings is a bug because of interning. *(Classic trap.)*

**Q: What's wrong with `def f(x, items=[])`?**
A: The default list is created once at function-definition time and shared across all calls, so it
accumulates state between calls. Fix with `items=None` then `items = items or []` (or
`if items is None`). *(They almost always ask this.)*

**Q: Explain the GIL. Does Python have real multithreading?**
A: CPython's Global Interpreter Lock allows only one thread to run Python bytecode at a time, so
threads don't give CPU parallelism — only concurrency for I/O-bound work where the GIL is released
during blocking calls. For CPU-bound parallelism (like running independent spin simulations) you use
`multiprocessing` (separate processes/GILs) or vectorized NumPy/C. Python 3.13 has an experimental
free-threaded build, but the default still has the GIL. *(For this job, tie it to parallel simulation.)*

**Q: Generator vs list? Why care?**
A: A list materializes all elements in memory; a generator yields lazily, one at a time, O(1) memory,
and can be infinite. For a 100M-spin simulation you must stream results through a generator and
aggregate online — you can't hold them all. *(Perfect slot tie-in.)*

**Q: What is a decorator?**
A: A callable that takes a function and returns a wrapped function, used to add behavior (timing,
retry, caching, auth) without modifying the original. `@functools.wraps` preserves the wrapped
function's metadata. *(Be ready to write `timed` or `retry`.)*

**Q: `@staticmethod` vs `@classmethod`?**
A: `classmethod` gets `cls` and is typically an alternative constructor or operates on class state;
`staticmethod` gets neither `self` nor `cls` — it's just a function namespaced on the class.

**Q: Shallow vs deep copy?**
A: Shallow copies the outer container but shares nested objects; deep copy (`copy.deepcopy`)
recursively duplicates everything. Matters when you copy reel strips that contain inner lists.

**Q: How does Python manage memory?**
A: Reference counting frees objects at zero refs; a cyclic garbage collector handles reference
cycles. `__slots__`, generators, and the `array`/NumPy modules reduce footprint at scale.

**Q: What does `__slots__` do?**
A: Replaces the per-instance `__dict__` with a fixed set of attributes, saving memory and speeding
attribute access — valuable when you create millions of `Spin`/`SpinResult` objects. Cost: no dynamic
attributes.

**Q: EAFP vs LBYL?**
A: "Easier to Ask Forgiveness than Permission" (try/except) is the pythonic style vs "Look Before You
Leap" (pre-checks). EAFP avoids race conditions and is usually cleaner.

**Q: Mutable default of FP — what are pure functions and why care here?**
A: A pure function's output depends only on its inputs with no side effects. For a simulation that
matters because pure + seeded RNG = reproducible and parallelizable spins, which regulators and QA
require.

---

## Slot / probability / math

**Q: What is RTP?**
A: Return To Player — the long-run expected fraction of total wagers returned to players, i.e.
expected return per unit bet. 96% RTP means a 4% house edge over the long run. It's an expectation
(Law of Large Numbers), not a guarantee for any session.

**Q: Two slots both have 96% RTP. How can they feel completely different?**
A: Volatility/variance. Low-volatility games pay small wins often; high-volatility games pay rarely
but big. Same mean return, very different distribution of outcomes.

**Q: How would you compute a game's RTP?**
A: Two ways. Analytically: sum over every reel-stop combination of (probability × payout) / bet —
the math model / PAR sheet. Or empirically: Monte Carlo — simulate millions of spins and take mean
return / bet. The simulation estimates the analytic value; they should converge.

**Q: Why simulate 50 million spins instead of 50 thousand?**
A: The standard error of the RTP estimate shrinks like 1/√n, so to get ±0.1% precision — especially
on high-volatility games with big rare wins — you need a very large sample. 4× the spins halves the
error.

**Q: P(at least one scatter across 5 reels) if each reel shows a scatter with p=0.1?**
A: Use the complement: 1 − (0.9)^5 = 1 − 0.59049 = 0.40951, about 41%.

**Q: Three independent reels, "7" appears once on each 32-symbol reel. P(three 7s)?**
A: Independent, so (1/32)^3 = 1/32768 ≈ 0.00305%.

**Q: A designer needs to lower RTP but can't change the paytable. Options?**
A: Reweight the reel strips — make premium symbols rarer (more blanks/low symbols), or use weighted
symbols / virtual reels so high-paying symbols hit less often. RTP falls without touching payouts.
*(This is exactly what I did tuning the demo engine.)*

**Q: How do you verify a simulation bot is correct?**
A: Build a tiny config whose RTP I can compute by hand analytically, then confirm the simulation
converges to it within the confidence interval. Plus: seed determinism tests, property tests
(payout ≥ 0), and a chi-square test that stop frequencies match the strip weights.

**Q: Why seed the RNG in simulation but never in a real-money game?**
A: In simulation, a seed gives reproducibility — replay an exact spin sequence to debug or to satisfy
a regulator's repeatability requirement. In production you need unpredictability and fairness, so you
use a certified CSPRNG with no recoverable seed.

**Q: Expected value of: win 10 at p=0.05, win 2 at p=0.2, else 0, bet 1. RTP?**
A: EV = 10·0.05 + 2·0.2 = 0.5 + 0.4 = 0.9 return per 1 bet → RTP 90%, house edge 10%.

---

## Architecture / engineering

**Q: In a real-money slot, why can't the client decide the outcome?**
A: Money and cheating. The server must be authoritative: it runs the certified RNG and math, debits
and credits the wallet atomically, and logs the round for audit. The client only animates the result
the server already computed.

**Q: How do you prevent a double-debit if the client retries a spin on a flaky network?**
A: Idempotency — the client sends a unique round/idempotency key; the server records it and returns
the original result on a duplicate instead of charging again. Wallet changes happen in one atomic DB
transaction.

**Q: Why store money as integer cents, not floats?**
A: Binary floating point can't represent values like 0.10 exactly, so arithmetic accumulates rounding
errors — unacceptable for money. Use integer minor units (or `decimal.Decimal`).

**Q: How would you architect the simulation to use all CPU cores?**
A: It's CPU-bound and embarrassingly parallel, so `multiprocessing`: split N spins across processes,
each with its own seed and engine instance, return partial stats (count, sum, sum-of-squares), then
combine means/variances. Threads wouldn't help because of the GIL.

**Q: How do you keep the game engine reusable by both the live server and the bot?**
A: Keep the math engine a pure, framework-agnostic library with no web/DB dependencies. The web
layer and the simulation bot both import it; the engine knows nothing about either.

---

## "Senior judgment" / behavioral-technical

**Q: You changed a reel strip and RTP shifted by 0.5%. How do you catch that before it ships?**
A: A regression/snapshot test on the math model that fails when RTP moves beyond tolerance, run in
CI. The failure forces a human to confirm the change is intentional.

**Q: A simulation that used to take 2 hours now takes 8. How do you investigate?**
A: Profile first (`cProfile`/`timeit`) — don't guess. Look for an accidental O(n²) (string building
in a loop, list membership instead of set), object churn (add `__slots__`), or a regression in the
hot path. Then consider vectorizing with NumPy or parallelizing. Measure before and after.

**Q: How do you decide between threads, processes, and async?**
A: I/O-bound and many waits → async or threads. CPU-bound and parallel → processes. The slot
simulation is CPU-bound → processes; a web server handling many concurrent spin requests is I/O-bound
→ async.

---

### The "I don't know" move
If stumped: *"I haven't worked with that directly. My mental model is X; I'd verify by Y. How does
your team handle it?"* Honesty + reasoning + curiosity beats a confident wrong answer every time —
especially for a role built on careful math and debugging.
