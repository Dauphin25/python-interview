#!/usr/bin/env python3
"""Interactive interview practice tool. Standard library only - runs anywhere.

Usage:
    python practice.py            # menu
    python practice.py qa         # flashcard Q&A (all categories)
    python practice.py qa python  # only python questions
    python practice.py math       # generated probability/RTP drills
    python practice.py mock       # timed mock-interview (random mix)
    python practice.py list       # list categories & counts

No internet, no pip installs. Press Enter to reveal answers; rate yourself.
"""
import random        # to shuffle cards and generate random math drills
import sys            # to read command-line arguments (which mode to run)
import textwrap       # to wrap long answer text neatly in the terminal

# ---------------------------------------------------------------------------
# FLASHCARDS  (category, question, answer)
# Each card is a 3-tuple. Add your own here - the tools below pick them up
# automatically. Categories group the cards so you can drill one topic.
# ---------------------------------------------------------------------------
CARDS = [
    # ---- python ----
    ("python", "Difference between `is` and `==`? When is `is` correct?",
     "`==` compares value; `is` compares identity (same object). Use `is` only for "
     "None/True/False. Relying on `is` for ints/strings is a bug (interning)."),
    ("python", "What's wrong with `def f(x, items=[])`?",
     "The default list is created once at def-time and shared across calls, so it "
     "accumulates state. Fix: items=None, then items = [] if items is None else items."),
    ("python", "Explain the GIL. Does Python have real multithreading?",
     "CPython's Global Interpreter Lock lets only one thread run bytecode at a time. "
     "Threads help I/O-bound work (GIL released on blocking I/O) but NOT CPU parallelism. "
     "For CPU-bound work like simulations use multiprocessing or NumPy/C."),
    ("python", "Generator vs list - why does it matter for a 100M-spin simulation?",
     "A list holds everything in memory; a generator yields lazily, O(1) memory, can be "
     "infinite. You can't store 100M results, so you stream and aggregate online."),
    ("python", "What is a decorator? What does functools.wraps do?",
     "A callable that takes a function and returns a wrapped one, adding behavior "
     "(timing/retry/cache/auth) without changing the original. wraps preserves the "
     "wrapped function's __name__/__doc__."),
    ("python", "classmethod vs staticmethod?",
     "classmethod receives cls (alt constructor / class state, subclass-friendly). "
     "staticmethod receives neither self nor cls - just a function namespaced on the class."),
    ("python", "Shallow vs deep copy?",
     "Shallow copies the outer container but shares nested objects; deepcopy duplicates "
     "recursively. Matters when copying reel strips that contain inner lists."),
    ("python", "How does Python manage memory / garbage collection?",
     "Reference counting frees objects at zero refs; a cyclic GC collects reference "
     "cycles. __slots__, generators and array/NumPy cut footprint at scale."),
    ("python", "What does __slots__ do and what's the cost?",
     "Replaces per-instance __dict__ with a fixed attribute set - saves memory and speeds "
     "attribute access when you create millions of objects. Cost: no dynamic attributes."),
    ("python", "EAFP vs LBYL?",
     "Easier to Ask Forgiveness than Permission (try/except) is pythonic and avoids race "
     "conditions, vs Look Before You Leap (pre-checks)."),
    ("python", "What is a pure function and why does it help a simulation?",
     "Output depends only on inputs, no side effects. With a seeded RNG it makes spins "
     "reproducible and parallelizable - exactly what QA and regulators need."),
    ("python", "List vs tuple - when use which?",
     "List is mutable; tuple is immutable+hashable. Tuple for fixed records / dict keys / "
     "'don't change this' (e.g. a board); list for collections that change."),
    ("python", "Late-binding closure trap: what does [lambda: i for i in range(3)] return when called?",
     "[2,2,2] - i is looked up at call time, not capture time. Fix: lambda i=i: i."),

    # ---- slotmath ----
    ("slotmath", "What is RTP?",
     "Return To Player: long-run expected fraction of wagers returned = expected return "
     "per unit bet. 96% RTP => 4% house edge. It's an expectation (LLN), not a per-session "
     "guarantee."),
    ("slotmath", "Two slots both 96% RTP - how can they feel totally different?",
     "Volatility/variance. Low-vol pays small wins often; high-vol pays rarely but big. "
     "Same mean, different distribution."),
    ("slotmath", "Two ways to compute a game's RTP?",
     "Analytically: sum over all reel-stop combos of probability x payout / bet (the math "
     "model/PAR sheet). Empirically: Monte Carlo - simulate millions of spins, take mean "
     "return / bet. They should converge."),
    ("slotmath", "Why simulate 50M spins instead of 50k?",
     "Standard error of the RTP estimate shrinks like 1/sqrt(n). 4x spins halves the error. "
     "High-volatility games need huge samples to converge."),
    ("slotmath", "Designer must LOWER RTP but can't change the paytable. Options?",
     "Reweight reel strips - make premium symbols rarer (more blanks), or use weighted "
     "symbols / virtual reels. RTP falls without touching payouts."),
    ("slotmath", "How do you verify a simulation bot is correct?",
     "Build a tiny config whose RTP you can compute by hand analytically, confirm the sim "
     "converges within the CI. Plus seed-determinism tests, property tests (payout>=0), and "
     "a chi-square test that stop frequencies match strip weights."),
    ("slotmath", "Why seed the RNG in simulation but never in production?",
     "Sim: a seed gives reproducibility - replay an exact spin to debug or satisfy regulator "
     "repeatability. Production: needs unpredictability/fairness -> certified CSPRNG, no "
     "recoverable seed."),
    ("slotmath", "EV of: win 10 @ p=0.05, win 2 @ p=0.2, else 0, bet 1. RTP?",
     "EV = 10*0.05 + 2*0.2 = 0.9 per 1 bet => RTP 90%, house edge 10%."),
    ("slotmath", "P(at least one scatter across 5 reels) if each reel p=0.1?",
     "Complement: 1 - 0.9^5 = 1 - 0.59049 = 0.40951 (~41%)."),
    ("slotmath", "Three reels, '7' once on each 32-symbol reel. P(three 7s)?",
     "Independent: (1/32)^3 = 1/32768 ~ 0.00305%."),
    ("slotmath", "Pseudo-random vs cryptographic RNG - which where?",
     "PRNG (Mersenne Twister, `random`) is fast + seedable -> simulations. CSPRNG "
     "(`secrets`/os.urandom) or certified hardware -> real-money fairness/security."),

    # ---- architecture ----
    ("arch", "In a real-money slot, why can't the client decide the outcome?",
     "Money + cheating. The server is authoritative: runs certified RNG and math, debits/"
     "credits the wallet atomically, logs the round for audit. The client only animates the "
     "server's result."),
    ("arch", "How do you prevent a double-debit if the client retries a spin?",
     "Idempotency: client sends a unique round/idempotency key; server records it and returns "
     "the original result on duplicates. Wallet change is one atomic DB transaction."),
    ("arch", "Why store money as integer cents, not floats?",
     "Binary float can't represent values like 0.10 exactly -> rounding errors accumulate, "
     "unacceptable for money. Use integer minor units or Decimal."),
    ("arch", "How would you use all CPU cores for the simulation?",
     "It's CPU-bound and embarrassingly parallel: multiprocessing. Split N spins across "
     "processes, each with its own seed+engine, return partial stats (count,sum,sum_sq), "
     "then combine. Threads wouldn't help (GIL)."),
    ("arch", "How keep the game engine reusable by both server and bot?",
     "Keep the math engine a pure, framework-agnostic library with no web/DB deps. Both the "
     "web layer and the bot import it; the engine knows nothing about either."),
    ("arch", "What makes a server 'stateless' and why does it help scaling?",
     "No per-client memory between requests; state lives in DB/Redis. Any instance can handle "
     "any request behind a load balancer -> horizontal scaling."),

    # ---- ai (talking about your AI usage) ----
    ("ai", "Do you use AI tools? How?",
     "Yes, as an assistant - not a replacement for understanding. I use it to scaffold "
     "boilerplate, explain unfamiliar code, draft tests, and rubber-duck design. I always "
     "read, test, and own the output; I never ship code I can't explain. For slot math I'd "
     "verify any AI output against an analytic model and simulation."),
    ("ai", "How could AI help in THIS slot-dev role?",
     "Generating test cases and property tests, scaffolding simulation/reporting code, "
     "exploring reel/paytable tuning ideas, writing docs, and speeding up debugging. The math "
     "correctness still comes from the analytic model + Monte Carlo validation, never blind "
     "trust in generated code."),
    ("ai", "What's the risk of using AI for game math, and how do you manage it?",
     "It can produce confident-but-wrong math or subtly biased RNG code. I manage it by "
     "validating against an exact analytic RTP on small configs, seed-reproducibility tests, "
     "and statistical tests - treat AI output as a draft to verify, never as ground truth."),
]


