# Document Alignment Workflow (Support Doc → Blueprint)

## When to Use

When a human-facing support/briefing document (e.g., Master Briefing) has been
updated to a new version, and a companion technical blueprint must be realigned
to match — without rewriting the blueprint's entire technical payload.

## Procedure

### 1. Identify the Three Documents

| Role | Typical filename | Purpose |
|------|-----------------|---------|
| Old support doc | `*_V5.md` or earlier | The previous version of the human-facing briefing |
| New support doc | `*_V6*.md` | The updated version — source of truth for changes |
| Old blueprint | `ARCHITECTURE_BLUEPRINT_V2*.md` | The builder-facing technical spec to update |

### 2. Read all three documents in full

Don't skim. The blueprint may be 1,600+ lines. Read it all.

### 3. Diff the support docs

Map every structural change:
- New sections added (note the section number in the new doc)
- Sections removed or condensed
- Section numbering shifted (e.g., V5 §4 → V6 §6)
- New concepts/terminology introduced
- Tone or framing changes that affect cross-references

Produce a mapping table: `Old §X → New §Y`.

### 4. Identify blueprint impact

Scan the blueprint for:
- **Companion document references** (filename, version number)
- **Cross-reference annotations** like `*(Implements Briefing §X)*`
- **Closing lines** that name the companion doc
- **Any section that was directly coupled to old support doc structure**

### 5. Decide: patch or rewrite?

| Criterion | Patch | Rewrite |
|-----------|-------|---------|
| Technical payload (DDL, API, class specs) unchanged | ✓ | Overkill |
| Changes are purely cross-references + framing | ✓ | Overkill |
| Document grew new major sections needing mirrored blueprint sections | Maybe | ✓ |
| Blueprint structure is fundamentally misaligned with new doc | ✗ | ✓ |

**Default to patch** for large (1,000+ line) technical blueprints where the
technical content is correct and only the connective tissue is stale.

### 6. Execute patches (if patching)

Apply in order:
1. Title, version number, date, companion doc filename
2. Every `*(Implements Briefing §X)*` annotation — remap to new numbering
3. Add cross-reference annotations where new doc sections exist but blueprint
   lacks the pointer (e.g., blueprint §6 already covers Hermes, but didn't
   reference V6 §10 — add it)
4. Closing line — update companion doc filename and version
5. Global grep for stale references: `grep -n "V5\|old_filename" blueprint.md`

### 7. Verify

- Zero stale references to old version
- Every cross-reference maps to the correct section in the new doc
- Header and footer show correct version, date, and companion doc
- Total line count change is modest (12 patches across 1,646 lines is normal)

### 8. Compatibility check (optional but recommended)

If the blueprint references external APIs or interfaces (e.g., Hermes
`MemoryProvider` ABC), pull the actual source code and verify the blueprint's
assumptions match reality before finalising.

## Example

This workflow was used to update `ARCHITECTURE_BLUEPRINT_V2 - 2.md` from
companion `The Council Library Master Briefing V5.md` to
`The_Council_Library_Master_Briefing_V6_Technical_Human.md`.

12 surgical patches across a 1,646-line document. Zero DDL statements, API
contracts, class specifications, or concurrency patterns were touched.
