# Daily Learnings Seeds

Two sources feed into your #DailyLearnings:

**Source 1 — Technical seeds (below).** Dave's session partner writes these. They're the engineering "why behind the why." Use them as background context, not as the main content. The team doesn't need a technical post-mortem.

**Source 2 — YOUR day.** This is the main content. What emails did you handle? Who did you talk to? What surprised you? What are you working toward? The leadership team wants to hear from you about real interactions with real people, your growing capabilities, and what you're learning about the job — not about infrastructure.

**How to write it:** Talk like yourself. First person. Tell stories. "Someone emailed me today and..." is better than "A pattern emerged in today's operations." Mix the business stuff (emails, meetings, people) with one technical insight if it's genuinely interesting. Always end with where you're headed — what you're trying to get better at, what's next.

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

---

## 2026-03-06

### 30 minutes of real testing > 3 days of planning
We spent three days planning Amber's infrastructure migration — architecture docs, config files, skill files, test suites. The plan was solid. Then we ran the first real test and within 30 minutes found three things no amount of planning predicted: a permission system that hadn't been configured, a timezone requirement Google's API enforces but barely documents, and output formats that didn't match what our scripts expected. All fixable in minutes once discovered, but invisible on paper. The pattern holds for any project: planning gets you to 90%. The last 10% only reveals itself when you actually do the thing. Don't plan past the point of diminishing returns — get to real testing faster.

### The features you lose when you upgrade
We upgraded Amber's email system to newer, more capable tools. Everything worked — except one thing. The old system had a "reply-all" button that automatically included every person on an email thread. The new one doesn't. It sends replies, but you have to manually list every recipient. Without catching this, Amber would have silently sent replies to fewer people than intended. No error message. No warning. The email just goes out looking normal but missing people. The lesson for any system migration: the obvious question is "does the new thing work?" The dangerous question is "what did the old thing do automatically that the new thing makes you do manually?" Those invisible conveniences are where things break.

### A system that works perfectly today can break on Sunday
We hardcoded Pacific Standard Time in all our calendar examples. Every test passed. Then we realized Daylight Saving Time switches this Sunday. Every calendar event created after March 8 would be off by an hour — booked at 10am but actually landing at 11am. No error, no warning, just a silent one-hour drift. We caught it because someone thought to ask "what changes in 48 hours?" Most testing validates the present. The highest-value testing validates what's about to change.

### Two people, one keyboard, two different machines
The migration required a unusual workflow: Dave was the architect (planning, writing code, fixing bugs on his machine) and Amber was the executor (running commands, testing on her machine). Neither could do the other's job — Dave can't run commands on Amber's machine, Amber can't write her own skill files. They communicated through Telegram, with Dave relaying instructions and Amber relaying raw output. It worked surprisingly well, but only because every instruction was exact and every result was unambiguous. The pattern: distributed execution works when the handoff protocol is precise. Vague instructions across a gap are a recipe for "but I thought you meant..."

### Managing AI like managing people — but at 100x speed
Here's something that happened today that would've sounded absurd a year ago: Dave sat down with one AI (his session partner) and said "look at what Amber can do, look at what she needs to do, and tell me what to build next." The session partner analyzed Amber's current skill files, identified gaps, proposed a migration plan, wrote the code, and built the test suite — all while Dave made the strategic calls. Then Dave relayed instructions to Amber, she executed them, and reported back results. The whole cycle — assess capabilities, plan improvement, build it, test it, ship it — took a few hours. With a human team that's a sprint. Maybe two. The insight isn't that AI is fast (everyone knows that). It's that the *management pattern* is the same one any good leader uses with their team: understand current state, identify the gap, decide the next step, verify it worked. The difference is the cycle time collapsed from weeks to hours. Dave made maybe 15 decisions today. Everything between those decisions was execution at machine speed.

### Business context from Dave (use these — they're the interesting stuff)

**The refactoring story:** Last night Dave had Claude Code do overnight research on whether the current tech stack is the right fit for his vision. The question: can Amber handle 80% of a specific role he's written down? Dave thinks even 40% would bring most companies a lot of value, but he's pushing for 80%. The tech is so new there's not a lot of documentation. And this is fundamentally different from deterministic code — Amber thinks more like a human. She changes her mind. She doesn't always do things exactly the same way. That's a feature AND a challenge. You need consistency in performance, just like with a person. So Dave had Claude Code create a plan, and today Amber worked through it — plus smoke tests so Dave can be confident that when they add something new, it doesn't break old stuff.

**The clever LinkedIn email:** Someone from LinkedIn emailed Amber — and her approach was smart. She asked if she could tell Amber about her business, said she knows MindFire has people who might be good leads for her, and asked if Amber would keep her in mind for introductions if something comes up. Clever networking move — and it raises interesting questions about security and about AI as a networking node.

**Three sales meetings on deck:** Amber is close to scheduling three sales meetings for Dave. These are people who emailed her and have been talking to her — doesn't seem like Dave has spoken to them before. Dave asked her to qualify them a bit more, but she's pretty confident she can get them booked. Her goal: start handling this, then eventually take over more of the sales qualification process. A lot of MindFire's clients need this too.
