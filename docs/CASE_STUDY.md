# Case Study: From Scattered Lab Reports to Chronological Cockpit

## The Problem

A patient has lab results from **5 different blood draws** spanning **6 years** (2020–2026), across **multiple laboratories** and **3 languages** (French, English, German). Each report is a separate PDF with different:

- Reference ranges (some missing entirely)
- Units (g/L vs mg/dL vs mg/L)
- Analyte naming (`Hämoglobin` / `Hemoglobin` / `Hémoglobine`)
- Date formats (DD/MM/YYYY, YYYY-MM-DD)
- Layouts (no standardized table structure)

**The clinician's challenge**: spotting trends across time. Is the LDL improving? Did the CRP spike resolve? Is HbA1c creeping up? With 5 separate PDFs, the answer requires manual cross-referencing — error-prone and time-consuming.

---

## The Solution

ChronosLab ingests all reports, normalizes them to a single canonical schema, and renders one **chronological cockpit** — parameters as rows, dates as columns, flags color-coded.

### Input
```
5 PDFs / HTML reports (2020-01-03 → 2026-09-18)
Languages: French, English, German
Units: g/L, mg/dL, mg/L, U/L, %, /µL, /nL, mU/L
Missing: Some reference ranges, some timepoints
```

### Processing
```
PDF/HTML → OCR (Tesseract) → Identity verification (HARD FAIL on mismatch)
→ Table extraction (geometric) → Analyte normalization (304-entry FR/EN/DE map)
→ Unit conversion (deterministic SI) → Panel assignment (constitution-locked)
→ Flag computation (value vs reference) → Chronological merge → HTML render
```

### Output
One HTML file: `clinician_cockpit_table_ft.html`

- **8 panels** in clinical priority order
- **55 analytes** across **5 date columns**
- **19 flags** (9 HIGH, 10 LOW) — color-coded only where reference ranges exist
- **Index banner** for navigation
- **Em-dash** for missing values (no fabrication)
- **Evidence attributes** (data-page, data-doc) for medico-legal traceability
- **Atomic write** (no partial output on crash)

---

## The Kinetics Revealed

The chronological view immediately surfaces clinically meaningful trends:

| Analyte | 2020-01 | 2020-12 | 2024-12 | 2026-01 | 2026-09 | What it tells the clinician |
|---------|---------|---------|---------|---------|---------|-----------------------------|
| **LDL** | — | 101 | **146** ⚠️ | 100 | **121** ⚠️ | Spike → recovery → creeping back up |
| **CRP** | 3 | **6** ⚠️ | — | 0.86 | 0.7 | Acute inflammation resolved |
| **HbA1c** | **5.7** ⚠️ | — | 5.2 | 4.8 | 5.2 | Prediabetic range → improved |
| **TSH** | 1.18 | 1.43 | 2.82 | **4.00** | 2.36 | Peak at upper limit → normalized |
| **Neutrophils** | 3800 | 2100 | 2650 | **1650** ⚠️ | 2780 | Transient neutropenia → recovered |
| **Lymphocytes** | 2500 | 3000 | 2720 | **3410** ⚠️ | 2500 | Reactive peak → resolved |

These patterns are **invisible** when viewing each report separately. They become **obvious** in the chronological cockpit.

---

## How It Stays Honest

ChronosLab does **not**:

- ❌ Fabricate missing values (em-dash `—` instead)
- ❌ Color values without reference ranges (silence over speculation)
- ❌ Add statistics, trends, or clinical interpretation (no "improving" labels)
- ❌ Show patient PII in the HTML body (Datenschutz)
- ❌ Use external resources, JavaScript, or tracking
- ❌ Silently fail (all errors are HARD FAIL with explicit messages)

ChronosLab **does**:

- ✅ Show raw measured values with evidence tracing
- ✅ Color-code HIGH/LOW flags — but only from reference range comparison
- ✅ Detect qualitative state changes (NEG→POS) with cross-language normalization
- ✅ Verify patient identity across documents (HARD STOP on mismatch)
- ✅ Verify constitution integrity via SHA256 hash (tamper detection)
- ✅ Write files atomically (no partial output on crash)

---

## Architecture in One Sentence

A **constitution-governed**, **deterministic**, **multilingual** pipeline that transforms scattered lab PDFs into a single chronological clinician cockpit — with anti-drift protections that prevent the system from "helpfully" fabricating data it doesn't have.

---

## Technical Highlights

| Capability | Implementation |
|-----------|---------------|
| Multilingual normalization | 304-entry FR/EN/DE analyte dictionary with fuzzy matching |
| Anti-drift governance | Constitution with SHA256 hash, locked panel order, linter enforcement |
| OCR | Tesseract 300 DPI, word-level bounding boxes, language auto-fallback |
| Identity verification | Regex extraction (name/DOB/ID), HARD FAIL on mismatch |
| Table extraction | Geometric row/column detection from OCR bounding boxes |
| Unit conversion | Deterministic SI (g/L→mg/dL ×100, mg/L→mg/dL ÷10) |
| Atomic writes | Temp file + os.replace (no partial output) |
| Evidence tracing | data-page, data-doc, data-bbox, data-confidence attributes |
| PII protection | Linter checks export for PII patterns before delivery |

---

## Try It

```bash
# JSON path (no Tesseract needed)
python demo.py

# See the output
open data/output/CASE-001-DEMO/clinician_cockpit_table_ft.html
```

---

*ChronosLab v1.6.0 — Truth over completeness. Silence over speculation.*
