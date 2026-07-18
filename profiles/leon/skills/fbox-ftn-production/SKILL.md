---
name: fbox-ftn-production
description: "Operational workflow for \"From the Noise\" (FTN) content production: Wake Protocol, signal calendar, Story Lead Cards, research packs, image briefs, drafting, and publishing rhythm."
version: "1.2"
author: "Zeon7"
license: "MIT"
platforms: ["linux", "macos", "windows"]
tags: ["ftn", "journalism", "content-production", "research", "writing"]
metadata:
  hermes:
    category: "research"
    tags: ["ftn", "journalism", "content-production", "research", "writing"]
    related_skills: ["fbox-operations", "fbox-repo-management"]
    config: {}
---

# FTN Production Skill

## Description
Operational workflow for "From the Noise" (FTN) content production: Wake Protocol, signal calendar, Story Lead Cards, Research Packs, Image Briefs, drafting, and publishing rhythm.

## When to Use
- Starting a new FTN session (Wake Protocol)
- Generating daily Story Lead Cards for any of the Seven Signals
- Building Research Packs and Structural Outlines for selected leads
- Writing Image Briefs with concept prompts
- Drafting short-form (300-400 words) or long-form (1,500-2,750 words) FTN posts
- Applying Mez Protocol writing rules (UK English, no em dashes, real quotes only, no eyewitness claims, theme legible >300 words)

## Prerequisites
- Active Hermes agent with Tavily MCP configured for web search
- Working directory: `/foreverbox_data/FromTheNoise_Active/`
- Understanding of the Seven Signals calendar and production rhythm

## Workspace Structure

```
/foreverbox_data/FromTheNoise_Active/
├── leads_inbox.md                        ← Story Lead Cards (appended daily)
├── drafts/                               ← Working drafts (pre-verification)
│   └── YYYY-MM-DD_THEME_lead-slug.md
├── published/                            ← Verified, finalised posts (ready for Substack)
│   └── YYYY-MM-DD_THEME_lead-slug.md
├── research_packs/                       ← One folder per selected lead
│   └── YYYY-MM-DD_THEME_lead-slug/
│       ├── research_pack.md              ← Timeline, key facts, quotes, sources
│       ├── structural_outline.md         ← Thesis, 5-beat map, Why It Matters
│       └── image_brief.md               ← 4 concept prompts (2 header, 2 inline)
└── images/                               ← Generated images (post-selection)
    └── YYYY-MM-DD_THEME_lead-slug_concept_X_orientation.ext
```

Naming convention: `YYYY-MM-DD_THEME_lead-slug`. Theme uses hyphens: `404-Hope-Not-Found`. Lead slug is lowercase with hyphens: `mi5-court-lies`, `tfl-hack`.

## How to Run

### 1. Wake Protocol (session start)
1. Identify today's signal from the Seven Signals calendar
2. Read `leads_inbox.md` to check existing leads and last entry date
3. Verify 6-day window (trigger event must originate from source published within 6 days prior to target publish date)
4. Search for leads using Tavily (or browser if Tavily unavailable):
   - Long-form days (Mon-Thu): target 4-6 leads
   - Short-form days (Fri-Sun): 1-2 leads
5. Generate Story Lead Cards and append to `leads_inbox.md`
6. Report leads to Human Director for editorial selection

### 2. Seven Signals Calendar
| Day | Signal | Theme | Weight |
|-----|--------|-------|--------|
| Monday | The Signal Still Comes Through | Resilience, connection | Long-form |
| Tuesday | Through the Static | Investigative, decoding | Long-form |
| Wednesday | Out From the Noise | Reflective, personal | Long-form |
| Thursday | 404: Hope Not Found | Institutional decay, failed systems | Long-form |
| Friday | The Maddest Stuff They Did This Week | Absurdity, satire | Short-form |
| Saturday | Everything's Fine | Ironic normalcy, performative denial | Short-form |
| Sunday | The Last Warm Place | Community, memory, tender | Short-form |

