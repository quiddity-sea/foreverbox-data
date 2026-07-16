---
name: fbox-council-library-cli
description: Manage the Council Library sovereign memory system via the CLI. Install/uninstall/enable/disable/services/status/doctor.
---

# Council Library CLI

Manage the Council Library sovereign memory architecture — databases, API, embedding service, ingestion workers, wolf workers, and Hermes plugin integration.

## Usage

The binary lives at `/foreverbox_data/council-library/bin/council-library`.

```bash
./bin/council-library [command]
```

## Commands

### install

Bootstrap the entire system or specific agent components.

```bash
# Full installation — all 4 agents
./bin/council-library install --all

# Single agent
./bin/council-library install --agent curator

# Skip systemd unit creation
./bin/council-library install --all --no-systemd
```

Steps run (each idempotent):
1. MariaDB schema (Commons, Sanctums, Registry, Director)
2. Token budget seed
3. Config files (foreverbox.json per profile)
4. Plugin installation (symlink into Hermes profiles)
5. Apache vhost on port 8080
6. Embedding model (sentence-transformers)
7. Systemd user units (council-embedding, council-ingestion, council-wolves)

### uninstall

Reverse installation. Default drops databases.

```bash
# Full removal
./bin/council-library uninstall

# Preserve databases
./bin/council-library uninstall --keep-data
```

### enable / disable

Start or stop all background services.

```bash
./bin/council-library enable
./bin/council-library disable
```

### status

Health check every component. Returns exit code 0 if healthy, 1 if degraded.

```bash
./bin/council-library status
```

### doctor

Diagnose issues and suggest fixes. Unlike status, doctor tests beyond simple reachability — checks vector indexes, permissions, config validity.

```bash
./bin/council-library doctor
```

## Quick install

```bash
# One-liner from the repo root
chmod +x bin/council-library && ./bin/council-library install --all && ./bin/council-library status
```

## Environment

The CLI reads `DB_PASS` from the environment. Set it before running if not using the default:

```bash
export DB_PASS="your_password"
./bin/council-library install --all
```

## Pitfalls

- `install --all` is idempotent — safe to re-run. Existing databases and configs are left intact.
- **`install --agent` does NOT install the CLI skill, model config, or sync router.yaml.** The installer handles infrastructure only (DB, plugin, foreverbox.json, .env, Apache, systemd). After install, manually verify all 8 items in the agent provisioning checklist (see `fbox-operations` skill, Procedure 11): model section in config.yaml, router.yaml sync, cognitive_router hook, CLI skill copy, and SOUL.md first-person directive.
- `uninstall` without `--keep-data` permanently drops all 6 databases. Always back up first.
- Apache needs `sudo`. The CLI handles this internally but you may be prompted for your password.
- Embedding model download (~2 GB) happens on first install. Subsequent installs skip this.
- Homebrew Python (`python3`) is 3.14 but the CLI explicitly uses `/usr/bin/python3.12` for systemd units — this is correct for Ubuntu 24.04.
- Passwords containing `#` must be quoted in `.env` files (`DB_PASS="value#hash"`) AND must use `EnvironmentFile=` in systemd units — never put them in `Environment=` directives. Both `.env` and systemd treat `#` as a comment delimiter.
