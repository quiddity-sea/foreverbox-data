---
name: stich-design-workflow
description: Stich design project conventions and site-building patterns for the ForeverBox specification site.
version: 1.0.0
---

# Stich Design Workflow

The Stich Project is the design system repository for the ForeverBox specification site at `/var/www/the-foreverbox-institute/history/Stich-Project/stitch_project_repository_analyzer/`.

## File Structure

### Latest Designs (subdirectory code.html)
The most recent design iteration for each page lives in a named subdirectory containing `code.html`:
- `foreverbox_responsive_hud_index/code.html` — Latest index page
- `foreverbox_part_i_the_mythic_frame_hud/code.html` — Latest Part I
- `foreverbox_part_iv_the_personas_hud/code.html` — Latest Part IV
- etc.

These are self-contained Tailwind CDN HTML files with inline config. Colors: background #0b141c, primary #ebffe2, neon green #00ff41. Fonts: Exo 2, Geist, JetBrains Mono.

### Older Versions (flat directory, `_N` suffix)
Earlier design iterations: `index.html_1.html` through `index.html_4.html`, `foreverbox.css_1.css` etc.

### DESIGN.md Files (Abstract Specs)
Four YAML specs (`mythic_hud/DESIGN.md`, `chlorophyll_protocol_1/DESIGN.md`, etc.) — these are abstract tokens and may NOT match the actual CSS implementation.

### Screenshots
Reference screenshots in `.png`/`.webp` directories, each containing `screen.png`.

### References
Supporting documentation in the `references/` directory:
- `references/anchor-id-convention.md` — Sidenav anchor ID mapping
- `references/built-vs-spec-content.md` — Handling built-vs-spec content in reconstructions

## Critical Pitfall: Build from Source, Not from Memory

**ALWAYS read the actual reference files before building.** Never build from a remembered summary or a previously-written blueprint. The user will detect mismatches immediately.

2026-07-23 session required three rebuilds:
1. Built dark HUD from REDESIGN_BLUEPRINT.md summary → user: "looks nothing like Stich"
2. Rebuilt from DESIGN.md abstract specs → user showed screenshots proving different
3. Rebuilt as old green theme → user showed latest Exo 2 HUD code.html files

**Correct approach:**
1. Ask which specific Stich files are the reference
2. Read them with read_file
3. If screenshots exist, view with vision_analyze
4. Build matching what you ACTUALLY read
5. Get visual sign-off before proceeding to other pages

## Component Injection for Tailwind CDN Pages

### Active State Pattern
Dynamic Tailwind classes via JS `classList.add()` are NOT picked up by the CDN. Use plain CSS:
```css
.fb-sidenav-active { background: rgba(28,84,36,0.2) !important; color: #ebffe2 !important; border-left: 4px solid #00ff41 !important; }
.fb-nav-active { color: #00ff41 !important; border-bottom: 2px solid #00ff41 !important; padding-bottom: 0.25rem !important; }
```

### Shared Component Architecture
- `components/header.html`, `components/sidenav.html`, `components/footer.html` — edit once
- `assets/nav.js` — fetches + injects all three, handles active state
- Each page: `<div id="fb-header">`, `<div id="fb-sidenav" class="flex flex-1 pt-16">`, `<div id="fb-footer">`
- Sub-menus: `.fb-sidenav-group:hover .fb-submenu { display: block }`, JS auto-expands active page

### Canonical shared location (as of 2026-07-31)
The canonical shared component system lives at `/var/www/the-foreverbox-institute/interactions/`:
- Assets: `/interactions/assets/` — `js/tailwind-config.js`, `css/pages.css`, `css/components.css`, `css/header.css`, `css/sidebar.css`, `css/footer.css`
- Component HTML: `/interactions/components/{header,sidenav,footer}.html`
- Injector: `/interactions/assets/nav.js` — fetches `components/*.html` **relative to the page URL** (NOT relative to the script). So a page served at `<vhost-root>/self.php` resolves `components/` to `<vhost-root>/components/`.
- Nexus references these with absolute paths `/interactions/assets/...`. Plutus mirrors its own copy at `/var/www/plutus.invigor.com/assets/`.

### Reusing the system for a NEW page outside interactions/ (self.php pattern, verified)
1. **Head**: fonts (Exo 2/Geist/JetBrains Mono + Material Symbols) + Tailwind CDN, then absolute shared assets: `<script src="/interactions/assets/js/tailwind-config.js">` + the five `/interactions/assets/css/*.css` links.
2. **Shell**: `<body class="bg-background text-on-surface font-body-md ...">`, two fixed overlay divs (`bg-surface-container-lowest opacity-90` + `hud-scanline`), then `#fb-header`, `#fb-sidenav`, `<main class="flex-1 md:ml-64 px-4 md:px-12 py-8">`, `#fb-footer`, `<script src="/interactions/assets/nav.js">`.
3. **Per-page components**: since nav.js resolves `components/*.html` relative to the page URL, create a `components/` dir in the page's own vhost root (e.g. `/var/www/the-foreverbox-institute/components/`) with SELF-branded header/sidenav/footer — shared CSS makes them render identically.
4. **File perms**: `chmod 644` the page AND its components; Apache runs as `www-data`. A `600` page returns HTTP 500 with `PHP Fatal error: Failed opening required ... Permission denied` — diagnose via `/var/log/apache2/<site>-error.log`.

