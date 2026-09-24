# Integration Plan: v1.5.1 → v1.6.0

## Changes from ChatGPT Session (2026-01-11)

### UI/UX Improvements
1. ✅ Index banner (clickable navigation)
2. ✅ Clinical panel order (not alphabetical)
3. ✅ Dark teal panel headers (#1a3a4a)
4. ✅ ISO 8601 dates (YYYY-MM-DD)
5. ✅ Unified date columns (same dates ALL panels)
6. ✅ Em-dash for missing values (— in gray)
7. ✅ Patient name in title
8. ❌ NO superscript flags (removed v2.1)
9. ❌ NO variable counts (removed v2.2)

### Panel Order (Clinical Priority)
1. Hémogramme (NFS)
2. Hémostase  
3. Inflammation (CRP, VS)
4. Rénal
5. Hépatique
6. Glycémie / HbA1c
7. Minéraux
8. Nutrition
9. Thyroïde
10. Marqueurs Tumoraux

### Files to Update
- [ ] config/constitution.json (version 1.6.0, clinical panel order)
- [ ] src/renderer.py (implement v1.6.0 spec)
- [ ] docs/HTML_GENERATION_SPEC.md → v1.6.0
- [ ] REPOSITORY_LOCK.md (update version)

### Constitutional Compliance
✅ Truth over completeness (em-dash for missing)
✅ Determinism (same input → same output)
✅ Clinician-first (clinical panel order, navigable)
✅ Evidence (data attributes preserved)
✅ No speculation (colored flags from reference only)

Status: Ready for implementation
