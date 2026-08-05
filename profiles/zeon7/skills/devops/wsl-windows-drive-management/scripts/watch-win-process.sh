#!/usr/bin/env bash
# watch-win-process.sh — Background monitor for Windows processes from WSL
# Usage: watch-win-process.sh <process-name> [poll-interval-seconds]
#   process-name: exact process name as seen by Get-Process (e.g., chkdsk, notepad)
#   poll-interval: seconds between checks (default: 30)
#
# Returns exit code 0 when process exits, prints "finished" to stdout
# Designed for use with terminal(background=true, notify_on_complete=true)

set -euo pipefail

proc_name="${1:-}"
interval="${2:-30}"

if [[ -z "$proc_name" ]]; then
    echo "Usage: $0 <process-name> [poll-interval-seconds]" >&2
    echo "Example: $0 chkdsk 30" >&2
    exit 1
fi

echo "Monitoring Windows process: $proc_name (poll every ${interval}s)"

while true; do
    # Check if process exists
    if ! powershell.exe -Command "Get-Process '$proc_name' -ErrorAction SilentlyContinue" 2>&1 | grep -q "$proc_name"; then
        echo "finished"
        exit 0
    fi
    
    echo "still running..."
    sleep "$interval"
done