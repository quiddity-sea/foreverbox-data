# Tier Naming — Blueprint Consistency Pitfall

**What happened:** The Cognitive Router was implemented with `system1_local`, `system2_light`, `system2_heavy` enum values instead of the blueprint's Layer 1/2/3 naming. The user corrected this.

**Root cause:** "System1/System2" comes from Kahneman's Dual Process Theory terminology, but the blueprint explicitly names them as three distinct layers: Layer 1 Intuitive Reflex, Layer 2 Analytical Engine, Layer 3 Deep Architect. Using System2 with a Light/Heavy split implies two tiers, not three.

**Fix applied:**
- `router.yaml`: `system1_local` → `layer_1_intuitive_reflex`, `system2_light` → `layer_2_analytical_engine`, `system2_heavy` → `layer_3_deep_architect`
- `router/__init__.py`: `ModelTier.SYSTEM1_LOCAL` → `ModelTier.LAYER_1_INTUITIVE_REFLEX`, etc.
- `bin/council-library`: SQL tier names updated
- `agent_registry.token_budget_ledger`: ENUM updated, data migrated, old rows truncated

**Lesson:** Always verify implementation naming against the blueprint's canonical names. Do not introduce alternative naming schemes — even well-known ones. The blueprint is the single source of truth.
