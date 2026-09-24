"""
ChronosLab Main Orchestrator
Coordinates the complete pipeline from PDF ingestion to HTML export.

Harmonization fixes:
- C10: _build_case_bundle now reads patient_name / patient_dob (were dropped
  on the JSON path -> renderer couldn't put the name in <title>).
- C7: mojibake in verify_constitution_integrity print strings fixed; uses logger.
- NOTE: load_constitution() is intentionally called WITHOUT verify_hash.
  verify_hash=True currently ALWAYS fails because config.py has two
  inconsistent hash methods (_compute_file_hash hashes raw bytes including the
  hash field; save_constitution_hash hashes normalized JSON without it).
  Enabling it would break startup. Left off until the hash methods are
  reconciled and the locked constitution is re-hashed (amendment process).
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

try:
    from .config import ConfigLoader
    from .datatypes import CaseBundle, CanonicalLabRow, LintResult
    from .linter import ChronosLabLinter
    from .renderer import ClinicianCockpitRenderer
    from .generation_planner import GenerationPlanner
    from .fileio import safe_write_json, FileIOError
    from .validation import CaseValidator, ValidationError
    from .logging_config import get_logger
except ImportError:
    from config import ConfigLoader
    from datatypes import CaseBundle, CanonicalLabRow, LintResult
    from linter import ChronosLabLinter
    from renderer import ClinicianCockpitRenderer
    from generation_planner import GenerationPlanner
    from fileio import safe_write_json, FileIOError
    from validation import CaseValidator, ValidationError
    from logging_config import get_logger


class ChronosLab:
    """
    Main ChronosLab orchestrator.

    Coordinates:
    - Configuration loading
    - PDF ingestion
    - Data extraction
    - Linting
    - Export generation
    """

    def __init__(self, config_dir: Path, log_file: Optional[Path] = None):
        """
        Initialize ChronosLab.

        Args:
            config_dir: Directory containing constitution.json and policies
            log_file: Optional path for log file
        """
        self.config_dir = Path(config_dir)
        self.config_loader = ConfigLoader(self.config_dir)
        self.logger = get_logger(log_file=log_file)

        # Load constitution (verify_hash intentionally OFF -- see module docstring)
        self.constitution = self.config_loader.load_constitution()

        # Initialize components
        self.linter = ChronosLabLinter(self.constitution)
        self.planner = GenerationPlanner(self.constitution)
        self.renderer = ClinicianCockpitRenderer(self.constitution)

        self.logger.info(f"ChronosLab v{self.constitution.version} initialized")

    def process_case_from_json(
        self,
        case_json_path: Path,
        output_dir: Path,
        verify_integrity: bool = True
    ) -> Dict[str, Any]:
        """
        Process a case from pre-extracted JSON data.

        Args:
            case_json_path: Path to JSON file with canonical_rows_long
            output_dir: Where to save outputs
            verify_integrity: Run linting checks

        Returns:
            Processing result with status and paths
        """
        self.logger.info(f"Processing case from: {case_json_path.name}")

        # Load and validate case data
        try:
            with open(case_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.logger.error(f"Case file not found: {case_json_path}")
            return {"status": "ERROR", "error": "File not found"}
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in {case_json_path}: {e}")
            return {"status": "ERROR", "error": f"Invalid JSON: {e}"}

        # Validate structure
        try:
            CaseValidator.validate(data)
        except ValidationError as e:
            self.logger.error(f"Validation failed: {e}")
            return {"status": "VALIDATION_FAILED", "error": str(e)}

        # Build CaseBundle
        try:
            case = self._build_case_bundle(data)
        except Exception as e:
            self.logger.log_error_with_context(e, "case bundle creation")
            return {"status": "ERROR", "error": str(e)}

        self.logger.info(f"Loaded {len(case.canonical_rows_long)} rows for case {case.case_id}")

        # Plan generation strategy
        plan = self.planner.plan_generation(case)
        self.planner.print_plan(plan)

        # Create output directory
        case_output_dir = output_dir / case.case_id
        case_output_dir.mkdir(parents=True, exist_ok=True)

        results = {
            "case_id": case.case_id,
            "status": "SUCCESS",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "outputs": {},
            "lint_results": {},
            "stats": {}
        }

        # Lint case if requested
        if verify_integrity:
            self.logger.info("Running linter...")
            lint_result = self.linter.lint_case(case)
            results["lint_results"]["case"] = lint_result.to_dict()

            if not lint_result.passed:
                self.logger.log_lint_result(case.case_id, False, len(lint_result.blocking_errors), len(lint_result.warnings))
                for error in lint_result.blocking_errors:
                    self.logger.error(f"  {error}")
                results["status"] = "LINT_FAILED"
                return results
            else:
                self.logger.log_lint_result(case.case_id, True, 0, len(lint_result.warnings))

        # Generate clinician cockpit HTML
        self.logger.info("Generating clinician cockpit...")
        cockpit_path = case_output_dir / "clinician_cockpit_table_ft.html"

        try:
            stats = self.renderer.render(case, cockpit_path)
            results["outputs"]["clinician_cockpit"] = str(cockpit_path)
            results["stats"] = stats
            self.logger.log_export(case.case_id, "HTML cockpit", cockpit_path, True)
        except Exception as e:
            self.logger.log_error_with_context(e, "rendering cockpit", case.case_id)
            results["status"] = "RENDER_FAILED"
            return results

        # Lint export
        if verify_integrity:
            self.logger.info("Verifying export...")
            export_lint = self.linter.lint_export(cockpit_path, case)
            results["lint_results"]["export"] = export_lint.to_dict()

            if not export_lint.passed:
                self.logger.error(f"Export verification failed")
                for error in export_lint.blocking_errors:
                    self.logger.error(f"  {error}")
                results["status"] = "EXPORT_FAILED"
            else:
                self.logger.info("Export verification passed")

        # Save case bundle as JSON
        bundle_path = case_output_dir / "case_bundle.json"
        try:
            safe_write_json(bundle_path, case.to_dict())
            results["outputs"]["case_bundle"] = str(bundle_path)
        except FileIOError as e:
            self.logger.error(f"Failed to save case bundle: {e}")

        # Save lint results
        if verify_integrity:
            lint_path = case_output_dir / "lint_report.json"
            try:
                safe_write_json(lint_path, results["lint_results"])
                results["outputs"]["lint_report"] = str(lint_path)
            except FileIOError as e:
                self.logger.error(f"Failed to save lint report: {e}")

        self.logger.log_case_processing(case.case_id, results["status"])
        return results

    def _build_case_bundle(self, data: Dict[str, Any]) -> CaseBundle:
        """
        Build CaseBundle from loaded JSON data.

        Args:
            data: Loaded JSON with canonical_rows_long

        Returns:
            CaseBundle
        """
        from datatypes import (
            CanonicalLabRow, ReferenceRange, SourceTrace,
            ValueType, Flag, DatetimePrecision
        )

        case_id = data.get("case_id", "CASE-UNKNOWN")

        # Parse rows
        rows = []
        for row_data in data.get("canonical_rows_long", []):
            # Build reference
            ref = ReferenceRange(
                text_raw=row_data.get("reference_text_raw"),
                low=row_data.get("reference_low"),
                high=row_data.get("reference_high"),
                unit_raw=row_data.get("reference_unit_raw")
            )

            # Build source trace if present
            source_trace = None
            if row_data.get("source_trace"):
                st = row_data["source_trace"]
                source_trace = SourceTrace(
                    doc_id=st.get("doc_id", ""),
                    page=st.get("page", 0),
                    text_span=st.get("text_span"),
                    bbox=st.get("bbox"),
                    confidence=st.get("confidence", 1.0),
                    extraction_method=st.get("extraction_method", "text")
                )

            # Parse enums
            value_type = ValueType(row_data.get("value_type", "UNKNOWN"))
            flag = Flag(row_data.get("flag", ""))
            precision = DatetimePrecision(row_data.get("datetime_precision", "DAY"))

            row = CanonicalLabRow(
                case_id=row_data.get("case_id", case_id),
                doc_id=row_data.get("doc_id", ""),
                page=row_data.get("page", 0),
                datetime=row_data.get("datetime", ""),
                datetime_precision=precision,
                analyte_raw=row_data.get("analyte_raw", ""),
                analyte_canonical=row_data.get("analyte_canonical", ""),
                analyte_category=row_data.get("analyte_category"),
                panel_key=row_data.get("panel_key", "MISC"),
                analyte_order=row_data.get("analyte_order", 999),
                value_raw=row_data.get("value_raw", ""),
                value_numeric=row_data.get("value_numeric"),
                value_type=value_type,
                unit_raw=row_data.get("unit_raw"),
                unit_canonical=row_data.get("unit_canonical"),
                flag=flag,
                reference=ref,
                confidence_parse=row_data.get("confidence_parse", 1.0),
                confidence_datetime=row_data.get("confidence_datetime", 1.0),
                confidence_unit=row_data.get("confidence_unit", 1.0),
                source_trace=source_trace
            )
            rows.append(row)

        return CaseBundle(
            case_id=case_id,
            canonical_rows_long=rows,
            identity_confidence=data.get("identity_confidence", 1.0),
            documents=data.get("documents", []),
            patient_name=data.get("patient_name"),   # NEW (C10)
            patient_dob=data.get("patient_dob"),     # NEW (C10)
        )

    def verify_constitution_integrity(self) -> bool:
        """
        Verify constitution hasn't been tampered with.

        Returns:
            True if integrity check passed
        """
        try:
            self.config_loader.load_constitution(verify_hash=True)
            self.logger.info("Constitution integrity verified")
            return True
        except Exception as e:
            self.logger.error(f"Constitution integrity check failed: {e}")
            return False

    def save_constitution_hash(self) -> None:
        """Compute and save constitution hash for future verification"""
        self.config_loader.save_constitution_hash()
