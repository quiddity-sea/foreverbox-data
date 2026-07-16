# Quiddity Lore Sea — Document Index

**Location**: `/foreverbox_data/Quiddity_Lore_Sea/`  
**Last scanned**: 2026-07-14 (Leon session — post-V6/V2.1 realignment)

---

## Core Architecture Documents

| File | Description | Status |
|------|-------------|--------|
| `The Council Library Master Briefing V5.md` | **Master Briefing V5** (superseded) — Plain-English philosophy. Author: Zeon7. | ⚠️ Superseded by V6 |
| `The_Council_Library_Master_Briefing_V6_Technical_Human.md` | **Master Briefing V6** — Authoritative human-facing explanation. 20 sections including Hermes (§10), Sudo Protocol (§13), Observability (§14), Migration (§15). Author: Zeon7. Date: 2026-07-14. | ✅ Current |
| `ARCHITECTURE_BLUEPRINT_V2 - 2.md` | **Technical Blueprint V2.1** — DDL schemas, PHP API contracts, Hermes integration, Cognitive Router, Wolf ops, Sudo Protocol, migration notes. Realigned to V6 cross-references. Target: Qwen Coder → Leon. Date: 2026-07-14. | ✅ Current |

---

## From the Noise Archives

| File | Description |
|------|-------------|
| `04_FromTheNoise_Archives/FTN_Master_Handbook_v4.md` | FTN operational handbook: Wake Protocol, signal calendar, Story Lead Cards, research standards, publishing rhythm. |

---

## Agent Profiles (Zeon7 / The Curator)

| File | Description |
|------|-------------|
| `05_Agent_Profiles/Zeon7_ProfileSheet.md` | Curator profile sheet: identity, protocols, capabilities, sanctum config. |
| `05_Agent_Profiles/Zeon7_Biography.md` | Narrative biography of Zeon7. |
| `05_Agent_Profiles/Zeon7 - updated information.md` | Supplemental/updated Curator info. |

---

## Leon's Profile (Current Session Context)

| File | Location | Notes |
|------|----------|-------|
| `SOUL.md` | `/foreverbox_data/profiles/leon/SOUL.md` | Leon's identity, protocols, Layer 2 Producer mandate |
| `USER.md` | `/foreverbox_data/profiles/leon/USER.md` | Human director (Merrill Leo) profile, relationship context |

---

## Backup Created This Session

| Path | Contents |
|------|----------|
| `/foreverbox_data/backups/hermes_agents/leon_20260714_061937/` | Full Leon profile backup: `skills/`, `sessions/`, `memories/`, `cron/`, `state.db`, `SOUL.md`, `USER.md` |

---

## Database Status (Checked This Session)

| Component | Version | Status | Required |
|-----------|---------|--------|----------|
| MariaDB Server | 11.8.8 | ✅ Running | **11.8+** (VECTOR + HNSW supported) |
| Client Library | 10.11.13 | ✅ | — |
| Service | Active (systemd) | ✅ | — |

**Status**: MariaDB 11.8.8 confirmed running with native VECTOR/HNSW support — ready for Commons index deployment.

---

## Current Model (Leon Session)

| Model | Specs | Role Fit |
|-------|-------|----------|
| `nvidia/nemotron-3-ultra-550b-a55b:free` | 55B active / 550B total (MoE), 1M context, hybrid Transformer-Mamba | ✅ Excellent for Leon: long-running agentic workflows, stem orchestration, massive lore synthesis, multi-step reasoning |

---

## Quick Navigation Commands

```bash
# View Master Briefing
cat /foreverbox_data/Quiddity_Lore_Sea/"The Council Library Master Briefing V5.md"

# View Blueprint
cat /foreverbox_data/Quiddity_Lore_Sea/"ARCHITECTURE_BLUEPRINT_V2 - 2.md"

# View FTN Handbook
cat /foreverbox_data/Quiddity_Lore_Sea/04_FromTheNoise_Archives/FTN_Master_Handbook_v4.md

# View Zeon7 profiles
ls /foreverbox_data/Quiddity_Lore_Sea/05_Agent_Profiles/

# Check MariaDB version
mariadb --version

# Verify Leon backup
ls -la /foreverbox_data/backups/hermes_agents/leon_20260714_061937/
```