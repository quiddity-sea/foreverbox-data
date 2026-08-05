# Phase 2 Upgrades — Planned Transactions + Spend-Task Manager (verified 2026-08-01)

Condensed, verified patterns from implementing the Phase 2 Upgrades Plan on
Plutus (Blocks 1 and 2). Commits: `1b53773` (B1), `c83bbdb` (B2).

## Block 1 — Planned Transaction System (projected vs actual)

### Schema
```sql
ALTER TABLE transactions
    ADD COLUMN projected_amount DECIMAL(10,2) NULL AFTER amount,
    ADD COLUMN status ENUM('planned','spent') NOT NULL DEFAULT 'spent' AFTER projected_amount;
ALTER TABLE transactions MODIFY amount DECIMAL(10,2) NULL;  -- required: planned rows have no actual
```
Key semantic: a planned row has `amount = NULL, projected_amount = X, status='planned'`;
marking spent sets `amount = actual` and KEEPS projected_amount — both persist.
Backfill existing rows to `'spent'`.

### API wiring
- Register `projected_amount` + `status` in the entity's ALLOWED_SCHEMAS fields.
- **Budget totals (`updateBudgetTotals`) must filter `AND status = 'spent'`** — planned
  rows must never move cost_paid. Guard the two call sites in save() (update branch
  and insert branch) with `($_POST['status'] ?? 'spent') === 'spent'`.
- **Validation is create-only**: full required-field checks only when `!$id`.
  Partial updates (mark-spent sends only `id + status + amount`) must skip the base
  required list. On update, only enforce `amount` required when status flips to spent.
  Remove `amount` from the base transaction required list; add it conditionally.
- Dashboard: add `planned_total` (= `SUM(projected_amount) WHERE status='planned'`
  under the same dateFilter) and a `planned_transactions` array to the response.

### Frontend
- PLAN TRANSACTION button opens the universal modal, then swaps the amount input
  name to `projected_amount` and presets status (setTimeout ~150ms after open).
- MARK SPENT = `prompt()` for actual (projected prefilled) → `save_object` with
  `status=spent, amount=actual`.
- Planned panel renders below the transaction log when `planned_transactions` non-empty.

## Block 2 — Spend-Based Task Manager + Google Calendar

### Schema
```sql
ALTER TABLE tasks
    MODIFY COLUMN type ENUM('periodic_payment','event_planning','general','spend') NOT NULL DEFAULT 'general',
    ADD COLUMN projected_cost DECIMAL(10,2) NULL AFTER status,
    ADD COLUMN actual_cost DECIMAL(10,2) NULL AFTER projected_cost,
    ADD COLUMN spent_at DATETIME NULL AFTER actual_cost,
    ADD COLUMN recurrence_type ENUM('none','daily','weekly','biweekly','monthly','yearly') NOT NULL DEFAULT 'none' AFTER spent_at,
    ADD COLUMN recurrence_days VARCHAR(14) NULL AFTER recurrence_type,
    ADD COLUMN recurrence_time TIME NULL AFTER recurrence_days,
    ADD COLUMN recurrence_count INT UNSIGNED NULL AFTER recurrence_time,  -- NULL = continuous
    ADD COLUMN recurrence_completed INT UNSIGNED NOT NULL DEFAULT 0 AFTER recurrence_count,
    ADD COLUMN paused_at DATETIME NULL AFTER recurrence_completed,
    ADD COLUMN google_calendar_id VARCHAR(255) NULL AFTER google_event_id,
    ADD COLUMN google_recurring_id VARCHAR(255) NULL AFTER google_calendar_id;
```
Pitfall hit: the users google_* token columns ALREADY existed from earlier work —
check `information_schema.columns` before ALTER, the duplicate-column error is
harmless but noisy.

