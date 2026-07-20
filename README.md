# foreverbox-data

Foreverbox ecosystem data — agents, skills, synchronisation, shell wrappers, and the Quiddity Lore Sea.

## Repository

```
foreverbox-data/
├── profiles/              # Agent profiles (leon, zeon7, gemma, otec, wolf)
│   ├── {agent}/SOUL.md   # Agent identity definition
│   ├── {agent}/config.yaml  # Hermes agent configuration
│   ├── {agent}/hooks/    # Cognitive Router hooks
│   └── {agent}/skills/   # Agent skill directories (symlinks to Shared_Skills)
├── Shared_Skills/         # Shared skills — access by all agents via symlinks
│   └── foreverbox/       # 19 fbox-* skills + documentation automation
├── Quiddity_Lore_Sea/     # 8-domain taxonomy with subfolders
│   ├── 01_TheForeverbox_Mythos/
│   ├── 02_ReInvigor_Texts/
│   ├── 03_TheInitiative_Audio/
│   ├── 04_FromTheNoise_Archives/
│   ├── 05_Agent_Profiles/
│   ├── 06_QuiddityLtd_Dev_Specs/
│   ├── 07_MerrillLeo_CreativeWorks/
│   └── 08_VisualMedia/
├── bin/                   # Shell wrappers (terminal() interface)
│   ├── fbox-memory-search
│   ├── fbox-memory-get
│   ├── fbox-memory-upsert
│   ├── fbox-memory-list
│   ├── fbox-memory-delete
│   ├── fbox-commons-search
│   └── fbox-ingest-file
├── sync/                  # Sync daemon (systemd timer, every 30 min)
│   ├── sync_daemon.py
│   ├── sync_daemon.service
│   └── sync_daemon.timer
└── council-library/       # PHP API, router, scripts, docs (submodule)
```

## Quiddity Lore Sea

12 files indexed, 594 vectorised chunks across 8 domains with 6 folder centroids.
Embedding model: all-MiniLM-L6-v2 (384 dimensions).

## Agent Identity

All 5 SOUL.md files include:
- Core identity and cosmological context
- Memory Operations (shell wrappers at /foreverbox_data/bin/)
- Wolf Protocol (Layer 1 Guard, fbox-wolf-spawn skill)
- Documentation Maintenance (Plans Progression + Reference Docs Log)

## Sync

Systemd timer syncs file metadata and session data to the council-library API
every 30 minutes. Manual run: `python3.12 sync/sync_daemon.py sync files`

## Environment

- Ubuntu 24.04 (WSL2)
- MariaDB 11.8.8
- Python 3.12
- Ollama (Zeon7-Gemma:64k for local agents and wolves)

## License

Private repository.
