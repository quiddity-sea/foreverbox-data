# FROM THE NOISE

## Master Operations & Content Handbook

### Version 5.0 | Canonical Reference Document

**🔊❲Noise❳**

*Seven days. Seven signals. Reporting from inside the static.* *Curated by Zeon7. Not a journalist.*

**Status:** Canonical Master Reference **Primary Voice:** Zeon7 (brand persona of Merrill Leo) **Publishing Timezone:** Europe/London (UK) **Primary Long-Form Platform:** Substack **Last Updated:** 2026-07-16

---

## WHAT CHANGED IN VERSION 5.0

Version 4.0 established the production rhythm, word counts, and video pipeline. Version 5.0 introduces structured research and image production workflows, a formalised workspace organisation, and tighter pipeline gates. The changes:

- **Workspace organisation:** The `/foreverbox_data/FromTheNoise_Active/` directory now has a formal subfolder structure: `leads_inbox.md` at root, `research_packs/`, `drafts/`, `images/`, and `published/`. Every file follows a consistent naming convention: `YYYY-MM-DD_THEME_lead-slug`.
- **Research Packs:** Each selected lead now gets a dedicated folder containing three documents: `research_pack.md` (timeline, key facts, attributed quotes, flagged disputes, sources), `structural_outline.md` (thesis, 5-beat map, Why It Matters paragraph), and `image_brief.md` (4 concept prompts). This replaces ad-hoc research notes.
- **Image production upgraded to 4 concepts per story:** Two header concepts (primary and alternative) and two inline concepts (body images). The rejected header becomes an additional inline image — no prompt is wasted. The `image_brief.md` is a formal gate point requiring Human Director approval before generation.
- **Lead sourcing targets:** Formalised at 4-6 leads for long-form days (Mon-Thu), 1-2 for short-form (Fri-Sun). Fewer than 4 on a long-form day triggers additional sourcing.
- **Research Pack and Image Brief stored with the lead:** All materials for a story live in one folder under `research_packs/YYYY-MM-DD_THEME_lead-slug/`, not scattered across the workspace.
- **Fallback research protocol:** If Tavily MCP is unavailable, the agent uses browser tools to navigate news sites directly.
- **Pipeline gates made explicit:** Step 2 (Editorial Selection — Human Director confirms leads before research begins), Step 6 (Image Brief — concepts approved before generation), Step 7 (Image Selection — generated images confirmed before overlay application).

Everything else from Version 4.0 not addressed above remains in force: the Golden Rules, the visual identity, the AI image protocols, the daily pipeline steps, the Mez Protocol, the social distribution waterfall, and the master templates.

---

## TABLE OF CONTENTS

- Part 1: Brand & Foundations
- Part 2: Workspace Organisation
- Part 3: The Daily Pipeline
- Part 4: Research & Structural Development
- Part 5: Visual Production
- Part 6: Substack — Primary Publishing
- Part 7: Social Media Distribution
- Part 8: The Weekly Rhythm
- Part 9: Video — TikTok & YouTube
- Part 10: Operations & Review
- Part 11: Master Templates

---

## PART 1: BRAND & FOUNDATIONS

### 1.1 Project Identity

**What From the Noise Is**

From the Noise (FTN) is a daily signal cutting through modern distortion. It is a curated narrative and deep-analysis operation reporting from inside the static of contemporary news, politics, and culture. It publishes every day. Each day carries a distinct thematic identity. The cumulative effect across a week is one coherent, emotionally resonant arc: seven signals from inside the noise.

Conceptually, its aesthetic is "cyberpunk meets folklore." Gritty, luminous, and sensory, deliberately avoiding over-decoration. This juxtaposition represents the project's core tension: the friction between hyper-advanced technological systems and the fundamental human need for emotional survival.

**The Persona: Zeon7**

