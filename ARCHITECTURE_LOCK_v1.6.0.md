# ChronosLab v1.6.0 - ARCHITECTURE LOCK

## 🔒 ARCHITECTURE LOCKED - 2026-01-11

**Version**: v1.6.0  
**Status**: PRODUCTION FROZEN  
**Amendment**: Constitutional (v1.5.1 → v1.6.0)  
**Authority**: User directive + ChatGPT session validation

---

## LOCK SCOPE

### ✅ LOCKED FOREVER

**1. Core Principles** (5 immutable)
```
- truth_over_completeness
- silence_over_speculation  
- determinism_over_cleverness
- clinician_first_readability
- datenschutz_by_design
```

**2. Panel Order** (10 clinical panels)
```
Hémogramme → Hémostase → Inflammation → Rénal → Hépatique → 
Glycémie/HbA1c → Minéraux → Nutrition → Thyroïde → Marqueurs Tumoraux
```

**3. Renal Membership** (7 analytes)
```
Sodium, Potassium, Chloride, Bicarbonate,
Calcium, Magnesium, Phosphorus
```

**4. NFS Suborder** (12 analytes)
```
Hemoglobin → Hematocrit → MCH → MCHC → MCV → WBC →
Neutrophils → Lymphocytes → Monocytes → Eosinophils → Basophils → Platelets
```

**5. HTML Structure** (v1.6.0 spec)
- Index banner navigation
- Clinical panel order
- Dark teal headers (#1a3a4a)
- Unified date columns (ISO 8601)
- Em-dash for missing values
- Collapsible `<details>` panels
- Evidence attributes (data-page, data-doc)

---

## UNLOCKED (Extensible)

✅ **Analyte Normalization**
- Add new FR/EN/DE mappings
- Current: 304 entries
- Format: YAML key-value

✅ **Bug Fixes**
- If constitutional-compliant
- Preserve principles
- No breaking changes

✅ **Documentation**
- Clarifications
- Examples
- Guides

✅ **Tests**
- Additional coverage
- Regression suites
- Validation tools

---

## IMPLEMENTATION STATUS

### ✅ Completed (v1.6.0)

- [x] Constitution updated (v1.6.0)
- [x] HTML spec defined (v1.6.0)
- [x] Panel order locked (clinical)
- [x] Display names defined (French)
- [x] Constitutional amendment ratified
- [x] Repository lock updated
- [x] Architecture locked (THIS DOCUMENT)

### ⏳ Pending Implementation

- [ ] Renderer update (src/renderer.py)
- [ ] Linter update (src/linter.py)
- [ ] Config loader (src/config.py)
- [ ] Test validation
- [ ] Package rebuild

**Note**: Architecture is LOCKED. Implementation follows spec.

---

## GOVERNANCE

### Change Authority

**Requires constitutional amendment**:
- Panel order changes
- Core principle modifications
- Locked component changes
- HTML structure changes

**Allowed without amendment**:
- Analyte normalization additions
- Bug fixes (principle-preserving)
- Documentation improvements
- Test additions

### Amendment Process

1. Written rationale
2. Constitutional review
3. Drift analysis
4. User approval
5. Version bump (major.minor.patch)
6. Full regression testing
7. Lock document update

---

## ANTI-DRIFT ENFORCEMENT

### Forbidden Patterns

❌ **"Let's add statistics"**  
→ Violates: Silence over speculation

❌ **"Reorder panels for my workflow"**  
→ Violates: Locked panel order

❌ **"Add helpful badges/indicators"**  
→ Violates: Silence over speculation

❌ **"Use AI to fill missing values"**  
→ Violates: Truth over completeness

❌ **"Make it interactive"**  
→ Violates: Determinism

### Approved Patterns

✅ **"Add German term for HbA1c"**  
→ Analyte normalization (extensible)

✅ **"Fix date parsing bug"**  
→ Bug fix (principle-preserving)

✅ **"Document panel rationale"**  
→ Documentation (no code change)

✅ **"Add test for edge case"**  
→ Test addition (validation)

---

## VERSION CONTROL

### Semantic Versioning

**Major** (X.0.0): Constitutional amendment  
**Minor** (x.Y.0): Feature addition (spec-compliant)  
**Patch** (x.y.Z): Bug fix (no spec change)

**Examples**:
- v1.5.1 → v1.6.0: Constitutional amendment (major)
- v1.6.0 → v1.6.1: Bug fix (patch)
- v1.6.0 → v1.7.0: Feature addition (minor)

### Current Version

**v1.6.0**
- Constitutional: YES (amendment ratified)
- Breaking: YES (HTML output changed)
- Frozen: YES (architecture locked)

---

## IMPLEMENTATION NOTES

### For Developers

**Before coding**:
1. Read `docs/README_FOR_LLMs.md`
2. Read `docs/HTML_GENERATION_SPEC.md` (v1.6.0)
3. Read `CONSTITUTIONAL_AMENDMENT_v1.6.0.md`
4. Read this document

**During coding**:
- Follow spec exactly
- No "improvements" without amendment
- Preserve all principles
- Test against locked components

**After coding**:
- Validate HTML output
- Run linter (constitutional compliance)
- Check no drift introduced
- Document changes

### For Future AI Sessions

**Restoration command**:
```bash
python sync_conversation.py --action restore
```

**Context includes**:
- Version: v1.6.0
- Constitutional: Amendment ratified
- Panel order: Clinical (locked)
- HTML spec: v1.6.0 (active)
- Drift prevention: Active

---

## LOCK CHECKSUM

### Files Under Lock

| File | Version | Hash | Status |
|------|---------|------|--------|
| constitution.json | 1.6.0 | TBD | 🔒 LOCKED |
| HTML_GENERATION_SPEC.md | 1.6.0 | TBD | 🔒 LOCKED |
| REPOSITORY_LOCK.md | 1.6.0 | TBD | 🔒 LOCKED |
| THIS FILE | 1.6.0 | TBD | 🔒 LOCKED |

**Hash algorithm**: SHA256  
**Recompute on**: Any spec change  
**Mismatch action**: Reject change

---

## AUDIT TRAIL

| Date | Version | Change | Authority |
|------|---------|--------|-----------|
| 2026-01-10 | v1.5.0 | OCR + normalization | Development |
| 2026-01-10 | v1.5.1 | Constitutional fixes | User directive |
| 2026-01-11 | v1.6.0 | Clinical UX improvements | **AMENDMENT** |
| 2026-01-11 | v1.6.0 | **Architecture locked** | **THIS DOCUMENT** |

---

## FINAL STATEMENT

**This architecture is FROZEN.**

**Changes require constitutional process.**

**Stability over innovation.**

**Quality over features.**

**Truth over completeness.**

---

**Lock date**: 2026-01-11  
**Lock version**: v1.6.0  
**Lock authority**: Constitutional amendment + User approval  
**Lock scope**: Complete architecture

🔒 **ARCHITECTURE LOCKED**

---

## Contact

**On drift violations**: Revert immediately  
**On amendment requests**: Follow constitutional process  
**On bugs**: Fix with principle preservation  
**On questions**: Read spec first

**Default answer**: Architecture is locked. No changes.

---

**End of lock document.**
