# Kendoo Python Developer — Interview Prep Roadmap

## The role, decoded

You're interviewing to build **backend logic for slot game modules** and a **simulation bot** that
plays the game millions of times to gather statistics (RTP, hit rate, volatility). This is a
*math-heavy, language-heavy* Python role — not a web/Django CRUD role.

What they will actually test:

| Area | Weight | Why |
|---|---|---|
| Modern Python language depth (OOP + FP) | High | Explicitly listed first |
| Probability & combinatorics (slot math) | High | Core of the daily work; "plus" but really central |
| Client-server architecture | Medium | Listed as required understanding |
| Simulation / Monte Carlo design | High | A literal responsibility |
| Testing & quality tooling | Medium | A literal responsibility |
| Performance / optimization | Medium | "Maintain and improve code efficiency" |
| Git | Low-Med | Listed as a plus |
| English B1 | Gate | You must be conversational |

## Your edge and your gaps

- **Edge:** you work *inside* a casino (application support). You understand the domain, players,
  bonuses, RTP regulation, "the house edge", operational reality. Lean on this hard — most Python
  candidates have zero gambling domain knowledge.
- **Gap to close:** (1) slot-specific math (reels/paylines/RTP/volatility), (2) Python internals
  (data model, GIL, generators, descriptors), (3) framing simulations cleanly.

## How to use this package (study order)

1. `01-python-core.md` — language fundamentals you MUST be fluent in.
2. `02-python-advanced.md` — internals & the tricky stuff interviewers love.
3. `03-oop-and-fp.md` — OOP + functional programming, since the JD names both.
4. `04-slot-math.md` — probability, combinatorics, RTP, volatility (the differentiator).
5. `05-slot-engine.md` — a real, runnable slot engine + Monte Carlo bot in Python.
6. `06-client-server.md` — architecture, protocols, where a game server fits.
7. `07-testing-and-quality.md` — pytest, property tests, simulating for QA.
8. `08-interview-qa.md` — tricky questions + strong answers.
9. `09-exercises.md` — coding drills with solutions.
10. `10-behavioral-and-english.md` — STAR stories, English B1 phrasing, questions to ask them.

## Interview-day strategy

- **Think out loud.** They want to see reasoning, not just the answer.
- When you don't know, say: *"I haven't used that directly, but here's how I'd reason about it…"*
  — far stronger than bluffing. They build games; they value honest debuggers.
- **Tie answers back to slots** whenever natural. "A generator is perfect here because a simulation
  of 10M spins shouldn't hold all results in memory."
- For math questions, **always sanity-check with expected value** and state your assumptions.
- Bring one question that shows domain insight (see file 10).
