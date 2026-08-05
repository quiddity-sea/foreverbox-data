---
name: json-unescape-pattern
description: "Pattern for recovering double-escaped JSON strings from database"
tags: ["json", "escaping", "database", "php"]
---

# JSON Double-Escape Recovery Pattern

## Problem
Database stores HTML/JSON with double-escaped sequences:
- `\\n` instead of `\n` (newline)
- `\\"` instead of `"` (quote)
- `\\\\` instead of `\` (backslash)
- `\\t` instead of `\t` (tab)

When rendered directly, these appear as literal text instead of being interpreted.

## Solution

```php
private function unescapeJsonString(string $value): string {
    // First attempt: treat as JSON-encoded string
    // Wrap in quotes to make valid JSON, then decode
    $decoded = json_decode('"' . $value . '"');
    if (json_last_error() === JSON_ERROR_NONE) {
        return $decoded;
    }
    
    // Fallback: manual unescape for common sequences
    return str_replace(
        ['\\n', '\\r', '\\t', '\\"', '\\\\', '\\/'],
        ["\n", "\r", "\t", '"', '\\', '/'],
        $value
    );
}
```

## Usage in Component Rendering

```php
public function renderComponent(int $loomId, array $variables): string {
    // ... fetch template ...
    
    foreach ($variables as $key => $value) {
        // Unescape double-escaped JSON strings from database
        if (is_string($value)) {
            $value = $this->unescapeJsonString($value);
        }
        $html = str_replace('{{' . strtoupper($key) . '}}', $value, $html);
    }
    
    // ... remove unreplaced tokens ...
    return $html;
}
```

## Test Cases

| Input | Expected Output |
|-------|-----------------|
| `Line 1\\nLine 2` | `Line 1\nLine 2` |
| `She said \\\"Hello\\\"` | `She said "Hello"` |
| `Path\\\\to\\\\file` | `Path\\to\file` |
| `Col1\\tCol2\\tCol3` | `Col1\tCol2\tCol3` |
| `https:\\/\\/example.com` | `https://example.com` |
| `Plain text` | `Plain text` (unchanged) |

## When to Use
- Database content sourced from JSON exports
- CMS content edited via JSON-aware editors
- Migration from systems that double-encode
- Any case where `json_encode()` was applied twice

## Anti-Patterns to Avoid
- ❌ `html_entity_decode()` — only handles HTML entities
- ❌ `stripslashes()` — only removes single backslashes
- ❌ `str_replace('\\n', "\n")` alone — misses other sequences
- ✅ Use `json_decode('"' . $str . '"')` as primary method