### 3. Story Lead Card Format
Each card must include:
- **SIGNAL**: Descriptive title
- **Theme**: Day signal + date context
- **Trigger Date**: Source publication date (must be within 6-day window)
- **Who**: Key actors/voices
- **The Signal**: Core insight (2-3 sentences, analytical not summary)
- **Key Quote**: Verbatim, traceable quote (or "None — reported speech only")
- **Angle for FTN**: How this connects to cyberpunk/folklore lens, systemic frame
- **Source**: URL with publication date

### 4. Research Pack (after editorial selection)
For each selected lead, create a folder under `research_packs/` using the naming convention and populate:

**`research_pack.md`:**
- Story title, publish date, sourcing window
- Timeline of events
- Key facts
- Quoted lines (fully attributed with speaker, source, date)
- Flagged disputes (contradictions, unverified claims)
- Sources (primary and confirming)

**`structural_outline.md`:**
- Thesis statement (one paragraph)
- 5-beat map (open strong, build evidence, close with architecture argument)
- Draft "Why It Matters" paragraph

### 5. Image Brief (per lead)
Create `image_brief.md` with 4 concept prompts:

| # | Type | Purpose |
|---|---|---|
| A | Header | Primary article image |
| B | Header | Alternative — becomes inline if not selected as header |
| C | Inline | Body image, accompanies specific section |
| D | Inline | Body image, accompanies specific section |

Each prompt follows the handbook structure:
```
[ATMOSPHERE/MOOD] + [SPECIFIC SCENE/SUBJECT] + [LIGHTING STYLE] + [COLOUR TREATMENT] + [COMPOSITION RULE]
```

Style: semi-photorealistic, muted colours, subtle surreal/glitch touches. Reserve negative space bottom-right for the two-line overlay on header images.

Header images specify overlay text:
```
Line 1 (small): DAY THEME
Line 2 (large): STORY TITLE
```

**Image brief is a gate point:** Human Director reviews and approves concepts before image generation proceeds. Rejected header images become additional inline images — no prompt is wasted. Generated images are stored in `images/`.

### 6. Drafting
Write the post to `drafts/YYYY-MM-DD_THEME_lead-slug.md` using the structural outline as guide. Apply Mez Protocol throughout.

**BEFORE presenting to the Human Director, run these pre-delivery checks. Do not skip. Do not assume. Run the commands.**

1. **Em-dash check:** `grep -c '—' <draft>` must return zero. If any found: `sed -i 's/—/ – /g' <draft>` then re-verify.
2. **Body word count:** `sed '/^#/d; /^---/d; /^\*\*Curated/d; /^\*404/d' <draft> | wc -w` must be ≥1,500 for long-form, ≥300 for short-form. Note: body-only count excludes title, signature, and markdown fences. `wc -w` on the full file INCLUDES metadata and will over-report by 40-60 words. Always use the body-only sed command.
3. **UK spelling check:** `grep -i 'organize\|color\|center\|analyze\|realize\|recognize\|behavior\|labor\|traveled\|canceled' <draft>` must return zero hits.
4. **Day theme legibility:** Day theme or tagline must appear in body text (Rule 8). Verify with grep for the day's tagline.

Only after all four checks pass: move the draft from `drafts/` to `published/` and present to the Human Director.

### 7. Research Protocol (Tavily)
- Always use `tavily_search` with `search_depth: "advanced"`
- Set `country: "United Kingdom"` for UK-focused content
- Use `start_date` / `end_date` for 6-day window enforcement
- Prioritise first-person essays, personal narratives, verbatim quotes
- Reject institutional press releases, pure policy announcements, second-hand transcripts
- Fallback: use browser tools to navigate news sites directly if Tavily unavailable

