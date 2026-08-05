---
name: wsl-environment-setup
description: Configuration and troubleshooting for Windows Subsystem for Linux environments, particularly for AI/ML development workloads
version: 1.0
author: Leon
---

# WSL Environment Setup and Troubleshooting

## Overview
This skill provides guidance for configuring and troubleshooting Windows Subsystem for Linux (WSL) environments, particularly for AI/ML development workloads like CUDA-based compilations.

## Key Principles
- Validate WSL configuration syntax before applying
- Memory settings must leave sufficient resources for Windows host
- CUDA compilation in WSL can trigger OOM killer due to memory spikes
- Prefer direct execution over delegation for iterative troubleshooting tasks
- Poll long-running operations at appropriate intervals (60+ seconds)

## WSL Configuration (.wslconfig)

### Correct Syntax
```ini
[wsl2]
memory=12GB          # Leave 4GB+ for Windows host on 16GB systems
swap=16GB            # Provides overflow for memory spikes
processors=6         # Use specific number, not "all" 
networkingMode=mirrored
```

### Common Mistakes to Avoid (Learned from Session)
- ❌ `processors=all` - Invalid value, must be specific number (corrected to 6 based on CPU count)
- ❌ `sparseVhd=true` - Not a valid wsl2 setting (removed after user correction)
- ❌ `autoMemoryReclaim=gradual` - Not a valid wsl2 setting (removed after user correction)
- ❌ Excessive memory allocation that starves Windows host

### Memory Guidelines
| Total RAM | WSL Memory | Swap Size | Notes |
|-----------|------------|-----------|-------|
| 16GB      | 12GB       | 16GB      | Leaves 4GB for Windows |
| 32GB      | 24GB       | 24GB      | Adjust based on workload |
| 64GB+     | 32-48GB    | 24-32GB   | More flexible allocation |

## Networking: Stale Windows Hosts Entries After WSL Restart

### Symptom
Sites served by Apache inside WSL time out from the Windows browser (`curl https://site.invigor.com` hangs), while local tests inside WSL return HTTP 200 instantly. Apache itself is healthy.

### Root Cause (hit in session)
The Windows hosts file (`C:\Windows\System32\drivers\etc\hosts`, mounted at `/mnt/c/Windows/System32/drivers/etc/hosts`) maps invigor.com subdomains to the **old WSL NAT IP** (e.g. `172.20.235.245`). After changing `.wslconfig` (`networkingMode=mirrored`) and running `wsl --shutdown`, WSL gets a new IP, so the old address is dead. DNS resolution inside WSL forwards through Windows and picks up the stale hosts entry, so even WSL-side curls to the hostname time out.

### Diagnosis
```bash
# 1. Show what the hostname resolves to (stale IP = smoking gun)
getent hosts plutus.invigor.com          # -> 172.20.235.245 (old NAT IP)

# 2. Show current WSL interfaces
ip -4 addr show                          # -> 10.2.0.2, 192.168.0.31, etc.

# 3. Test Apache locally bypassing DNS
curl -sk -o /dev/null -w "%{http_code} in %{time_total}s\n" \
  --resolve plutus.invigor.com:443:127.0.0.1 https://plutus.invigor.com/

# 4. Read the Windows hosts file
grep -i invigor /mnt/c/Windows/System32/drivers/etc/hosts
```

