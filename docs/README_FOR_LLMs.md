# README FOR LLMs

**CRITICAL: Read in this exact order before touching code.**

---

## Read Order (Mandatory)

### 1. Constitution First
```bash
config/constitution.json
```
**Why**: Defines frozen invariants. Violations = hard fail.

**Key sections**:
- `panel_order` (frozen)
- `renal_membership_locked` (7 analytes, non-negotiable)
- `nfs_suborder` (frozen)
- `core_principles` (behavioral foundation)

### 2. Lagom Principles
**Core axioms**:
- Truth > completeness
- Silence > speculation
- Determinism > cleverness
- Clinician-first readability
- Datenschutz by design

**What this means**:
- Missing data stays missing (no inference)
- No guessing units/references
- Same input → same output (always)
- Order matches clinical workflow
- Privacy is non-negotiable

### 3. SPOF Documentation
```bash
docs/SPOF_ANALYSIS.md
```
**Why**: 8 SPOFs were eliminated. Don't reintroduce them.

**Critical SPOFs eliminated**:
1. Non-atomic file writes
2. Missing input validation
3. No structured logging
4. Unsafe file I/O
5. No error context
6. Date parsing fragility
7. Config load crashes
8. Silent partial writes

### 4. Data Flow
```
Input JSON → Validation → CaseBundle → Linting → Rendering → HTML
```

**Key modules**:
- `datatypes.py` - Canonical structures
- `validation.py` - Input validation
- `linter.py` - Invariant enforcement
- `renderer.py` - HTML generation

### 5. Code Structure
```bash
src/
├── chronoslab.py       # Orchestrator (start here)
├── datatypes.py        # Data structures
├── config.py           # Config loader
├── renderer.py         # HTML generator
├── linter.py           # Invariant enforcer
├── validation.py       # Input validator
├── fileio.py           # Atomic I/O
└── logging_config.py   # Structured logging
```

---

## Anti-Patterns (Do NOT Do)

### ❌ Never Infer
```python
# WRONG
if not row.unit:
    row.unit = "g/dL"  # NEVER GUESS

# RIGHT
if not row.unit:
    # Leave empty, flag as uncertain
    pass
```

### ❌ Never Reorder Panels
```python
# WRONG
panels_sorted = sorted(panels, key=lambda p: row_count)

# RIGHT
panels_sorted = [p for p in constitution.panel_order if p in panels]
```

### ❌ Never Add "Helpful" Defaults
```python
# WRONG
reference_low = reference_low or 0  # NEVER

# RIGHT
reference_low = reference_low  # Stays None if missing
```

### ❌ Never Silently Fail
```python
# WRONG
try:
    parse_date(date_str)
except:
    pass  # SILENT FAILURE

# RIGHT
try:
    parse_date(date_str)
except ValueError as e:
    raise ValidationError(f"Invalid date: {e}")
```

### ❌ Never Truncate Output
```python
# WRONG
if len(rows) > 100:
    rows = rows[:100]  # TRUNCATION

# RIGHT
# Render ALL rows, calculate parts if needed
plan = planner.plan_generation(case)
```

---

## What ChronosLab IS

- **Epistemic engine** (extracts facts)
- **Timeline builder** (organizes chronologically)
- **Data presenter** (renders without judgment)

## What ChronosLab IS NOT

- ❌ Diagnostic system
- ❌ Treatment recommender
- ❌ Risk predictor
- ❌ Clinical decision engine

---

## Immutability Rules

Changes require:
1. Version bump
2. Written rationale
3. Full revalidation
4. Hash recomputation

**Frozen elements**:
- Panel order
- Renal membership (7 analytes)
- NFS suborder
- Reference policy (never infer)

---

## When Adding Features

### ✅ Good Additions
- Atomic operations
- Error context
- Validation layers
- Evidence preservation
- SPOF elimination

### ❌ Bad Additions
- Inference engines
- Smart defaults
- Auto-corrections
- Predictive models
- "Helpful" modifications

---

## Testing Requirements

Before committing:
```bash
# 1. Run demo
python demo.py

# 2. Check linting passes
# Output should show: ✓ Lint passed

# 3. Verify completeness
# Check: "✓ All N analytes rendered"

# 4. No truncation
# HTML must contain all rows from input
```

---

## Error Handling Pattern

```python
# Always provide context
try:
    operation()
except SpecificError as e:
    logger.error_with_context(e, "operation_name", case_id)
    raise  # Don't swallow
```

---

## Remember

**This is medical data. Errors have consequences.**

- When in doubt, fail explicitly
- Never guess, never infer
- Preserve all evidence
- Make uncertainty visible

**If you're not sure → Ask. Don't improvise.**

---

## Quick Reference

**To validate input**:
```python
from validation import CaseValidator
CaseValidator.validate(data)
```

**To check constitutional compliance**:
```python
from linter import ChronosLabLinter
lint_result = linter.lint_case(case)
```

**To render HTML**:
```python
from renderer import ClinicianCockpitRenderer
renderer.render(case, output_path)
```

**To plan generation**:
```python
from generation_planner import GenerationPlanner
plan = planner.plan_generation(case)
```

---

**Bottom line: Read before writing. Understand before changing.**
