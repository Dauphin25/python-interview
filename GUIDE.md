# How To Use This Project (the right way)

This kit only works if you **use it actively**. Reading it like a novel will feel productive and teach
you almost nothing. This guide is the discipline that turns the files into a real skill. Read it once,
then follow it.

---

## The core principle: active recall, not passive reading

Your brain learns by **retrieving**, not by **re-reading**. The single rule that matters:

> **Never read an answer until you've tried to produce it yourself — out loud or on paper.**

Every prep file ends with a "Drill yourself" block and `practice.py` exists for exactly this. If you
only do one thing differently, do this: **cover the answer, attempt it, then check.**

Three modes, in order of value (do more of the higher ones):
1. **Produce from memory** (say it out loud / write code in a blank file) — highest value.
2. **Explain it to someone / to the rubber duck** — if you can teach it, you know it.
3. **Re-read** — lowest value; only to fill a gap you just discovered by failing 1 or 2.

---

## The loop for each prep file (repeat for 00 → 13)

1. **Read once, slowly**, to understand — not to memorize.
2. **Close the file.** Answer the "Drill yourself" questions from memory, out loud.
3. **Check** what you missed. Re-read only those parts.
4. **Drill it** with `python practice.py qa <category>` until you can answer without hesitating.
5. **Move on.** Come back tomorrow and re-attempt the same drills cold (spaced repetition).

A topic is "done" when you can explain it cold, **in English, out loud, in your own words** — because
that's the actual interview condition.

---

## The weekly plan (7 days, ~1–1.5h/day around your job)

| Day | Read | Drill | "Done" check |
|---|---|---|---|
| 1 | `01` Python core | `practice.py qa python` | Explain is-vs-==, mutable default, generators |
| 2 | `02` advanced, `03` OOP+FP | `qa python` | Explain GIL + why processes for sims; pure functions |
| 3 | `04` slot math | `practice.py math` | Define RTP/volatility; do EV by hand |
| 4 | `05` engine | rebuild engine from memory | Write `score_line` + bot from a blank file |
| 5 | `06` arch, `07` testing | `qa arch` | Why server-authoritative; how you'd test the bot |
| 6 | `08` Q&A, `09` exercises | `practice.py mock` | Survive a full mock without notes |
| 7 | `10`, `12`, `13`, `11` cheatsheet | `qa ai` + STAR out loud | "Tell me about yourself" + AI stance fluent |

If you have less than a week, do **Day 3, 4, 6** (slot math, engine, Q&A) — that's the differentiating
core for this specific job.

---

## How to use each part correctly

### The prep guides (`prep/00`–`13`)
- Read **in order** the first pass; after that, jump to weak spots.
- The ★ files (`04` slot math, `08` Q&A, `12` AI) are highest priority — over-invest there.
- Don't highlight. Highlighting feels like learning but isn't. **Write a one-line summary** of each
  section in your own words instead.

### `practice.py` (your daily driver)
- `qa` — flashcards. Be honest with `[g]ood`/`[a]gain`. If you hesitated at all, it's `again`.
- `math` — do this **every day**. Probability is a muscle; it atrophies fast. Aim to answer without
  a calculator where you can.
- `mock` — use it 2–3 times in the final days. **Answer out loud, fully, before revealing.** Record
  yourself once and listen — you'll hear where you ramble or freeze.

### The engine (`slot_engine/`) — the most important asset
This is your proof you can do the job. Treat it as a thing to **rebuild**, not just read.
- Day 4: read `machine.py` + `bot.py` line by line until nothing is mysterious.
- Then **delete your mental copy and rewrite the core from a blank file** in ~30 min: `ReelStrip`,
  `Paytable.score_line`, `SlotMachine.spin`, and a streaming `RunningStats` bot.
- Run it and **tune it**: change the reel strip / paytable and predict the RTP direction *before*
  running. When you can predict it, you understand slot math.
- Be ready to explain **every design choice** (injected RNG, frozen dataclass, generator, Welford).
  Interviewers probe "why did you do it this way?"

### The tests (`tests/test_engine.py`)
- Read the test that proves **the bot converges to the exact analytic RTP**. That's your single best
  talking point — be able to describe it in two sentences.
- Run `python tests/test_engine.py` and make sure you understand each assertion.

---

## What "ready" looks like (self-assessment — be honest)

Tick these only when true **without notes, out loud, in English**:

- [ ] I can explain `is` vs `==`, the mutable-default bug, generators, and the GIL.
- [ ] I can say why a CPU-bound simulation uses **processes**, not threads.
- [ ] I can define **RTP** and **volatility** and explain how two 96% games differ.
- [ ] I can compute an **EV / RTP** by hand and sanity-check a probability.
- [ ] I can explain how to **lower RTP without changing the paytable** (reweight strips).
- [ ] I can **write a slot engine + bot from scratch** in ~30 min and justify each choice.
- [ ] I can explain **why the server must be authoritative** and how idempotency prevents double-debit.
- [ ] I can describe how I'd **test the bot** (analytic check, seeds, property/statistical tests).
- [ ] I have my **AI stance** down in one fluent paragraph.
- [ ] I have **"tell me about yourself" + 3 STAR stories** rehearsed in English.
- [ ] I have **3 questions to ask them** ready.

When most boxes are ticked, you're interview-ready. Aim for "I can teach it," not "I recognize it."

---

## Habits that make this stick

- **Spaced repetition beats cramming.** 60 min/day for 7 days >> one 7-hour day.
- **Re-attempt yesterday's drills cold** before learning new material.
- **Speak English while you study** — narrate your reasoning out loud. The interview is spoken; train
  the spoken muscle, not just the reading one.
- **Track your misses.** Keep a tiny "fumbled it" list and re-drill only those. That list is your
  real study plan by Day 5.
- **Sleep before the interview.** Tired brains fail probability math first.

---

## Common traps (how people waste this kit)

- ❌ Reading all 14 files once and feeling "prepared." → ✅ Drill from memory; failing is the point.
- ❌ Studying silently in your head. → ✅ Out loud, in English.
- ❌ Memorizing answers word-for-word. → ✅ Understand the *why* so you can handle a reworded question.
- ❌ Skipping the math because it's uncomfortable. → ✅ That discomfort *is* the gap this job tests.
- ❌ Only reading the engine. → ✅ Rebuild it and tune it.
- ❌ Bluffing what you don't know. → ✅ Practice the honest move: "I haven't used that, but I'd reason…"

---

## The day before / day of

- **Day before:** light only. Skim `11-cheatsheet.md`, do one `practice.py mock`, rehearse your intro
  and questions. No new material. Sleep.
- **Day of:** read the cheat sheet once. Do 3 quick `practice.py math` problems to warm up the brain.
  Then close the laptop. You're ready.
- **In the interview:** think out loud, sanity-check math with EV, tie answers to slots when natural,
  and use your casino-domain edge. If stuck: state your mental model, say how you'd verify, ask them
  how their team does it.

> The goal isn't to memorize this kit. It's to become someone who **doesn't need it** — who can
> reason about Python, slot math, and simulations on the spot. Use it until you don't need it.
