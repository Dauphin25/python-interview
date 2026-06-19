# 07 — Testing & Quality (a literal JD responsibility)

The JD says: *"Integrate testing tools into the game module to enhance debugging and quality
assurance."* So testing isn't a side note here — it's part of the job. Show fluency.

---

## 1. The testing pyramid

- **Unit tests** (many, fast): one function/class in isolation — `Paytable.score_line`, RNG draws.
- **Integration tests** (some): components together — `SlotMachine.spin()` end-to-end.
- **Statistical/simulation tests** (special to this domain): run many spins, assert RTP/hit-rate are
  within tolerance of the math model.

## 2. pytest essentials (the standard)

```python
# test_paytable.py
import pytest
from slot_engine.machine import Paytable

def test_three_of_a_kind_pays():
    pt = Paytable({("BAR", 3): 15})
    assert pt.score_line(["BAR", "BAR", "BAR", "CHERRY", "BELL"]) == 15

def test_wild_substitutes():
    pt = Paytable({("BAR", 3): 15})
    assert pt.score_line(["BAR", "WILD", "BAR", "CHERRY", "BELL"]) == 15

@pytest.mark.parametrize("line,expected", [
    (["7","7","7","7","7"], 500),
    (["7","7","7","BAR","7"], 40),
    (["CHERRY","BELL","BAR","7","WILD"], 0),
])
def test_various_lines(line, expected):
    pt = Paytable({("7",3):40, ("7",5):500})
    assert pt.score_line(line) == expected
```

Know: `assert`, `pytest.raises`, `parametrize`, `fixture`, `pytest.approx` (for floats!), markers,
`conftest.py`, running with `pytest -v -k name`.

```python
def test_rtp_within_tolerance():
    result = run_small_sim(seed=1, n=200_000)
    assert result["rtp"] == pytest.approx(0.933, abs=0.01)   # never == on floats
```

## 3. Fixtures & dependency injection (why the engine design helps)

Because the machine takes an **injected RNG**, tests are deterministic:

```python
import random, pytest
from slot_engine.machine import SlotMachine, ReelStrip, Paytable

@pytest.fixture
def fixed_machine():
    rng = random.Random(123)            # seeded -> reproducible board
    reels = [ReelStrip(["7","BAR","CHERRY","WILD","SCATTER","BELL"]) for _ in range(5)]
    return SlotMachine(reels, Paytable({("7",3):50}), rng=rng)

def test_spin_is_deterministic(fixed_machine):
    r1 = fixed_machine.spin()
    rng2 = random.Random(123)
    # rebuild with same seed -> identical first board
```

This is the payoff of "inject the RNG": **reproducible tests**. Make this point in the interview.

## 4. Mocking

```python
from unittest.mock import patch, MagicMock

def test_handles_server_error():
    client = MagicMock()
    client.get.side_effect = TimeoutError
    with pytest.raises(TimeoutError):
        fetch_config(client)

@patch("module.random.randrange", return_value=0)   # force a known stop
def test_forced_outcome(mock_rng): ...
```
Mock at the boundary (network, time, randomness), not the logic under test.

## 5. Property-based testing (great for game math) — `hypothesis`

Instead of fixed cases, assert *invariants* over generated inputs:

```python
from hypothesis import given, strategies as st

@given(st.lists(st.sampled_from(SYMBOLS), min_size=5, max_size=5))
def test_score_is_never_negative(line):
    assert Paytable(TABLE).score_line(line) >= 0
```
Invariants that must always hold for a slot: payout ≥ 0; RTP ∈ [0,1] for a sane config; more spins ⇒
tighter CI; a frozen `SpinResult` can't be mutated.

## 6. Statistical/QA testing specific to slots

- **RTP convergence test:** with a fixed seed and N spins, RTP must fall within the math model ± ε.
- **Distribution test:** chi-square / KS test that symbol-stop frequencies match the strip weights
  (catches a broken RNG).
- **Regression test on the math model:** if someone changes a reel strip, a snapshot test flags the
  RTP change so it's intentional, not accidental.
- **Reproducibility test:** same seed ⇒ byte-identical result sequence (regulators require this).

## 7. Quality tooling (name-drop the modern stack)

- **Formatter/linter:** `ruff` (fast, now standard), `black`, `flake8`.
- **Type checking:** `mypy` / `pyright`.
- **Coverage:** `pytest-cov` (aim for meaningful coverage, not 100% vanity).
- **CI:** GitHub Actions/GitLab CI runs lint + types + tests on every push (your DevOps background).
- **Pre-commit hooks** to enforce all of the above before commit.

## 8. Debugging toolkit

- `pdb` / `breakpoint()`, `python -m pdb`, post-mortem.
- Logging over print: `logging` with levels; structured logs for production.
- For "why did this spin pay X" → **replay with the recorded seed** (only possible because the engine
  is seedable + pure). This directly answers "enhance debugging."

---

### Drill yourself
- Why use `pytest.approx` for the RTP assertion instead of `==`?
- How does injecting the RNG make tests deterministic?
- Give two invariants a property test would check on a slot. (payout≥0, RTP∈[0,1])
- How would you catch a subtly broken RNG? (distribution / chi-square test on stop frequencies)
- How do you debug a rare big-win bug in a game? (record seed -> replay deterministically)
