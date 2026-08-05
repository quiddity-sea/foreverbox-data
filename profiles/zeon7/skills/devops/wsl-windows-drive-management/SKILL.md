---
name: wsl-windows-drive-management
category: devops
description: Mount, repair, and manage Windows drives from WSL2. Covers drvfs mounting, chkdsk repair, PowerShell command invocation, and background monitoring of long-running Windows processes.
---

# WSL Windows Drive Management

Class-level skill for mounting, repairing, and managing Windows drives from within WSL2.

## Triggers
- User asks to access a Windows drive (D:, E:, etc.) from WSL
- Windows drive shows corruption/unreadable directories in WSL
- Need to run Windows filesystem repair (chkdsk) from WSL
- Long-running Windows commands that need background monitoring

## Core Workflows

### 1. Mount a Windows Drive in WSL
```bash
sudo mkdir -p /mnt/<letter>
sudo mount -t drvfs <LETTER>: /mnt/<letter>
```
- `drvfs` is the WSL filesystem driver for Windows volumes
- Mount point must exist first
- Requires sudo

### 2. Run Windows Commands from WSL
```bash
powershell.exe -Command "<command>"
```
- Use for chkdsk, Get-ChildItem, Get-Process, etc.
- Escape quotes carefully: `powershell.exe -Command "chkdsk D: /f /r /x"`
- For interactive prompts, use `/x` flag to force dismount (chkdsk) or pipe `echo Y |`

### 3. Repair Corrupted NTFS Volume (chkdsk)
```bash
powershell.exe -Command "chkdsk <LETTER>: /f /r /x"
```
Flags:
- `/f` — fix errors on disk
- `/r` — locate bad sectors and recover readable info
- `/x` — force dismount first (implies `/f`)

**Stages:** 1=file records, 2=indexes, 3=security descriptors, 4=file data, 5=free space. Stage 3 (orphan recovery) can take hours on large drives.

### 4. Background Monitor Long-Running Windows Process
```bash
# Start monitor in background
terminal(command="while powershell.exe -Command 'Get-Process <name> -ErrorAction SilentlyContinue' 2>&1 | grep -q <name>; do echo 'still running...'; sleep 30; done; echo 'finished'", background=true, notify_on_complete=true)

# Poll for status
process(action="poll", session_id="<id>")
```
- Use `Get-Process <name> -ErrorAction SilentlyContinue` to check existence
- Poll every 30-60s for chkdsk (can run hours)
- `notify_on_complete=true` delivers result when process exits

## Pitfalls & Gotchas
- **Mount fails after chkdsk dismounts**: Remount with `sudo mount -t drvfs D: /mnt/d` after chkdsk completes
- **PowerShell command parsing**: WSL bash mangles quotes; keep PowerShell commands simple, avoid nested quotes
- **"Invalid argument" on ls**: Directory is corrupted at filesystem level — chkdsk required
- **chkdsk "volume in use"**: Use `/x` to force dismount; all open handles invalidated
- **Background process tcsetattr noise**: Harmless terminal warning, process still runs

## Verification Steps
1. After mount: `ls -la /mnt/<letter>/`
2. After chkdsk: `powershell.exe -Command "Get-ChildItem '<LETTER>:\<folder>' -Force"`
3. If still unreadable: re-run chkdsk or check hardware (SMART, USB controller)

## References
- `references/chkdsk-stages.md` — stage breakdown and time estimates
- `references/powershell-from-wsl.md` — quoting/escaping patterns
- `scripts/mount-win-drive.sh` — idempotent mount helper
- `scripts/watch-win-process.sh` — reusable background monitor