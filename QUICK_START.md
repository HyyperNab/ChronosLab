# ChronosLab v1.6.0 - Quick Start

## Install Dependencies
```bash
pip install -r requirements.txt

# Optional: For PDF OCR
sudo apt-get install tesseract-ocr tesseract-ocr-fra tesseract-ocr-deu  # Ubuntu/Debian
brew install tesseract tesseract-lang                                    # macOS
```

## Run
```bash
# From JSON (fastest — no Tesseract needed)
python demo.py

# From PDFs (requires Tesseract + language packs)
python demo_ocr.py your_lab1.pdf your_lab2.pdf your_lab3.pdf
```

## What You Get
- Chronological HTML clinician cockpit (dark theme, collapsible panels)
- FR/EN/DE analyte normalization (304 mappings)
- High/Low coloring (red/blue) — only when reference ranges exist
- Evidence tracing (data-page, data-doc, data-bbox attributes)
- Index banner navigation, em-dash for missing values
- Constitutional compliance (anti-drift governance)

## Key Features
✓ Multi-language support (FR/EN/DE)
✓ Deterministic (same input → same output)
✓ No user interaction required (HARD FAIL on errors)
✓ Evidence-traced (medico-legal defensibility)
✓ Atomic file writes (no partial output on crash)
✓ Constitution hash verification (tamper detection)

## What Happens on Error
- Identity mismatch → HARD FAIL (no prompt, no fallback)
- Missing sample date → HARD FAIL (no fallback)
- Unknown analyte → Logged as UNKNOWN, placed in MISC panel
- Constitution hash mismatch → HARD FAIL (tamper detected)

No silent failures. All errors explicit.

## Output Location
```
data/output/CASE-XXX/clinician_cockpit_table_ft.html
```

Open in browser to view chronological lab evolution.

---
Version: v1.6.0
Status: Production Ready
Constitutional: Compliant
