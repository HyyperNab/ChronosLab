# OCR Infrastructure Documentation

## Overview

ChronosLab now supports **direct PDF ingestion** with OCR.

**Workflow**:
```
Multiple PDFs → OCR → Identity Verification → Data Extraction → Chronological Merge → HTML Cockpit
```

---

## Components

### 1. OCR Engine (`ocr_engine.py`)

**Purpose**: Extract text from PDF lab results using Tesseract

**Key classes**:
- `PDFOCREngine` - Tesseract wrapper
- `FrenchReferenceParser` - Parses French reference ranges

**Usage**:
```python
from ocr_engine import PDFOCREngine, FrenchReferenceParser

# Initialize
engine = PDFOCREngine(dpi=300, lang="fra")

# Extract text
pages = engine.extract_from_pdf(Path("lab_results.pdf"))

for page in pages:
    print(f"Page {page.page_num}: {page.confidence_avg:.1f}% confidence")
```

**Reference parsing**:
```python
# Parse French reference ranges
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

### 2. Identity Clustering (`identity_clustering.py`)

**Purpose**: Verify multiple PDFs belong to same patient

**Signals used**:
- Patient name
- Date of birth (DOB)
- Patient ID (optional)

**Identity verification**:
```python
from identity_clustering import PatientIdentityClusterer

clusterer = PatientIdentityClusterer()

# Extract identity from OCR text
identity = clusterer.extract_identity(ocr_text, doc_id="DOC-001")

print(f"Name: {identity.name}")
print(f"DOB: {identity.dob}")
print(f"Confidence: {identity.confidence:.1%}")
```

**Mismatch handling**:
```python
# Verify all documents match
identities = [identity1, identity2, identity3]

try:
    same_patient = clusterer.verify_same_patient(
        identities,
        interactive=True  # Ask user if mismatch
    )
except IdentityMismatchError as e:
    # HARD STOP - documents do not match
    print(f"Error: {e}")
```

**Interactive mode**:
If identity mismatch detected, user is prompted:
```
⚠️  IDENTITY MISMATCH DETECTED
============================================================
  Names: DUPONT JEAN, MARTIN PIERRE
  DOBs: 1975-03-15, 1980-07-22

Documents:
  1. lab_jan.pdf
     Name: DUPONT JEAN
     DOB: 1975-03-15
  2. lab_feb.pdf
     Name: MARTIN PIERRE
     DOB: 1980-07-22
============================================================

Are these documents for the SAME patient? (Y/N):
```

If user answers **N** → HARD STOP  
If user answers **Y** → Processing continues

---

### 3. Multi-PDF Processor (`pdf_processor.py`)

**Purpose**: Orchestrate complete PDF ingestion workflow

**Workflow**:
1. OCR each PDF
2. Extract identity from each
3. Verify same patient (**HARD STOP** if mismatch)
4. Extract lab data
5. Merge chronologically
6. Generate case JSON

**Usage**:
```python
from pdf_processor import MultiPDFProcessor

processor = MultiPDFProcessor(ocr_dpi=300, lang="fra")

result = processor.process_multiple_pdfs(
    pdf_paths=[
        Path("lab_jan.pdf"),
        Path("lab_feb.pdf"),
        Path("lab_mar.pdf")
    ],
    output_dir=Path("output"),
    interactive=True
)

print(f"Case ID: {result['case_id']}")
print(f"Rows extracted: {result['rows_extracted']}")
print(f"Case JSON: {result['case_json_path']}")
```

---

## Command-Line Usage

### Demo Script
```bash
python demo_ocr.py lab1.pdf lab2.pdf lab3.pdf
```

**What it does**:
1. OCR all PDFs
2. Extract patient identity
3. Verify same patient (asks if mismatch)
4. Extract lab results
5. Generate HTML cockpit

**Example output**:
```
Processing 3 PDFs:
  1. lab_jan_2024.pdf
  2. lab_feb_2024.pdf
  3. lab_mar_2024.pdf

Processing: lab_jan_2024.pdf
  OCR: 2 pages at 300 DPI
  Avg confidence: 92.3%
  Identity: DUPONT JEAN / 1975-03-15

Processing: lab_feb_2024.pdf
  OCR: 1 page at 300 DPI
  Avg confidence: 89.7%
  Identity: DUPONT JEAN / 1975-03-15

✓ Identity verified: All documents match

Extracted 47 lab results
Saved: output/PAT-12345_extracted.json

Generating HTML cockpit...
✓ SUCCESS

