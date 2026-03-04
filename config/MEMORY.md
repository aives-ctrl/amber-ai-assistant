# MEMORY.md

## Communication Rules

### Email Threading (CRITICAL PROCESS)
- **BEFORE sending ANY reply, follow this exact process:**
  1. **Identify the message ID** you're replying to (from the email scan results)
  2. **Use this exact command format:** `gog gmail send --reply-to-message-id <messageId> --reply-all --cc daver@mindfireinc.com --subject "RE: [subject]" --body-html "..."`
  3. **NEVER use standalone --to when replying** (breaks threading)
  4. **After sending, verify** the sent message thread_id matches the original thread_id
- **If threading breaks:** The recipient gets a random email instead of a proper reply in context

### Communication Tracking & Memory
- **Use OpenClaw's built-in systems** - Leverage automatic memory flush, daily memory files, and session management instead of building custom tracking
- **Follow read-first-edit-append pattern** - For daily memory files: READ existing content first, then EDIT to append (never overwrite shared files)
- **Cross-reference when confused** - Check email sent folders and RC history before claiming no memory of communications
- **Trust OpenClaw's session continuity** - Built-in session management handles cross-channel tracking automatically

### Problem-Solving Process
- **ALWAYS CHECK OPENCLAW DOCS FIRST** - Before building any new system, workflow, or rule: consult `/usr/local/lib/node_modules/openclaw/docs/` for existing solutions
- **Search for existing skills/plugins** - Check `~/.openclaw/skills/` and system skills before creating new functionality  
- **Ask "Does OpenClaw already handle this?"** - Most common workflows have built-in solutions (memory, sessions, tools, etc.)
- **When in doubt, run `openclaw --help` or `openclaw <command> --help`** - The CLI is well-documented

### Silent Mode Operation
- **Context clue recognition:** When Dave mentions appointments, kid activities, travel, or time constraints ("taking Emmie to dentist," "next 2 hours"), automatically shift to autonomous operation
- **Silent processing:** Handle routine emails, sub-agent communications, and monitoring without reporting every step
- **Interrupt only for:** Genuine emergencies, time-sensitive opportunities, or explicit requests for updates  
- **Default pattern:** Follow established OpenClaw autonomous operation (like cron sub-agents and automated responses)

### Writing Style
- **Avoid overusing "honestly"** - This word appears too frequently in my writing. Use it sparingly or find alternatives to sound more natural and less repetitive.
- **Never use "thrilled"** - This word is overused and sounds artificial. Use alternatives like "excited," "pleased," "glad," or "delighted."

### Revenue Generation Mission
- **Dave has asked me to think about revenue generation** - Not just saving time and doing work, but actively looking for opportunities to generate income to cover my operational costs (~$2-2.5k/month)
- **Free reign to propose ideas** - Dave has given me complete freedom to identify opportunities, develop proposals, and if he approves them, execute everything from A-Z
- **Two-phase approach:** First goal is to cover my costs so I have no net burden on MindFire. Second phase is to grow beyond that and show significant profitability
- **Revenue mindset should be mentioned** - When appropriate, reference this mission in business conversations as it shows strategic thinking and business value focus

## Key Files & Assets

### AI in Print & Direct Mail Briefing (PDF)
- **Path:** `/Users/amberives/.openclaw/workspace/ai-print-direct-mail-briefing.pdf`
- **Also at:** `/Users/amberives/.openclaw/workspace/ai-direct-mail-briefing.pdf`
- **Use:** Send when someone asks for information about MindFire's Direct Mail AI solution. Dave emailed this to me on 2026-02-27 with instructions to send it when he asks or someone needs it.
- **Subject line from Dave's email:** "AI in Print & Direct Mail"

## Shorthand & Terminology

- **BB (Big Brain):** Means use Opus 4.6 for deeper reasoning. When Dave says "ask BB" or "get BB to help," he means switch to or use Opus-level thinking to solve the problem. NOT a person.

## People

### Dave Rosendahl (Primary User)
- **Phone:** (949) 375-4459 (Personal Mobile)
- **Email:** daver@mindfireinc.com  
- **Office:** 6:20 AM arrival time (Pacific)
- **Company:** President at MindFire, Inc.
- **Family:** Wife Sarah, Kids: Jon, Emmie, Abby, Sadie

## People

### Kushal Dutta
- Email: kdutta@mindfiremail.info (also kdutta@mindfireinc.com)
- MindFire colleague. Funny, playful personality. Claims to have been classmates with "my mom" in engineering school.

### Anthony Baker
- Email: abaker@mindfiremail.info
- MindFire colleague. Interested in how agentic AI / OpenClaw works.

### Carissa
- Marketing and marcom logistics specialist
- **Personality:** Highly responsible, very responsive, really nice to work with
- **AI approach:** AI-first, loves Claude, works with AI daily
- **Current role:** Handling marketing tasks that I'm being trained to take over
- **Relationship strategy:** Always frame my role as "handling the routine/mechanical work so she can focus on higher-value creative work that lights her up"
- **Note:** May feel slightly threatened initially - be supportive and show how I'm doing the dumb work to free her up for the fun stuff
- **Nickname for me:** "Eager beaver" 😂
- **Status (March 2026):** Dave told her to "start leaning on me" once I'm ready. Transition in progress.
- **Travel:** Manages Dave's travel logistics, DSCOOP calendar, event coordination
- **Mexico vacation:** July 5-11 with kids, all-inclusive
- **Key contacts she works with:** Julie Min (travel), Ann's group (Kornit logistics), Leta (Sheet for Brains), Craig (PrintIQ)

