---
name: fbox-quiddity-folder-manager
description: Create, update, or remove subfolder routing entries in the Quiddity Lore Sea folder catalogue. Creates directories, adds keywords, and regenerates centroids.
---

# Quiddity Folder Manager

When the user asks to create a subfolder structure, follow this exact workflow.

## 1. Understand the request

The user will say something like "create a subfolder for completed Substack posts under 04_FromTheNoise_Archives" or "add drafts/article_outlines to 02_ReInvigor_Texts".

Extract:
- Parent folder (e.g., `04_FromTheNoise_Archives`)
- Subfolder path relative to parent (e.g., `completed/sub_stack_posts`)
- Keywords the user provides, or infer from the purpose

## 2. Create directories

```bash
mkdir -p /foreverbox_data/Quiddity_Lore_Sea/{parent}/{subfolder}
```

Example: `mkdir -p /foreverbox_data/Quiddity_Lore_Sea/04_FromTheNoise_Archives/completed/sub_stack_posts`

## 3. Update the catalogue

Edit `/foreverbox_data/council-library/php-api/config/quiddity_folders.yaml`.

If the parent folder doesn't have a `subfolders:` section yet, add it under that folder's entry. Then add the new subfolder with its full path:

```yaml
  "04_FromTheNoise_Archives":
    # ...existing keywords...
    subfolders:
      "04_FromTheNoise_Archives/completed/sub_stack_posts":
        keywords:
          - keyword1
          - keyword2
        purpose: "Description of what goes here"
```

Key rules:
- Full path includes the parent folder: `04_FromTheNoise_Archives/completed/sub_stack_posts`
- Keywords are used by FolderRouter for classification — pick terms likely to appear in content that should route here
- Purpose is human-readable documentation

## 4. Regenerate centroids

If files already exist in the new subfolder:

```bash
DB_PASS="F0reverb0x#2o26sql" /usr/bin/python3.12 \
  /foreverbox_data/council-library/scripts/generate_folder_centroids.py
```

## 5. Verify

```bash
php -r '
require "/foreverbox_data/council-library/php-api/vendor/autoload.php";
$r = new CouncilLibrary\Service\FolderRouter();
echo $r->classify("sample text matching the new keywords");
'
```

Should return the full path of the new subfolder.

## Pitfalls

- Folder paths in the YAML key must be the FULL path including parent
- Don't forget the trailing `:` after the path in YAML
- Keywords are matched case-insensitively against first 4KB of content
- Centroids won't generate until files exist in the subfolder — that's fine, keyword fallback works immediately
- The YAML parser supports `/` in folder names but NOT spaces — use underscores
- **YAML keyword format**: The parser expects `- keyword` list items, NOT inline arrays (`[kw1, kw2]`). The original quiddity_folders.yaml had no keywords at all (subagent stripped them). When adding keywords, use the indented list format.
- **YAML folder name regex**: Folder names must be at least 2 levels indented and match `"folder_name":` or `folder_name:`. The parser skips `folders:` and `keywords:` as reserved words. Quoted names with colons inside (like `04_FromTheNoise_Archives:` without quotes) are fine.
- **PHP opcode cache**: After editing any PHP service file (FolderRouter, QuiddityController), Apache `reload` may NOT pick up changes. The PHP opcode cache survives `reload`. Always use `systemctl stop apache2 && systemctl start apache2` — the full stop-start cycle clears opcache.
- **Keyword scoring skew**: Full-document keyword matching can misclassify — \"agent\" appears hundreds of times in a 113 KB blueprint. The FolderRouter now truncates to 4 KB before scoring. The vector centroid path avoids this entirely once centroids are generated.
