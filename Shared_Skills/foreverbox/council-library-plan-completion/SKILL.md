---
name: council-library-plan-completion
category: foreverbox
description: Completing and closing out Council Library planning documents — ticking task checkboxes, honest exception handling, sign-off tables, and regenerating the Plans Progression dashboard with the template-line exclusion the shared parser misses.
version: 1.0
---

# Council Library Plan Completion

Class-level skill for finishing a Council Library plan document after the work is
done: marking tasks complete, handling genuinely-impossible items honestly, updating
sign-off tables, and regenerating the Plans Progression dashboard.

## When to Use

- After executing a multi-phase plan (e.g. a project update plan), when the user says
  "complete all parts of the plan" or "tick everything off"
- Whenever a planning document in `Current Started Plans/` changes
- Before reporting a plan as complete

## Workflow

1. **Inventory first**: `grep -n "^- \[ \]" <plan.md>` to list every unchecked box.
   Many will already be done from execution — tick what is genuinely complete.
2. **Ticking script** (see `scripts/update_plan_ticks.py`): tick every `- [ ]` line
   EXCEPT:
   - **Template lines**: the Task Tracking Template at the bottom of most plans has
     example checkboxes (`- [ ] Criterion 1`, `- [ ] Criterion 2`,
     `- [ ] Test command / manual steps`, `- [ ] Expected output`). These are NOT
     tasks and must never count against completion — the shared
     `update-plans-progression` parser does NOT exclude them, so a plan with the
     template can never reach 100% and never relocate to Completed.
   - **Honest exceptions**: items that are impossible/not-applicable in this
     environment (e.g. "SSH to Wales Hub" external infra, "OWASP ZAP" when replaced
     by a focused scan, "Lighthouse > 90" with no headless Chrome). Keep them
     unticked and explain WHY in a Completion Note section — never silently tick
     something you didn't do.
3. **Sign-off table**: fill the Reviewed-by / Approved-by rows with the real dates
   and ✓. This is what turns the plan from "proposed" into "executed".
4. **Completion Note**: append a dated section stating status, git commits, the
   unticked exceptions and why, and any N/A items.
5. **Regenerate the dashboard**: run the engine in
   `scripts/regenerate_progression.py` (see below) — do NOT hand-edit
   `Plans Progression.md`.

## The Progression Dashboard Engine

The shared `update-plans-progression` / `plans-progression-dashboard` skills describe
the detection rules but ship no runnable script. Working implementation:
`scripts/regenerate_progression.py` — scans the four docs folders, parses checkboxes +
inline `- DONE` headers, auto-relocates 100% plans Started → Completed, and writes the
dashboard. Key behaviours beyond the documented rules:

- **TEMPLATE_LINES exclusion** (critical): the 4 template example lines above are
  stripped from task counting, otherwise template-bearing plans never reach 100%.
- **0/0 plans** (pure reference docs like user manuals, onboarding guides) count as
  100% so they don't drag the overall percentage down.
- Header inline status: `## Section - DONE` counts done; `- NOT DONE`/`- BLOCKED`/
  `- PARTIALLY COMPLETE` counts not done.
- Output: `Current Reference Documentation/Plans Progression.md` with per-plan table,
  overall %, and a Relocations section listing any moves.

## Verification

- `grep -c "^- \[x\]"` and `grep -c "^- \[ \]"` on the plan: expect ticked + unticked
  to match the reported totals; unticked should be exactly the exceptions + template
  lines.
- Dashboard shows the plan still in `Current Started Plans` at its true % (e.g.
  120/123 = 98%) when exceptions remain — it must NOT be relocated while <100%.
- The plan's sign-off table shows all three rows ✓.

## Pitfalls

- A time-window `DELETE FROM audit_log WHERE created_at > NOW() - INTERVAL ...`
  during verification cleanup also wipes legitimate backfill rows — scope by
  `entity_type`/`action`, or re-run `scripts/backfill_audit.php` afterwards.
- Ticking everything including impossible items reads as fabrication to the user;
  they explicitly value the honest exception note.
- The docs are a git repo too — offer to commit the updated plan/manual/blueprint
  after completion.

## Scripts

- `scripts/update_plan_ticks.py` — ticks completed items, preserves template lines +
  exceptions, updates sign-off, appends Completion Note
- `scripts/regenerate_progression.py` — dashboard engine (portable; run with plain
  `python3`, no deps)
