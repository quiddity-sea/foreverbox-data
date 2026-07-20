# Privacy Scan Patterns — Cognitive Router

The `scan_for_private_data()` function in `router/__init__.py` detects sensitive data
in message content to prevent leaking to cloud models.

## Default Patterns

```python
patterns = [
    r"api[_-]?key",
    r"secret",
    r"password",
    r"token",
    r"\bsk-[a-zA-Z0-9]{20,}\b",           # OpenAI API keys
    r"\bgh[pousr]_[a-zA-Z0-9]{16,}\b",    # GitHub tokens (PAT, OAuth, etc.)
    r"\bBearer\s+[a-zA-Z0-9._-]+\b",       # Bearer tokens (JWT, etc.)
    r"/home/",
    r"/Users/",
    r"C:\\Users\\",
]
```

## Deep Scan (Tool Call Arguments)

Also scans `tool_calls[].arguments` values for file paths:
- Starts with `/home`
- Starts with `/Users`
- Contains `C:\Users`

## What Gets Blocked

When private data is detected AND no local model is available, the router
**hard-stops** — it raises a RuntimeError rather than leaking data to a cloud model.

When private data is detected AND a local model IS available, the router
returns the local model profile regardless of the cognitive load score.

## Maintenance

Add new patterns if common credential formats emerge. Keep patterns as specific
as reasonable to avoid false positives on legitimate content.

## Verified Patterns (2026-07-20)

- OpenAI `sk-...` keys (>=20 alphanumeric chars after prefix)
- GitHub tokens: `ghp_` (PAT), `gho_` (OAuth), `ghu_` (user), `ghs_` (server), `ghr_` (refresh)
- Bearer tokens in Authorization headers
- Pattern boundaries prevent false matches on ordinary words containing "secret" or "token"
- Deep scan catches file paths in tool call arguments
