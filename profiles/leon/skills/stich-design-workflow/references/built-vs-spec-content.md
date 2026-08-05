# Handling Built/Actual vs. Spec Content in Stich Reconstruction

When reconstructing historical parts for the Stich repository, some source documents contain appended sections documenting what was actually built versus the original specification (e.g., "WHAT WAS ACTUALLY BUILT — July 2026" sections).

## Rule
- **Only include the original specification content** - exclude appended "as-built" or "what was actually built" sections
- The spec content ends before any section header like "WHAT WAS ACTUALLY BUILT" or similar appendices
- These appendices document deviations from the plan and belong in documentation, not in the reconstructed historical part
- When in doubt, refer to earlier parts (1-6) which contain only specification content without build notes

## Example from Session
During the part7.html reconstruction, the source file `/var/www/the-foreverbox-institute/history/the-project/part7-build-manual.html` contained:
1. The original Build Manual specification (content to include)
2. An appended section starting with `<!-- WHAT WAS ACTUALLY BUILT — July 2026 -->` (content to exclude)

The reconstructed part7.html should only contain the specification content, ending before the "WHAT WAS ACTUALLY BUILT" comment.