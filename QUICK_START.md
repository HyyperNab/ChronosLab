# ChronosLab v1.5.1 - Quick Start

## Extract
```bash
tar -xzf chronoslab_v1.5.1_CONSTITUTIONAL.tar.gz
cd chronoslab
```

## Install Dependencies
```bash
pip install -r requirements.txt

# Optional: For PDF OCR
sudo apt-get install tesseract-ocr  # Ubuntu/Debian
brew install tesseract              # macOS
```

## Run
```bash
# From JSON
python demo.py

# From PDFs
python demo_ocr.py your_lab1.pdf your_lab2.pdf your_lab3.pdf
```

## What You Get
- Chronological HTML table
- FR/EN/DE analyte normalization (304 mappings)
- High/Low coloring (blue/red)
- Evidence tracing (data-page, data-doc)
- Constitutional compliance

## Key Features
✓ Multi-language support (FR/EN/DE)
✓ Deterministic (same input → same output)
✓ No user interaction required
✓ Evidence-traced
✓ SPOF-free

## What Happens on Error
- Identity mismatch → HARD FAIL (no prompt)
- Missing sample date → HARD FAIL (no fallback)
- Unknown analyte → Logged as UNKNOWN, placed in MISC panel

No silent failures. All errors explicit.

## Output Location
```
data/output/CASE-XXX/clinician_cockpit_table_ft.html
```

Open in browser to view chronological lab evolution.

---
Version: v1.5.1
Status: Production Ready
Constitutional: Compliant