### Fix
Update the Windows hosts file to point the subdomains at `127.0.0.1` (with mirrored networking, WSL's Apache is reachable on localhost from Windows). Requires explicit user approval before editing a Windows system file:
```
127.0.0.1 merrills-notebook.invigor.com
127.0.0.1 the-foreverbox-institute.invigor.com
127.0.0.1 plutus.invigor.com
```

**How to actually edit the Windows hosts file from WSL (hit in session):** the file is read-only in the WSL mount and `chmod`/direct write fail with Permission denied. The working method is an elevated PowerShell script launched via UAC:
```bash
# 1. Write the .ps1 to WSL /tmp, then COPY it to a Windows-visible temp path.
#    (A script left only in /tmp is NOT reachable from powershell.exe by Windows path.)
cp /tmp/fix_hosts.ps1 /mnt/c/Users/<user>/AppData/Local/Temp/fix_hosts.ps1

# 2. Launch it elevated — this pops a UAC prompt on the Windows desktop the user must approve.
powershell.exe -NoProfile -Command "Start-Process powershell -Verb RunAs -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File','C:\Users\<user>\AppData\Local\Temp\fix_hosts.ps1'"
```
The .ps1 should back up the file (`Copy-Item $hosts "$hosts.bak.YYYYMMDD" -Force`) before editing, then `-replace` the stale IP with `127.0.0.1` and `Set-Content $hosts $content -Encoding ASCII`. Verify afterwards by re-reading `/mnt/c/Windows/System32/drivers/etc/hosts`.

Also check vhost routing: `http://localhost/the-foreverbox-institute/self.php` 404s when the default vhost's DocumentRoot is elsewhere (e.g. `/mnt/c/projects/www/zeon7`) — the Foreverbox site is served by its own vhost hostname, not the default.

### General Rule
After ANY WSL networking/config change that restarts the instance, verify that Windows hosts entries still match the current WSL IP before debugging web services. Changing `.wslconfig` networking mode invalidates hosts-file IPs.

## CUDA Build Troubleshooting in WSL

### Common Issues Encountered
1. **nvcc terminated by OOM killer**: CUDA compiler has extreme memory spikes during template instantiation
2. **Missing directory errors**: Build process expects directories that don't exist
3. **Assembler failures**: Often secondary to memory allocation issues

### Workarounds Discovered
1. **Increase swap significantly**: 1.5x-2x RAM size for build workloads
2. **Reduce build parallelism**: Use `-j1` instead of `-j$(nproc)` to limit memory pressure
3. **Verify directory structure**: Create expected directories before building
4. **Consider CPU-only fallback**: For immediate needs when GPU build persistently fails

### Validation Steps
1. Check WSL memory allocation: `free -h`
2. Verify swap usage: `swapon --show`
3. Monitor build process with appropriate polling intervals
4. Check exit codes and error messages carefully

## Polling Best Practices (Learned from Session)

### For Long-Running Operations
- Use 60+ second intervals for compilation/build monitoring (user correction: "only poll every 60 seconds")
- Avoid frequent polling that adds overhead
- Combine with timeout mechanisms to prevent infinite waits

### Implementation Pattern
```
# Instead of rapid polling (which we initially did incorrectly)
while [ condition ]; do
  sleep 60  # Wait appropriate interval as per user correction
  check_status
done
```

## Direct Work Preference
For iterative troubleshooting tasks (like WSL configuration or build debugging):
- Perform actions directly rather than delegating
- Provide immediate feedback on each attempt
- Adjust approach based on real-time results
- Maintain context throughout the troubleshooting process

## Sudo Session Caching (Hermes terminal calls, hit 2026-07-31)

### Symptom
The user types their sudo password once (via a PTY `sudo -v`) expecting it to stay
cached "for this whole session", but the very next `terminal()` call fails with
`sudo: a password is required` — even when run with `pty=true` again.

### Root Cause
Each Hermes `terminal()` call opens a fresh shell/TTY. Sudo's credential timestamp
is TTY-scoped by default, so a password typed in one call's PTY does NOT carry over
to the next call. `sudo -v` returning exit 0 only proves the password was accepted
on that specific TTY.

### Fix (the reliable pattern)
A session-wide (or permanent) sudoers drop-in is the only thing that persists across
Hermes terminal calls:

```bash
# One-time setup (user runs this, or approves it):
echo 'zeon7 ALL=(ALL) NOPASSWD:ALL' | sudo tee /etc/sudoers.d/zeon7-session
sudo chmod 440 /etc/sudoers.d/zeon7-session

# Verify it works non-interactively:
sudo -n true && echo "SUDO CACHED OK"

# Remove when done (if it was meant to be temporary):
sudo rm /etc/sudoers.d/zeon7-session
```

Then `sudo` works non-interactively from ANY subsequent terminal call without
prompts. Note: with this in place, expect the security scanner to flag
`sudo`/`sudo bash -c` commands more aggressively (nested-shell and privilege-flag
warnings) — they are auto-approvable but the user may still see prompts; retry
once if they say they missed the prompt.

### Related
The elevated-PowerShell UAC route (hosts-file edits, see above) is a DIFFERENT
credential domain — sudoers drop-ins do not cover Windows-side elevation.

## Cleanup Procedures
After failed builds or experiments:
1. Remove build directories: `rm -rf /path/to/build`
2. Clean up downloaded artifacts: `rm -f /path/to/downloaded/files`
3. Verify cleanup: `find /home/username -name "*project-name*" -type d`
4. Confirm disk space recovery

**Scope discipline (user correction, hit in session):** when the user says "clean up everything, do not do anything else", obey the scope literally. Do NOT create example folders, demo directories, or scaffolding while explaining the next step — the user checks for stray artifacts (e.g. `/home/<user>/ollama_models/` created as an "example" during a cleanup-only instruction, then had to be deleted). If a demonstration requires a directory, say so in text only; do not create it. Model files belong in the shared Ollama store, never in home directories (see `local-model-ollama-context`).

## Verification
After applying WSL configuration changes:
1. Fully restart WSL: `wsl --shutdown` from PowerShell
2. Reload Linux distribution
3. Verify settings: `cat /proc/meminfo | grep -E "MemTotal|SwapTotal"`
4. Test with representative workload before committing to large builds