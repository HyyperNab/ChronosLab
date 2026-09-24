"""
ChronosLab Linter
Enforces constitutional invariants and detects violations.

Harmonization fixes:
- R2: uses the shared is_valid_iso() from validation (was a divergent copy).
- K3: new _check_flag_validity -- flags were never validated; the Flag enum
  was being misused as strings/undefined members elsewhere.
"""

import re
from typing import List
from pathlib import Path

try:
    from .datatypes import CaseBundle, LintResult, CanonicalLabRow, Flag
    from .config import Constitution
    from .validation import is_valid_iso
except ImportError:
    from datatypes import CaseBundle, LintResult, CanonicalLabRow, Flag
    from config import Constitution
    from validation import is_valid_iso


class ChronosLabLinter:
    """
    Enforces ChronosLab constitutional invariants.
    Blocks execution on critical violations.
    """

    def __init__(self, constitution: Constitution):
        self.constitution = constitution

    def lint_case(self, case: CaseBundle) -> LintResult:
        """
        Run all lint checks on a case bundle.

        Args:
            case: CaseBundle to lint

        Returns:
            LintResult with pass/fail and details
        """
        result = LintResult(passed=True)

        # Run all checks
        self._check_panel_misclassification(case, result)
        self._check_renal_membership(case, result)
        self._check_nfs_suborder(case, result)
        self._check_date_ambiguity(case, result)
        self._check_missing_required_fields(case, result)
        self._check_duplicate_rows(case, result)
        self._check_flag_validity(case, result)  # NEW (K3)

        # Determine overall pass/fail
        result.passed = len(result.blocking_errors) == 0

        return result

    def _check_panel_misclassification(self, case: CaseBundle, result: LintResult):
        """Verify analytes are in correct panels"""
        for row in case.canonical_rows_long:
            # Check if analyte is in the panel it claims to be in
            if row.panel_key not in self.constitution.panel_order:
                result.warnings.append(
                    f"Unknown panel '{row.panel_key}' for analyte '{row.analyte_canonical}'"
                )

    def _check_renal_membership(self, case: CaseBundle, result: LintResult):
        """
        HARD CHECK: Verify locked renal analytes are in RENAL panel.
        This is a blocking error per constitution.
        """
        renal_locked = set(self.constitution.renal_membership_locked)

        for row in case.canonical_rows_long:
            if row.analyte_canonical in renal_locked:
                if row.panel_key != "RENAL":
                    result.blocking_errors.append(
                        f"RENAL MEMBERSHIP VIOLATION: '{row.analyte_canonical}' "
                        f"must be in RENAL panel, found in '{row.panel_key}'"
                    )

    def _check_nfs_suborder(self, case: CaseBundle, result: LintResult):
        """
        Verify NFS analytes follow frozen suborder.
        """
        nfs_rows = [r for r in case.canonical_rows_long if r.panel_key == "NFS"]

        if not nfs_rows:
            return

        # Build expected order map
        expected_order = {
            analyte: idx
            for idx, analyte in enumerate(self.constitution.nfs_suborder)
        }

        # Check each NFS analyte has correct order
        for row in nfs_rows:
            canonical = row.analyte_canonical
            if canonical in expected_order:
                expected = expected_order[canonical]
                if row.analyte_order != expected:
                    result.blocking_errors.append(
                        f"NFS SUBORDER VIOLATION: '{canonical}' has order {row.analyte_order}, "
                        f"expected {expected}"
                    )

    def _check_date_ambiguity(self, case: CaseBundle, result: LintResult):
        """
        Check for ambiguous dates. R2: uses the shared is_valid_iso().
        """
        for row in case.canonical_rows_long:
            if row.confidence_datetime < 0.5:
                result.warnings.append(
                    f"Low datetime confidence ({row.confidence_datetime:.2f}) for "
                    f"{row.analyte_canonical} on {row.datetime}"
                )

            # Check for obviously invalid dates
            if not is_valid_iso(row.datetime):
                result.blocking_errors.append(
                    f"DATE AMBIGUITY: Invalid datetime '{row.datetime}' for "
                    f"{row.analyte_canonical}"
                )

    def _check_missing_required_fields(self, case: CaseBundle, result: LintResult):
        """
        Verify all required fields are present.
        """
        required = set(self.constitution.canonical_row_required_fields)

        for idx, row in enumerate(case.canonical_rows_long):
            row_dict = row.to_dict()
            missing = []

            for field in required:
                value = row_dict.get(field)
                if value is None or value == "":
                    missing.append(field)

            if missing:
                result.warnings.append(
                    f"Row {idx} ({row.analyte_canonical}): missing fields {missing}"
                )

    def _check_duplicate_rows(self, case: CaseBundle, result: LintResult):
        """
        Detect duplicate rows (same analyte, same datetime).
        """
        seen = set()

        for row in case.canonical_rows_long:
            key = (row.analyte_canonical, row.datetime[:10])  # Use date only

            if key in seen:
                result.warnings.append(
                    f"Potential duplicate: {row.analyte_canonical} on {row.datetime[:10]}"
                )
            else:
                seen.add(key)

    def _check_flag_validity(self, case: CaseBundle, result: LintResult):
        """
        NEW (K3): ensure every flag is a defined Flag enum member.
        Catches the kind of bug where code produced Flag.NONE / Flag.L /
        ValueType.TEXT (undefined members) that silently broke classification.
        """
        valid_values = {f.value for f in Flag}
        for row in case.canonical_rows_long:
            if row.flag.value not in valid_values:
                result.blocking_errors.append(
                    f"INVALID FLAG: '{row.flag}' for {row.analyte_canonical} "
                    f"(valid values: {sorted(v or 'NORMAL' for v in valid_values)})"
                )

    def lint_export(self, export_path: Path, case: CaseBundle) -> LintResult:
        """
        Lint exported files for PII leaks and completeness.

        Args:
            export_path: Path to exported file
            case: Original case bundle

        Returns:
            LintResult
        """
        result = LintResult(passed=True)

        if not export_path.exists():
            result.blocking_errors.append(f"Export file not found: {export_path}")
            result.passed = False
            return result

        # Read export content
        content = export_path.read_text(encoding='utf-8')

        # Check for PII patterns
        pii_patterns = self.constitution.privacy.get("pii_patterns", [])
        for pattern in pii_patterns:
            matches = re.findall(pattern, content)
            if matches:
                result.blocking_errors.append(
                    f"PII LEAK: Pattern '{pattern}' found {len(matches)} times in export"
                )

        # Check completeness (for HTML exports)
        if export_path.suffix == '.html':
            self._check_html_completeness(content, case, result)

        result.passed = len(result.blocking_errors) == 0
        return result

    def _check_html_completeness(self, html: str, case: CaseBundle, result: LintResult):
        """
        Verify HTML export contains all extracted analytes.
        Anti-truncation check.
        """
        # Count unique analytes in case
        unique_analytes = set(row.analyte_canonical for row in case.canonical_rows_long)

        # Check each analyte appears in HTML
        missing = []
        for analyte in unique_analytes:
            if analyte not in html:
                missing.append(analyte)

        if missing:
            result.blocking_errors.append(
                f"INCOMPLETE RENDER: {len(missing)} analytes missing from HTML: {missing[:5]}"
            )
            result.info.append(
                f"Expected {len(unique_analytes)} analytes, found {len(unique_analytes) - len(missing)}"
            )

    @staticmethod
    def _is_valid_iso_date(date_str: str) -> bool:
        """Backward-compatible wrapper around the shared validator (R2)."""
        return is_valid_iso(date_str)
