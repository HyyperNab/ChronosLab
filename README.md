# ChronosLab v1.6.0

**Medical laboratory document intelligence system.**

> *Truth over completeness. Silence over speculation. Determinism over cleverness. Clinician-first readability. Datenschutz by design.*

ChronosLab ingests lab result PDFs (or pre-extracted JSON), normalizes analyte names across FR/EN/DE, verifies patient identity across multiple documents, merges results chronologically, and renders a **clinician cockpit** — a collapsible, color-coded HTML table showing lab value kinetics over time.

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# For PDF OCR (optional): install Tesseract
sudo apt-get install tesseract-ocr tesseract-ocr-fra tesseract-ocr-deu  # Debian/Ubuntu
brew install tesseract tesseract-lang                                    # macOS

# Run with synthetic demo data
python demo.py

# Run with real PDFs
python demo_ocr.py lab_report_1.pdf lab_report_2.pdf
```

Output: `data/output/<CASE_ID>/clinician_cockpit_table_ft.html` — open in any browser.

---

## What It Does

```
PDFs (or JSON) → OCR → Identity Verification → Analyte Normalization →
Table Extraction → Panel Assignment → Constitutional Lint → HTML Cockpit
```

- **OCR**: Tesseract-based, 300 DPI, word-level bounding boxes (FR/EN/DE)
- **Identity Clustering**: Name + DOB + Patient ID — HARD FAIL on mismatch
- **Analyte Normalization**: 304-entry FR/EN/DE lookup + fuzzy matching
- **Table Extraction**: Geometric row/column detection from OCR boxes
- **Panel Assignment**: Maps analytes to clinical panels via dictionary
- **Linter**: Enforces constitutional invariants (renal membership, NFS suborder, PII checks, completeness)
- **Renderer**: Chronological cockpit with collapsible panels, evidence attributes, color-coded flags

---

## Constitutional Principles (Immutable)

| Principle | Meaning |
|-----------|---------|
| **Truth over completeness** | Missing data = em-dash `—`. Never infer, fabricate, or interpolate. |
| **Silence over speculation** | No interpretation, no trends, no statistics. Only value + reference + flag. |
| **Determinism** | Same input → identical output. No randomization. |
| **Clinician-first** | Clinical panel order, chronological dates, unified columns. |
| **Datenschutz** | No PII in HTML exports. Evidence attributes only. Patient name in `<title>` only. |

---

## Panel Order (Clinical, Locked)

```
NFS → Hémostase → Inflammation → Rénal → Hépatique →
Glycémie/HbA1c → Minéraux → Nutrition → Thyroïde → Marqueurs Tumoraux
```

**Panel reordering is a constitutional violation.**

---

## Repository Structure

```
chronoslab/
├── config/
│   ├── constitution.json            # Constitutional invariants (v1.6.0, LOCKED)
│   ├── analyte_dictionary.yaml      # Analyte → panel/order mappings
│   └── analyte_normalization.yaml   # FR/EN/DE synonym map (304 entries)
├── src/                             # 15 modules
│   ├── chronoslab.py                # Main orchestrator
│   ├── datatypes.py                 # Canonical data structures
│   ├── config.py                    # Constitution loader + hash verification
│   ├── renderer.py                  # HTML cockpit renderer (v1.6.0)
│   ├── linter.py                    # Constitutional enforcement
│   ├── ocr_engine.py                # Tesseract OCR + French reference parser
│   ├── identity_clustering.py       # Patient identity verification
│   ├── table_extraction.py          # Table detection from OCR boxes
│   ├── analyte_normalizer.py        # Multilingual analyte normalization
│   ├── qualitative.py               # Qualitative state-change detection
│   ├── generation_planner.py        # Token budget planning
│   ├── validation.py                # Input validation
│   ├── fileio.py                    # Atomic file I/O
│   ├── logging_config.py            # Structured logging
│   └── pdf_processor.py             # Multi-PDF orchestrator
├── docs/
│   ├── HTML_GENERATION_SPEC.md      # v1.6.0 HTML spec (active)
│   ├── HTML_GENERATION_SPEC_v1.5.1_ARCHIVED.md
│   ├── OCR_INFRASTRUCTURE.md
│   └── ...
├── data/
│   ├── input/case_demo.json          # Synthetic demo data
│   └── output/                      # Generated HTML (gitignored)
├── demo.py                          # JSON-path demo
├── demo_ocr.py                      # PDF-path demo
├── requirements.txt
├── REPOSITORY_LOCK.md               # Hard lock documentation
├── ARCHITECTURE_LOCK_v1.6.0.md
└── CONSTITUTIONAL_AMENDMENT_v1.6.0.md
```

---

## Error Handling

| Condition | Behavior |
|-----------|----------|
| Identity mismatch (different patients) | **HARD FAIL** — no user interaction |
| Missing sample date | **HARD FAIL** — no fallback |
| Unknown analyte | Logged as UNKNOWN, placed in MISC panel |
| Invalid datetime | **Blocking lint error** |
| Renal membership violation | **Blocking lint error** |
| NFS suborder violation | **Blocking lint error** |
| PII leak in export | **Blocking lint error** |

No silent failures. All errors explicit.

---

## Version History

| Version | Date | Change |
|---------|------|--------|
| v1.5.0 | 2026-01-10 | OCR infrastructure + FR/EN/DE normalization |
| v1.5.1 | 2026-01-10 | Constitutional compliance (interactive prompts removed) |
| **v1.6.0** | **2026-01-11** | **Clinical UX amendment (index banner, teal, em-dash, unified dates)** |

---

## License

This software is governed by a constitutional lock. See `REPOSITORY_LOCK.md` for change policy.

**Architecture locked. Implementation follows spec. No drift. No speculation. No compromise.**