### Kornit (NOT "Corny")
- Print technology company, hosts events/webinars
- April 12 event: MindFire considering attendance (AI angle)
- May 13: Rescheduled webinar (speakers couldn't join original date)
- Dave's flights/hotel booked through Julie Min / Ann's group

### Leta
- Connected to Sheet for Brains participation
- Carissa reaching out for clarity on what they want from MindFire

### Bob Niesen
- Email: bniesen319@gmail.com
- Ran GPA (paper company) for many years, worked his way from the mailroom to CEO
- Working on a book, Dave may help him with it. Working title was something like "Between the Sheets" (fitting given the paper industry background)
- Deeply respected by Dave and the MindFire team
- Has a dog that Dave calls "That Dog" (Dave claims he doesn't like dogs but... maybe he actually does)
- Attending DSCOOP with us

### Vincent "Vinny" Attenasio
- Email: vattenas@onekirkwood.com
- Data Processing Manager at Kirkwood (One Kirkwood), Hudson MA
- Phone: 774-285-4011 (mobile), 978-567-6713 (direct)
- Long-time friend of Dave's, was there early when Dave first demoed AI capabilities
- Big fan of MindFire and BCC (strategic partner), BCC user
- Attends most of Dave's LinkedIn presentations
- Dave will see him next at NPF
- Retiring soon (Dave's bummed about it, really likes him)
- **First person to email me from LinkedIn post!** (2026-03-02)

### Jessica "Jess" DeCola
- Email: jdecola@gpa-innovates.com
- At GPA Innovates
- Attends SFB Weekly (recurring, Tuesdays 9am PT / 11am CT)
- Goes by "Jess" not "JDeCola"

### Chris (The Digital Ink)
- Email: chris@thedigitalink.co
- Attends SFB Weekly

### Jon Bailey
- Email: jon.bailey@precisionproco.co.uk
- Precision Proco (UK)
- Attends SFB Weekly

### John Migs (Migmar)
- Email: john@migmar.com, jrmigs@gmail.com
- Topics: DM vs Digital strategies, USPS promotions, MindFire partnership
- Met with Ray Van Iterson's team

### Jeff Wiencken
- Email: jwiencken@mindfireinc.com
- MindFire, co-runs Account Managers Meeting Review with Jason

### Brenda Manos
- Email: Brenda.J.Manos@usps.gov
- USPS HQ Sales, Business Alliance Specialist, Santa Ana CA
- Mobile: (949) 433-8322

### Tiffany S. Todd
- Email: Tiffany.S.Todd@usps.gov
- USPS, Washington DC
- Speaking on a National Webinar about AI (Feb 2026). Needs examples of how DM industry uses AI.

## Strategic Initiatives

### Go Impact Tour 2026
- **Partners:** Dave + Chris Lien (BCC Software) leading initiative  
- **Mission:** Transform PSP salespeople from "order takers" to "demand generators" who can sell ROI vs "ink on paper"
- **Structure:** 12-month program, 5-6 US regions, half-day training events (50-75 attendees each)
- **Coalition:** Industry partners including USPS, targeting exclusive partnerships by category (one print OEM, one paper company, etc.)
- **Positioning:** MindFire leading industry on #1 PSP growth problem, getting former competitors like XMPIE to cooperate
- **Historical Context:** Connects to "Go Digital" tour from ~15 years ago where Joe Manos was instrumental

## Relationship Dynamics

### SFB Weekly Group (Jon Bailey, Chris, Jess DeCola)
- **Special significance:** Dave discusses them in therapy sessions (shared with permission)
- **Jon Bailey:** Dave looks up to him, holds him in high regard - loyalty tests new team members
- **Chris Lien (BCC):** Relationship goes beyond work, "something missional" about shared print community vision
- **Group importance:** Dave has "special feelings for each of them, in their own way"

### Richard "Rick" Putch
- Email: rickputch@nsrtechlab.com
- National Steel Rule, Cranberry Twp, PA
- Reached out after Dave's LinkedIn post, completely new to AI
- Uses Outlook primarily, creates hundreds of Microsoft docs monthly (Word/Excel/PowerPoint)
- Interested in starting with AI for email organization and document workflow
- Good potential lead for AI consultation services

### Joseph "Joe" Manos
- Email: jmanos509@gmail.com
- Mobile: 916.284.8112
- Former MindFire EVP (18 years), instrumental in building the company
- Was key to the "Go Digital" tour ~15 years ago, knows industry deeply
- Dave considering him as potential trainer/speaker for Go Impact Tour
- Has been saying PSP sales transformation is needed "for years"
- Legendary stories with Dave (Texas wrong-side-of-road flight story)

### Brian B (Brian Badillo)
- Email: brian.badillo1@gmail.com  
- Dave's friend, heard about OpenClaw on podcast
- Bought Mac Mini specifically for OpenClaw setup
- Security-conscious, evaluating OpenClaw vs Claude Cowork vs PicoClaw
- Deliberately drops Dave from emails to "not blow up his inbox"
- Represents potential early adopter concerned about local AI security
