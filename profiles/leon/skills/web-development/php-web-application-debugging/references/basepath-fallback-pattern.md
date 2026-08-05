---
name: basepath-fallback-pattern
description: "Pattern for handling base path resolution in PHP templates across different directory depths"
tags: ["php", "templates", "basepath", "routing", "asset-resolution"]
---

# Base Path Fallback Pattern

## Problem
PHP templates shared across pages at different directory depths need correct asset paths:
- `/institute/index.php` → `assets/css/`
- `/institute/pages/origin.php` → `../assets/css/`

Hardcoding paths breaks when pages move or new subdirectories are added.

## Solution

```php
// In header.php (included first)
$basePath = (basename(dirname($_SERVER['PHP_SELF'])) === 'pages') ? '../' : '';

// In footer.php (included last)
$basePath = $basePath ?? ((basename(dirname($_SERVER['PHP_SELF'])) === 'pages') ? '../' : '');
```

## How It Works

| Page | `$_SERVER['PHP_SELF']` | `dirname` | `basename` | Result |
|------|------------------------|-----------|------------|--------|
| `/institute/index.php` | `/institute/index.php` | `/institute` | `institute` | `''` |
| `/institute/pages/origin.php` | `/institute/pages/origin.php` | `/institute/pages` | `pages` | `'../'` |
| `/institute/pages/about.php` | `/institute/pages/about.php` | `/institute/pages` | `pages` | `'../'` |

## Usage in Templates

```php
<!-- header.php -->
<script src="<?php echo $basePath; ?>assets/js/tailwind-config.js"></script>
<link rel="stylesheet" href="<?php echo $basePath; ?>assets/css/pages.css">

<!-- footer.php -->
<script src="<?php echo $basePath; ?>assets/js/nav.js"></script>
<?php if(file_exists($basePath . 'js/animations.js')): ?>
    <script src="<?php echo $basePath; ?>js/animations.js"></script>
<?php endif; ?>
```

## Key Points

1. **Define early, fallback late** — Set in header, fallback in footer for safety
2. **Use `??` null coalescing** — Handles cases where header wasn't included
3. **Check `basename(dirname())`** — More reliable than counting slashes
4. **Empty string for root** — No leading `./` needed for same-directory assets

## Anti-Patterns

- ❌ Hardcoded `../assets/` in every template
- ❌ `dirname($_SERVER['SCRIPT_NAME'])` — fails with mod_rewrite
- ❌ `substr_count($path, '/')` — fragile, breaks with rewrites
- ❌ Global constant — can't handle multiple entry points