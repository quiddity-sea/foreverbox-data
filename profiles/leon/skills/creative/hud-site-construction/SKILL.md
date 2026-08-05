---
name: hud-site-construction
description: Build and maintain high-fidelity HUD (Heads-Up Display) websites with shared component injection and dynamic state highlighting.
---

# HUD Site Construction

This skill governs the creation of the "Stich" style HUD websites. It prioritizes a dark-mode, technical aesthetic with neon accents and a shared-component architecture to ensure consistency across multi-page archives.

## Core Principles

- **Single Source of Truth**: UI elements (header, side nav, footer) live in one place; edits propagate instantly.
- **Predictable Injection**: JavaScript fetches components and places them into fixed DOM IDs.
- **Styling Consistency**: All pages share the same Tailwind config, custom CSS, and font imports.
- **Anchor-Driven Navigation**: Side‑nav links use fragment identifiers (`#partX-N`) that must match exact heading IDs.
- **HUD Visual Language**: Dark background (`#0b141c`), neon green (`#00ff41`), glass panels, 1px HUD borders, and corner accents.
- **Content-Type-Specific Design**: Parts 1‑6 each have distinct visual identities (narrative, cube visualization, swarm diagrams, persona cards, workflow specs, dream warrior specs) while sharing the same visual vocabulary. When building new pages, select a "design ancestor" from parts 1‑6 that matches the content type and reverse‑engineer its component patterns.
- **Component-Based, Not Template-Based**: The system is a reusable component library (layout containers, content-specific cards, typography patterns) that can be composed flexibly — never a single rigid template.
- **Preservation of Injection System**: The three injection divs (`fb-header`, `fb-sidenav`, `fb-footer`) and `nav.js` script must remain untouched in every page.
- **Anchor Integrity**: Every heading that appears in the side nav must have an exact `id` attribute matching the link (e.g., `id="part4-14"`, `id="appendix-a"`).
- **Content-Type-Specific Design**: Parts 1‑6 each have distinct visual identities (narrative, cube visualization, swarm diagrams, persona cards, workflow specs, dream warrior specs) while sharing the same visual vocabulary. When building new pages, select a "design ancestor" from parts 1‑6 that matches the content type and reverse‑engineer its component patterns.
- **Component-Based, Not Template-Based**: The system is a reusable component library (layout containers, content-specific cards, typography patterns) that can be composed flexibly — never a single rigid template.
- **Design Ancestor Mapping**: When creating new pages, choose a "design ancestor" from parts 1‑6 that matches the content type:
  - **Narrative / procedural content** (e.g., Part 7's build phases) → **Part 1** (The Mythic Frame)
  - **Technical / specification content** (e.g., Appendices with code/tables) → **Parts 2 or 3** (The Cube / Swarm of Mites)
  - **Visualization-heavy content** (e.g., network diagrams) → **Part 3** (Swarm of Mites)
  - **Persona-style content** → **Part 4** (The Personas)
- **Component Library**: The design system is built from a reusable, combinable component library organized into three categories:

  **A. Layout & Containers**
  | Component | Purpose | Key Classes | Example Usage |
  |-----------|---------|-------------|---------------|
  | `hud-border` | Base container for all content blocks | `border border-outline-variant/20` | Wraps sections, cards, panels |
  | `glass-panel` | Semi‑transparent blurred panel | `bg-[rgba(0,255,65,0.05)] backdrop-blur-sm border border-primary/20` | Epigraphs, code blocks, data panels |
  | `hud-glow` | Outer glow effect (optional) | `drop-shadow-[0_0_20px_rgba(0,255,65,0.3)]` | Hero sections, key visualizations |
  | `corner-accent` | 2x2px colored corner markers | `absolute w-2 h-2 border-t border-l border-primary-container` (and mirrored) | Inside `hud-border` or `glass-panel` for depth |
  | `scanline-overlay` | Animated scanline effect | `bg-[linear-gradient(rgba(0,255,65,0.05)_1px,transparent_1px)] bg-[size:100%_4px] pointer-events-none` | Over images or panels |
  | `content-container` | Centers content with padding | `max-w-5xl mx-auto space-y-16 mt-8 md:mt-16 px-4 md:px-8` | Main content wrapper |

  **B. Content-Specific Components**
  | Component | Purpose | Key Classes | Example Usage |
  |-----------|---------|-------------|---------------|
  | `hero-section` | Page introduction with accent bar | `border-l-4 border-primary-container pl-6` + `font-code-label text-code-label uppercase text-primary/60 tracking-widest mb-2` (label) + `h1`/`h2` | Part 1, 2, 3 headers |
  | `epigraph-block` | Quoted passage with attribution | `glass-panel hud-border p-6` + vertical `w-1 bg-primary-container` bar | Part 1 opening quotes |
  | `narrative-card` | Text‑heavy explanatory section | `hud-border p-6 bg-surface-dim/50 backdrop-blur-sm` + corner accents | Part 1 sections (The Origin, etc.) |
  | `tech-card` | Technical specification card | `hud-border bg-surface-container/30 hover:bg-surface-container/50 transition-colors duration-300` + `p-6` | Part 2/3 cards (Layers, Nodes) |
  | `data-table` | Structured information display | `w-full font-code-label text-code-label text-left border-collapse` + `border-b border-primary/30` on headers | Part 3 memory/network tables |
  | `code-block` | Syntax‑highlighted snippet | `bg-[#05090c] border border-primary/20 p-4 font-code-label text-code-label overflow-x-auto relative group` | All code snippets |
  | `status-badge` | Categorical indicator | `px-2 py-1 bg-background/80 text-[0.65rem] rounded` + color‐specific text (e.g., `text-primary`) | Part 4/5 status indicators |
  | `section-header` | Major section divider | `font-anchor-sm text-anchor-sm text-primary uppercase tracking-widest mb-6 border-b border-primary/30 pb-2` + optional icon | All chapter/section titles |
  | `data-node-label` | Machine‑readable identifier | `font-code-label text-[10px] text-primary/50` | `DATA_NODE_77A`, `RECORDS: 02` |
  | `image-frame` | Image with HUD overlay | `relative overflow-hidden hud-glow aspect-[1.50]` + `hud-border-active -m-4 pointer-events-none opacity-20 group-hover:opacity-100` overlay | Part 1 images, Part 3 node photos |

  **C. Typography Patterns**
  | Use Case | Classes | Example |
  |----------|---------|---------|
  | Hero label (`INITIALIZATION_SEQUENCE`) | `font-code-label text-code-label uppercase text-primary/60 tracking-widest` | Part 1, 2, 3 headers |
  | Section title | `font-headline-md text-headline-md font-semibold text-primary mb-4 flex items-center gap-2` + `w-1.5 h-6 bg-primary inline-block` | Part 1 section heads |
  | Body text | `text-on-surface-variant leading-relaxed text-sm` | Paragraphs throughout |
  | Caption/footnote | `text-on-surface-variant/70 text-[0.8rem]` | Image captions, footnotes |
  | Code label (inside snippet) | `font-code-label text-[10px] text-primary/70` | `// Tailscale Mesh Configuration` |

- **Content Handling Patterns**:
  - **Hero Sections** (Parts 1, 2, 3): `border-l-4 border-primary-container pl-6` with blurred accent bar + `INITIALIZATION_SEQUENCE` label + Exo 2 Thin/Exo 2 Semibold hero text.
  - **Epigraphs/Quotes**: `glass-panel hud-border p-6` with vertical `w-1 bg-primary-container` accent bar + `font-code-label text-[10px] text-primary/30` source label in top-right.
  - **Narrative Cards** (Part 1): `hud-border p-6 bg-surface-dim/50 backdrop-blur-sm` with alternating corner accents (top-left/bottom-right, then top-right/bottom-left).
  - **Technical Cards** (Parts 2, 3): `hud-border bg-surface-container/30 hover:bg-surface-container/50 transition-colors duration-300` with `p-6` padding.
  - **Code Blocks**: `bg-[#05090c] border border-primary/20 p-4 font-code-label text-code-label overflow-x-auto relative group` with `DATA_NODE` / `RECORDS: XX` labels in top-right.
  - **Data Tables**: `w-full font-code-label text-code-label text-left border-collapse` with `border-b border-primary/30 pb-2` on headers.
  - **Corner Accents**: 2x2px `border-t border-l border-primary-container` (and mirrored variants) inside `hud-border` or `glass-panel` containers.
  - **Data Node Labels**: `font-code-label text-[10px] text-primary/50` placed at corners of code blocks, tables, or important notes (e.g., `DATA_NODE_77A`, `RECORDS: 02`, `IMG_REF: 038`).
  - **Scanline Overlay**: `bg-[linear-gradient(rgba(0,255,65,0.05)_1px,transparent_1px)] bg-[size:100%_4px] pointer-events-none` on images/panels.
  - **Image Frames**: `relative overflow-hidden hud-glow aspect-[1.50]` with `hud-border-active -m-4` overlay showing corner brackets + data labels.

- **Part 7 (Build Manual) Specific Patterns**:
  - Use **Part 1** as design ancestor (narrative/procedural content).
  - Hero section with `border-l-4 border-primary-container` + `INITIALIZATION_SEQUENCE` label.
  - Each major phase (24–29) as `hud-border` section with corner accents.
  - Technical steps (Tailscale, MariaDB, Vector primer) as `narrative-card` style blocks.
  - **Code blocks** (SQL, Bash, config) use high-contrast `code-block` component with `DATA_NODE` labels and `RECORDS: XX` markers.
  - Tables (IP assignments, dimensional coordinates) use `data-table` component.
  - Preserve all anchor IDs (`part7-24`, `part7-24-1`, etc.) for side-nav linking.

- **Appendices Specific Patterns**:
  - Use **Parts 2/3** as design ancestors (technical/specification content).
  - Each appendix (A–K) as `hud-border` / `glass-panel` section with corner accents.
  - Code blocks use `code-block` component with `DATA_NODE` labels.
  - Tables use `data-table` component.
  - Preserve "Historical record" / "Active template" labels as `status-badge` or section-header notes.
  - Preserve all anchor IDs (`appendix-a` through `appendix-o`) for side-nav linking.

## Required Files & Directories

```
/var/www/the-foreverbox-institute/history/Stich-Project/stitch_project_repository_analyzer/
├── components/
│   ├── header.html
│   ├── sidenav.html
│   └── footer.html
├── assets/
│   └── nav.js
└── [page].html   (index.html, part1.html … part7.html, appendices.html)
```

## Detailed Workflow

### 1. Prepare the Environment

Ensure the target directory exists and is writable.

```bash
mkdir -p /var/www/the-foreverbox-institute/history/Stich-Project/stitch_project_repository_analyzer/components
mkdir -p /var/www/the-foreverbox-institute/history/Stich-Project/stitch_project_repository_analyzer/assets
```

### 2. Author or Update Shared Components

Edit the files directly with `write_file` or `patch`. Keep them minimal—only the markup that should appear in every page.

**components/header.html**
```html
<header class="bg-background/80 backdrop-blur-md border-b border-outline-variant flex justify-between items-center w-full px-margin-safe h-16 sticky top-0 z-50">
  <a href="index.html" class="font-hero-text text-[1.5rem] font-bold tracking-tight">F:BOX</a>
  <nav class="flex space-x-4">
    <a href="index.html" class="fb-nav-item text-[0.875rem] hover:text-primary transition-colors">INDEX</a>
    <a href="appendices.html" class="fb-nav-item text-[0.875rem] hover:text-primary transition-colors">APPENDICES</a>
    <a href="logs.html" class="fb-nav-item text-[0.875rem] hover:text-primary transition-colors">LOGS</a>
  </nav>
</header>
```

**components/sidenav.html**
```html
<aside class="hidden md:flex bg-surface-container-low border-r border-outline-variant fixed left-0 top-16 h-[calc(100vh-64px)] w-64 flex-col py-grid-unit z-40">
  <div class="px-4 py-6 border-b border-outline-variant/30 mb-4">
    <div class="flex items-center space-x-3 mb-2">
      <div class="w-10 h-10 rounded bg-surface-variant flex items-center justify-center border border-primary/20 panel-glow">
        <span class="material-symbols-outlined text-primary">psychology</span>
      </div>
      <div>
        <div class="font-headline-md text-headline-md text-primary" style="font-size: 1rem; line-height: 1.25rem;">ARCHIVE_01</div>
        <div class="font-code-label text-code-label tracking-tighter text-secondary">STATUS: STABLE <span class="inline-block w-2 h-2 bg-primary rounded-full animate-pulse ml-1"></span></div>
      </div>
    </div>
  </div>
  <nav class="flex-1 overflow-y-auto font-code-label text-code-label tracking-tighter space-y-1">
    <!-- PART I -->
    <div class="fb-sidenav-group" data-page="part1">
      <a class="fb-sidenav-link flex items-center space-x-3 text-on-surface-variant px-4 py-3 opacity-60 hover:bg-surface-variant/30 hover:opacity-100 transition-all duration-200 hover:translate-x-1 no-underline" href="part1.html"><span class="material-symbols-outlined text-sm">memory</span><span>PART I: THE MYTHIC FRAME</span></a>
      <div class="fb-submenu hidden ml-6 border-l border-outline-variant/30 space-y-1 py-1">
        <a class="fb-sidenav-link block text-on-surface-variant/70 hover:text-primary no-underline py-1 px-3 text-[0.65rem] transition-colors" href="part1.html#part1-1">1. The Origin</a>
        <a class="fb-sidenav-link block text-on-surface-variant/50 hover:text-primary no-underline py-1 px-5 text-[0.6rem] transition-colors" href="part1.html#part1-1-1">1.1 The Diagnosis</a>
        <!-- ... repeat for all sub-items ... -->
      </div>
    </div>
    <!-- Repeat for PART II through PART VII and APPENDICES -->
  </nav>
  <div class="mt-auto border-t border-outline-variant/30 pt-4 px-2 space-y-1 font-code-label text-code-label tracking-tighter">
    <a class="fb-sidenav-link flex items-center space-x-3 text-on-surface-variant px-4 py-2 opacity-60 hover:text-primary hover:opacity-100 transition-colors no-underline" href="appendices.html" data-page="appendices"><span class="material-symbols-outlined text-sm">folder_open</span><span>APPENDICES</span></a>
    <a class="fb-sidenav-link flex items-center space-x-3 text-on-surface-variant px-4 py-2 opacity-60 hover:text-primary hover:opacity-100 transition-colors no-underline" href="index.html" data-page="index"><span class="material-symbols-outlined text-sm">keyboard</span><span>INDEX</span></a>
  </div>
</aside>
```

**components/footer.html**
```html
<footer class="bg-background border-t border-outline-variant docked full-width bottom-0 flex justify-between items-center w-full px-margin-safe py-4 text-[0.625rem] z-50">
  <div class="font-code-label text-[0.625rem] text-on-surface-variant">SYS.MEM: 4096TB // UPTIME: 99.999%</div>
  <div class="font-code-label text-[0.625rem] text-on-surface-variant">© ForeverBox Institute</div>
</footer>
```

**assets/nav.js**
```javascript
(function() {
  'use strict';

  const current = location.pathname.split('/').pop() || 'index.html';
  const baseName = current.replace('.html', '');

  function setActive() {
    setTimeout(() => {
      // Side nav: highlight active part and expand its submenu
      document.querySelectorAll('.fb-sidenav-group > .fb-sidenav-link').forEach(el => {
        const group = el.closest('.fb-sidenav-group');
        const page = group.getAttribute('data-page');
        if (page === baseName) {
          el.classList.add('fb-sidenav-active');
          const sub = group.querySelector('.fb-submenu');
          if (sub) sub.classList.add('block');
        }
      });

      // Top nav: highlight active item (INDEX, ARCHIVE, APPENDICES, LOGS)
      document.querySelectorAll('.fb-nav-item').forEach(el => {
        if (el.getAttribute('data-page') === baseName) {
          el.classList.add('fb-nav-active');
        }
      });
    }, 50);
  }

  function inject(id, url, cb) {
    const container = document.getElementById(id);
    if (!container) return;
    fetch(url)
      .then(r => r.text())
      .then(html => {
        container.innerHTML = html;
        if (cb) cb();
      })
      .catch(() => {});
  }

  inject('fb-header', 'components/header.html', () => {
    inject('fb-sidenav', 'components/sidenav.html', function() {
      setActive();
    });
  });
  inject('fb-footer', 'components/footer.html');
})();
```

### 3. Create the Page Template

Every page must share the exact same `<head>` and end with the nav.js script. Use this boilerplate:

```html
<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>PAGE TITLE — F:BOX STITCH PROJECT</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com">
  <link href="https://fonts.googleapis.com/css2?family=Exo+2:wght@100;200;400;600;900&family=Geist:wght@400&family=JetBrains+Mono:wght@400&display=swap" rel="stylesheet">
  <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
  <script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
  <script id="tailwind-config">
    tailwind.config = {
      darkMode: "class",
      theme: {
        extend: {
          colors: {
            'on-tertiary': '#2d3137',
            'surface-container-low': '#141c24',
            'tertiary': '#f8f8ff',
            'inverse-on-surface': '#29313a',
            'surface-container-high': '#222b33',
            'outline': '#84967e',
            'tertiary-container': '#d9dce5',
            'on-background': '#dae3ee',
            'on-primary-fixed-variant': '#00530e',
            'on-primary': '#003907',
            'surface-container-highest': '#2d363e',
            'primary': '#ebffe2',
            'primary-container': '#00ff41',
            'surface': '#0b141c',
            'background': '#0b141c',
          }
        }
      }
    };
  </script>
  <style>
    /* HUD-specific utilities */
    .hud-border { border: 1px solid rgba(0,255,65,0.1); }
    .glass-panel { background: rgba(11,20,28,0.4); backdrop-filter: blur(4px); }
    .fb-sidenav-active { background: rgba(28,84,36,0.2) !important; color: #ebffe2 !important; border-left: 4px solid #00ff41 !important; }
    .fb-nav-active { color: #00ff41 !important; border-bottom: 2px solid #00ff41 !important; padding-bottom: 0.25rem !important; }
    .fb-sidenav-group:hover .fb-submenu { display: block !important; }
    .fb-sidenav-group .fb-submenu { display: none; transition: max-height 0.3s ease; }
    .blinking-cursor { animation: blink 1s step-end infinite; }
    @keyframes blink { 0%,100% { opacity:1; } 50% { opacity:0; } }
  </style>
</head>
<body>
  <div id="fb-header"></div>
  <div id="fb-sidenav" class="flex flex-1 pt-16"></div>
  <main class="flex-1 md:ml-64 p-margin-safe max-w-container-max mx-auto w-full">
    <!-- PAGE‑SPECIFIC CONTENT GOES HERE -->
  </main>
  <div id="fb-footer"></div>
  <script src="assets/nav.js"></script>
</body>
</html>
```

### 4. Populate Page‑Specific Content

For each page (index.html, part1.html … part7.html, appendices.html):

1. **Obtain the source content**  
   - For `index.html`: use `/history/the-project/index.html` (preface + grid overview).  
   - For parts 1‑7: use `/history/the-project/partX-[name].html`.  
   - For `appendices.html`: use `/history/the-project/appendices.html`.

2. **Strip boilerplate**  
   Remove `<!DOCTYPE html>`, `<html>`, `<head>`, `<body>`, and any existing injection divs or script tags. Keep only the inner markup you wish to display.

3. **Wrap in HUD containers**  
   - Wrap logical sections in `<section class="hud-border ...">` or `<div class="glass-panel ...">`.  
   - Add corner‑accent divs inside those containers as needed.  
   - Insert `data-node` markers (e.g., `<div class="font-code-label text-[10px] text-primary/50">DATA_NODE</div>`) on code blocks, tables, or important notes.  
   - Style headings with the utility classes from the `<style>` block (`font-anchor-sm`, etc.).  
   - Ensure every heading that appears in the side nav has an exact `id` attribute matching the link (e.g., `<h2 id="part4-14">14. The Mez Filter</h2>`).

4. **Preserve the injection points**  
   Do **not** alter or remove the three `<div id="fb‑*">` placeholders or the `<script src="assets/nav.js"></script>` line.

### 5. Validate the Build

Start a temporary server and inspect:

```bash
cd /var/www/the-foreverbox-institute/history/Stich-Project/stitch_project_repository_analyzer/
python3 -m http.server 11438
```

Open `http://localhost:11438/index.html` and verify:

- Header, side nav, and footer appear on every page and are identical.
- Clicking a chapter in the side nav scrolls to the correct section (anchor match).
- Hovering over a part title expands its submenu.
- The visual style matches the HUD spec (dark bg, Exo 2/Geist/JetBrains Mono, neon green accents, glass panels, HUD borders, corner accents).
- No missing content or broken links.

### Common Pitfalls & How to Avoid Them

| Pitfall | Symptoms | Fix |
|---------|----------|-----|
| **Using dynamic Tailwind classes for active states** (e.g., `bg-secondary-container/20`) | Active highlights disappear in production because the CDN only sees static classes. | Use predefined CSS classes (`.fb-sidenav-active`, `.fb-nav-active`) defined in the `<style>` block and toggled via JavaScript. |
| **Missing or mismatched anchor IDs** | Clicking a sub‑menu item does nothing or jumps to the wrong place. | Ensure every `href="partX.html#partY-Z"` has a corresponding `<h2 id="partY-Z">`, `<h3 id="partY-Z">`, or `<section id="partY-Z">` on the target page. |
| **Over‑aggressive HTML stripping** | Accidentally removes needed markup (e.g., tables, lists) or leaves broken tags. | Extract only the visible content you want to display; keep semantic tags (`<table>`, `<ul>`, `<p>`, `<img>`). Use an HTML‑aware tool or simple regex that respects tag boundaries. |
| **Forgotten injection points** | Header, nav, or footer missing; page looks broken. | Always keep `<div id="fb-header"></div>`, `<div id="fb-sidenav" class="flex flex-1 pt-16"></div>`, `<div id="fb-footer"></div>`, and `<script src="assets/nav.js"></script>` exactly as in the template. |
| **Incorrect z‑index / stacking** | Side nav appears under header or content. | Keep header at `z-50`, side nav at `z-40`, and main content at default (`auto`). Adjust only if you add new fixed/elements. |
| **Over‑reliance on client‑side JS for essential layout** | Users with JS disabled see a blank page. | The injection runs on every load; however, the basic HTML structure (injection divs) is present, so if JS fails the page will show empty sections—this is acceptable for this internal tool. If broader accessibility is needed, consider server‑side includes. |

## Maintenance

- **Updating shared content**: Edit the relevant file in `components/` or `assets/`; all pages update instantly.
- **Adding a new section** (e.g., a new part):  
  1. Create the HTML file using the template.  
  2. Populate with source content, apply HUD styling, and set correct IDs.  
  3. Add an entry to `components/sidenav.html` (both the top‑level link and submenu items).  
  3. Verify the new page appears in the nav and links work.
- **Changing colors or fonts**: Update the `<script id="tailwind-config">` block and the `<link>` tags in the template; rebuild all pages (or just update the template and reuse it for future pages).

## References

- `references/part7-rebuild.md` – session log of rebuilding part7.html using this skill (component-based approach with Part 1 as design ancestor).
- `references/appendices-rebuild.md` – session log of rebuilding appendices.html (component-based approach with Parts 2/3 as design ancestors).
- `references/history-section-build.md` – session log of constructing the full History section (parts I‑VII + appendices).
- `references/hud-component-spec.md` – detailed spec of the shared components and nav.js (optional).
-feature design ancestor mappings.

## Verification Checklist

- [ ] All nine pages share identical `<head>` (Tailwind config, fonts, custom CSS).  
- [ ] Each page contains exactly three injection divs (`#fb-header`, `#fb-sidenav`, `#fb-footer`) and the nav.js script before `</body>`.  
- [ ] Header, side nav, and footer are visually consistent across pages.  
- [ ] Clicking a side‑nav chapter scrolls to the matching `id` on the page.  
- [ ] Hovering over a part title expands its submenu list.  
- [ ] The active part is highlighted in the side nav (`fb-sidenav-active`) and the corresponding top‑nav item is highlighted (`fb-nav-active`).  
- [ ] Visual style matches the HUD spec (dark mode, Exo 2/Geist/JetBrains Mono, neon green accents, glass panels, HUD borders, corner accents, scanlines where applicable).  
- [ ] No missing content, broken links, or stray tags.

--- 

*End of skill documentation.*