---
name: plans-progression-dashboard
description: Scans planning documents, parses task status across multiple formats, auto-relocates completed plans, and regenerates the dashboard. Runs the same detection engine as the update-plans-progression skill.
---

# Plans Progression Dashboard Management

## Purpose

Scans all planning docs, identifies task status, auto-relocates 100% complete plans, and regenerates Plans Progression.md.

## When to Run

After any change to planning documents.

## Parser Limitations (Critical)

The task detection engine has blind spots discovered in production:

1. **Section headers without `- DONE` markers are counted as "Not Done" tasks.** Always add `- DONE` inline to completed section headers. Table-based status markers (e.g. `| Stage 7 | ... | DONE |`) are NOT detected.

2. **AC checkbox format is strict.** Must be `- [x] AC-N:` on its own line. Variations like `* [x]` or `AC #1` or bullet-without-dash are missed.

3. **Reference sections vs tasks.** Spec/architecture sections (`## 1. ARCHITECTURE DECISION`) are not tasks but the parser counts them. Mark them `## 1. ARCHITECTURE DECISION - DONE` to get accurate percentages.