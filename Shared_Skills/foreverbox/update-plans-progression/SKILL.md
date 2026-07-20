---
name: update-plans-progression
description: Scans all planning documents in the Council Library docs folders, identifies completed and uncompleted tasks using multi-format parsing, moves 100% complete plans to Current Completed Plans, and regenerates the Plans Progression.md dashboard. Run this after any change to a planning document.
---

# Skill: Update Plans Progression

## Purpose

Scans all planning docs, identifies task status, auto-relocates 100% complete plans, and regenerates the Plans Progression.md dashboard.

## When to Run

After any change to a planning document: task completed, task added, plan moved, new plan created.

## Automatic Plan Relocation

When a plan in `Current Started Plans/` reaches **100%** (all tasks Done), move it to `Current Completed Plans/`. If a plan in Completed Plans drops below 100%, move it back to Started Plans.

## Execution Steps

1. Scan four folders:
   - `Current Started Plans/`
   - `Current Completed Plans/`
   - `Current Unstarted Plans/`
   - `archives/`

2. Read each .md file. Parse tasks using rules below.

3. Calculate completion percentage.

4. **Auto-relocate**: `mv` 100% plans from Started to Completed. `mv` <100% plans from Completed back to Started. Report moves.

5. Write dashboard to `/foreverbox_data/council-library/docs/Current Reference Documentation/Plans Progression.md`.

6. Report summary: moves, percentage changes, new tasks.

## Task Detection Rules

1. **Checkboxes**: `- [x]` = Done, `- [ ]` = Not Done
2. **Inline status**: Headers ending `- DONE`/`- COMPLETE`/`- VERIFIED` = Done. `- NOT DONE`/`- BLOCKED`/`- PARTIALLY COMPLETE` = Not Done.
3. **Numbered headers** (### 1./Step/Stage): Check next 3 lines for status. Default: Not Done.
4. **AC criteria**: `- [x] AC-N:` = Done, `- [ ] AC-N:` = Not Done.

## Percentage

`% = (Done / Total) * 100`

Overall % counts Started + Unstarted only (not Completed or Archived).

## Pitfalls

- Only explicit Done counts. Partial/Blocked/In Progress = Not Done.
- Auto-relocation only between Started and Completed.
- Non-planning docs are not scanned.
