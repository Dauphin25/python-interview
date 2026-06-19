# Kendoo Python Developer — Interview Prep

Self-contained study kit for a **Python Developer (slot games / iGaming)** interview.
**No internet, no pip installs, no setup** — only the Python standard library. Runs on any machine
with **Python 3.8+** (works fine on a locked-down work computer).

## Open this first

0. **Read `GUIDE.md`** — *how to use this kit the right way* (active recall, the weekly loop, what
   "ready" looks like). Do this before anything else — it's what makes the rest work.
1. Read `prep/00-README-roadmap.md` — the role decoded + study order.
2. Then work through `prep/01` → `prep/13` in order.
3. Practice with the interactive tool below.
4. Skim `prep/11-cheatsheet.md` the night before.

## Quick start (copy-paste)

```bash
# 1) Interactive flashcards (Q&A) — the most comfortable way to study at work
python practice.py qa            # all categories
python practice.py qa python     # just Python questions
python practice.py qa slotmath   # just slot-math questions
python practice.py qa ai         # how to talk about AI

# 2) Generated math drills (probability / RTP / EV) — type answers, get graded
python practice.py math

# 3) Mock interview — random mix, answer OUT LOUD, then reveal
python practice.py mock

# 4) See the real slot engine + simulation bot run
python -m slot_engine.simulate 1000000 42

# 5) Run the test suite (shows the bot matches the exact analytic RTP)
python tests/test_engine.py
```

If `python` isn't found on the work machine, try `py` (Windows launcher) or `python3`.

## What's inside

```
README.md                      <- you are here
practice.py                    <- interactive quiz / math drills / mock interview
prep/                          <- the study guides (read in order)
  00-README-roadmap.md         role decoded, strategy
  01-python-core.md            language fundamentals
  02-python-advanced.md        internals: GIL, generators, descriptors, perf
  03-oop-and-fp.md             OOP + functional programming
  04-slot-math.md            ★ probability, combinatorics, RTP, volatility
  05-slot-engine.md            walkthrough of the engine + bot
  06-client-server.md          architecture for a game backend
  07-testing-and-quality.md    pytest, property tests, statistical QA
  08-interview-qa.md         ★ tricky questions + model answers
  09-exercises.md              coding drills with solutions
  10-behavioral-and-english.md STAR stories, B1 English phrasing
  11-cheatsheet.md             one-page last-minute review
  12-ai-usage.md             ★ how to talk about AI in the interview
  13-advanced-slot-features.md bonus rounds, ways-to-win, Megaways, parallel sim
slot_engine/                   <- runnable mini slot engine (stdlib only)
  machine.py  bot.py  simulate.py  parallel.py
tests/                         <- test suite (proves the bot is correct)
  test_engine.py
```

## Suggested 1-week plan

- **Day 1–2:** `01`, `02`, `03` (Python). Drill `practice.py qa python`.
- **Day 3–4:** `04`, `05` (slot math + engine). Drill `practice.py math`. Rebuild `slot_engine` from memory.
- **Day 5:** `06`, `07` (architecture + testing). Run + read the tests.
- **Day 6:** `08`, `09` (Q&A + exercises). `practice.py mock`.
- **Day 7:** `10`, `12` (behavioral + AI), `11` cheatsheet. Rehearse out loud.

## How to move this to your work computer

Everything is plain text + stdlib Python. Just copy the whole `python-interview` folder
(USB / cloud drive / `git clone`) to the work machine and run the commands above. Nothing to install.

> Tip: `python practice.py mock` before bed, `python practice.py math` over coffee. Spaced repetition
> beats one long cram.
