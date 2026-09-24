# HTML Generation Specification v1.6.0
## ChronosLab Clinician Cockpit - IMMUTABLE RULES

**Version**: v1.6.0  
**Status**: HARD LOCK  
**Purpose**: Anti-drift specification for HTML generation  
**Updated**: 2026-01-11 (integrated ChatGPT session v2.2 changes)

---

## CRITICAL PRINCIPLES (NON-NEGOTIABLE)

### 1. Truth Over Completeness
- Missing data = em-dash `—` in light gray `#999`
- Never infer, never interpolate, never estimate
- If value doesn't exist → `<td><span class="missing">—</span></td>`

### 2. Silence Over Speculation
- No "normal", "abnormal", "concerning" labels
- No severity indicators
- Only factual flags: HIGH (blue), LOW (red) via colored bold text
- Flag logic: ONLY based on reference range comparison
- **NO superscript flags** (removed in v2.1)

### 3. Determinism Over Cleverness
- Same input → **identical** HTML output
- No random ordering
- Panel order: **Clinical** (not alphabetical)
- Analyte order: **Per constitution NFS suborder**, others alphabetical within panel

### 4. Clinician-First Readability
- Time flows left to right (chronological)
- Parameters flow top to bottom (by panel)
- Dates: ISO 8601 format `YYYY-MM-DD`
- **Unified date columns**: Same dates across ALL panels
- Collapsible panels: `<details>` tags, all `open` by default

### 5. Datenschutz By Design
- Patient name in title only: `ChronosLab — [PATIENT NAME]`
- Evidence attributes: `data-page`, `data-doc`, `data-bbox` (inspectable, not visible)
- No external resources, no CDN, no tracking

---

## HTML STRUCTURE (v1.6.0)

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ChronosLab — [PATIENT NAME]</title>
    <style>
        /* Inline CSS only */
    </style>
</head>
<body>
    <!-- Index Banner -->
    <nav class="index-banner">
        <a href="#hemogramme">Hémogramme</a>
        <a href="#hemostase">Hémostase</a>
        <a href="#inflammation">Inflammation</a>
        <!-- ... all panels ... -->
    </nav>
    
    <h1>ChronosLab — [PATIENT NAME]</h1>
    
    <!-- Panel 1: Hémogramme -->
    <details class="panel" id="hemogramme" open>
        <summary>Hémogramme (NFS)</summary>
        <table>
            <thead>
                <tr>
                    <th class="var">Variable</th>
                    <th>2024-11-16</th>
                    <th>2024-12-03</th>
                    <!-- ... all dates ... -->
                </tr>
            </thead>
            <tbody>
                <!-- Rows -->
            </tbody>
        </table>
    </details>
    
    <!-- More panels... -->
</body>
</html>
```

---

## NEW FEATURES (v1.6.0)

### 1. Index Banner (Navigation)
```html
<nav class="index-banner">
    <a href="#hemogramme">Hémogramme</a>
    <a href="#hemostase">Hémostase</a>
    <a href="#inflammation">Inflammation</a>
    <a href="#renal">Rénal</a>
    <a href="#hepatique">Hépatique</a>
    <a href="#glycemie">Glycémie / HbA1c</a>
    <a href="#mineraux">Minéraux</a>
    <a href="#nutrition">Nutrition</a>
    <a href="#thyroide">Thyroïde</a>
    <a href="#marqueurs">Marqueurs Tumoraux</a>
