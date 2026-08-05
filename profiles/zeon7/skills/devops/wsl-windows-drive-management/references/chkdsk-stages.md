# chkdsk Stages and Time Estimates

Reference for understanding chkdsk progress when monitoring from WSL.

## Stage Breakdown (NTFS)

| Stage | Description | Typical Duration |
|-------|-------------|------------------|
| 1 | Examining basic file system structure (file records) | Seconds to minutes |
| 2 | Examining file name linkage (indexes) | Minutes |
| 3 | Examining security descriptors | Seconds to minutes |
| 4 | Verifying file data (all clusters in files) | **Hours** on large drives |
| 5 | Verifying free space | Minutes to hours |

## Stage 3 Detail: Orphan File Recovery
- "Recovering orphaned file X into directory file Y"
- Each orphan file = one directory entry recreated
- Can process tens of thousands of files
- Progress shows: `Progress: N of M done; Stage: X%; Total: Y%`
- ETA often wildly inaccurate (extrapolates from current rate)

## Stage 4 Detail: File Data Verification
- Reads every cluster allocated to files
- **Slowest stage** on large volumes with many files
- Bad sector detection/recovery happens here (`/r` flag)
- Can take 2-6+ hours on 1TB+ drives with corruption

## Stage 5 Detail: Free Space Verification
- Scans unallocated clusters
- Faster than Stage 4 but still significant on large drives

## Monitoring from WSL
```bash
# Check if chkdsk still running
powershell.exe -Command "Get-Process chkdsk -ErrorAction SilentlyContinue"

# CPU time in output indicates active work
# Memory ~50MB = normal; growing = active scanning
```

## Time Expectations (rough)
| Drive Size | Clean | Light Corruption | Heavy Corruption (/r) |
|------------|-------|------------------|----------------------|
| 32GB SD    | 2-5 min | 10-30 min      | 30-90 min           |
| 256GB      | 5-15 min | 30-60 min     | 2-6 hours           |
| 1TB        | 15-45 min | 1-3 hours    | 6-24+ hours         |

## Exit Codes
- `0` — No errors found
- `1` — Errors found and fixed
- `2` — Disk cleanup (orphan recovery) performed
- `3` — Could not check / could not fix (run without `/f`)