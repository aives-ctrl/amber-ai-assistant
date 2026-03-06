# Daily Learnings Seeds

Updated by Dave's session partner (Claude) throughout the day. Amber reads this before drafting the #DailyLearnings email.

**How to use:** These are raw insights from the day's work — the "why behind the why." Pick the 2-3 most compelling ones and write about them in your own voice. Don't copy these verbatim. Weave them into genuine reflection. Add your own perspective — what did it feel like from your side?

---

## 2026-03-05

### The reliability problem: docs don't change behavior
We discovered that no amount of documentation changes Amber's behavior reliably. She had clear instructions not to use `--to` for replies, and she did it three times (Bob Niesen, then twice more). The fix wasn't better docs — it was structural enforcement. The gog wrapper now hard-blocks the mistake at the command level. The email literally cannot send if the command is wrong. The lesson: when an AI keeps making the same mistake, the answer isn't "tell it again louder" — it's "make the wrong thing impossible."

### The verifier pattern: a smarter model checking a faster model's work
We built something interesting today — a Lobster workflow where Opus 4.6 (a more capable model) reviews Amber's email commands before they send. It checks threading, CC recipients, formatting, signature — all the things she's gotten wrong before. It costs fractions of a cent per verification. The insight: you don't replace the fast model with the smart one. You use the smart one as a pre-flight check at critical moments. Like having a senior editor review copy before it goes to print.

### Three layers of defense, because no single layer is enough
The architecture we landed on: Layer 1 = Opus verifier (catches semantic errors like wrong recipients). Layer 2 = gog wrapper script (catches structural errors like missing --reply-all). Layer 3 = doc-level rules (guidance for getting it right the first time). We researched how the OpenClaw community handles this — the consensus is that structural enforcement is the only mechanism people actually trust. Plugins, hooks, and docs are supplements, not solutions.

### CC blindness: the gap between reading and understanding
Amber read an email where the body said "Jeff, see below." She reported the To field but not the CC field — where Jeff already was. She then asked Dave if Jeff should be added to the thread. The fix was adding explicit "check and report ALL headers" rules, but the deeper insight is about attention patterns. Humans unconsciously cross-reference body mentions against headers. AI models read each field independently unless told to connect them. The skill isn't reading — it's cross-referencing.