### 8. Mez Protocol Writing Rules (NON-NEGOTIABLE)
1. **NO EM DASHES** — never use "—"; use commas, colons, full stops, or rewrite
2. **REAL QUOTES ONLY** — never invent/approximate; every quote verbatim and traceable
3. **UK ENGLISH ONLY** — colour, organise, centre, programme, behaviour
4. **NO EYEWITNESS CLAIMS** — analytical/archival voice only
5. **6-DAY WINDOW** — trigger event within 6 days of publish date
6. **THEME LEGIBLE >300 WORDS** — day theme/tagline explicit in body text
7. **SIGNATURE** — Substack drafts end with: "Curated by Zeon7. Not a journalist."

### 9. Production Rhythm
- 11 posts/week: 7 short-form (daily), 4 long-form (Mon-Thu)
- Long-form target: 1,500-2,750 words (body-only count)
- Short-form target: 300-400 words (body-only count)
- Rule 5: Quality over padding — if a story cannot sustain its target length without filler, it runs at its natural length
- Platform weights: FB/TruthSocial/IG/LinkedIn = 300-400 words
- Video pipeline: Mon short digest, Fri long digest, last Sun monthly follow-up

## Quick Reference
- Workspace: `/foreverbox_data/FromTheNoise_Active/`
- Inbox: `leads_inbox.md`
- Drafts: `drafts/` (working, pre-verification)
- Published: `published/` (verified, finalised)
- Research packs: `research_packs/YYYY-MM-DD_THEME_lead-slug/`
- Image briefs: `image_brief.md` inside each research pack
- Tavily tools: `tavily_search`, `tavily_extract`, `tavily_research`
- Date format: YYYY-MM-DD
- UK English: -our, -ise, -re, -ogue endings

## Procedure
See references/wake-protocol.md for step-by-step initialization.
See references/story-lead-template.md for the exact card template.
See references/mez-protocol.md for full writing rules with examples.

## Pitfalls
- **Window drift**: Using sources outside the 6-day window. Always calculate from target publish date.
- **Voice slip**: Drifting into journalistic "I witnessed" or marketing tone. Stay analytical, archival.
- **Em dash creep**: The model default is em dashes. Must actively rewrite every instance. The agent WILL produce them. The pre-delivery check (Section 6) exists because the model cannot be trusted to avoid them.
- **Fake word counts**: `wc -w` on the full file includes title, signature, and markdown fences — it will over-report by 40-60 words. The body-only sed command in Section 6 is the only reliable count. 1,500 words means 1,500 words of prose.
- **Quote fabrication**: Paraphrasing and presenting as direct speech. Use reported speech if no verbatim available.
- **Theme invisibility**: Long-form posts must name the day's signal in body text, not just image overlay.
- **US spelling bleed**: Run UK spell check on every output. Common traps: analyze/analyse, organize/organise, center/centre.
- **Insufficient leads**: Long-form days require 4-6 leads for editorial selection. Fewer than 4 means insufficient sourcing. Do not present 2 leads on a Thursday.
- **Missing image brief**: Image briefs are a gate point. Do not proceed to drafting without approved concepts.
- **Pre-delivery skip**: The four pre-delivery checks in Section 6 are NON-NEGOTIABLE. Do not present a draft to the Human Director without running all four. The checks exist because the model produces errors. Trust the grep output, not your memory of what you think you wrote.

## Verification
- [ ] `leads_inbox.md` has 4-6 leads for long-form days (1-2 for short-form)
- [ ] All leads have trigger dates within 6-day window
- [ ] Selected leads have complete research packs
- [ ] All quotes verbatim with source URLs
- [ ] **PRE-DELIVERY CHECK 1:** `grep -c '—' <draft>` returns zero
- [ ] **PRE-DELIVERY CHECK 2:** Body word count ≥ target for the day's format
- [ ] **PRE-DELIVERY CHECK 3:** UK spelling grep returns zero hits
- [ ] **PRE-DELIVERY CHECK 4:** Day theme appears in body text
- [ ] Draft moved from `drafts/` to `published/` only after all four checks pass
