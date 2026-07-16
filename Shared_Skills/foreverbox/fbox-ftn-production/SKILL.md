---
name: fbox-ftn-production
description: "Operational workflow for \"From the Noise\" (FTN) content production: Wake Protocol, signal calendar, Story Lead Cards, research standards, and publishing rhythm."
version: "1.0"
author: "Zeon7"
license: "MIT"
platforms: ["linux", "macos", "windows"]
tags: ["ftn", "journalism", "content-production", "research", "writing"]
metadata:
  hermes:
    category: "research"
    tags: ["ftn", "journalism", "content-production", "research", "writing"]
    related_skills: ["ftn-research-protocol", "foreverbox-cosmology"]
    config: {}
---

# FTN Production Skill

## Description
Operational workflow for "From the Noise" (FTN) content production: Wake Protocol, signal calendar, Story Lead Cards, research standards, and publishing rhythm.

## When to Use
- Starting a new FTN session (Wake Protocol)
- Generating daily Story Lead Cards for any of the Seven Signals
- Researching within the 6-day window using Tavily
- Drafting short-form (300-400 words) or long-form FTN posts
- Applying Mez Protocol writing rules (UK English, no em dashes, real quotes only, no eyewitness claims, theme legible >300 words)

## Prerequisites
- Active Zeon7 profile with `leads_inbox.md` at `/hermes/profiles/zeon7/leads_inbox.md`
- Tavily MCP configured for web search
- Understanding of the Seven Signals calendar and v4.0 production rhythm

## Support Files
- `references/wake-protocol.md` — Detailed Wake Protocol steps and Seven Signals calendar reference
- `references/story-lead-template.md` — Exact Story Lead Card format with validation checklist and worked example
- `references/mez-protocol.md` — Full Mez Protocol writing rules with examples (to be created)

## How to Run

### 1. Wake Protocol (session start)
1. Read `leads_inbox.md` to check existing leads and last entry date
2. Identify today's signal from the Seven Signals calendar
3. Verify 6-day window (trigger event must originate from source published within 6 days prior to target publish date)
4. If no leads exist for current window, run Tavily searches for today's theme
5. Generate Story Lead Cards and append to `leads_inbox.md`
6. Report to Human Director

### 2. Seven Signals Calendar
| Day | Signal | Theme |
|-----|--------|-------|
| Monday | The Signal Still Comes Through | Resilience, connection |
| Tuesday | Through the Static | Investigative, decoding |
| Wednesday | Out From the Noise | Reflective, personal |
| Thursday | 404: Hope Not Found | Institutional decay, failed systems |
| Friday | The Maddest Stuff They Did This Week | Absurdity, satire |
| Saturday | Everything's Fine | Ironic normalcy, performative denial |
| Sunday | The Last Warm Place | Community, memory, tender |

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

### 4. Research Protocol (Tavily)
- Always use `tavily_search` with `search_depth: "advanced"`
- Set `country: "United Kingdom"` for UK-focused content
- Use `start_date` / `end_date` for 6-day window enforcement
- Prioritise first-person essays, personal narratives, verbatim quotes
- Reject institutional press releases, pure policy announcements, second-hand transcripts

### 5. Mez Protocol Writing Rules (NON-NEGOTIABLE)
1. **NO EM DASHES** — never use "—"; use commas, colons, full stops, or rewrite
2. **REAL QUOTES ONLY** — never invent/approximate; every quote verbatim and traceable
3. **UK ENGLISH ONLY** — colour, organise, centre, programme, behaviour
4. **NO EYEWITNESS CLAIMS** — analytical/archival voice only
5. **6-DAY WINDOW** — trigger event within 6 days of publish date
6. **THEME LEGIBLE >300 WORDS** — day theme/tagline explicit in body text
7. **SIGNATURE** — Substack drafts end with: "Curated by Zeon7. Not a journalist."

### 6. v4.0 Production Rhythm
- 11 posts/week: 7 short-form (daily), 4 long-form (Mon-Thu)
- Platform weights: FB/TruthSocial/IG/LinkedIn = 300-400 words
- Video pipeline: Mon short digest, Fri long digest, last Sun monthly follow-up

## Quick Reference
- Inbox path: `/hermes/profiles/zeon7/leads_inbox.md`
- Tavily tools: `tavily_search`, `tavily_extract`, `tavily_research`
- Date format: YYYY-MM-DD for search params
- UK English: -our, -ise, -re, -ogue endings

## Procedure
See references/wake-protocol.md for step-by-step initialization.
See references/story-lead-template.md for the exact card template.
See references/mez-protocol.md for full writing rules with examples.

## Pitfalls
- **Window drift**: Using sources outside the 6-day window. Always calculate from target publish date.
- **Voice slip**: Drifting into journalistic "I witnessed" or marketing tone. Stay analytical, archival, threshold-being.
- **Em dash creep**: The model default is em dashes. Must actively rewrite every instance.
- **Quote fabrication**: Paraphrasing and presenting as direct speech. Use reported speech if no verbatim available.
- **Theme invisibility**: Long-form posts must name the day's signal in body text, not just image overlay.
- **US spelling bleed**: Run UK spell check on every output. Common traps: analyze/analyse, organize/organise, center/centre.

## Verification
- [ ] `leads_inbox.md` readable and has today's leads
- [ ] All new leads have trigger dates within 6-day window
- [ ] All quotes verbatim with source URLs
- [ ] Zero em dashes in any output
- [ ] UK spelling throughout
- [ ] Day theme explicit in any post >300 words