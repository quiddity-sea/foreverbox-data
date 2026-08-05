---
name: otec-absorb
description: Transfer an agent's memory to Otec — additive only, never overwrites.
triggers:
  - "transfer my memories to Otec"
  - "copy my memories to Otec"
  - "add my memories to Otec"
  - "Otec absorb"
  - "otec-absorb"
---

# Otec Absorb

Transfer the calling agent's Hermes profile memories and Council Library Sanctum entries to Otec (agent_director). Always additive — read existing Otec entries first, merge, then write. Never overwrite or delete Otec's own memories.

## Step 1: Verify Otec's current state

```bash
# Check if Otec has a memories folder
ls /foreverbox_data/profiles/otec/memories/ 2>/dev/null || echo "No memories folder"

# Check Otec's Sanctum memory count
echo "SELECT COUNT(*) FROM agent_director.memory_lore;" | mariadb -u zeon7_user -p"F0reverb0x#2o26sql" -N
```

If Otec has NO memories folder, create one (mkdir). If Otec HAS existing MEMORY.md and USER.md, read both files first — new entries are appended below existing ones, separated by `§`.

## Step 2: Build the merged content

Read the calling agent's MEMORY.md and USER.md. Read Otec's existing files if they exist. Build the merged content:

- Otec's existing entries come FIRST (top of file)
- The calling agent's entries come SECOND (appended below)
- Separate blocks with `§` (section marker used by the Hermes memory formatter)
- Strip first-person language ("I prefer", "my conventions") — rewrite in neutral operational voice suitable for Otec
- Do NOT remove or alter any of Otec's existing entries

## Step 3: Write merged files

```bash
# Write the merged content — takes two arguments: file_path and merged_content
cat > /path/to/file << 'HEREDOC'
[merged content with Otec's original entries first, then new entries]
HEREDOC
```

Use `write_file(cross_profile=True)` to write to `/foreverbox_data/profiles/otec/memories/MEMORY.md` and `/foreverbox_data/profiles/otec/memories/USER.md`.

## Step 4: Copy Sanctum entries

Only copy the calling agent's own entries (WHERE agent_slug = '<calling_agent>'):

```sql
INSERT INTO agent_director.memory_lore 
(agent_slug, namespace, key_name, content_json, content_text, source_type, source_ref, importance, tags)
SELECT 'director', namespace, key_name, content_json, content_text, source_type, source_ref, importance, tags
FROM <calling_agent_db>.memory_lore
WHERE agent_slug = '<calling_agent_slug>'
AND NOT EXISTS (
    SELECT 1 FROM agent_director.memory_lore
    WHERE agent_director.memory_lore.key_name = <calling_agent_db>.memory_lore.key_name
    AND agent_director.memory_lore.namespace = <calling_agent_db>.memory_lore.namespace
);
```

The NOT EXISTS clause prevents duplicate entries if the same memory was already transferred in a previous absorb.

## Step 5: Confirm

Report what was added:
- X new entries appended to Otec's MEMORY.md
- Y new entries appended to Otec's USER.md
- Z new Sanctum entries added to agent_director.memory_lore
- N entries skipped (already present — no duplicates)

## Pitfalls

- Never use a simple `cp` — this overwrites Otec's existing files
- Never use `INSERT ... SELECT` without the NOT EXISTS guard — creates duplicates on re-absorb
- The calling agent's voice and phrasing must be neutralised. Otec is a director, not a copy of the calling agent
- Cross-profile writes require `cross_profile=True`
- Always read Otec's existing files FIRST before merging, even if you think the folder is empty
