# HTML Generation Specification
## ChronosLab Clinician Cockpit - IMMUTABLE RULES

**Version**: v1.5.0  
**Status**: HARD LOCK  
**Purpose**: Anti-drift specification for HTML generation

---

## CRITICAL PRINCIPLES (NON-NEGOTIABLE)

### 1. Truth Over Completeness
- Missing data = empty cell (not "N/A", not "-", not "—")
- Never infer, never interpolate, never estimate
- If value doesn't exist → cell is literally empty: `<td></td>`

### 2. Silence Over Speculation
- No "normal", "abnormal", "concerning" labels
- No green/yellow/red severity indicators
- Only factual flags: HIGH (blue), LOW (red), LL (dark red), HH (dark blue)
- Flag logic: ONLY based on reference range comparison

### 3. Determinism Over Cleverness
- Same input → **identical** HTML output
- No random ordering, no "smart" grouping
- Panel order: **Constitutionally frozen**
- Analyte order: **Per constitution NFS suborder**, others alphabetical within panel

### 4. Clinician-First Readability
- Time flows left to right (chronological)
- Parameters flow top to bottom (by panel)
- No pivoting, no transposing
- Headers: Dates (not "Test 1", "Test 2")

### 5. Datenschutz By Design
- No PII in HTML (name, DOB, ID only in <title> if needed)
- Evidence attributes: `data-page`, `data-doc`, `data-bbox` (inspectable, not visible)
- No external resources, no CDN, no tracking

---

## HTML STRUCTURE (IMMUTABLE)

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>ChronosLab - Case [CASE_ID]</title>
    <style>
        /* Inline CSS only - no external files */
    </style>
</head>
<body>
    <h1>Chronological Lab Results</h1>
    <p class="meta">Case ID: [CASE_ID] | Generated: [TIMESTAMP]</p>
    
    <!-- Panels in constitutional order -->
    <details class="panel" open>
        <summary><span class="chev">▶</span> [PANEL_NAME]</summary>
        <div class="panelBody">
            <table>...</table>
        </div>
    </details>
</body>
</html>
```

---

## TABLE STRUCTURE

```html
<table>
    <thead>
        <tr>
            <th class="var">Variable</th>
            <th>2024-01-15</th>
            <th>2024-02-20</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <th class="var">
                Hemoglobin <span class="unit">(g/dL)</span><br>
                <span class="refline">ref: 12–16</span>
            </th>
            <td data-page="1" data-doc="DOC-001">
                <span class="val">13.2</span>
            </td>
            <td data-page="1" data-doc="DOC-002">
                <span class="val low">11.8</span>
            </td>
        </tr>
    </tbody>
</table>
```

---

## PANEL ORDER (FROZEN)

1. NFS - Hémogramme
2. VS_H1, VS_H2
3. CRP
4. COAG
5. **RENAL** ← 7 locked analytes
6. HEPATIC
7. AMYLASE_LIPASE
8. LIPIDS
9. GLUCOSE_A1C
10. NUTRITION
11. THYROID
12. TUMOR_MARKERS
13. MISC

**Non-negotiable. Violation = rebuild required.**

---

## RENAL MEMBERSHIP (LOCKED)

Must be in RENAL panel:
1. Sodium
2. Potassium
3. Chloride
4. Bicarbonate
5. Calcium
6. Magnesium
7. Phosphorus

---

## NFS SUBORDER (LOCKED)

1. Hemoglobin
2. Hematocrit
3. MCH, MCHC, MCV
4. WBC
5. Neutrophils → Lymphocytes → Monocytes → Eosinophils → Basophils
6. Platelets

---

## FLAG CLASSES

```css
.val { font-weight: normal; }
.val.low { color: #d32f2f; font-weight: bold; }
.val.high { color: #1976d2; font-weight: bold; }
.val.ll { color: #b71c1c; font-weight: bold; }
.val.hh { color: #0d47a1; font-weight: bold; }
```

Mapping:
- Flag.NONE → no class
- Flag.L → `low`
- Flag.H → `high`
- Flag.LL → `ll`
- Flag.HH → `hh`

**No other flags allowed.**

---

## EVIDENCE ATTRIBUTES

Every value cell:
```html
<td data-page="[NUM]" 
    data-doc="[ID]" 
    data-bbox="[X,Y,W,H]" 
    data-confidence="[0-1]">
```

Not visible to user. Inspectable in dev tools.

---

## EMPTY CELLS

```html
<td data-page="" data-doc=""></td>
```

**NOT**:
- `<td>-</td>`
- `<td>N/A</td>`
- `<td>&nbsp;</td>`

---

## REFERENCE RANGES

Show ONLY if both low AND high exist:
```html
<span class="refline">ref: 12–16</span>
```

Omit if only low or only high.

---

## FORBIDDEN ELEMENTS

**NEVER include**:
- ❌ Statistics (mean, median)
- ❌ Trend arrows (↑↓)
- ❌ Graphs/sparklines
- ❌ "Normal"/"Abnormal" labels
- ❌ Severity indicators
- ❌ Auto-interpretation
- ❌ External JS/CSS
- ❌ CDN resources
- ❌ Analytics

---

## VALIDATION CHECKLIST

- [ ] Panel order matches constitution
- [ ] NFS suborder correct
- [ ] Renal membership correct
- [ ] Dates chronological
- [ ] Evidence attributes present
- [ ] Flags correct (low/high/ll/hh only)
- [ ] Empty cells truly empty
- [ ] CSS inline
- [ ] No external resources

---

## ANTI-DRIFT

**When tempted to add features**:
1. Read "Truth over completeness"
2. Read "Silence over speculation"
3. Don't add it

**When panel order seems wrong**:
1. Check constitution
2. Follow constitution
3. Don't reorder

---

**HTML = Data Table. Nothing More.**

Rows = Parameters  
Columns = Dates (chronological)  
Values = Facts (with evidence)  
Colors = Flags (HIGH/LOW from reference)

**Clinician sees data. Clinician decides.**

**End of specification. Lock applied.**
