# OCR Infrastructure

## Overview

ChronosLab supports **direct PDF ingestion** with OCR.

**Workflow**:
```
Multiple PDFs → OCR → Identity Verification → Table Extraction → Chronological Merge → HTML Cockpit
```

---

## Components

### 1. OCR Engine (`src/ocr_engine.py`)

**Purpose**: Extract text from PDF lab results using Tesseract

**Key classes**:
- `PDFOCREngine` — Tesseract wrapper with language auto-fallback
- `FrenchReferenceParser` — Parses French/German reference ranges

**Usage**:
```python
from src.ocr_engine import PDFOCREngine, FrenchReferenceParser

engine = PDFOCREngine(dpi=300, lang="eng+fra+deu")
pages = engine.extract_from_pdf(Path("lab_results.pdf"))

for page in pages:
    print(f"Page {page.page_num}: {page.confidence_avg:.1f}% confidence")
```

**Reference parsing**:
```python
low, high, conf = FrenchReferenceParser.parse("Réf: 12.0 - 16.0")
# → low=12.0, high=16.0, conf="HIGH"

low, high, conf = FrenchReferenceParser.parse("< 5")
# → low=None, high=5.0, conf="LOW"
```

**Supported formats**:
- `Réf: 12.0 - 16.0` → HIGH confidence
- `Valeurs usuelles: 135-145` → HIGH confidence
- `Référence : 4,5 - 5,5` → HIGH confidence (handles comma decimals)
- `< 5` → LOW confidence (upper bound only)
- `> 10` → LOW confidence (lower bound only)

---

### 2. Identity Clustering (`src/identity_clustering.py`)

**Purpose**: Verify multiple PDFs belong to the same patient

**Signals used**:
- Patient name (regex extraction)
- Date of birth (DOB)
- Patient ID (optional)

**Identity verification**:
```python
from src.identity_clustering import PatientIdentityClusterer

clusterer = PatientIdentityClusterer()
identity = clusterer.extract_identity(ocr_text, doc_id="DOC-001")

print(f"Name: {identity.name}")
print(f"DOB: {identity.dob}")
print(f"Confidence: {identity.confidence:.1%}")
```

**Mismatch handling** (HARD FAIL — no user interaction):
```python
try:
    same_patient = clusterer.verify_same_patient(identities)
except IdentityMismatchError as e:
    # HARD STOP — documents do not match
    # No prompt, no fallback, no user interaction
    print(f"Error: {e}")
```

If a mismatch is detected, processing stops immediately with an
`IdentityMismatchError`. This is a constitutional requirement: no
interactive prompts (removed in v1.5.1).

---

### 3. Table Extraction (`src/table_extraction.py`)

**Purpose**: Detect and extract structured data from OCR bounding boxes

**Implementation** (fully implemented — not a placeholder):
- `TableExtractor` — groups OCR boxes into rows/columns by geometry
- `LabDataParser` — classifies columns (analyte/value/unit/reference),
  parses values, normalizes analyte names, assigns flags

**Column detection**:
- Groups boxes by Y-position (rows, tolerance: 15px)
- Clusters X-positions into column boundaries (tolerance: 20px)
- Splits tables by vertical gaps (>50px)
- Classifies columns: >70% numeric → value, >50% unit-pattern → unit,
  >50% ref-pattern → reference, else → analyte

**Value parsing**:
- Qualitative: NEG/POS/NEGATIF/POSITIF → `ValueType.QUALITATIVE`
- Inequalities: `<5` → numeric + LOW flag, `>100` → numeric + HIGH flag
- Numeric: `float()` with comma→dot conversion
- Flag determination: value vs reference range → LOW/HIGH/NORMAL

---

### 4. Multi-PDF Processor (`src/pdf_processor.py`)

**Purpose**: Orchestrate complete PDF ingestion workflow

**Workflow**:
1. OCR each PDF (Tesseract, 300 DPI)
2. Extract identity from each (regex: name, DOB, patient ID)
3. Verify same patient (**HARD STOP** if mismatch — no interaction)
4. Extract sample date (**HARD STOP** if missing — no fallback)
5. Extract lab data (table extraction + normalization)
6. Assign panels via `ConfigLoader.resolve_analyte()`
7. Merge chronologically
8. Generate case JSON

**Usage**:
```python
from src.pdf_processor import MultiPDFProcessor
from src.config import ConfigLoader

processor = MultiPDFProcessor(
    ocr_dpi=300,
    lang="eng+fra+deu",
    config_loader=ConfigLoader(Path("config")),  # Required for panel assignment
)

result = processor.process_multiple_pdfs(
    pdf_paths=[Path("lab_jan.pdf"), Path("lab_feb.pdf")],
    output_dir=Path("output"),
)

print(f"Case ID: {result['case_id']}")
print(f"Rows extracted: {result['rows_extracted']}")
```

---

## Command-Line Usage

### Demo Scripts
```bash
# JSON path (no Tesseract needed)
python demo.py

# PDF path (requires Tesseract + language packs)
python demo_ocr.py lab1.pdf lab2.pdf lab3.pdf
```

---

## OCR Configuration

### Tesseract Language
Default: `eng+fra+deu` (multilingual, auto-fallback to available)

```python
engine = PDFOCREngine(dpi=300, lang="fra")  # French only
```

### DPI Setting
Default: **300 DPI** (recommended balance of accuracy and speed)

| DPI | Use case |
|-----|----------|
| 200 | Fast processing, acceptable quality |
| 300 | Standard (recommended) |
| 400 | High quality for poor scans |

---

## Error Handling

### OCR Failures
- `OCRError` — PDF rendering or OCR failure
- Low confidence warning logged if average < 70%

### Identity Mismatch
- `IdentityMismatchError` — HARD STOP, no user interaction
- Constitutional requirement (v1.5.1): interactive prompts removed

### Missing Sample Date
- `PDFProcessingError` — HARD STOP, no fallback
- Document must contain "Date du prélèvement", "Prélevé le", or similar

---

## Dependencies

```
pytesseract>=0.3.10    # Tesseract wrapper
pdf2image>=1.16.0      # PDF to image conversion
Pillow>=10.0.0         # Image processing
pdfplumber>=0.10.0     # PDF text extraction (optional)
```

**System requirements**:
- Tesseract OCR engine installed
  - Ubuntu/Debian: `apt-get install tesseract-ocr tesseract-ocr-fra tesseract-ocr-deu`
  - macOS: `brew install tesseract tesseract-lang`
  - Windows: Download from GitHub

---

**Status**: Fully implemented. All components operational.