def _wrap(text, width=78, indent="    "):
    """Indent and word-wrap text so long answers read nicely in a terminal.

    We split on existing newlines first, then wrap each paragraph, then re-join
    so intentional line breaks in the answer are preserved.
    """
    return "\n".join(textwrap.fill(p, width=width, initial_indent=indent,
                                   subsequent_indent=indent)
                     for p in text.split("\n"))


def run_flashcards(category=None):
    """Active-recall flashcards: show a question, wait, reveal, self-grade."""
    # Keep only cards in the chosen category. `category in (None, c[0])` means:
    # if no category was given (None) keep everything, else keep matches.
    cards = [c for c in CARDS if category in (None, c[0])]
    if not cards:
        print(f"No cards for category '{category}'. Try: python practice.py list")
        return
    random.shuffle(cards)                       # randomize order so you don't memorize sequence
    score = {"good": 0, "again": 0}             # tally of how you rated yourself
    print(f"\n=== Flashcards: {category or 'ALL'} ({len(cards)} cards) ===")
    print("Press Enter to reveal the answer. After each: [g]ood / [a]gain / [q]uit\n")
    # enumerate(..., 1) numbers the cards starting at 1; each card unpacks to (category, question, answer).
    for i, (cat, q, a) in enumerate(cards, 1):
        print(f"[{i}/{len(cards)}] ({cat})")
        print(_wrap("Q: " + q))
        try:
            input("  ... press Enter for answer ...")   # pause so you answer from memory first
        except (EOFError, KeyboardInterrupt):
            break                                # Ctrl+C / piped-EOF cleanly ends the session
        print(_wrap(a))                          # now reveal the model answer
        try:
            # .strip() removes stray spaces, .lower() makes input case-insensitive.
            choice = input("\n  [g]ood / [a]gain / [q]uit > ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            break
        if choice == "q":
            break
        elif choice == "a":                      # "again" = you want to review this one
            score["again"] += 1
        else:                                    # anything else counts as "good/confident"
            score["good"] += 1
        print("-" * 60)
    print(f"\nDone. Confident: {score['good']}  |  Review again: {score['again']}")


def run_math_drills(rounds=8):
    """Generated probability / EV / RTP problems with checked answers.

    Each round picks a random drill-generator, which returns
    (question_text, numeric_answer, explanation). We then check what you typed.
    """
    print("\n=== Math drills (probability / RTP / EV) ===")
    print("Type your numeric answer; 's' to skip, 'q' to quit. Tolerance is generous.\n")
    correct = 0          # how many you got right
    total = 0            # how many you actually attempted
    # The pool of question makers (functions are first-class objects, so we store them in a list).
    generators = [_drill_three_of_a_kind, _drill_at_least_one, _drill_rtp_from_ev,
                  _drill_house_edge, _drill_combos]
    for r in range(rounds):
        gen = random.choice(generators)         # pick a random drill type
        question, answer, explain = gen()       # generate a fresh problem + its answer
        print(f"[{r+1}/{rounds}] {question}")
        try:
            raw = input("  your answer > ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            break
        if raw == "q":
            break
        total += 1
        if raw == "s":                          # skip: just show the answer, don't score it
            print(f"  -> answer: {answer:.6g}\n     {explain}\n")
            continue
        try:
            # Accept "0.41" or "41%": strip a trailing % and divide by 100 if present.
            val = float(raw.rstrip("%"))
            if "%" in raw:
                val /= 100.0
        except ValueError:                      # input wasn't a number at all
            print(f"  couldn't parse. answer was {answer:.6g}\n     {explain}\n")
            continue
        # Correct if within a tiny absolute tolerance OR 2% relative (rounding-friendly).
        ok = abs(val - answer) <= max(1e-4, abs(answer) * 0.02)
        # Also accept a percentage typed without the % sign (e.g. 41 for 0.41).
        if not ok and abs(val/100 - answer) <= max(1e-4, abs(answer)*0.02):
            ok = True
        print(("  CORRECT" if ok else f"  not quite -> {answer:.6g}") + f"\n     {explain}\n")
        correct += ok                           # bool adds as 0 or 1
    if total:
        print(f"Score: {correct}/{total}")


# --- drill generators: each returns (question, numeric_answer, explanation) ---

def _drill_three_of_a_kind():
    """P(three of a kind) = p^3 for independent reels. p = count / strip length."""
    strip_len = random.choice([20, 24, 30, 32])
    count = random.choice([1, 2, 3])
    p = count / strip_len                       # probability of the symbol on one reel
    ans = p ** 3                                # three independent reels -> multiply
    return (f"A symbol appears {count} time(s) on each of 3 independent {strip_len}-position "
            f"reels. P(three of them on one line)?",
            ans, f"({count}/{strip_len})^3 = {ans:.6g}")


def _drill_at_least_one():
    """'At least one' is easiest via the complement: 1 - P(none)."""
    reels = random.choice([3, 4, 5])
    p = random.choice([0.05, 0.08, 0.1, 0.2])
    ans = 1 - (1 - p) ** reels                  # 1 - (probability it appears on no reel)
    return (f"Each of {reels} reels shows a scatter with probability {p}. "
            f"P(at least one scatter)?",
            ans, f"1 - (1-{p})^{reels} = {ans:.6g}")


def _drill_rtp_from_ev():
    """RTP = expected value of the return per unit bet = sum(payout * probability)."""
    pay1, p1 = random.choice([(10, 0.05), (5, 0.1), (20, 0.03)])
    pay2, p2 = random.choice([(2, 0.2), (3, 0.15), (1, 0.3)])
    ev = pay1 * p1 + pay2 * p2
    return (f"Bet 1. Win {pay1} with p={p1}, win {pay2} with p={p2}, else 0. RTP?",
            ev, f"EV = {pay1}*{p1} + {pay2}*{p2} = {ev:.4g} per unit bet -> RTP {ev:.4g}")


def _drill_house_edge():
    """House edge is simply 1 - RTP."""
    rtp = random.choice([0.92, 0.94, 0.955, 0.965, 0.97])
    ans = 1 - rtp
    return (f"A game has RTP = {rtp:.3g}. What is the house edge?",
            ans, f"1 - {rtp} = {ans:.4g}")


def _drill_combos():
    """Total combinations = stops ^ reels (multiplication principle, independent reels)."""
    reels = random.choice([3, 4, 5])
    stops = random.choice([20, 24, 32])
    ans = stops ** reels
    return (f"{reels} reels, each with {stops} stop positions. How many total stop "
            f"combinations? (order matters, independent reels)",
            ans, f"{stops}^{reels} = {ans} (multiplication principle)")


def run_mock(n=10):
    """Timed-feel mock: random mix of flashcards, you self-grade out loud."""
    print("\n=== MOCK INTERVIEW (say answers OUT LOUD, then reveal) ===")
    print("Simulate the real thing: speak your full answer before pressing Enter.\n")
    # random.sample picks n DISTINCT cards (no repeats), capped at how many we have.
    cards = random.sample(CARDS, min(n, len(CARDS)))
    for i, (cat, q, a) in enumerate(cards, 1):
        print(f"Question {i}/{len(cards)}  ({cat})")
        print(f"  {q}")
        try:
            input("  (answer out loud, then Enter for model answer) ")
        except (EOFError, KeyboardInterrupt):
            break
        print(_wrap(a))
        print("=" * 60)
    print("\nMock complete. Note which ones you fumbled and re-drill those categories.")


def list_categories():
    """Print each category and how many cards it has."""
    from collections import Counter            # Counter tallies occurrences for us
    counts = Counter(c[0] for c in CARDS)       # count cards by their category (c[0])
    print("\nCategories (use: python practice.py qa <category>):")
    for cat, n in sorted(counts.items()):
        print(f"  {cat:12} {n} cards")          # :12 pads the name to 12 chars for alignment
    print(f"  {'TOTAL':12} {len(CARDS)} cards\n")


def menu():
    """Default screen: show usage (the module docstring) + categories."""
    print(__doc__)                              # __doc__ is the triple-quoted string at the top of the file
    list_categories()
    print("Quick start:  python practice.py qa   |   python practice.py math   |   "
          "python practice.py mock")


def main():
    """Entry point: read the first CLI arg and dispatch to the right mode."""
    args = sys.argv[1:]                         # everything after the script name
    if not args:
        menu(); return                          # no args -> show the menu and stop
    cmd = args[0]
    if cmd == "qa":
        # Optional second arg is the category to filter by (or None for all).
        run_flashcards(args[1] if len(args) > 1 else None)
    elif cmd == "math":
        run_math_drills()
    elif cmd == "mock":
        run_mock()
    elif cmd == "list":
        list_categories()
    else:
        menu()                                  # unknown command -> fall back to the menu


# This guard means main() runs only when the file is executed directly
# (python practice.py), NOT when it's imported by another module.
if __name__ == "__main__":
    main()
