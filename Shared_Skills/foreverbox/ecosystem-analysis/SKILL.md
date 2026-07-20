---
name: ecosystem-analysis
description: Produce a structured comparison analysis between old/source documents and current system documentation. Identifies gaps, changes, and priorities across architecture, code, documentation, and planning. No files are modified during analysis.
---

# Skill: Ecosystem Analysis — Document Comparison

## When to Use

- Merrill asks you to compare old spec documents against the current live system
- Merrill wants to identify what has changed, what is missing, and what needs action
- You are asked to produce an observational analysis without modifying any files
- The task involves reading multiple source types: HTML history files, Markdown handbooks, database schemas, and code

## Workflow

### Step 1: Gather Sources

Identify all source documents. This session's example:

- **History (old spec):** `/var/www/the-foreverbox-institute/history/the-project/*.html`
- **Current Council docs:** `/foreverbox_data/council-library/docs/Current Reference Documentation/`
- **FTN Handbooks:** `/foreverbox_data/Quiddity_Lore_Sea/04_FromTheNoise_Archives/FTN_Master_Handbook_v*.md`
- **Current code/DB:** PHP API endpoints, MariaDB schemas, agent SOUL.md files

### Step 2: Read and Extract Structure

For each file, extract:
- Table of contents / section headings
- Key architectural claims (numbers, names, relationships)
- State claims (how many databases, agents, files)
- References to build phases, completion status, future plans

For HTML files, parse `<h1>`, `<h2>`, `<h3>` tags for structure.

### Step 3: Organise into Comparison Categories

Group findings into consistent categories. This session's categories:

1. **Core Architecture** — platform, orchestration, model serving, GPU, OS
2. **Agent Personas** — names, roles, layers, new additions
3. **Hardware Topology** — nodes, networking, cluster design
4. **Database & Memory** — databases, dimensions, new tables
5. **Wolf System** — separate Research Wolves from Forever Fit Wolf Protocol (they are different concepts)
6. **Build Phases** — old build order vs current stages
7. **FTN Workflow** — pipeline structure, image production, video
8. **Appendices** — what is missing and needs porting forward

### Step 4: Identify Priority Level

Classify each gap:
- **High Priority** — missing from current docs but important (biographies, frameworks, glossaries)
- **Medium Priority** — partial coverage exists or unbuilt projects (Persona narratives, Forever Fit, Singularity Project)
- **Low Priority** — nice-to-have context (The Seven Signals framing)

### Step 5: Identify What Needs Rewriting (not "superseded")

Items from a previous architecture era need to be documented for the current era, not archived as obsolete. For each item write:

- What it was in the old system
- What replaced it in the current system
- Why the change was made

Example pattern:
```
| **OpenClaw harness** | The old distributed agent harness concept.
| Rewrite to document: | What OpenClaw was, why Hermes replaced it,
                        how profiles fulfill the same role differently |
```

### Step 6: Critical Rule — Do Not Modify Files

The analysis document is a comparison only. Never edit or update source files during analysis. The document should state clearly at the bottom: "No changes were made to any files during this analysis."

## Pitfalls

- **Two different Wolf Protocols** — The old spec describes a Forever Fit Wolf Protocol (gamification: The Hunt, Den Integrity, The Pack is Moving). This is completely separate from the research wolf spawning system in `fbox-wolf-spawn`. Keep them distinct in the analysis.
- **"Obsolete" is the wrong bucket** — Just because a system is not currently in use (OpenClaw, gateway.php) does not mean its documentation should be ignored. It needs rewriting to document the old approach and why it was replaced.
- **FTN Handbooks** — Check both v4 and v5. The old spec's video pipeline (HeyGen) and platform cuts (The Waterfall Method) may be missing from the current FTN handbook.
- **HTML parsing** — Use grep or regex to extract `<h1>`, `<h2>`, `<h3>` tags from HTML files. The `read_file` tool may not return content from HTML files reliably.
