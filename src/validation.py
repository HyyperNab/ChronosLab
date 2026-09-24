"""
Input validation framework for ChronosLab.
Validates all external inputs before processing.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime


class ValidationError(Exception):
    """Raised when input validation fails"""
    pass


def is_valid_iso(s: str) -> bool:
    """
    Single shared ISO 8601 validator (R2 dedup).
    Accepts a full datetime OR a date-only string.
    Used by both CaseValidator and the linter so the two cannot disagree.
    """
    if not isinstance(s, str) or not s:
        return False
    # Full datetime (tolerate trailing 'Z')
    try:
        datetime.fromisoformat(s.replace('Z', '+00:00'))
        return True
    except (ValueError, TypeError):
        pass
    # Date only
    try:
        datetime.strptime(s[:10], '%Y-%m-%d')
        return True
    except (ValueError, TypeError):
        return False


class CaseValidator:
    """Validates case bundle JSON structure"""

    REQUIRED_FIELDS = [
        "case_id",
        "canonical_rows_long"
    ]

    REQUIRED_ROW_FIELDS = [
        "case_id",
        "doc_id",
        "page",
        "datetime",
        "analyte_canonical",
        "panel_key"
    ]

    @classmethod
    def validate(cls, data: Dict[str, Any]) -> None:
        """
        Validate case bundle structure.

        Args:
            data: Raw case data

        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(data, dict):
            raise ValidationError("Case data must be a dictionary")

        # Check required fields
        for field in cls.REQUIRED_FIELDS:
            if field not in data:
                raise ValidationError(f"Missing required field: {field}")

        # Validate case_id
        case_id = data["case_id"]
        if not isinstance(case_id, str) or not case_id:
            raise ValidationError("case_id must be non-empty string")

        # Validate rows
        rows = data["canonical_rows_long"]
        if not isinstance(rows, list):
            raise ValidationError("canonical_rows_long must be a list")

        if not rows:
            raise ValidationError("canonical_rows_long cannot be empty")

        # Validate each row
        for idx, row in enumerate(rows):
            cls._validate_row(row, idx)

    @classmethod
    def _validate_row(cls, row: Dict[str, Any], idx: int) -> None:
        """Validate single row structure"""
        if not isinstance(row, dict):
            raise ValidationError(f"Row {idx}: must be a dictionary")

        # Check required fields
        for field in cls.REQUIRED_ROW_FIELDS:
            if field not in row:
                raise ValidationError(f"Row {idx}: missing required field '{field}'")

        # Validate types
        if not isinstance(row["page"], int) or row["page"] < 0:
            raise ValidationError(f"Row {idx}: page must be non-negative integer")

        # Validate datetime format
        if not isinstance(row["datetime"], str):
            raise ValidationError(f"Row {idx}: datetime must be string")

        # Basic ISO 8601 check (shared validator)
        if not is_valid_iso(row["datetime"]):
            raise ValidationError(
                f"Row {idx}: datetime must be valid ISO 8601 format, got: {row['datetime']}"
            )

    @staticmethod
    def _is_valid_iso_datetime(dt_str: str) -> bool:
        """Backward-compatible wrapper around the shared validator."""
        return is_valid_iso(dt_str)


class ConfigValidator:
    """Validates configuration files"""

    @staticmethod
    def validate_constitution(data: Dict[str, Any]) -> None:
        """
        Validate constitution structure.

        Args:
            data: Constitution data

        Raises:
            ValidationError: If validation fails
        """
        required = ["name", "version", "panel_order", "core_principles"]

        for field in required:
            if field not in data:
                raise ValidationError(f"Constitution missing required field: {field}")

        # Validate panel_order is list
        if not isinstance(data["panel_order"], list):
            raise ValidationError("panel_order must be a list")

        if not data["panel_order"]:
            raise ValidationError("panel_order cannot be empty")

    @staticmethod
    def validate_analyte_dict(data: Dict[str, Any]) -> None:
        """
        Validate analyte dictionary structure.

        Args:
            data: Analyte dictionary data

        Raises:
            ValidationError: If validation fails
        """
        if "analytes" not in data:
            raise ValidationError("Analyte dictionary must contain 'analytes' key")

        analytes = data["analytes"]
        if not isinstance(analytes, list):
            raise ValidationError("'analytes' must be a list")

        if not analytes:
            raise ValidationError("'analytes' cannot be empty")

        # Validate each analyte entry
        for idx, analyte in enumerate(analytes):
            if not isinstance(analyte, dict):
                raise ValidationError(f"Analyte {idx}: must be dictionary")

            required = ["canonical", "panel", "order"]
            for field in required:
                if field not in analyte:
                    raise ValidationError(
                        f"Analyte {idx}: missing required field '{field}'"
                    )


def sanitize_string(s: str, max_length: int = 1000) -> str:
    """
    Sanitize string input.

    Args:
        s: Input string
        max_length: Maximum allowed length

    Returns:
        Sanitized string

    Raises:
        ValidationError: If input is invalid
    """
    if not isinstance(s, str):
        raise ValidationError(f"Expected string, got {type(s)}")

    if len(s) > max_length:
        raise ValidationError(f"String exceeds maximum length of {max_length}")

    # Remove null bytes
    s = s.replace('\x00', '')

    return s
