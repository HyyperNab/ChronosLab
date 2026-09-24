# Constitutional Amendment: v1.5.1 → v1.6.0

## Amendment Date: 2026-01-11

## Rationale

ChatGPT session (2026-01-11) produced UI/UX improvements that enhance clinician-first readability while preserving all core constitutional principles. These improvements warrant constitutional amendment rather than rejection.

---

## What Changed

### Panel Order: Alphabetical → Clinical Priority

**v1.5.1** (14 panels, alphabetical):
```
NFS → VS_H1 → VS_H2 → CRP → COAG → RENAL → HEPATIC → 
AMYLASE_LIPASE → LIPIDS → GLUCOSE_A1C → NUTRITION → 
THYROID → TUMOR_MARKERS → MISC
```

**v1.6.0** (10 panels, clinical):
```
1. Hémogramme (NFS)
2. Hémostase (Coagulation)
3. Inflammation (CRP + VS merged)
4. Rénal
5. Hépatique
6. Glycémie / HbA1c
7. Minéraux
8. Nutrition
9. Thyroïde
10. Marqueurs Tumoraux
```

**Justification**: Clinical priority order improves clinician workflow (complete blood → coagulation → inflammation → organ function)

### UI Improvements

| Feature | v1.5.1 | v1.6.0 | Justification |
|---------|--------|--------|---------------|
| Navigation | None | Index banner | Faster panel access |
| Panel headers | Gray | Dark teal #1a3a4a | Professional appearance |
| Missing values | Empty cell | Em-dash — | Clear visual indicator |
| Date columns | Per-panel | Unified (all panels) | Easier comparison |

---

## Core Principles: PRESERVED

| Principle | v1.5.1 | v1.6.0 | Status |
|-----------|--------|--------|--------|
| Truth over completeness | ✓ | ✓ | PRESERVED |
| Silence over speculation | ✓ | ✓ | PRESERVED |
| Determinism | ✓ | ✓ | PRESERVED |
| Clinician-first | ✓ | ✓✓ | **IMPROVED** |
| Datenschutz | ✓ | ✓ | PRESERVED |

**Clinician-first improvements**:
- Clinical panel order (vs arbitrary alphabetical)
- Index banner (quick navigation to any panel)
- Unified date columns (easier horizontal comparison)

---

## What Was REJECTED (Anti-Drift)

During ChatGPT session development:

❌ **Superscript flags (L/H/N)** - Rejected v2.0 → v2.1
- Reason: Visual noise, redundant with color

❌ **"Variables: X" count in headers** - Rejected v2.1 → v2.2
- Reason: Machine language, not clinician-focused

These rejections demonstrate constitutional compliance during iteration.

---

## Panel Membership Changes

### Merged Panels

1. **Inflammation** = CRP + VS_H1 + VS_H2
   - Rationale: All inflammation markers together
   
2. **Hémostase** = COAG
   - Rationale: French clinical terminology

3. **Glycémie / HbA1c** = GLUCOSE_A1C
   - Rationale: Clearer naming

### New Panel

4. **Minéraux** (separate from Rénal)
   - Rationale: Calcium, Magnesium, Phosphorus have distinct clinical context

### Removed Panels

5. **AMYLASE_LIPASE** → Merged into Hépatique
6. **LIPIDS** → Merged into Nutrition
7. **MISC** → Distributed to appropriate panels

---

## Renal Membership: UNCHANGED

**Still locked** (7 analytes):
1. Sodium
2. Potassium
3. Chloride
4. Bicarbonate
5. Calcium → **Now also in Minéraux panel**
6. Magnesium → **Now also in Minéraux panel**
7. Phosphorus → **Now also in Minéraux panel**

**Note**: Electrolytes can appear in BOTH Rénal and Minéraux contexts.

---

## NFS Suborder: UNCHANGED

**Still locked** (12 analytes in exact order):
1. Hemoglobin
2. Hematocrit
3. MCH
4. MCHC
5. MCV
6. WBC
7. Neutrophils
8. Lymphocytes
9. Monocytes
10. Eosinophils
11. Basophils
12. Platelets

---

## Implementation Status

### Completed
- ✅ Constitution updated (v1.6.0)
- ✅ HTML spec updated (v1.6.0)
- ✅ Panel order defined (clinical)
- ✅ Display names defined (French)

### Pending
- ⏳ Renderer implementation (src/renderer.py)
- ⏳ Linter updates (src/linter.py)
- ⏳ Config loader updates (src/config.py)
- ⏳ Test validation

---

## Breaking Changes

**HTML Output**:
- Panel order changed (alphabetical → clinical)
- Panel names changed (English → French)
- Date columns unified (different per panel → same all panels)
- Missing values visible (empty → em-dash)

**Backward Compatibility**: NONE
- v1.6.0 HTML is incompatible with v1.5.1 expectations
- This is intentional (constitutional amendment, not patch)

---

## Migration Notes

**For existing users**:
1. v1.5.1 engine remains stable (code unchanged)
2. v1.6.0 produces new HTML format
3. Old HTML files remain valid (static snapshots)
4. New processing uses v1.6.0 format

**Version selection**: Automatic (constitution.json version field)

---

## Amendment Authority

**Approved by**: User (2026-01-11)
**Rationale**: ChatGPT session demonstrated genuine UX improvements
**Process**: Full constitutional amendment (not hotfix)
**Effective**: v1.6.0 release

---

## Lock Status

**v1.6.0 Panel Order**: 🔒 LOCKED  
**v1.6.0 Display Names**: 🔒 LOCKED  
**Core Principles**: 🔒 LOCKED (unchanged)  
**Renal Membership**: 🔒 LOCKED (unchanged)  
**NFS Suborder**: 🔒 LOCKED (unchanged)

---

## Audit Trail

| Version | Date | Change | Authority |
|---------|------|--------|-----------|
| v1.5.0 | 2026-01-10 | Initial OCR + normalization | Development |
| v1.5.1 | 2026-01-10 | Constitutional compliance fixes | User directive |
| v1.6.0 | 2026-01-11 | Clinical panel order + UX improvements | **This amendment** |

---

**Amendment status**: ✅ RATIFIED  
**Effective version**: v1.6.0  
**HTML spec**: docs/HTML_GENERATION_SPEC.md (v1.6.0)
