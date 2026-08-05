# PowerShell from WSL: Quoting and Escaping Patterns

Reference for safely invoking PowerShell commands from WSL bash.

## Basic Invocation
```bash
powershell.exe -Command "<command>"
```

## Quote Handling Rules

### Simple Commands (no internal quotes)
```bash
powershell.exe -Command "Get-ChildItem D:\Pictures -Force"
```

### Commands with Single Quotes (use double outside)
```bash
powershell.exe -Command "Get-ChildItem 'D:\Pictures' -Force"
```

### Commands with Double Quotes (escape with backslash)
```bash
powershell.exe -Command "Get-ChildItem \"D:\My Pictures\" -Force"
```

### Commands with Both Quote Types
```bash
# Wrap in double, escape internal doubles, use singles internally
powershell.exe -Command "Get-ChildItem \"D:\My Pictures\" -Filter '*.jpg' -Force"
```

## Variable Expansion
- **WSL variables**: Expand in bash before passing
  ```bash
  drive="D:"
  powershell.exe -Command "chkdsk $drive /f /r /x"
  ```
- **PowerShell variables**: Use single quotes inside command
  ```bash
  powershell.exe -Command '$drive = "D:"; chkdsk $drive /f'
  ```

## Pipeline and Redirection
```bash
# Pipe to file on Windows side
powershell.exe -Command "chkdsk D: /f /r /x > D:\chkdsk.log 2>&1"

# Pipe between commands
powershell.exe -Command "Get-Process chkdsk | Select-Object Id, CPU, WS"
```

## Common Patterns

### Check Process Exists
```bash
powershell.exe -Command "Get-Process chkdsk -ErrorAction SilentlyContinue"
# Returns nothing if not running, process object if running
```

### Force Dismount and Check
```bash
powershell.exe -Command "chkdsk D: /f /r /x"
# /x forces dismount, implies /f
```

### Get Directory Listing with Hidden/System Files
```bash
powershell.exe -Command "Get-ChildItem 'D:\Pictures' -Force -ErrorAction Stop"
```

## Anti-Patterns to Avoid
- ❌ Nested double quotes without escaping: `"Get-ChildItem \"D:\""`
- ❌ Heredocs with PowerShell (doesn't work via -Command)
- ❌ Complex scripts in -Command (write .ps1 file instead)
- ❌ Assuming bash escapes work inside PowerShell string

## For Complex Scripts
Write a .ps1 file on Windows side, then invoke:
```bash
powershell.exe -File "D:\scripts\repair.ps1"
```