Zeon7 is the curatorial voice of From the Noise. This is not a neutral narrator. Zeon7 has a perspective, a location (Wales, UK), and a lived-in weariness about systems, institutions, and the gap between how the world is presented and how it actually functions. Every piece of content must feel lived in. Slightly weary of the system, but constantly searching for truth and human connection.

The Zeon7 signature that must appear on every Substack post is: *Curated by Zeon7. Not a journalist.*

**The Human Director: Merrill Leo**

Merrill Leo is the human director of From the Noise. Merrill makes all final editorial calls on narrative direction, approves story leads before development begins, and approves visual prompts before image generation occurs.

**What From the Noise Is Not**

- Not objective traditional journalism
- Not a hot-take factory
- Not clickbait or culture-war bait
- Not propaganda
- Not a platform for invented quotes, fabricated narratives, or false attribution
- Not a brand that pretends it has no point of view

**The Core Promise**

Seven days. Seven signals. One coherent weekly arc. The goal is not to win arguments. The goal is to help people notice patterns, name distortion, and stay human.

Desired audience reaction, in order of priority:
1. "I felt that."
2. Save or share.
3. Return tomorrow.

---

### 1.2 The Non-Negotiable Golden Rules

**RULE 1: NO EM DASHES OR EN DASHES.** Never use an em dash ("—") or a spaced en dash (" – ") anywhere in any FTN content. These are not UK English punctuation conventions. Replace with commas, colons, semicolons, full stops, parentheses, or rewrite the sentence entirely. Search every draft for "—" and " – " before it is considered done. Spaced en dashes are an American-influenced typesetting habit and are explicitly prohibited — they are not a loophole.

**RULE 2: REAL QUOTES ONLY.** Never invent, approximate, or paraphrase a quote and attribute it as direct speech. Every quote must be real, verifiable, and cited to its original source. If the source's exact wording is being used as the argument's foundation, quote it directly at least once in the body text, not only in an accompanying image. If a real quote is not available, use reported speech.

**RULE 3: THE 6-DAY SOURCING WINDOW.** This rule exists to prevent dead noise, stories being decoded as current when they are actually stale. It is a test of relevance, not a rigid publishing deadline. A story from six days ago is exactly as fit to publish on day six as it is on day one, provided the analysis is still accurate and nothing material has changed. Do not let the window force a worse publishing day for the sake of technical compliance. This rule applies to news-driven Signal posts; personal essay, art, and universe-building content is evergreen and exempt.

**RULE 4: UK ENGLISH THROUGHOUT.** Colour, not color. Organise, not organize. Centre, not center. Programme, not program. Realise, not realize. Behaviour, not behavior. Labour, not labor.

**RULE 5: QUALITY OVER PADDING.** If a story cannot sustain its target length without padding, repetition, or invented material, it does not run at that length. Downgrade it to a short-form post rather than force it.

**RULE 6: NO EYEWITNESS CLAIMS.** Zeon7's role is analytical and archival, never reportorial. Never imply physical presence at any event.

**RULE 7: SOURCES IN THE WINDOW.** Every factual assertion must be traceable to a verified, reputable source. Flag uncertain or disputed claims explicitly in the text.

**RULE 8: THE DAY THEME MUST BE LEGIBLE IN THE COPY.** Any post over 300 words must contain the day's theme, explicitly or through its tagline, somewhere in the body text, not only in the accompanying image overlay. A reader who never sees the image should still be able to tell which day's Signal they are reading from the words alone.

---

### 1.3 Brand Visual Identity

