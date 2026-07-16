# Subfolder Classification Routing

## Problem

Files in the Lore Sea should route to nested subdirectories, not just top-level folders. A completed Substack article should go to `04_FromTheNoise_Archives/completed/sub_stack_posts/`, not just `04_FromTheNoise_Archives/`.

## Solution

Three components work together:

### 1. YAML catalogue (`quiddity_folders.yaml`)

Subfolders are defined as full-path keys under `subfolders:` within a parent folder entry:

```yaml
"04_FromTheNoise_Archives":
  keywords: [ftn, editorial, article, research]
  purpose: "Published articles, editorial guidelines, research"
  subfolders:
    "04_FromTheNoise_Archives/completed/sub_stack_posts":
      keywords: [substack, published, post, newsletter]
      purpose: "Finished and published Substack articles"
    "04_FromTheNoise_Archives/completed/blogs":
      keywords: [blog, website, published, post]
      purpose: "Published blog articles"
```

Keys must include the full path (`parent/subfolder`), not just the leaf.

### 2. FolderRouter parser

The YAML parser regex must allow `/` and `_` in folder names:

```php
// Old: only matches \w[\w_]*
// New: matches \w[\w_\/]*
preg_match('/^\s+"?([\w][\w_\/]*)"?\s*:\s*$/', $line, $m)
```

The `subfolders` key itself is skipped by the `continue` guard.

### 3. Centroid generator

Subfolder paths are added to the FOLDERS list alongside top-level folders. The `WHERE relative_path LIKE 'folder/%'` query matches files at the exact path and any depth below it.

### 4. Route logic (QuiddityController sync)

`mkdir($targetDir, 0755, true)` — the recursive flag handles nested directory creation automatically. No changes needed to the `rename()` logic.

## Verification

```bash
# Test classification
php -r '
require "vendor/autoload.php";
$r = new CouncilLibrary\Service\FolderRouter();
echo $r->classify("My latest Substack newsletter post") . "\n";
# Output: 04_FromTheNoise_Archives/completed/sub_stack_posts
'

# Full pipeline test
curl -X POST localhost:8080/v1/commons/files/sync \
  -H "Authorization: Bearer ***" -H "X-Agent-ID: curator" \
  -H "Content-Type: application/json" \
  -d '{"paths":["my_article.md"],"organise":true}'
```

## Pitfalls

- Subfolder keys must use FULL paths. `"completed/sub_stack_posts"` routes to `/foreverbox_data/Quiddity_Lore_Sea/completed/sub_stack_posts/` (wrong). Use `"04_FromTheNoise_Archives/completed/sub_stack_posts"`.
- Parent folder keywords still apply — files matching `substack` go to the subfolder, files matching only `editorial` go to the parent. The classifier picks the highest keyword score across ALL folders (parent + subfolders).
- Keywords are more important for subfolders than parents — a Substack article that also mentions "editorial" should still route to `sub_stack_posts`, which means the subfolder needs distinct, specific keywords.
