---
name: reference-doc-alteration-log
description: Updates the Reference Docs Log.md file after any reference document is added, updated, or removed from the Current Reference Documentation folder. Determines whether a change is small or large by comparing content size and checking for version number changes. Run this after any modification to a reference doc.
---

# Skill: Reference Doc Alteration Log

## Purpose

This skill maintains a chronological log of all changes to reference documents in the `Current Reference Documentation` folder. It records the filename, action (added, updated, removed), the agent who made the change, the change type (small or large), and relevant details.

## When to Run

Run this skill after ANY change to a reference document:
- A new reference doc is created or added to the folder
- An existing reference doc is updated (content changed)
- A reference doc is moved out of the folder or deleted
- A reference doc is replaced with a new version (e.g. V2 to V3)
- A reference doc is renamed

## Change Classification Rules

### Large Change
A change is classified as **Large** if ANY of the following are true:
1. **Version number change**: The filename or document header contains a version number that has incremented (e.g. V2 to V3, V1 to V2). This is always a large change regardless of content size.
2. **Content delta > 20%**: The content of the file has changed by more than 20% compared to the last logged state. This is calculated as:
   ```
   change_ratio = abs(new_size - old_size) / max(old_size, 1)
   If change_ratio > 0.20: Large
   ```

### Small Change
A change is classified as **Small** if ALL of the following are true:
1. No version number change in the filename or document header
2. Content delta is 20% or less of the previous file size

### Baseline
When a document is first registered in the log (either because it pre-exists the logging system or because it was just created), it is logged as a **Baseline** entry with action "Added (baseline)".

## How It Works

### Step 1: Determine the Agent Identity

The agent running this skill identifies itself by its profile name. This is the "Who" column. Common values:
- Leon (producer profile)
- Zeon7 (curator profile)
- Gemma (coach profile)
- Otec (director profile)

### Step 2: Read the Current Log

Read the existing log file:
```
/foreverbox_data/council-library/docs/Current Reference Documentation/Reference Docs Log.md
```

### Step 3: Determine the Change

For the file being logged:

1. **Check if the file is new** (not previously in the log):
   - If new: Action = "Added", Change Type = "Baseline" (if first registration) or "Large" (if it is a new document with significant content)

2. **Check if the file was removed**:
   - If the file no longer exists in the folder but was in the log: Action = "Removed", Change Type = "N/A"

3. **Check if the file was updated**:
   - If the file exists and was previously logged: Action = "Updated"
   - Compare the current file size to the last logged size for this filename
   - Check for version number changes in the filename or document header (look for patterns like V1, V2, V3, v1, v2, v3, Version 1, Version 2)
   - Apply the classification rules above to determine Small vs Large

### Step 4: Calculate Content Delta

To calculate the percentage of content that has changed:

1. Read the current file size in bytes: `new_size`
2. Find the last log entry for this filename and extract the previously recorded size: `old_size`
3. Calculate:
   ```
   change_ratio = abs(new_size - old_size) / max(old_size, 1)
   ```
4. If `change_ratio > 0.20`: Large change
5. If `change_ratio <= 0.20` AND no version number change: Small change

**Important**: The skill should store the file size (in bytes) in the Details column so that future runs can compare against it. Format: `size:NNNN bytes`

### Step 5: Check for Version Changes

Scan the filename and the first 20 lines of the document for version patterns:
- `V1`, `V2`, `V3`, `V4`, `V5`, `V6` etc.
- `v1`, `v2`, `v3` etc.
- `Version 1`, `Version 2` etc.
- `VERSION 1.0`, `VERSION 2.0` etc.

If the version number in the current file is higher than the version number in the last logged entry for this filename, it is a Large change regardless of content delta.

### Step 6: Append to the Log

Append a new row to the table in `Reference Docs Log.md`:

| Date | Filename | Action | Agent | Change Type | Details |

- **Date**: ISO format (YYYY-MM-DD), or include time if precision is needed (YYYY-MM-DD HH:MM)
- **Filename**: Just the filename, not the full path
- **Action**: "Added", "Added (baseline)", "Updated", "Removed", "Moved"
- **Agent**: The profile name of the agent making the change
- **Change Type**: "Baseline", "Small", "Large", "Large (version change)", "N/A"
- **Details**: Include file size and any relevant notes. Format: `size:NNNN bytes; [additional notes]`

### Step 7: Report

After updating the log, report to the user:
- What was logged
- The change type determination
- The file size and delta percentage if applicable

## Execution Steps

When invoked, the agent should:

1. **Identify itself** (which profile am I running as?)

2. **Read the current log**:
   ```
   read_file("/foreverbox_data/council-library/docs/Current Reference Documentation/Reference Docs Log.md")
   ```

3. **Determine what changed**:
   - What file was added, updated, or removed?
   - What is the current file size?
   - What was the previous file size (from the log)?
   - Has the version number changed?

4. **Classify the change** using the rules above.

5. **Append the new entry** to the log table using `patch` or `write_file`.

6. **Report** the result.

## Example Log Entries

```
| 2026-07-20 | COUNCIL_LIBRARY_HANDBOOK_V1.md | Updated | Leon | Small | size:21095 bytes; 3 lines changed in troubleshooting section |
| 2026-07-20 | ARCHITECTURE_BLUEPRINT_V3.md | Updated | Leon | Large (version change) | size:125000 bytes; V3 to V4; complete rewrite of ingestion pipeline section |
| 2026-07-21 | NEW_SECURITY_SPEC.md | Added | Zeon7 | Baseline | size:8500 bytes; new security specification document |
| 2026-07-22 | Souls Configuration Canvas - V2.md | Removed | Leon | N/A | size:9577 bytes; superseded by V3 |
```

## Pitfalls

- **File size is a proxy, not a perfect measure**: A file could have 50% of its content rewritten but end up the same size. The 20% size delta rule is a heuristic. If the agent knows the change was substantial (e.g. a full section rewrite), it should override the size-based classification and mark it as Large.
- **Version numbers in headers vs filenames**: Some docs have version numbers in the filename (e.g. `MASTER_BRIEFING_V6.md`), others have it in the document header (e.g. `# Version 6`). Check both locations.
- **Baseline entries**: When the logging system is first deployed, all existing reference docs are logged as "Added (baseline)". This is a one-time operation. Do not re-log them as baselines on subsequent runs.
- **Removed files**: When a file is removed, log it as "Removed" with the last known file size. Do not delete the file's historical log entries.
- **Moved files**: If a file is moved from one folder to another (e.g. from Current Started Plans to Current Reference Documentation), log it as "Moved" and note the source and destination.
- **Non-reference docs**: Only log files in the `Current Reference Documentation` folder. Do not log changes to planning docs (those are tracked by the `update-plans-progression` skill).
- **Manual edits**: If a human manually edits the log file, do not overwrite their changes. The skill appends new entries; it does not rewrite the entire file.
