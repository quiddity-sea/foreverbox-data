---
name: service-user-webapp-operations
category: foreverbox
description: Operating and verifying PHP web apps deployed under the Apache service user (www-data) — file editing workflow, git as the service user, staging sync pitfalls, and the ad-hoc read-only verification pattern. Durable operational lessons from Plutus Phases 1-6.
version: 1.0
---

# Service-User Webapp Operations

Class-level skill for day-to-day operation of ForeverBox PHP webapps whose site
files are owned by the Apache service user (`www-data`), where the agent's own
user is NOT in the www-data group. Covers the edit workflow, git quirks, staging
sync, and the verification pattern that kept every phase honest.

## When to Use

- Editing any file under `/var/www/<site>/` owned by `www-data`
- Running git in a repo owned by `www-data`
- Syncing live → staging and re-pointing environment config
- Proving a multi-phase change is actually working (verification evidence)

## Editing www-data-owned files

Direct `patch`/`write_file` fail with Permission denied. Proven workflow:

1. Write a Python string-replace patch script in `/tmp`
2. `sudo cp /tmp/patch.py /var/www/<site>/.patch.py && sudo chown www-data:www-data .patch.py`
3. `sudo -u www-data python3 /var/www/<site>/.patch.py`
4. `sudo rm /var/www/<site>/.patch.py`

Notes:
- `/tmp` is unreadable to www-data — the script must live in the site dir while running.
- CRLF files (e.g. Plutus `assets/js/app.js`): normalise `\r\n`→`\n`, patch, restore, or the Python `\n`-only old-string silently MISSes.
- For PHP edits prefer `patch` scripts that assert the anchor exists (`if old not in content: print MISS`) so a shifted anchor is caught instead of silently skipped.
- Batch installs: `sudo cp` each file, then `sudo chown -R www-data:www-data` + `chmod 644` the whole set.

## Git as the service user

- Repos are `git init` as www-data, identity `quiddity-sea <lightweavers74@gmail.com>`, branch `main`.
- `git commit` may SUCCEED then a later `git log`/`status` fails with
  `fatal: detected dubious ownership` — check `git log` before assuming the commit failed.
- Fix once: create `/var/www/.gitconfig` (www-data's HOME is `/var/www`) owned by www-data:
  ```
  [safe]
      directory = /var/www/<site>
      directory = /var/www/<site>-staging
  ```
  `sudo -u www-data git config --global --add safe.directory` FAILS with
  "could not lock config file /var/www/.gitconfig: Permission denied" — create the
  file as root first, then git reads it.
- Do not run `git log`/`status` as the non-owner shell user (`zeon7`) on a
  www-data repo without the same safe.directory entry — that is a different user
  and will also trip dubious ownership. Always `sudo -u www-data git ...`.

## Staging sync pitfall

`rsync -a --exclude='.git' ... /var/www/<live>/ /var/www/<site>-staging/` copies
`db.php` OVER the staging pointer. After EVERY live→staging sync:

```bash
sudo sed -i "s/\$db = 'plutus_thoughts';/\$db = 'plutus_thoughts_staging';/" \
  /var/www/<site>-staging/db.php
sudo -u www-data bash /var/www/<site>/scripts/smoke_staging.sh   # expect 7/7
```

The smoke test's "anonymised data present" check is the leak guard — if it fails,
the sync overwrote db.php. Also re-apply any DB migrations to the staging DB and
re-deploy `dist/` (build output is excluded from the rsync but index.php references it).

## Verification pattern (ad-hoc, read-only)

There is no single canonical test command for the PHP/JS/Apache stack. Before
declaring work done, run a focused read-only verification covering exactly the
changed behaviour:

- `php -l` on every changed PHP file (correct paths — e.g. `api/bootstrap.php` is
  under `api/`, NOT `api/controllers/`)
- `node --check` on changed JS
- PHPUnit + PHPStan (`sudo -u www-data vendor/bin/phpunit`, `vendor/bin/phpstan analyse`)
- Vitest + `tsc --noEmit` (run from the build dir where node deps live)
- curl HTTP status checks on the live endpoints
- Playwright E2E against staging (`PLUTUS_BASE_URL=... npx playwright test`)

Save as `/tmp/hermes-verify-<topic>.sh`, run it, report PASS/FAIL counts, delete it.
State clearly it is ad-hoc verification, not a suite green.

## Build/test config pitfalls

- `tsc --noEmit` with `checkJs` FAILS on vitest test files (`global.fetch` mocks)
  — exclude `src/__tests__` and `src/types` in tsconfig; tests are covered by
  vitest's own runner.
- `npm install` of a new dev dependency can REMOVE an existing one (e.g. vitest
  install dropped typescript) — reinstall before re-running `npx tsc`.
- PHPStan level 5 on controllers: annotate globals with `/** @var PDO $pdo */`
  after the bootstrap require, drop unused properties, and never concatenate a
  `void` method return into a string (call it first, then use the buffer).

## Related Skills

- `foreverbox-project-development` — class-level project dev (architecture, security patterns)
- `council-library-plan-completion` — ticking plan checkboxes + progression dashboard
- `php-web-application-debugging` — debugging PHP DB apps

## References

- `references/plutus-operational-patterns.md` — session detail for Plutus specifics