Open: output/PAT-12345/clinician_cockpit_table_ft.html
```

---

## OCR Configuration

### Tesseract Language
Default: **French** (`fra`)

To change:
```python
engine = PDFOCREngine(dpi=300, lang="eng")  # English
```

Available languages (if installed):
- `fra` - French
- `eng` - English
- `deu` - German
- `ita` - Italian
- `spa` - Spanish

### DPI Setting
Default: **300 DPI**

Higher DPI = better accuracy, slower processing:
```python
engine = PDFOCREngine(dpi=400, lang="fra")  # Higher quality
```

Recommended:
- 300 DPI: Standard quality, good balance
- 400 DPI: High quality for poor scans
- 200 DPI: Fast processing, acceptable quality

---

## Error Handling

### OCR Failures
```python
from ocr_engine import OCRError

try:
    pages = engine.extract_from_pdf(pdf_path)
except OCRError as e:
    print(f"OCR failed: {e}")
```

**OCR error signals**:
- `OCRError` - PDF rendering or OCR failure
- Low confidence warning logged if avg < 70%

### Identity Mismatch
```python
from identity_clustering import IdentityMismatchError

try:
    clusterer.verify_same_patient(identities, interactive=False)
except IdentityMismatchError as e:
    print(f"Not same patient: {e}")
    # HARD STOP
```

**Non-interactive mode**: Raises error immediately  
**Interactive mode**: Asks user for confirmation

---

## Data Flow

```
PDF Files
  ↓
OCR (Tesseract)
  ↓
Identity Extraction
  ├─ Name (regex)
  ├─ DOB (date parser)
  └─ Patient ID (regex)
  ↓
Identity Verification
  ├─ Match → Continue
  └─ Mismatch → Ask user or HARD STOP
  ↓
Table Extraction (TODO)
  ├─ Detect tables
  ├─ Extract columns
  └─ Parse rows
  ↓
Canonical Rows
  ↓
Chronological Sort
  ↓
Case JSON
  ↓
ChronosLab Renderer
  ↓
HTML Cockpit
```

---

## TODO: Table Extraction

**Current status**: Identity verification works, table extraction is **PLACEHOLDER**

**Next steps**:
1. Implement table detection from OCR boxes
2. Column alignment (analyte, value, unit, reference)
3. Row parsing
4. Value type detection (numeric vs qualitative)
5. Reference range extraction using `FrenchReferenceParser`

**Approach**:
- Use OCR bounding boxes to detect table structure
- Group boxes by vertical alignment (rows)
- Classify columns by position and content
- Extract values and parse types

---

## Dependencies

**New requirements**:
```
pytesseract>=0.3.10    # Tesseract wrapper
pdf2image>=1.16.0      # PDF to image conversion
Pillow>=10.0.0         # Image processing
pdfplumber>=0.10.0     # PDF text extraction
```

**System requirements**:
- Tesseract OCR engine installed
  - Ubuntu/Debian: `apt-get install tesseract-ocr tesseract-ocr-fra`
  - macOS: `brew install tesseract tesseract-lang`
  - Windows: Download from GitHub

---

## Testing

### Test Reference Parser
```bash
cd chronoslab
python src/ocr_engine.py
```

### Test Identity Extraction
```bash
python src/identity_clustering.py
```

### Test Full Workflow
```bash
python demo_ocr.py path/to/lab1.pdf path/to/lab2.pdf
```

---

## Production Checklist

Before using in production:

- [ ] Install Tesseract system package
- [ ] Install French language data (`tesseract-ocr-fra`)
- [ ] Test OCR on sample PDFs
- [ ] Verify identity extraction accuracy
- [ ] Implement table extraction (currently TODO)
- [ ] Test multi-PDF workflow end-to-end
- [ ] Configure logging level
- [ ] Set up error monitoring

---

## Known Limitations

1. **Table extraction not implemented** - Placeholder in `_extract_lab_rows()`
2. **Single-page table assumption** - Tables spanning pages not handled
3. **Language**: French only (easily extensible)
4. **Reference formats**: Common French formats supported
5. **Identity signals**: Assumes standard lab report format

---

## Next Development Phase

Priority order:
1. Implement table detection from OCR boxes
2. Column classification (analyte, value, unit, ref)
3. Row extraction and parsing
4. Value type detection (numeric vs qualitative)
5. Multi-language support (DE, EN)
6. Complex table handling (merged cells, spans)

---

**Status**: Foundation complete, table extraction pending.
