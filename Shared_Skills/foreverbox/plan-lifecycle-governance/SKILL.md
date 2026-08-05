---
name: plan-lifecycle-governance
description: Council Library plan lifecycle governance — when a plan may move from Started to Completed, how to report completion honestly, and the user-approved sign-off gate. Use after implementing a plan's tasks or regenerating the Plans Progression dashboard.
---

# Skill: Plan Lifecycle Governance

## Purpose

Governs how plans move through the Council Library lifecycle: Started → Completed. Encodes the rule that implementation completion is NOT review completion.

## The Core Rule

A plan with 100% task tickboxes is *implementation-complete*, NOT *reviewed-complete*.
The sign-off table (Reviewed by / Approved by) is the authoritative gate: if Merrill
has not signed off, the plan stays in `Current Started Plans/` even at 100%.

- Do NOT move a plan to `Current Completed Plans/` on your own.
- Do NOT let the progression dashboard generator auto-move it either — the generator
  script must have NO auto-relocation logic.
- Moving to Completed happens ONLY after Merrill has tested the work and explicitly
  approved the move.
- If a plan in Completed Plans drops below 100%, moving it back to Started is also
  Merrill's decision, not the script's.

## Origin

2026-08-01: the Phase 2 upgrades plan was auto-moved to Completed at 100% before
Merrill tested it. His correction: "why have you moved it to compleated before I
have tested it". Fix applied: reverted the move, kept the plan in Started Plans,
and disabled auto-relocation in the dashboard generator.

## Reporting Completion Honestly

When reporting that a plan is "done":

1. Distinguish implementation-complete (tickboxes ticked, tests pass) from
   reviewed-complete (Merrill has used it and approved).
2. State which exceptions remain unticked and WHY (external infra, tool not run,
   credentials pending) — never silently tick around them.
3. Keep the plan in Started Plans until sign-off; say so explicitly in the report.

## Pitfalls

- The `plans-progression-dashboard` / `update-plans-progression` skills historically
  described auto-relocation on 100% — that behaviour was removed after the correction.
- Automated tests passing (E2E, PHPUnit, PHPStan) are NOT user acceptance. Merrill's
  in-browser testing and sign-off are the only valid gate to Completed.
