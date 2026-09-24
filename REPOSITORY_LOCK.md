# ChronosLab v1.6.0 - REPOSITORY LOCK

**Date**: 2026-01-11  
**Version**: v1.6.0  
**Status**: HARD LOCKED  
**Codename**: ALLSTARDS  
**Amendment**: Constitutional (v1.5.1 → v1.6.0)

---

## LOCK STATUS: ✅ ACTIVE

This repository is **HARD LOCKED** against drift.

**Changes require**:
1. Version bump
2. Written rationale
3. Constitutional amendment process
4. Validation against HTML_GENERATION_SPEC.md (v1.6.0)
5. Full regression testing

---

## WHAT IS LOCKED

### 1. Panel Order (Clinical v1.6.0)
```
Hémogramme (NFS) → Hémostase → Inflammation → Rénal → Hépatique → 
Glycémie/HbA1c → Minéraux → Nutrition → Thyroïde → Marqueurs Tumoraux
```

**10 panels** (clinical priority order)

**Frozen**. Do not reorder.

### 2. Renal Membership (7 Analytes) - UNCHANGED
```
Sodium, Potassium, Chloride, Bicarbonate, 
Calcium, Magnesium, Phosphorus
```

**Must** be in RENAL panel. Violation = lint failure.

**Note**: Ca/Mg/P can ALSO appear in Minéraux panel.

### 3. NFS Suborder - UNCHANGED
```
Hemoglobin → Hematocrit → MCH/MCHC/MCV → WBC → 
Neutrophils → Lymphocytes → Monocytes → Eosinophils → Basophils → 
Platelets
```

**Frozen**. Do not reorder.

### 4. Core Principles - UNCHANGED
```
1. truth_over_completeness
2. silence_over_speculation
3. determinism_over_cleverness
4. clinician_first_readability
5. datenschutz_by_design
```

**Immutable**. These govern all decisions.

### 5. HTML Generation Rules (v1.6.0)
See: `docs/HTML_GENERATION_SPEC.md`

**New in v1.6.0**:
- Index banner navigation
- Clinical panel order
- Dark teal headers (#1a3a4a)
- Unified date columns
- Em-dash for missing values

**Every rule is mandatory**. No exceptions.

### 6. Analyte Normalization
File: `config/analyte_normalization.yaml`

**304 entries** covering FR/EN/DE variants.

**Extensible** (add new mappings), but existing mappings **frozen**.

---

## WHAT CAN CHANGE

### Safe Additions
✅ New analyte mappings to `analyte_normalization.yaml`  
✅ New panels (if clinically justified)  
✅ Bug fixes (if they don't violate principles)  
✅ Documentation improvements  
✅ Test additions  

### Forbidden Changes
❌ Panel reordering (clinical order locked)  
❌ Renal membership modification  
❌ NFS suborder modification  
❌ Core principle violations  
❌ HTML structure changes (without spec update)  
❌ "Helpful" features (stats, trends, interpretation)  

---

## CODEBASE STRUCTURE

```
chronoslab/ (3,765 lines code + 304 config)
├── config/
│   ├── constitution.json (v1.6.0, LOCKED)
│   ├── analyte_dictionary.yaml
│   └── analyte_normalization.yaml (304 entries, FR/EN/DE)
│
├── src/ (15 modules, 3,765 lines)
│   ├── chronoslab.py (286 lines)
│   ├── datatypes.py (171 lines)
│   ├── config.py (241 lines)
│   ├── renderer.py (442 lines) ← v1.6.0 updates pending
│   ├── linter.py (230 lines) ← v1.6.0 updates pending
│   ├── generation_planner.py (152 lines)
│   ├── validation.py (199 lines)
│   ├── fileio.py (142 lines)
│   ├── logging_config.py (154 lines)
│   ├── qualitative.py (120 lines)
│   ├── ocr_engine.py (250 lines)
│   ├── identity_clustering.py (295 lines)
│   ├── table_extraction.py (536 lines)
│   ├── pdf_processor.py (295 lines)
│   └── analyte_normalizer.py (138 lines)
│
├── docs/
│   ├── HTML_GENERATION_SPEC.md (v1.6.0, ACTIVE)
│   ├── HTML_GENERATION_SPEC_v1.5.1_ARCHIVED.md
│   ├── README_FOR_LLMs.md
│   ├── PRAGMATIC_USAGE.md
│   ├── SPOF_ANALYSIS.md
│   └── OCR_INFRASTRUCTURE.md
│
├── CONSTITUTIONAL_AMENDMENT_v1.6.0.md (RATIFIED)
├── REPOSITORY_LOCK.md (THIS FILE)
├── sync_conversation.py
└── VERSION_LOCK.txt
```

---

## VERSION HISTORY

- **v1.0.0** - Initial release
- **v1.4.3** - SPOF elimination + Generation planning
- **v1.4.4** - Qualitative analysis + Evidence surfacing
- **v1.5.0** - OCR infrastructure + FR/EN/DE normalization
- **v1.5.1** - Constitutional compliance fixes (interactive prompts removed)
- **v1.6.0** - ChatGPT session UX improvements:
  - **CONSTITUTIONAL AMENDMENT**
  - Clinical panel order (10 panels)
  - Index banner navigation
  - Dark teal headers (#1a3a4a)
  - Unified date columns
  - Em-dash for missing values
  - Patient name in title
  - French panel display names

---

## ANTI-DRIFT PROTOCOL

**When Someone Suggests a Change**:

1. **Read** `CONSTITUTIONAL_AMENDMENT_v1.6.0.md` first
2. **Check** if violates core principles
3. **Verify** against `HTML_GENERATION_SPEC.md` (v1.6.0)
4. **If in doubt** → Don't change

**Common Anti-Patterns to Reject**:

❌ "Add statistics to tables"  
→ Violates "Silence over speculation"

❌ "Reorder panels alphabetically"  
→ Violates clinical order (locked v1.6.0)

❌ "Add superscript flags"  
→ Already rejected (ChatGPT v2.0 → v2.1)

❌ "Add variable counts"  
→ Already rejected (ChatGPT v2.1 → v2.2)

❌ "Show empty cells instead of em-dash"  
→ Violates v1.6.0 spec

**Default Answer**: No.

**Only exception**: Bug fixes or spec-compliant additions.

---

## CONTACT ON VIOLATIONS

If you see:
- Panel reordering
- Renal membership changes
- NFS suborder violations
- Core principle violations
- Unauthorized "helpful" features

**Action**: Revert immediately.

**Rationale**: This document + HTML_GENERATION_SPEC.md + CONSTITUTIONAL_AMENDMENT_v1.6.0.md

---

## SUMMARY

**This repository is production medical software.**

**Changes have consequences.**

**Default to stability over innovation.**

**When in doubt, read the spec and don't change.**

---

**Lock effective date**: 2026-01-11  
**Lock authority**: Constitutional amendment v1.6.0  
**Lock scope**: All components

✅ **REPOSITORY LOCKED - v1.6.0**
