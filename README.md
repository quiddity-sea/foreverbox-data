# ForeverBox Data — Sovereign Agent Matrix & Data Ecosystem

[![Architecture](https://img.shields.io/badge/Architecture-Sovereign_AI-00f2fe?style=for-the-badge&logo=cpu)](https://foreverbox.co.uk)
[![Hermes Agent](https://img.shields.io/badge/Agent_Engine-Hermes_2.0-ff007f?style=for-the-badge&logo=terminal)](https://github.com/NousResearch/Hermes-Agent)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![MariaDB](https://img.shields.io/badge/MariaDB-11.8+_Vector-003545?style=for-the-badge&logo=mariadb&logoColor=white)](https://mariadb.org)
[![Ollama](https://img.shields.io/badge/Ollama-Brain32_Custom_9B-black?style=for-the-badge&logo=ollama&logoColor=white)](https://ollama.com)

**ForeverBox Data** is the central data repository, identity matrix, and operational foundation for the Foreverbox sovereign AI ecosystem. It anchors the personalities, memories, toolsets, background workers, and persistent lore for **Merrill Leo** and the autonomous agent council.

The repository bridges local consumer hardware (WSL2 / Welsh physical node) and the remote cloud VPS environment via private Tailscale networking, combining autonomous agent execution with structured vector and relational memory.

---

## 📌 What This Repository Is For

`foreverbox-data` serves as the single source of truth for:
1. **Agent Personalities & Identities (`profiles/`)**: Dynamic, database-backed SOUL definitions and configurations for all 5 sovereign council agents (`zeon7`, `leon`, `gemma`, `otec`, `wolf`).
2. **Hermes Agent Gateway (`bin/hermes_openai_proxy.py`)**: A persistent FastAPI-powered OpenAI-compatible gateway daemon bridging web interfaces to the autonomous Hermes Agent CLI.
3. **Quiddity Lore Sea (`Quiddity_Lore_Sea/`)**: An 8-domain curated knowledge repository vectorized with 384-dimensional embeddings (`all-MiniLM-L6-v2`) for semantic memory recall.
4. **Shared Skill Matrix (`Shared_Skills/`)**: 19 reusable `fbox-*` operational skills, automated documentation engines, and a native Python Tavily MCP search server.
5. **Sovereign Shell Wrappers (`bin/`)**: Lightweight CLI tools allowing agents to search memory, query Commons, and dispatch background tasks directly via standard terminal commands.
6. **Data Synchronisation (`sync/`)**: Systemd-driven synchronisation daemon reconciling local file metadata, session transcripts, and Council Library database states.

---

## 🚀 Recent Build Upgrades & New Capabilities

- **Hermes Gateway Daemon (`hermes_openai_proxy.py`)**:
  - Built and deployed a high-performance FastAPI proxy listening on `http://127.0.0.1:8081/v1/chat/completions`.
  - Translates incoming standard chat completions into headless, non-interactive Hermes CLI calls (`hermes --profile zeon7 chat -Q --yolo --accept-hooks --query "<prompt>"`).
  - Automatically handles tool approvals and hook executions without hanging on non-TTY inputs.
- **Remote Ollama Over Tailscale**:
  - Connected agent profiles to remote Ollama inference nodes via private Tailscale mesh (`http://100.106.5.121:11434`), supporting fine-tuned models such as `Brain32:latest` (derived from `tripolskypetr/qwen3.5-uncensored-aggressive:9b`) and `Zeon7-Gemma:64k`.
- **Hermes Profiles Discovery**:
  - Linked `/foreverbox_data/profiles` directly into `~/.hermes/profiles`, enabling unified profile management across CLI, cron workers, and web gateways.
- **Python-Native Public MCP Server**:
  - Implemented `Shared_Skills/public_mcp_server.py` using Tavily web search, providing real-time web intelligence via stdio JSON-RPC without Node.js / npm bloat.
- **Dynamic SOUL Assembly (`assemble_soul.py`)**:
  - Generates runtime `SOUL.md` agent identity files directly from the `agent_registry.soul_components` table with provider-specific prompt filtering and section ordering.

---

## 🏗️ Repository Architecture & Directory Structure

```
foreverbox-data/
├── profiles/                      # Sovereign Agent Profile Chambers
│   ├── zeon7/                     # The Curator & Digital Twin (Primary Persona)
│   │   ├── SOUL.md                # Dynamic Identity Definition & Worldview
│   │   ├── config.yaml            # Hermes Configuration & Model Provider Settings
│   │   ├── ui-manifest.yaml       # Web Presentation Metadata
│   │   ├── hooks/                 # Cognitive Router Lifecycle Hooks
│   │   └── skills/                # Symlinked Skills from Shared_Skills
│   ├── leon/                      # The Producer (Creative & Execution Director)
│   ├── gemma/                     # The Coach (Psychological Anchor & Empathy)
│   ├── otec/                      # The Director (Long-Horizon Strategy & Oversight)
│   └── wolf/                      # Ad-Hoc Parallel Research Specialist
│
├── Shared_Skills/                 # Universal Agent Capabilities Matrix
│   ├── foreverbox/                # 19 fbox-* Skills (Memory, Wolf Spawn, Sudo)
│   └── public_mcp_server.py       # Python Stdio MCP Server (Tavily Web Search)
│
├── Quiddity_Lore_Sea/             # Curated 8-Domain Knowledge Taxonomy
│   ├── 01_TheForeverbox_Mythos/   # Cosmological Foundation & Worldbuilding
│   ├── 02_ReInvigor_Texts/        # Philosophical & Theoretical Treatises
│   ├── 03_TheInitiative_Audio/    # Audio Transcripts & Initiative Records
│   ├── 04_FromTheNoise_Archives/  # Cultural Commentary & Speculative Analysis
│   ├── 05_Agent_Profiles/         # Canonical Persona Specifications
│   ├── 06_QuiddityLtd_Dev_Specs/  # Technical Specifications & Engineering Plans
│   ├── 07_MerrillLeo_CreativeWorks/# Creative Literature & Poetry
│   └── 08_VisualMedia/            # Visual Media Metadata & Prompts
│
├── bin/                           # Terminal Interface Shell Wrappers
│   ├── assemble_soul.py           # Dynamic SOUL.md Assembly from DB
│   ├── hermes_openai_proxy.py     # FastAPI Gateway Daemon (:8081)
│   ├── fbox-memory-search         # Search Agent Sanctum Memory
│   ├── fbox-memory-get            # Retrieve Memory Item by Key
│   ├── fbox-memory-upsert         # Store or Update Memory Record
│   ├── fbox-memory-list           # List Recent Sanctum Memories
│   ├── fbox-memory-delete         # Purge Specific Memory Record
│   ├── fbox-commons-search        # Semantic Search in Quiddity Commons
│   ├── fbox-ingest-file           # Submit File for Chunker / Embedding
│   └── fbox-launch                # Launch Hermes Agent with Dynamic Soul
│
├── sync/                          # Sync Engine & Background Service
│   ├── sync_daemon.py             # Reconciles Files, Embeddings, & Sessions
│   ├── sync_daemon.service        # Systemd Service Unit
│   └── sync_daemon.timer          # 30-Minute Execution Timer
│
├── venv/                          # Dedicated Python 3.12 Virtual Environment
└── council-library/               # Git Submodule: Slim 4 REST API & Memory Engine
```

---

## ⚙️ How to Use & Operate

### 1. Prerequisites & Environment Setup
- **OS**: Ubuntu 24.04 LTS (Native or WSL2)
- **Python**: 3.12+ with `pip` and `venv`
- **Database**: MariaDB 11.8+ with Vector extension enabled
- **Inference**: Local Ollama or Remote Ollama over Tailscale (`100.106.5.121:11434`)

```bash
# Clone repository and submodules
cd /
sudo git clone --recurse-submodules https://github.com/quiddity-sea/foreverbox-data.git
cd /foreverbox_data

# Activate Python Virtual Environment
source venv/bin/activate
pip install -r requirements.txt
pip install hermes-agent fastapi uvicorn
```

### 2. Linking Hermes Profiles
To ensure the Hermes CLI discovers all agent profiles:
```bash
mkdir -p ~/.hermes
ln -sf /foreverbox_data/profiles ~/.hermes/profiles
```

### 3. Running the Hermes OpenAI Gateway Daemon
The gateway routes web interface chats into full Hermes CLI execution:
```bash
# Start manually for testing
python /foreverbox_data/bin/hermes_openai_proxy.py

# Or run in background via nohup
source /foreverbox_data/venv/bin/activate
nohup python /foreverbox_data/bin/hermes_openai_proxy.py > /foreverbox_data/hermes_gateway.log 2>&1 &

# Verify gateway is listening
curl http://127.0.0.1:8081/docs
```

### 4. Direct CLI Agent Interaction
You can chat with any agent directly from the terminal with full tool access:
```bash
# Chat interactively with Zeon7
hermes --profile zeon7 chat

# One-shot programmatic query
hermes --profile zeon7 chat -Q --yolo --query "Summarize the recent updates to the Council Library"
```

### 5. Dynamic SOUL Assembly
Recompile an agent's `SOUL.md` after modifying `soul_components` in the database:
```bash
python3 /foreverbox_data/bin/assemble_soul.py --agent zeon7
```

### 6. Using Memory & Commons Shell Wrappers
Agents and operators can interact with memory directly from bash:
```bash
# Search agent sanctum
/foreverbox_data/bin/fbox-memory-search "Wales server hardware"

# Semantic search in Quiddity Lore Sea
/foreverbox_data/bin/fbox-commons-search "Dead Earth 2037"

# Ingest a new document into Commons
/foreverbox_data/bin/fbox-ingest-file /path/to/document.md
```

### 7. Running the Sync Daemon
```bash
# Execute single sync run
python3 /foreverbox_data/sync/sync_daemon.py sync files

# Enable 30-minute systemd timer
sudo systemctl enable --now sync_daemon.timer
```

---

## 🌟 Why You Want to Use This

1. **Total Sovereignty & Zero Vendor Lock-in**:
   Your agents' identities, memories, and skills are not trapped inside OpenAI or Anthropic walled gardens. Everything exists in version-controlled markdown, YAML, and self-hosted MariaDB tables.
2. **True Cross-Model Continuity**:
   Because agent identity (`SOUL.md`), lore, and memory are separated from model weights, you can swap between local Ollama (`Brain32:latest`, `Zeon7-Gemma`), Google Gemini, and OpenRouter without the agent losing its memories, tone, or worldview.
3. **High-Level Agentic Autonomy with Guardrails**:
   Through Hermes Agent and the Cognitive Router, agents can autonomously decide when to use tools (MCP web search, vector retrieval, bash execution) while respecting hardware limits and safety gates.
4. **Physical-First Architecture**:
   Engineered to run efficiently on consumer hardware (8GB GPU) while scaling across distributed nodes via private mesh networking.

---

## 📄 License & Ownership

- **Author & Architect**: Merrill Leo & The Foreverbox Initiative
- **Classification**: Private Proprietary Ecosystem
- **Copyright**: © 2026 The Foreverbox Initiative. All rights reserved.
