# ChronosLab - Pragmatic Usage Guide

## What It Does

Upload your patient's lab PDFs → Get chronological HTML table

**Works with**:
- French labs ("Hémoglobine glyquée" → HbA1c)
- English labs ("Hemoglobin A1c" → HbA1c)
- German labs ("Glykiertes Hämoglobin" → HbA1c)

**No advanced OCR needed** - Simple normalization handles variants.

---

## Quick Start

### 1. Upload Patient PDFs
```bash
# Place PDFs in data/pdfs/
cp ~/patient_labs_*.pdf data/pdfs/
```

### 2. Run OCR
```bash
python demo_ocr.py data/pdfs/lab_jan.pdf data/pdfs/lab_feb.pdf data/pdfs/lab_mar.pdf
```

### 3. System Will:
1. ✅ OCR each PDF
2. ✅ Extract patient identity
3. ✅ **Ask you if mismatch detected**: "Same patient? Y/N"
4. ✅ Normalize analyte names:
   - "Hémoglobine glyquée" → HbA1c
   - "Hemoglobin A1c" → HbA1c
   - "Glykiertes Hämoglobin" → HbA1c
5. ✅ Extract tables
6. ✅ Sort chronologically
7. ✅ Generate HTML cockpit

### 4. View Results
```
Open: data/output/CASE-XXX/clinician_cockpit_table_ft.html
```

---

## How It Handles Multilingual

### Analyte Normalization
**File**: `config/analyte_normalization.yaml`

**Current mappings**:
```yaml
"Hémoglobine glyquée": "HbA1c"
"Hemoglobin A1c": "HbA1c"
"Glykiertes Hämoglobin": "HbA1c"

"Créatinine": "Creatinine"
"Creatinine": "Creatinine"
"Kreatinin": "Creatinine"

"Glycémie": "Glucose"
"Glucose": "Glucose"
"Glykämie": "Glucose"
```

### Adding New Variants
**Just edit the YAML**:
```yaml
"Your OCR Text": "Canonical Name"
```

**Example**:
```yaml
"Hb glyquée": "HbA1c"
"A1c": "HbA1c"
```

**No code changes needed** - normalizer handles:
- Case insensitive
- Accent removal (é→e, ä→a, etc.)
- Fuzzy matching

---

## OCR Language Support

**Current**: English only (system default)

**To add French/German** (if needed):
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr-fra tesseract-ocr-deu

# macOS
brew install tesseract-lang
```

**But you probably don't need it** - English OCR + normalization handles multilingual analyte names fine.

---

## Identity Verification

### What It Checks
- Patient name
- Date of birth
- Patient ID (if present)

### If Mismatch Detected
```
⚠️  IDENTITY MISMATCH DETECTED
Names: DUPONT JEAN, MARTIN PIERRE

Are these documents for the SAME patient? (Y/N):
```

**Type Y** → Continue processing  
**Type N** → **HARD STOP** (prevents mixing patients)

---

## Sample Workflow

```bash
# You have 3 PDFs for one patient
ls data/pdfs/
# → patient_2024_01.pdf
# → patient_2024_02.pdf  
# → patient_2024_03.pdf

# Run OCR
python demo_ocr.py data/pdfs/patient_*.pdf

# Output:
Processing 3 PDFs...
✓ Identity verified: SMITH JOHN / 1980-05-15
✓ Extracted 42 lab results
✓ HTML: data/output/PAT-12345/clinician_cockpit_table_ft.html

# Open HTML
firefox data/output/PAT-12345/clinician_cockpit_table_ft.html
```

**You see**:
```
Panel: Glucose & HbA1c
Parameter           Jan 15    Feb 20    Mar 10
HbA1c (%)          7.2       6.9       6.5
Glucose (mg/dL)    145       132       118
```

All chronologically sorted. All normalized.

---

## Adding More Analytes

**Just update** `config/analyte_normalization.yaml`:

```yaml
# Thyroid
"TSH": "TSH"
"Thyréostimuline": "TSH"
"Thyroid Stimulating Hormone": "TSH"

# Lipids
"Cholestérol total": "Total Cholesterol"
"Total Cholesterol": "Total Cholesterol"
"Gesamtcholesterin": "Total Cholesterol"

"LDL": "LDL Cholesterol"
"LDL-Cholestérol": "LDL Cholesterol"
"LDL-Cholesterin": "LDL Cholesterol"
```

**Restart** - no code changes.

---

## Tips

### 1. OCR Quality
- 300 DPI is good balance
- Increase to 400 DPI if PDFs are poor quality
- In `demo_ocr.py`: `processor = MultiPDFProcessor(ocr_dpi=400)`

### 2. Unknown Analytes
If OCR extracts something you don't recognize:
1. Check `data/output/CASE-XXX/case_bundle.json`
2. Look for `analyte_raw` field
3. Add mapping to `analyte_normalization.yaml`
4. Re-run

### 3. Date Extraction
System auto-detects sample dates from:
- "Date du prélèvement: XX/XX/XXXX"
- "Prélevé le XX/XX/XXXX"
- "Le XX/XX/XXXX"

If missing → Uses patient DOB as fallback

---

## Troubleshooting

### "No tables detected"
→ PDF might be image-only  
→ Check OCR confidence in logs  
→ Try higher DPI

### "Identity mismatch"
→ Normal if different patients  
→ Type N to stop  
→ Process separately

### "Unknown analyte"
→ Add to `analyte_normalization.yaml`  
→ Re-run

---

## What You Get

**HTML Table**:
- All parameters (rows)
- All dates (columns)
- Chronologically sorted
- High/Low colored (red/blue)
- Collapsible panels
- Evidence traced (data attributes)

**No stats, no badges, no theater** - just your patient's lab evolution over time.

---

**That's it. Upload PDFs → Get table.**
