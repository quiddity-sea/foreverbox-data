#!/usr/bin/env bash
# mount-win-drive.sh — Idempotent Windows drive mount for WSL2
# Usage: mount-win-drive.sh <drive-letter> [mount-point]
#   drive-letter: single letter (D, E, F, etc.)
#   mount-point:  optional, defaults to /mnt/<letter>

set -euo pipefail

drive_letter="${1^^}"  # uppercase
mount_point="${2:-/mnt/${drive_letter,,}}"  # lowercase

if [[ ! "$drive_letter" =~ ^[A-Z]$ ]]; then
    echo "Usage: $0 <drive-letter> [mount-point]" >&2
    echo "Example: $0 D" >&2
    echo "Example: $0 E /mnt/external" >&2
    exit 1
fi

# Check if already mounted at target
if mountpoint -q "$mount_point" 2>/dev/null; then
    echo "Already mounted: $drive_letter: -> $mount_point"
    exit 0
fi

# Create mount point
sudo mkdir -p "$mount_point"

# Mount
echo "Mounting $drive_letter: to $mount_point..."
sudo mount -t drvfs "${drive_letter}:" "$mount_point"

# Verify
if mountpoint -q "$mount_point"; then
    echo "Mounted successfully: $drive_letter: -> $mount_point"
    ls -la "$mount_point" | head -20
else
    echo "ERROR: Mount failed" >&2
    exit 1
fi