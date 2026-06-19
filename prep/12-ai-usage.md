# 12 — Talking About AI (how you use it, how it fits this role)

Interviewers increasingly ask about AI. For a **gambling math** role the wrong answer ("I let AI
write it") is disqualifying, and the right answer ("AI accelerates me, but I own and verify every
line, especially the math") signals maturity. Here's exactly how to handle it.

---

## 1. The one-sentence stance (memorize this)

> "I use AI as an **accelerator and a thinking partner, not a replacement for understanding** — I
> never ship code I can't read, test, and explain, and for anything math-critical like RTP I verify
> it against an analytic model and simulation, not the AI's word."

That single sentence answers 80% of AI questions. Everything below is supporting detail.

## 2. If they ask: "Do you use AI tools? Which ones / how?"

Be honest and concrete:

> "Yes — tools like ChatGPT / Claude / Copilot. I use them for:
> - **Scaffolding & boilerplate** — test skeletons, argument parsing, repetitive code.
> - **Explaining unfamiliar code or errors** — faster than digging blind.
> - **Rubber-ducking design** — I describe a problem and pressure-test my approach.
> - **Drafting tests and docs** — then I review and harden them.
>
> But I treat the output as a **draft to verify**, never as ground truth. I read every line, run it,
> and make sure I can explain it in review. If I can't explain it, it doesn't go in."

Why this lands: it shows productivity *and* ownership. Studios want speed without losing rigor.

## 3. If they ask: "How would you use AI in THIS role specifically?"

Tie it to the actual JD tasks:

- **Simulation & tooling:** scaffold the bot's reporting, generate test cases and property-based
  tests, draft the statistics/plotting code.
- **Reel/paytable exploration:** brainstorm tuning strategies to hit a target RTP/volatility — but
  the *decision* comes from the measured numbers, not the AI.
- **Debugging:** paste a failing test or a weird stack trace to get hypotheses faster.
- **Onboarding:** ask AI to explain an unfamiliar part of the codebase or a math concept I'm rusty on.
- **Docs & English:** since English is my second language, I use AI to polish written comms — which
  is exactly the kind of support this company already offers with corporate English classes.

Then the crucial caveat:

> "The one place I'm careful is the **game math and RNG**. AI can produce confident-but-wrong
> probability or subtly biased random code. So correctness there always comes from the **analytic
> RTP model plus Monte Carlo validation and statistical tests** — I'd never trust generated math
> blindly in a real-money product."

## 4. If they ask: "What are the risks of using AI? How do you manage them?"

Show you've thought about it like a senior:

| Risk | How I manage it |
|---|---|
| Confident wrong answers (hallucination), esp. math | Validate against analytic model + simulation + tests |
| Subtly biased / insecure RNG code | Use certified CSPRNG patterns; chi-square test the distribution |
| Leaking proprietary code/secrets to a third-party tool | Don't paste secrets or proprietary game math into public tools; follow company policy |
| Over-reliance / skill atrophy | Use it to learn faster, not to skip understanding; I still read the docs |
| Licensing / provenance of generated code | Keep it small, review it, don't paste large unknown blocks |
| Reproducibility & audit (regulated product) | Human-owned, tested, version-controlled code — AI assists, doesn't author the source of truth |

## 5. The mindset to convey (and a strong closing line)

> "AI makes me faster at the boring parts so I can spend more time on the hard parts — the math, the
> edge cases, the design. It raises the floor, but the responsibility for correctness is still mine.
> In a regulated, money-handling product, that ownership matters more, not less."

## 6. Red flags to avoid when answering

- ❌ "I let it write everything / I don't really check it." → sounds reckless.
- ❌ "I never use AI." → sounds rigid / out of touch (and probably untrue).
- ❌ Pasting proprietary/regulated math into public AI tools → mention you respect company policy.
- ✅ Honest + responsible + verification-first + domain-aware (the gambling/regulatory angle).

## 7. Bonus: turn it into a question for THEM

Shows you're already thinking like a teammate:

> "What's the team's stance on AI-assisted development — are there guidelines, especially around the
> game math and anything that touches certification?"

---

### 30-second script to rehearse out loud
"I use AI as an accelerator — scaffolding, tests, explaining code, polishing English — but I read,
test, and own everything; I never ship code I can't explain. For this role I'd use it on the
simulation tooling and debugging, but the game math and RNG correctness always comes from an analytic
model plus Monte Carlo validation, never from trusting generated code. In a regulated money product,
ownership of correctness matters more, not less."
