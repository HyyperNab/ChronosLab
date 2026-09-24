"""
ChronosLab Core Types
Defines the canonical data structures used throughout the system.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime, timezone
from enum import Enum


class ValueType(str, Enum):
    """Type of lab result value"""
    NUMERIC = "NUMERIC"
    QUALITATIVE = "QUALITATIVE"
    UNKNOWN = "UNKNOWN"


class Flag(str, Enum):
    """Lab result flag"""
    NORMAL = ""
    LOW = "L"
    HIGH = "H"
    CRITICAL_LOW = "LL"
    CRITICAL_HIGH = "HH"


class DatetimePrecision(str, Enum):
    """Precision of extracted datetime"""
    FULL = "FULL"  # YYYY-MM-DD HH:MM:SS
    DAY = "DAY"    # YYYY-MM-DD
    MONTH = "MONTH"  # YYYY-MM
    YEAR = "YEAR"  # YYYY
    UNKNOWN = "UNKNOWN"


@dataclass
class SourceTrace:
    """Provenance information for extracted data"""
    doc_id: str
    page: int
    text_span: Optional[str] = None
    bbox: Optional[tuple] = None  # (x0, y0, x1, y1)
    confidence: float = 1.0
    extraction_method: str = "text"  # "text" or "ocr"


@dataclass
class ReferenceRange:
    """Reference range for a lab analyte"""
    text_raw: Optional[str] = None
    low: Optional[float] = None
    high: Optional[float] = None
    unit_raw: Optional[str] = None
    source_trace: Optional[SourceTrace] = None
    parse_confidence: str = "HIGH"  # "HIGH" or "LOW"


@dataclass
class CanonicalLabRow:
    """
    Canonical representation of a single lab result.
    This is the single source of truth for all lab data.
    """
    # Identity
    case_id: str
    doc_id: str
    page: int

    # Temporal
    datetime: str  # ISO 8601 format
    datetime_precision: DatetimePrecision

    # Analyte
    analyte_raw: str
    analyte_canonical: str
    analyte_category: Optional[str] = None
    panel_key: str = "MISC"
    analyte_order: int = 999

    # Value
    value_raw: str = ""
    value_numeric: Optional[float] = None
    value_type: ValueType = ValueType.UNKNOWN

    # Units
    unit_raw: Optional[str] = None
    unit_canonical: Optional[str] = None

    # Clinical interpretation
    flag: Flag = Flag.NORMAL

    # Reference range
    reference: ReferenceRange = field(default_factory=ReferenceRange)

    # Confidence scores
    confidence_parse: float = 1.0
    confidence_datetime: float = 1.0
    confidence_unit: float = 1.0

    # Provenance
    source_trace: Optional[SourceTrace] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "case_id": self.case_id,
            "doc_id": self.doc_id,
            "page": self.page,
            "datetime": self.datetime,
            "datetime_precision": self.datetime_precision.value,
            "analyte_raw": self.analyte_raw,
            "analyte_canonical": self.analyte_canonical,
            "analyte_category": self.analyte_category,
            "panel_key": self.panel_key,
            "analyte_order": self.analyte_order,
            "value_raw": self.value_raw,
            "value_numeric": self.value_numeric,
            "value_type": self.value_type.value,
            "unit_raw": self.unit_raw,
            "unit_canonical": self.unit_canonical,
            "flag": self.flag.value,
            "reference_text_raw": self.reference.text_raw,
            "reference_low": self.reference.low,
            "reference_high": self.reference.high,
            "reference_unit_raw": self.reference.unit_raw,
            "reference_parse_confidence": self.reference.parse_confidence,
            "reference_source_trace": self.reference.source_trace.__dict__ if self.reference.source_trace else None,
            "confidence_parse": self.confidence_parse,
            "confidence_datetime": self.confidence_datetime,
            "confidence_unit": self.confidence_unit,
            "source_trace": self.source_trace.__dict__ if self.source_trace else None
        }


@dataclass
class CaseBundle:
    """
    Complete data for a single patient case.
    Contains all extracted lab results and metadata.
    """
    case_id: str
    canonical_rows_long: List[CanonicalLabRow]
    documents: List[Dict[str, Any]] = field(default_factory=list)
    identity_confidence: float = 0.0
    # NEW (v1.6.0 Datenschutz): patient name used ONLY in <title>, never in body.
    patient_name: Optional[str] = None
    patient_dob: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "case_id": self.case_id,
            "canonical_rows_long": [row.to_dict() for row in self.canonical_rows_long],
            "documents": self.documents,
            "identity_confidence": self.identity_confidence,
            "patient_name": self.patient_name,
            "patient_dob": self.patient_dob,
            "created_at": self.created_at
        }


@dataclass
class LintResult:
    """Result of linting operation"""
    passed: bool
    blocking_errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    info: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "blocking_errors": self.blocking_errors,
            "warnings": self.warnings,
            "info": self.info
        }
