<div align="center">

# 🔬 ChronosLab

### Medical Laboratory Document Intelligence System

**From scattered multilingual lab PDFs → one chronological clinician cockpit**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-v1.6.0-teal.svg)](https://github.com/HyyperNab/ChronosLab)
[![Status](https://img.shields.io/badge/status-architecture%20locked-red.svg)](REPOSITORY_LOCK.md)
[![Constitutional](https://img.shields.io/badge/governance-constitutional-1a3a4a.svg)](CONSTITUTIONAL_AMENDMENT_v1.6.0.md)
[![Languages](https://img.shields.io/badge/normalization-FR%20%7C%20EN%20%7C%20DE-success.svg)](config/analyte_normalization.yaml)

</div>

---

> *Truth over completeness. Silence over speculation. Determinism over cleverness. Clinician-first readability. Datenschutz by design.*

ChronosLab is a **constitution-governed** pipeline that ingests lab result PDFs across multiple languages (French, English, German), normalizes them to a canonical schema, verifies patient identity, and renders a **chronological clinician cockpit** — parameters as rows, dates as columns, flags color-coded — so a clinician can see lab value kinetics at a glance.

📖 **[Read the case study →](docs/CASE_STUDY.md)** — how 5 reports across 6 years and 3 languages became one cockpit showing LDL spike-and-recovery, CRP resolution, and HbA1c improvement.

---

## 🎯 The Problem It Solves

A patient has blood work from **5 different labs**, in **3 languages**, over **6 years**. Each PDF has different units (g/L vs mg/dL), different names (`Hämoglobin` vs `Hemoglobin` vs `Hémoglobine`), and different reference ranges.

**Before**: A clinician manually cross-references 5 PDFs to spot trends.

**After**: One HTML file. Parameters as rows, dates as columns. Flags where values exceed reference ranges. Kinetics visible instantly.

---

## 🚀 Quick Start

```bash
# Install
pip install -r requirements.txt

# PDF OCR (optional): install Tesseract + language packs
sudo apt-get install tesseract-ocr tesseract-ocr-fra tesseract-ocr-deu  # Linux
brew install tesseract tesseract-lang                                    # macOS

# Run with synthetic demo data (no Tesseract needed)
python demo.py

# Run with real PDFs
python demo_ocr.py lab_report_1.pdf lab_report_2.pdf

# View the output
open data/output/<CASE_ID>/clinician_cockpit_table_ft.html
```

---

## 🏗️ Architecture

```
PDFs / JSON
    │
    ▼
┌──────────────┐    ┌───────────────────┐    ┌──────────────────┐
│  OCR Engine  │───▶│ Identity Clustering│───▶│ Table Extraction │
│  (Tesseract) │    │  (HARD FAIL on    │    │ (geometric row/  │
│  FR/EN/DE    │    │   mismatch)       │    │  col detection)  │
└──────────────┘    └───────────────────┘    └────────┬─────────┘
                                                      │
                    ┌──────────────────┐    ┌────────▼─────────┐
                    │  Analyte         │◀───│  Panel Assignment │
                    │  Normalizer      │    │ (via dictionary)  │
                    │  (304 entries)   │    └────────┬─────────┘
                    └──────────────────┘              │
                                                      ▼
                    ┌──────────────────┐    ┌────────────────────┐
                    │    Renderer      │◀───│     Linter         │
                    │  (HTML cockpit)  │    │ (constitutional    │
                    │  Atomic write    │    │  enforcement)      │
                    └──────────────────┘    └────────────────────┘
```

**15 source modules** · **3,765 lines** · **304-entry multilingual dictionary** · **0 JavaScript dependencies**

---

## 📜 Constitutional Governance (Anti-Drift)

ChronosLab is governed by a **constitution** — a versioned, SHA256-hashed JSON file that defines immutable invariants. Changes require a formal amendment process.

| Principle | Enforcement |
|-----------|-------------|
| **Truth over completeness** | Missing data = em-dash `—`. Never infer, fabricate, or interpolate. |
| **Silence over speculation** | No interpretation, trends, or statistics. Only value + reference + flag. |
| **Determinism** | Same input → identical output. No randomization, no "smart" reordering. |
| **Clinician-first** | Clinical panel order, chronological dates, unified columns. |
| **Datenschutz** | No PII in HTML body. Evidence attributes only. Patient name in `<title>` only. |

**Anti-drift protections:**
- Panel order is **locked** — reordering is a constitutional violation
- Renal membership (7 analytes) is **immutable**
- NFS suborder (12 analytes) is **frozen**
- Constitution hash verified on load (tamper detection)
- Linter enforces all invariants with **blocking errors**
- "Helpful" features (statistics, trends, interpretation) are **explicitly forbidden**

See [`REPOSITORY_LOCK.md`](REPOSITORY_LOCK.md) and [`CONSTITUTIONAL_AMENDMENT_v1.6.0.md`](CONSTITUTIONAL_AMENDMENT_v1.6.0.md).

---

## 🛡️ Engineering Quality

| Guarantee | How |
|-----------|-----|
| **No partial output** | Atomic file writes (temp + os.replace) |
| **No silent failures** | All errors are HARD FAIL with explicit messages |
| **No tampering** | Constitution SHA256 hash verification on load |
| **No PII leaks** | Linter scans exports for PII patterns before delivery |
| **No truncation** | Linter verifies all analytes appear in HTML output |
| **No fabrication** | Missing values = em-dash, not "N/A" or estimates |
| **No interpretation** | Flags from reference comparison only — no "improving" labels |
| **Medico-legal traceability** | Every cell has data-page, data-doc, data-bbox, data-confidence |

---

## 📁 Repository Structure

```
chronoslab/
├── config/
│   ├── constitution.json             # Constitutional invariants (v1.6.0, hash-locked)
│   ├── analyte_dictionary.yaml       # Analyte → panel/order mappings
│   └── analyte_normalization.yaml    # FR/EN/DE synonym map (304 entries)
├── src/                              # 15 modules, 3,765 lines
│   ├── chronoslab.py                 # Main orchestrator
│   ├── datatypes.py                  # Canonical data structures
│   ├── config.py                     # Constitution loader + hash verification
│   ├── renderer.py                   # HTML cockpit renderer
│   ├── linter.py                     # Constitutional enforcement
│   ├── ocr_engine.py                 # Tesseract OCR + reference parser
│   ├── identity_clustering.py        # Patient identity verification
│   ├── table_extraction.py           # Table detection from OCR boxes
│   ├── analyte_normalizer.py         # Multilingual normalization
│   ├── qualitative.py                # State-change detection (FR/EN/DE)
│   ├── generation_planner.py        # Token budget planning
│   ├── validation.py                 # Input validation
│   ├── fileio.py                     # Atomic file I/O
│   ├── logging_config.py            # Structured logging
│   └── pdf_processor.py              # Multi-PDF orchestrator
├── docs/
│   ├── CASE_STUDY.md                 # Before/after case study ← start here
│   ├── HTML_GENERATION_SPEC.md       # v1.6.0 HTML spec (active)
│   ├── OCR_INFRASTRUCTURE.md         # OCR pipeline documentation
│   └── SPOF_ANALYSIS.md              # Single-point-of-failure audit
├── data/
│   ├── input/case_demo.json          # Synthetic demo data (no PII)
│   └── output/                       # Generated HTML (gitignored)
├── tests/
│   └── test_spof_fixes.py            # Regression tests
├── demo.py                           # JSON-path demo
├── demo_ocr.py                        # PDF-path demo
├── requirements.txt
├── REPOSITORY_LOCK.md                # Hard lock documentation
└── CONSTITUTIONAL_AMENDMENT_v1.6.0.md # Amendment ratification
```

---

## ❌ Error Handling (No Silent Failures)

| Condition | Behavior |
|-----------|----------|
| Identity mismatch (different patients) | **HARD FAIL** — no interaction, no fallback |
| Missing sample date | **HARD FAIL** — no fallback |
| Constitution hash mismatch | **HARD FAIL** — tamper detected |
| Unknown analyte | Logged as UNKNOWN → MISC panel |
| Invalid datetime | **Blocking lint error** |
| Renal membership violation | **Blocking lint error** |
| NFS suborder violation | **Blocking lint error** |
| PII leak in export | **Blocking lint error** |
| Incomplete HTML render | **Blocking lint error** |

---

## 📊 Version History

| Version | Date | Change |
|---------|------|--------|
| v1.5.0 | 2026-01-10 | OCR infrastructure + FR/EN/DE normalization |
| v1.5.1 | 2026-01-10 | Constitutional compliance (interactive prompts removed) |
| **v1.6.0** | **2026-01-11** | **Clinical UX amendment (index banner, em-dash, unified dates, state-change detection)** |

---

## 📄 License

MIT License — see [LICENSE](LICENSE).

The architecture is governed by a constitutional lock. See [`REPOSITORY_LOCK.md`](REPOSITORY_LOCK.md) for the change policy.

---

<div align="center">

**Architecture locked. Implementation follows spec.**

*No drift. No speculation. No compromise.*

</div>