### TaskController actions (routes: complete_task / pause_task / resume_task / stop_task / google_auth / oauth_callback)
- `complete_task`: set actual_cost+spent_at+status='completed'; optionally INSERT
  a transaction with both amount and projected_amount (from task's projected_cost);
  recompute budget totals spent-only; increment recurrence_completed; if continuing
  (continuous OR completed < count), INSERT the next instance via `createNextInstance`
  with the next occurrence date.
- `nextOccurrence`: weekly-with-days walks the chosen weekdays strictly forward
  (diff 0 → 7); biweekly = +14d; monthly = +1 month; yearly = +1 year.
- `pause_task` sets paused_at + removes Google RRULE; `resume_task` clears +
  re-adds; `stop_task` sets cancelled + deletes Google series.
- Response helper takes ONE arg: use `http_response_code(404); response([...]);`.

### GoogleCalendarService (degrade-gracefully pattern)
- `isConfigured()` reads env `PLUTUS_GOOGLE_CLIENT_ID/SECRET` via private accessor
  methods (NOT `defined('X') ? X : ''` — PHPStan rejects that).
- Every method returns false/null when unconfigured so the rest of the app works
  without Google credentials. `google_auth` returns `GOOGLE_NOT_CONFIGURED`.
- OAuth: accessType=offline + prompt=consent; persist access/refresh/expiry on the
  user row; refresh transparently via fetchAccessTokenWithRefreshToken.
- Event create: RRULE builder (FREQ=WEEKLY;BYDAY=MO,TH + optional COUNT=N);
  store `events.insert()` id + recurringEventId. Recurrence-time events use
  EventDateTime with timezone; all-day use setDate.
- Composer dependency: `composer require google/apiclient:^2.15` (as www-data).
- External prerequisite (documented, NOT codable): Google Cloud project, OAuth
  client with redirect `https://<host>/api.php?action=oauth_callback`, consent
  screen, dedicated "Plutus" calendar. Until credentials exist, the code path is
  dormant — this is a legitimate plan exception to record, not a bug.

### Frontend
- ADD SPEND TASK: inline overlay form (title, projected cost, budget dropdown
  from `appState.metadata.budget`, recurrence type select, day checkboxes shown
  only for weekly, continuous checkbox toggling count input).
- Tasks panel rows: spend tasks get a £ badge + recurrence label
  (`WEEKLY THU 15:30`) + complete/pause/resume/stop icon buttons; calendar status
  indicator top-right (CONNECTED/DISCONNECTED from a google_auth probe).
- Pitfall: inline onclick strings inside single-quoted JS strings must not contain
  raw `$('#...')` — extract to a named helper (`closeSpendTask()`) to avoid
  quote-breaking SyntaxError.

## Block 1 Addendum — Planned Income (verified 2026-08-01, commit `c963f86`)

Planned income was storable (transaction `type` enum already had `income`) but the
dashboard summed ALL planned projected_amounts as spending. Fix:

- Dashboard splits by type: `planned_total` = planned EXPENSE only (kept backward
  compatible — the existing frontend panel reads it unchanged), new
  `planned_income_total` = planned INCOME. Helper: `plannedTotalByType($dateFilter, $type)`
  with `plannedTotalFor()` (expense) and `plannedIncomeFor()` wrappers.
- Personal/household branch: also filter the planned-total query by
  `t.type = 'expense'` (the planned_transactions array still returns both types —
  the frontend splits them).
- Frontend planned panel: IIFE split — `expenses` vs `incomes` filtered on `t.type`,
  two sub-tables (PLANNED SPENDING / PLANNED INCOME, income rows green with `+£`),
  header shows `NET +£x.xx (IN £y / OUT £z)`.
- Pitfall: when adding the income query to the personal/household branch, the
  original `$plannedTotal` query was REPLACED and the response still referenced it —
  PHPStan caught `Undefined variable: $plannedTotal`. Keep the expense query and
  add the income query alongside; both must be defined before the response.

## E2E coverage
- `e2e/planned.spec.js`: create planned tx → mark spent → verify both values → cleanup.
- `e2e/spendtasks.spec.js`: create weekly spend-task → complete (tx + next instance)
  → pause/resume/stop → cleanup. 7/7 suite passes.
- The two pitfalls that cost time here (CSRF regeneration after reload breaking
  cleanup; get_objects response shape being `data`) are in the parent SKILL.md.

## Verification recipe (ad-hoc, read-only)
php -l on changed controllers → node --check app.js → PHPUnit → PHPStan
(expect 0) → DB column presence via information_schema → curl live API actions
(with a throwaway `__` user for authenticated ones) → sync to staging (rsync +
db.php re-point) → smoke → playwright spec. Clean up `__` test rows and the
patch scripts afterwards.
