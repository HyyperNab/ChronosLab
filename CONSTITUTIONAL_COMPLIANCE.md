# Constitutional Compliance - v1.5.1

## Changes from v1.5.0

### VIOLATIONS CORRECTED

1. **Interactive Identity Verification → REMOVED**
   - Previous: Asked user "Same patient? Y/N"
   - Now: HARD FAIL on mismatch
   - Reason: Breaks determinism + auditability

2. **Fuzzy Matching → CONSTRAINED**
   - Previous: Silent fuzzy matching
   - Now: Logged + LOW confidence tag
   - Reason: Evidence requirements

3. **Fallback Logic → REMOVED**
   - Previous: "Use DOB if no sample date"
   - Now: FAIL if sample date missing
   - Reason: Truth over completeness

### SAFE EXTRACTIONS KEPT

1. ✅ YAML analyte dictionary (304 entries)
   - Exact match: HIGH confidence
   - Synonym match: HIGH confidence  
   - Fuzzy match: LOW confidence + logged

2. ✅ Accent normalization utility
   - é→e, ä→a, ü→u, etc.
   - Evidence-traced
   - Confidence-tagged

### CONSTITUTIONAL PRINCIPLES RESTORED

- ✅ Determinism (same input → same output)
- ✅ Auditability (no user interaction)
- ✅ Evidence preservation (all matches logged)
- ✅ Truth over completeness (no fallbacks)

---

**Status**: CONSTITUTIONAL COMPLIANCE RESTORED
**Version**: v1.5.1
**Lock**: ACTIVE