### One File to Change Navigation
The entire nav tree lives in `components/sidenav.html` — 7 part groups with chapter sub-links, plus APPENDICES and INDEX entries at the bottom.

## Sidenav Anchor ID Convention

Sidenav sub-menu entries link to section headings via `id="partX-N"` anchors. The convention is `part{page}-{chapter}` for major headings and `part{page}-{chapter}-{sub}` for sub-sections. The full mapping of all 67 anchors is documented in `references/anchor-id-convention.md`. Run `scripts/verify-anchors.sh` from the project root to check all links resolve.

When adding or changing chapters in the sidenav, always update both the `href` in `components/sidenav.html` and add the matching `id` to the target heading in the part file. Missing anchors cause the sub-menu links to scroll nowhere.

## Porting Spec Content into the HUD Template

When rebuilding part pages that already exist as plain-HTML spec documents under `/var/www/the-foreverbox-institute/history/the-project/`:

1. **Read the source spec file** from `the-project/` — these contain the canonical prose, tables, and structure.
2. **Read an existing HUD template page** (part2.html or part3.html) from `stitch_project_repository_analyzer/` — this establishes the visual pattern: hero header with `border-l-4`, section dividers with DATA_NODE labels, glass panels with corner accents, code-label font markers.
3. **Port ALL spec content** — every paragraph, table row, quoted phrase, footnote, update notice. No summarising. No skipping "pending" entries.
4. **Preserve injection points**: `<div id="fb-header">`, `<div id="fb-sidenav" class="flex flex-1 pt-16">`, `<div id="fb-footer">`, and `<script src="assets/nav.js">` must all remain exactly as in the reference pages.
5. **Preserve ALL anchor IDs** from the spec — including sub-anchors like `part4-15-3` and `part6-22-9` that the old stubs didn't have.
6. **Verify with the pattern**: structural tags present, injection points present, every anchor ID resolves, every key content phrase from source exists in output (case-insensitive).

### HUD-specific formatting for tables

When porting tables (Seven Signals, Platform Matrix, Track Listing), render them with the dark HUD style: `font-code-label` headers, `hover:bg-primary/5 transition-colors` rows, `border-primary/10` dividers, code-formatted first columns. Pending/placeholder rows get muted styling (`text-on-surface-variant/50`) to visually distinguish them from completed entries.

### Pitfall: Extra `</div>` after `</main>`

All part pages have a `</div>` between `</main>` and `<div id="fb-footer">` that appears unmatched by a visible opening tag. This is a **pre-existing pattern** in parts 1-7 — it pairs with dynamically injected content from `assets/nav.js`. Do NOT remove it; do NOT treat it as a bug or try to "fix" it during rebuilds. The tag-balance checker will flag it; that's expected.

## Content Verification Pattern

After writing a rebuilt page, run a verification check against the source spec:

```python
# Key checks:
# 1. Injection points (fb-header, fb-sidenav, fb-footer, nav.js) present
# 2. All structural tags (DOCTYPE, html, head, body, main) present
# 3. Every anchor ID from the spec appears in the output
# 4. Every key content phrase from source spec appears (case-insensitive)
# 5. HUD design elements (hud-scanline, glass-panel, hud-border, INITIALIZATION_SEQUENCE) present
```

The `</div>` tag-balance issue is a known false positive — skip it.

### Ad-hoc verification script (no canonical test command exists)
When the site has no test/lint/build command, the workspace-verification system expects a focused ad-hoc script: write to `/tmp/hermes-verify-<topic>.sh` (OS-safe tempfile path, `hermes-verify-` prefix), run it, clean it up, and report explicitly as **ad-hoc verification**, not suite green.

Good checks for a PHP page + shared components (self.php pattern, verified 2026-07-31):
1. `php -l <page>` — syntax
2. `stat -c %a` == 644 on the page AND its `components/*.html` (www-data readability; 600 → HTTP 500)
3. `curl -sk -o /dev/null -w "%{http_code}"` == 200 for: the page over HTTPS, each shared asset (`/interactions/assets/nav.js`, `tailwind-config.js`, `css/pages.css`), and each `components/{header,sidenav,footer}.html`
4. For a POST-proxy backend: POST a test message, assert `"ok":true` in JSON and that the response does NOT contain thinking-preamble markers
5. Clean up: `rm -f /tmp/hermes-verify-*.sh` after running

Report format: list PASS lines per check, `RESULT: N passed, M failed`, and explicitly state visual layout is unverified when the browser daemon is unavailable.

## Delegate_task and Local Models
`delegate_task` subagents inherit the PARENT model — they do NOT run on local Ollama. To use a local model: use `hermes -z` (one-shot) or `hermes --cli chat` (interactive PTY).
