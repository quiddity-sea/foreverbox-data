# Stich Design Lesson: Reference Files vs Summaries

> Added 2026-07-23 after three failed redesign attempts

## The Lesson
When redesigning or replicating a design system, NEVER base the work on summaries or DESIGN.md spec files. Always read the ACTUAL implementation files and screenshots.

## What Went Wrong

1. **First attempt**: Built from REDESIGN_BLUEPRINT.md (my summary of the Stich designs). The summary was an approximation.
2. **Second attempt**: Built from DESIGN.md YAML specs (Mythic HUD, Chlorophyll Protocol). These were abstract specs that were never fully implemented.
3. **Third discovery**: The actual Stich designs were standalone Tailwind HTML files with:
   - Dark background (#0b141c), not the #101413 in DESIGN.md
   - Exo 2/Geist/JetBrains Mono, not Libre Caslon Text
   - Glass panels with neon green glow
   - Side navigation, not horizontal dropdowns
   - Self-contained Tailwind CDN, not modular CSS files

## The Fix Pattern
1. Find the ACTUAL rendered HTML/CSS files (not DESIGN.md)
2. Look at screenshots (the project had screen.png files of actual renderings)
3. Open the pages in a browser and use vision_analyze
4. Read the code.html files in the latest version subdirectories
5. Build from the actual implementation, not the abstract spec

## Directory Pattern
Stich stored each design iteration in its own directory:
- `foreverbox_responsive_hud_index/` - latest index
- `foreverbox_part_iv_the_personas_hud/` - latest personas page
- etc.

The latest version is identifiable by naming: "hud" suffix, "responsive" prefix, newer directory names.