</nav>
```

**Style**:
```css
.index-banner {
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 2rem;
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.index-banner a {
    background: white;
    border: 1px solid #dee2e6;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    text-decoration: none;
    color: #495057;
    font-size: 0.9rem;
}

.index-banner a:hover {
    background: #e9ecef;
    border-color: #adb5bd;
}
```

### 2. Panel Headers (Dark Teal)
```html
<details class="panel" id="hemogramme" open>
    <summary>Hémogramme (NFS)</summary>
    ...
</details>
```

**Style**:
```css
.panel summary {
    background: #1a3a4a;  /* Dark teal */
    color: white;
    padding: 0.75rem 1rem;
    cursor: pointer;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.panel summary:hover {
    background: #0f2832;
}
```

### 3. Missing Values (Em-dash)
```html
<td><span class="missing">—</span></td>
```

**Style**:
```css
.missing {
    color: #999;
}
```

### 4. Date Format (ISO 8601)
**Always**: `YYYY-MM-DD`
**Example**: `2024-11-16`

**NOT**:
- ~~16/11/24~~
- ~~Nov 16, 2024~~
- ~~2024-11-16T00:00:00~~

---

## PANEL ORDER (CLINICAL v1.6.0)

**Clinical priority** (not alphabetical):

1. **Hémogramme (NFS)** - `#hemogramme`
2. **Hémostase** - `#hemostase`
3. **Inflammation (CRP, VS)** - `#inflammation`
4. **Rénal** - `#renal`
5. **Hépatique** - `#hepatique`
6. **Glycémie / HbA1c** - `#glycemie`
7. **Minéraux** - `#mineraux`
8. **Nutrition** - `#nutrition`
9. **Thyroïde** - `#thyroide`
10. **Marqueurs Tumoraux** - `#marqueurs`

**Violation = Constitutional breach**

---

## UNIFIED DATE COLUMNS

**CRITICAL**: All panels MUST have same date columns

**Example**:
```
Panel: Hémogramme
Dates: 2024-11-16 | 2024-12-03 | 2025-01-08 | ...

Panel: Hépatique  
Dates: 2024-11-16 | 2024-12-03 | 2025-01-08 | ...  (SAME)
```

**Implementation**:
1. Collect ALL unique dates from case
2. Sort chronologically
3. Use SAME date list for ALL panels
4. If analyte missing for date → em-dash `—`

---

## FLAG COLORING (Simplified v2.1)

**Low values**:
```css
.val.low {
    color: #c1121f;  /* Red */
    font-weight: bold;
}
```

**High values**:
```css
.val.high {
    color: #0066cc;  /* Blue */
    font-weight: bold;
}
```

**NO superscript flags** (removed in v2.1)

---

## REMOVED FEATURES (v2.0 → v2.2)

❌ **Superscript flags** (L/H/N) - Removed in v2.1 (too noisy)  
❌ **"Variables: X" count** - Removed in v2.2 (machine language)  
❌ **French date format** (16/11/24) - Changed to ISO 8601

---

## CSS RULES (Complete v1.6.0)

```css
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    max-width: 1600px;
    margin: 2rem auto;
    padding: 0 2rem;
    background: #fafafa;
}

h1 {
    font-size: 1.75rem;
    font-weight: 600;
    margin-bottom: 2rem;
    color: #212529;
}

/* Index Banner */
.index-banner {
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 2rem;
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.index-banner a {
    background: white;
    border: 1px solid #dee2e6;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    text-decoration: none;
    color: #495057;
    font-size: 0.9rem;
}

.index-banner a:hover {
    background: #e9ecef;
    border-color: #adb5bd;
}

/* Panels */
.panel {
    background: white;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    margin-bottom: 1.5rem;
    overflow: hidden;
}

.panel summary {
    background: #1a3a4a;
    color: white;
    padding: 0.75rem 1rem;
    cursor: pointer;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    user-select: none;
}

.panel summary:hover {
    background: #0f2832;
}

.panel[open] summary {
    border-bottom: 1px solid #dee2e6;
}

/* Tables */
table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9rem;
}

th, td {
    padding: 0.75rem;
    text-align: left;
    border-bottom: 1px solid #f0f0f0;
}

th {
    background: #f8f9fa;
    font-weight: 600;
    position: sticky;
    top: 0;
    z-index: 10;
}

th.var {
    min-width: 200px;
    background: #f8f9fa;
    position: sticky;
    left: 0;
    z-index: 11;
}

/* Values */
.val {
    font-weight: normal;
}

.val.low {
    color: #c1121f;
    font-weight: bold;
}

.val.high {
    color: #0066cc;
    font-weight: bold;
}

.missing {
    color: #999;
}

.unit {
    color: #6c757d;
    font-size: 0.85rem;
    font-weight: normal;
}

.refline {
    color: #adb5bd;
    font-size: 0.8rem;
    font-weight: normal;
}

/* Print */
@media print {
    .index-banner {
        display: none;
    }
    
    .panel {
        page-break-inside: avoid;
    }
    
    .panel summary {
        display: none;
    }
    
    .panel > table {
        display: table !important;
    }
}
```

---

## VALIDATION CHECKLIST (v1.6.0)

Before generating HTML:

- [ ] Panel order matches clinical priority (10 panels)
- [ ] Date format is ISO 8601 (`YYYY-MM-DD`)
- [ ] Unified date columns (same dates ALL panels)
- [ ] Index banner present with all panel links
- [ ] Panel headers dark teal `#1a3a4a`
- [ ] Missing values = em-dash `—` (not empty)
- [ ] Low/High colored bold (no superscripts)
- [ ] All `<details>` have `open` attribute
- [ ] Patient name in title
- [ ] No "Variables: X" count
- [ ] CSS inline in `<style>` tag
- [ ] No external resources

---

## ANTI-DRIFT RULES

**If ChatGPT suggests**:
- "Add superscript flags" → NO (removed v2.1)
- "Add variable count" → NO (removed v2.2)
- "Use French dates" → NO (ISO 8601 only)
- "Make panels alphabetical" → NO (clinical order)
- "Different dates per panel" → NO (unified columns)

**Read this spec first. Follow it exactly.**

---

## VERSION HISTORY

- **v1.5.0** - Original constitutional spec
- **v1.5.1** - Constitutional compliance fixes
- **v1.6.0** - ChatGPT session integration:
  - Index banner navigation
  - Clinical panel order
  - Dark teal headers (#1a3a4a)
  - ISO 8601 dates
  - Unified date columns
  - Em-dash for missing values
  - Removed superscript flags
  - Removed variable counts
  - Patient name in title

---

**HTML = Clinical Data Table. Clean. Navigable. Professional.**

**End of specification. Lock applied.**
