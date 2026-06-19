# 10 — Behavioral, English (B1), and Questions to Ask

The JD requires **B1 English (spoken & written)** and offers corporate English classes — so they
expect *conversational*, not perfect. Clarity and confidence beat fancy vocabulary.

---

## 1. Your positioning (the narrative to repeat)

You are an **application support engineer at a casino** moving into **Python game development**. Spin
this as a strength, not a gap:

> "I work in application support at an online casino, so I understand the product from the operations
> side — players, bonuses, RTP, payments, and the bugs that actually hurt. I know Python, Django,
> SQL and some DevOps, and I want to move into building the game logic itself. This role is a perfect
> bridge: I already speak the iGaming domain, and I'm strong on the engineering fundamentals."

Why it works: most candidates have zero casino domain knowledge. You de-risk yourself.

## 2. STAR stories — prepare 3–4 (Situation, Task, Action, Result)

Have these ready in English. Keep each ~60–90 seconds.

- **A hard bug you debugged.** (Ideal: something with reproducibility / data / a tricky root cause.)
  Show method: reproduce → isolate → fix → verify → prevent regression.
- **A time you automated or improved something.** (DevOps/script/process — shows initiative + the
  "improve code efficiency" value.)
- **A time you learned a new tech fast.** (Shows you can ramp into slot math / their stack.)
- **A time you worked with a team / handled disagreement.** (JD stresses collaboration.)

Template to rehearse out loud:
> "**Situation:** … **Task:** my job was to … **Action:** I did X, then Y, and checked Z …
> **Result:** it reduced/fixed/improved … and I learned …"

## 3. "Tell me about yourself" (memorize a 60-second version)

1. Who you are now (support engineer at a casino, Python/Django/SQL).
2. What you've built / your strengths (debugging, domain knowledge, automation).
3. Why this role (move into game backend; you love the math + simulation side).
4. One sentence of enthusiasm for Kendoo / slots.

## 4. "Why do you want to work here / on slots?"

> "I find the math behind slots genuinely interesting — RTP, volatility, the simulation work to
> verify a game behaves as designed. From the support side I've seen how much the game math matters
> to players and to the business, and I want to be the one building and tuning it."

## 5. Questions YOU should ask (shows seniority + domain insight)

Pick 3–4. The domain-aware ones land hardest:

- "Do you compute RTP analytically with a math model, or primarily through Monte Carlo simulation —
  or both, cross-checking each other?"
- "How many spins do you typically run to certify a game's RTP, and how do you handle high-volatility
  games where convergence is slower?"
- "How is the simulation bot architected — is it parallelized across cores/machines?"
- "How do you keep the game math engine reusable between the live server and the simulation tooling?"
- "What does the certification/regulatory process look like, and how does it shape how you test?"
- "What does the Python stack look like day to day, and where does the team feel the most
  technical-debt or performance pain?"
- "What would success in the first 3–6 months look like for this role?"

## 6. English phrases that buy you thinking time (and sound natural)

- "That's a good question — let me think for a second."
- "Let me make sure I understand: you're asking …?" (clarify before answering)
- "There are a couple of ways to approach this. The main trade-off is …"
- "I'd start by … then …"
- "I'm not 100% sure, but my reasoning would be …"
- "To give a concrete example, …"
- "Could you say a bit more about what you mean by …?"

## 7. Talking about code in English (vocabulary)

- "This function **iterates over** the spins and **accumulates** the total."
- "We **inject** the random generator so the test is **deterministic / reproducible**."
- "The bottleneck was **CPU-bound**, so I moved it to **multiple processes**."
- "We store money as **integer cents** to avoid **floating-point rounding errors**."
- "RTP is the **long-run expected return**; volatility is the **spread of outcomes**."

## 8. Communication do's

- Short sentences. Pause. It's fine to be slow — B1 is conversational, not fluent.
- If you don't catch a question: "Sorry, could you repeat that?" — totally normal, not a red flag.
- Restate the question before answering complex ones; it shows you listen and buys time.
- Smile, show curiosity. They're hiring a teammate, not a dictionary.

## 9. Red flags to avoid

- Don't bluff math — work it out loud and sanity-check with expected value.
- Don't claim deep experience you don't have; bridge with reasoning.
- Don't badmouth your current employer; frame the move as growth toward building.
- Don't forget the domain — always be ready to connect an answer back to slots.

---

### Night-before checklist
- [ ] Re-read `08-interview-qa.md` aloud.
- [ ] Re-derive RTP for the file 04 §10 example by hand.
- [ ] Rebuild `slot_engine` core from memory in a blank file (machine + bot).
- [ ] Run `python -m slot_engine.simulate` and read the numbers.
- [ ] Rehearse "tell me about yourself" + 3 STAR stories in English.
- [ ] Prepare 3 questions to ask them.
- [ ] Sleep. Tired brains fail math.