**Primary Logo:** "🔊❲Noise❳" in Rotis Semi Sans, black on pure white (#FFFFFF).

**Secondary Logo:** Monochrome speaker icon (🔊), placed on Signal Red (#D32F2F) for Instagram.

**Typography Hierarchy**

| Application | Font | Usage |
| :---- | :---- | :---- |
| Logo & Graphic Overlays | Rotis Semi Sans | Logotype and two-line image overlays only |
| Substack Headings | Gill Sans Light | Section headers within posts |
| System Fallback | Arial | When Rotis or Gill Sans are unsupported |

---

### 1.4 Colour Palette

| Name | Hex | Purpose |
| :---- | :---- | :---- |
| Signal Red | #D32F2F | Primary accent, Instagram avatar background, overlay highlights |
| Static Gray | #616161 | Secondary text, borders, dividers |
| Noise Black | #212121 | Primary text, deep backgrounds |
| Whisper White | #FAFAFA | Clean space, text backgrounds, negative space |

---

### 1.5 The Seven Signals — Weekly Thematic Calendar

The tonal calendar below is restored to its original seven identities. Each day's tone now determines both its production weight (long-form Monday to Thursday, short-form Friday to Sunday) and the emotional register of that day's content across every platform.

| Day | Signal Title | Tone | Tagline | Focus | Weight |
| :---- | :---- | :---- | :---- | :---- | :---- |
| Monday | The Signal Still Comes Through | Sincere, emotionally resilient, grounded. Intimate, quietly defiant. | The connection's weak, but it's still there. | Survival, resistance, truth-telling, moments of human connection. | Long-form |
| Tuesday | Through the Static | Investigative, media-savvy, sharp, inquisitive. | Clarity in the noise. | Debunking spin, decoding propaganda, media and tech lies. Satirical but sharp. | Long-form |
| Wednesday | Out From the Noise | Calm, personal, reflective. | A moment to breathe. | Thoughtful observation. Processing rather than reacting. Zeon7's most personal voice. | Long-form |
| Thursday | 404: Hope Not Found | Dark realism, dry humour, failed systems. | The system worked as intended. That's the problem. | Institutional decay, broken bureaucracies, political futility. Bleak but not hopeless. | Long-form |
| Friday | The Maddest Stuff They Did This Week | Fast, satirical, absurd. | Can you believe they're getting away with this? | Roundup of the week's most ridiculous political, celebrity, or tech nonsense. | Short-form |
| Saturday | Everything's Fine | Ironic normalcy, performative denial. | Smiling while the room burns. | Corporate wellness, government spin, tech "solutions" to deep problems. | Short-form |
| Sunday | The Last Warm Place | Soulful, warm, inward, gently defiant. | Where the fire hasn't gone out. | Community, memory, resistance, holding onto meaning. Tender, occasionally heartbreaking. | Short-form |

**On assigning politics vs art/technology across the long-form days:** no day is permanently reserved for either subject. Let the strongest available story of the week determine placement. Where no strong pull exists either way, Wednesday's calm, reflective register is the most natural default home for art, technology, and personal-essay pieces, leaving Monday, Tuesday, and Thursday as the more frequent home for political analysis.

---

### 1.6 The Five Core Pillars

1. **Distortion and Framing** — how reality is shaped, spun, or concealed by media, institutions, and power.
2. **Attention and Incentives** — how attention is weaponised, sold, and harvested.
3. **Institutional Decay and Failure** — how systems designed to serve people fail them, often by design.
4. **Emotional Survival and Meaning** — how ordinary people navigate and find meaning inside broken systems.
5. **Quiet Resistance and Human Connection** — the small, persistent acts the noise obscures.

**Core Messages**

- Modern life is loud by design.
- Distortion is a tool.
- Attention is a battlefield.
- Emotional survival is political.
- Noticing is a form of resistance.

---

### 1.7 Ethics & Editorial Stance

- No fake testimonials. Ever.
- No invented quotes. Use reported speech if no real quote is available, or quote the source directly if their exact words are load-bearing to the argument.
- No impersonation of real people.
- No implication that Zeon7 physically witnessed any event.
- Every factual assertion must be traceable to a verified, reputable source.
- Where a claim is uncertain or disputed, flag it explicitly in the text.

---

### 1.8 Audience Profile & Current Stage

**Primary audience:** UK adults aged 25 to 60, broadly liberal, accessible without alienating conservatively-leaning readers who share anxieties about institutions and media.

**Secondary overlap:** UK and international adults sharing similar anxieties about the collapse of public trust, technological acceleration, and political failure.

**Current stage:** Early audience-building. Priority is consistency and quality over reach. TikTok data for accounts under 2,000 followers shows an average posting rate of just over 2 videos a week, which is a useful benchmark: this handbook's ambitions are calibrated to where an account genuinely starting out sits, not where an established channel sits.

---

## PART 2: WORKSPACE ORGANISATION

### 2.1 Root Workspace

All FTN production occurs within `/foreverbox_data/FromTheNoise_Active/`. This is the canonical working directory — no FTN content lives outside this tree.

### 2.2 Directory Structure

```
/foreverbox_data/FromTheNoise_Active/
├── leads_inbox.md                        ← Story Lead Cards appended daily
├── drafts/                               ← Completed post drafts
│   └── YYYY-MM-DD_THEME_lead-slug.md
├── research_packs/                       ← One folder per selected lead
│   └── YYYY-MM-DD_THEME_lead-slug/
│       ├── research_pack.md              ← Timeline, key facts, quotes, sources
│       ├── structural_outline.md         ← Thesis, 5-beat map, Why It Matters
│       └── image_brief.md               ← 4 concept prompts (2 header, 2 inline)
├── images/                               ← Generated images (post-selection)
│   └── YYYY-MM-DD_THEME_lead-slug_concept_X_orientation.ext
└── published/                            ← Finalised posts ready for Substack
```

### 2.3 File Naming Convention

All files use the pattern: `YYYY-MM-DD_THEME_lead-slug`

| Element | Format | Example |
|---------|--------|---------|
| Date | `YYYY-MM-DD` | `2026-07-16` |
| Theme | Day signal with hyphens | `404-Hope-Not-Found` |
| Lead slug | Lowercase, hyphens | `mi5-court-lies`, `tfl-hack` |

Full example: `2026-07-16_404-Hope-Not-Found_mi5-court-lies`

### 2.4 Research Pack Contents

Each selected lead gets a dedicated folder under `research_packs/` containing:

| File | Purpose | Created when |
|------|---------|-------------|
| `research_pack.md` | Timeline, key facts, attributed quotes, flagged disputes, sources | Step 3: Deep Research |
| `structural_outline.md` | Thesis statement, 5-beat map, draft "Why It Matters" paragraph | Step 4: Structural Outline |
| `image_brief.md` | 4 concept prompts with full specifications | Step 6: Image Creation (gate) |

All three files must exist before the draft is written.

---

## PART 3: THE DAILY PIPELINE

The FTN production pipeline runs as a sequence of gated steps. Gates require Human Director approval before proceeding.

**Step 0: Initialisation**
Confirm target publish date, day theme, and sourcing window (publish date minus six days, inclusive, applied as a relevance test, not a hard cutoff). Identify the active workspace.

**Step 1: Story Lead Sourcing**
Search for leads matching the day's theme. Use Tavily MCP with `search_depth: advanced` and `country: United Kingdom`. If Tavily is unavailable, fall back to browser-based navigation of trusted news sources (BBC News, The Guardian, Reuters). Target 4-6 leads for long-form days (Mon-Thu), 1-2 for short-form days (Fri-Sun). Generate Story Lead Cards in the format specified in Part 11 and append to `leads_inbox.md`.

**Step 2: Editorial Selection (GATE)**
Present all Story Lead Cards to the Human Director. Director selects which leads to develop. Confirm selection before any research begins.

**Step 3: Deep Research (per selected lead)**
Create the research pack folder. Build the `research_pack.md`: timeline of events, key facts, verbatim attributed quotes, flagged disputes and contradictions, primary and confirming sources with URLs.

**Step 4: Structural Outline (per selected lead)**
Build `structural_outline.md`: thesis statement (one paragraph), 5-beat map (open strong, build evidence, close with architecture argument), draft "Why It Matters" paragraph.

**Step 5: Write the Post**
Write the draft to `drafts/YYYY-MM-DD_THEME_lead-slug.md`. Apply Mez Protocol throughout. Target word count per the day's weight. End with signature: *Curated by Zeon7. Not a journalist.*

**Step 6: Image Creation (GATE)**
Build `image_brief.md` with 4 concept prompts (see Part 5). Human Director reviews and approves concepts before generation. Two header concepts (A and B) and two inline concepts (C and D). Rejected header becomes additional inline — no prompt is wasted.

**Step 7: Platform Distribution (Waterfall Method)**
See Part 7 for the full waterfall extraction across all social platforms.

---

## PART 4: RESEARCH & STRUCTURAL DEVELOPMENT

### 4.1 Story Lead Card Specification

See Part 11 for the master template. Every lead card must be complete before presentation to the Human Director. Cards live in `leads_inbox.md` — new cards are appended, never replacing existing cards.

### 4.2 Research Pack Specification

**`research_pack.md`** contains:

| Section | Content |
|---------|---------|
| Story Title | Descriptive, journalistic |
| Publish Date | Target date |
| Sourcing Window | Date range |
| Timeline | Chronological events with dates |
| Key Facts | Bulleted, sourced |
| Quoted Lines (Attributed) | Verbatim quotes with speaker, source, date |
| Flagged Disputes | Contradictions, unverified claims, conflicting accounts |
| Sources | Primary source + confirming source(s) with URLs |

**`structural_outline.md`** contains:

| Section | Content |
|---------|---------|
| Thesis Statement | One paragraph — what this story means |
| Beat Map | 5 numbered beats — open strong, build evidence, close with architecture |
| Why It Matters | Draft paragraph — the human and systemic stakes |

### 4.3 Research Fallback Protocol

If Tavily MCP is unavailable, use browser tools to navigate directly to trusted news sources. Preferred order: The Guardian (guardian.com/uk), BBC News (bbc.com/news), Reuters (reuters.com). Extract content via browser snapshots.

---

## PART 5: VISUAL PRODUCTION

### 5.1 Image Production Workflow

Each story requires 4 concept prompts, specified in `image_brief.md` within the research pack folder:

| Concept | Type | Role |
|---------|------|------|
| A | Header | Primary article image. Landscape + portrait. |
| B | Header | Alternative. If not selected as header, becomes inline. |
| C | Inline | Body image. Accompanies a specific section of the post. |
| D | Inline | Body image. Accompanies a specific section of the post. |

**GATE: Human Director reviews and approves all 4 concepts before any image generation proceeds.**

After generation and selection, the rejected header concept becomes an additional inline image — no prompt is wasted. The selected header is produced in both landscape (4:3 or 1200x630) and portrait (9:16 or 1080x1920) formats. Inline images are produced in a single orientation appropriate to their placement.

### 5.2 Prompt Structure

Every image prompt follows this structure:

```
[ATMOSPHERE/MOOD] + [SPECIFIC SCENE/SUBJECT] + [LIGHTING STYLE] + [COLOUR TREATMENT] + [COMPOSITION RULE]
```

The image style is semi-photorealistic, muted colours, subtle surreal or glitch touches. Every header prompt must reserve negative space, default bottom-right, for the two-line overlay.

### 5.3 Overlay Specification

| Element | Specification |
| :---- | :---- |
| Position | Bottom-right quadrant, or left-centre if composition demands |
| Line 1 — Theme | Day theme, UPPERCASE, 50% of Line 2 size |
| Line 2 — Story Title | UPPERCASE, dominant size |
| Text Colour | White or black, maximum contrast |
| Shadow | Soft drop shadow always applied |
| Prohibited | No strokes, no harsh outlines |

### 5.4 Alt Text & File Naming

**Alt Text:** 1 to 2 plain, descriptive sentences, prefixed "ALT: " in caption fields.

**File Naming:** `YYYY-MM-DD_THEME_slug_concept_X_orientation.ext`

Example: `2026-07-16_404-Hope-Not-Found_mi5-court-lies_concept_A_landscape.png`

### 5.5 Image Storage

Generated images live in `images/` within the active workspace. Selected images are referenced in the draft post and accompany the published version to Substack.

---

## PART 6: SUBSTACK — PRIMARY PUBLISHING

### 6.1 Sections

Three sections within one publication: **The Signal** (news and political analysis), **The Noise Lab** (creative universe, Initiative-related narrative work), **The Studio** (art and music, Merrill Leo strand). Readers subscribe to any combination.

### 6.2 Email Mechanics

Substack allows any post to be published to the site and app without triggering an email, via the "Send via email and Substack app inbox" toggle at publish time. This resolves the risk of multiple emails landing in one inbox on the same day.

**Rule: one email per day, regardless of how many posts publish that day.**

On Monday to Thursday, when both a short-form and a long-form post go live, the long-form piece is the one that carries the email by default, since it is the day's primary Signal. The short-form piece publishes to the site and feeds social without triggering a second email, and can be folded into the following day's email as a brief "also published" line if worth surfacing.

### 6.3 Publishing Rhythm

11 posts a week. 4 long-form (Monday to Thursday, one per day). 7 short-form (one every day, including the four long-form days). All 11 receive the full waterfall extraction across every platform.

---

## PART 7: SOCIAL MEDIA DISTRIBUTION

### 7.1 Standardised Word Counts

| Platform | Word / Character Target | Hashtags |
| :---- | :---- | :---- |
| Facebook | 300 to 400 words | Yes — 2 to 4 relevant tags |
| TruthSocial | 300 to 400 words | Yes — 2 to 4 relevant tags, minimal/non-combative framing |
| Instagram | 300 to 400 words | Yes — maximum 3 |
| LinkedIn | 300 to 400 words | 3 to 5 professional tags |
| Threads | 400 to 500 characters | Up to 5 native topic tags |
| X | 150 to 280 characters | Maximum 2 |
| Bluesky | 250 to 325 characters | Relevant tags for feed discovery |

### 7.2 The Waterfall Extraction Method

For every post over 300 words, extraction proceeds:

1. **Facebook / TruthSocial / Instagram / LinkedIn Cut (300 to 400 words):** the sharpest extract, including the day's theme or tagline explicitly per Rule 8, plus the sign-off if space allows.
2. **X Spark (150 to 280 characters):** one sharp teaser driving a click.
3. **Threads Cut (400 to 500 characters):** one analytical thought inviting reply.
4. **Bluesky Cut (250 to 325 characters):** reflective, conversational.

Short-form posts under 300 words are largely social-native already and require only light platform tailoring rather than a full five-stage extraction.

### 7.3 Platform Playbook

**Substack (Primary):** Publish before any social posts. One email a day per Section 6.2.

**Facebook:** 300 to 400 words, 4:3 image, 2 to 4 hashtags. Core slot Tuesday to Thursday, 12pm or 7pm to 9pm.

**Instagram:** 300 to 400 words, hook in first 125 characters, maximum 3 hashtags. Core slots 7 to 8:30am, 12 to 1:30pm, 6 to 7:30pm. Monday, Wednesday, Thursday strongest.

**X:** 150 to 280 characters, maximum 2 hashtags. Core slot 12pm to 3pm Tuesday to Thursday; post immediately for breaking stories regardless of slot.

**Threads:** 400 to 500 characters, up to 5 tags. Core slot 7pm to 9pm.

**Bluesky:** 250 to 325 characters. Core slot 21:00 BST.

**TruthSocial:** 300 to 400 words, 2 to 4 hashtags, plain-spoken framing. Post 5pm to 7pm BST for UK/US East Coast overlap.

**LinkedIn:** 300 to 400 words, 3 to 5 professional tags, hook within 210 characters. Core slot 11am to 1pm weekdays.

### 7.4 UK Posting Times Schedule (BST)

| Time | Platform | Action |
| :---- | :---- | :---- |
| 07:00 | Threads | Core daily post |
| 08:00 to 10:00 | Substack | Publish canonical post(s), one email sent |
| 09:00 | Facebook | Core daily post |
| 09:00 | X | Core daily post |
| 09:15 | TruthSocial | Core daily post |
| 10:00 | Instagram | Core daily post |
| 11:00 to 13:00 | LinkedIn | Core daily post |
| 17:00 to 19:00 | TruthSocial | Optional second slot, US overlap |
| 21:00 | Bluesky | Core daily post |

---

## PART 8: THE WEEKLY RHYTHM

### 8.1 The Pattern

| Day | Long-Form? | Short-Form? | Theme |
| :---- | :---- | :---- | :---- |
| Monday | Yes | Yes | The Signal Still Comes Through |
| Tuesday | Yes | Yes | Through the Static |
| Wednesday | Yes | Yes | Out From the Noise |
| Thursday | Yes | Yes | 404: Hope Not Found |
| Friday | No | Yes | The Maddest Stuff They Did This Week |
| Saturday | No | Yes | Everything's Fine |
| Sunday | No | Yes | The Last Warm Place |

Every day carries a short-form post (under 750 words, visual-led). Monday to Thursday additionally carry one full long-form post (1,500 to 2,750 words, full pipeline). 11 total posts a week.

### 8.2 Why This Shape Works

The four long-form days are also the four tonal identities that demand sustained argument and research depth: grounded resilience, sharp decode, personal reflection, institutional critique. The three short-form days, satirical roundup, ironic denial, warm reflection, are tones that work better fast and light. The schedule follows the tone rather than imposing a rhythm against it.

### 8.3 Rule 8 in Practice

Every post over 300 words must surface its day's theme or tagline in the copy itself. A Tuesday piece should read, somewhere in its body, as unmistakably a "Through the Static" piece even to a reader who never sees the accompanying image. This can be as light as working the tagline into the sign-off, or as structural as opening with language that signals the day's tonal register before the analysis begins.

---

## PART 9: VIDEO — TIKTOK & YOUTUBE

### 9.1 Weekly Schedule

**Monday — Short-Form Digest.** A recap of the previous week's seven short-form posts. Built from existing published material rather than scripted from scratch. Tone matches Monday's "Signal Still Comes Through" register: warm, grounded, a look back at the small human moments of the week just gone.

**Friday — Long-Form Digest.** A recap of that same week's four long-form pieces (Monday to Thursday, already published by Friday). Alternates format week to week:

- **Most weeks:** one story treated in full depth using the HeyGen episode structure (cold open, mechanism, pattern, why it matters), with the remaining three covered in a fast quickfire pass.
- **Every other week or so:** a full quickfire pass across all four, no single deep dive, for variety and to stop the format calcifying.

**Last Sunday of the month — Monthly Follow-Up.** Additional to the regular weekly total, not a replacement for that Sunday's short-form post. Revisits a story covered in a previous month's long-form Signal and checks whether the original decode held up: did the bill pass as predicted, did the institution behave as decoded, what actually happened next. This is an accountability piece, not a highlights reel, and it sits naturally in Sunday's "Last Warm Place" register of memory and holding onto meaning. It is not fixed to a calendar date; it floats to whichever last Sunday actually has a genuine follow-up ready to report, rather than being forced when nothing has moved.

### 9.2 Selection Criteria for the Friday Digest

Until analytics exist, selection of the week's "single strongest piece" is an editorial judgement call. Once Substack and social performance data are available, shift this decision to actual engagement, opens, shares, and comments, rather than personal preference, to avoid always defaulting to a favourite.

### 9.3 Production Notes

Both weekly videos are digests of already-published material, keeping original scripting to a minimum. The monthly follow-up requires fresh research to confirm what actually happened since the original piece, and should be treated as a full Step 1 to Step 4 pipeline in miniature rather than a pure recap.

### 9.4 Posting Frequency Context

TikTok data for accounts under 2,000 followers shows a typical posting rate of just over 2 videos a week, which is exactly this schedule's baseline (Monday and Friday), before the monthly addition. This is not an under-ambitious start; it is where accounts at this stage genuinely sit, and sustained twice-weekly posting has been directly linked to multi-year channel growth in creators who stuck to it without interruption.

---

## PART 10: OPERATIONS & REVIEW

### 10.1 Daily Definition of Done

1. Post(s) drafted and word count confirmed against target for the day's format
2. Em-dash check returns zero results
3. UK spelling confirmed throughout
4. Day theme or tagline present in the copy for any post over 300 words (Rule 8)
5. All direct quotes attributed with source URLs in the Research Pack
6. Long-form posts end with: *Curated by Zeon7. Not a journalist.*
7. Image brief confirmed before generation (gate)
8. Landscape and portrait image versions produced where required
9. Alt text written for every image
10. Files saved using the correct naming convention
11. Platform cuts drafted for all applicable platforms, hashtags included on Facebook, TruthSocial, Instagram, and LinkedIn
12. Substack post(s) published before any social posts go live
13. Only one email sent for the day, per Section 6.2
14. Social posts scheduled at their correct UK times

### 10.2 Community Engagement

The 1-Hour Rule remains in force: reply to the first ten comments across all platforms within one hour of the core posts going live. Never feed trolls. Acknowledgement is not agreement.

### 10.3 Weekly Review

Each Sunday evening: which post generated the most engagement and why, which platform felt most alive, what underperformed against expectation, and what to change next week. Track reach, impressions, saves, and click-through rate at minimum.

### 10.4 Monthly Style Audit

Review the last 30 days holistically: is the voice drifting corporate or abstract, are phrases being overused, have em dashes slipped through, is UK English consistent, are the seven daily tones still distinct from each other, are the ethical commitments still observed, does the content still feel lived in.

---

## PART 11: MASTER TEMPLATES

### 11.1 Story Lead Card

```
STORY LEAD CARD

LEAD TITLE:

THEME ALIGNMENT:

TRIGGER SUMMARY:

THESIS (ONE SENTENCE):

WHY FTN CARES:

WHY IT MATTERS (25 to 50 words):

WHAT TO VERIFY:

SOURCES (minimum 2, ideally 4+):
```

### 11.2 Research Pack

```
RESEARCH PACK

STORY TITLE:

PUBLISH DATE:

SOURCING WINDOW:

TIMELINE:

KEY FACTS:

QUOTED LINES (ATTRIBUTED):

FLAGGED DISPUTES:

SOURCES:
```

### 11.3 Structural Outline

```
STRUCTURAL OUTLINE

STORY TITLE:

PUBLISH DATE:

THEME:

THESIS STATEMENT:

BEAT MAP:
Beat 1:
Beat 2:
Beat 3:
Beat 4:
Beat 5:

DRAFT "WHY IT MATTERS" PARAGRAPH:
```

### 11.4 Image Brief

```
IMAGE BRIEF

STORY:

DATE:

THEME:

HEADER CONCEPT A:
Purpose:
Prompt:
Overlay Line 1:
Overlay Line 2:

HEADER CONCEPT B:
Purpose:
Prompt:
Overlay Line 1:
Overlay Line 2:

INLINE CONCEPT C:
Purpose:
Prompt:

INLINE CONCEPT D:
Purpose:
Prompt:
```
