"""
ChronosLab - Medical Laboratory Document Intelligence System

Truth over completeness. Silence over speculation.
"""

__version__ = "1.6.0"
__codename__ = "ALLSTARDS"

from .chronoslab import ChronosLab
from .datatypes import (
    CaseBundle,
    CanonicalLabRow,
    ReferenceRange,
    SourceTrace,
    ValueType,
    Flag,
    DatetimePrecision,
    LintResult
)
from .config import ConfigLoader, Constitution
from .linter import ChronosLabLinter
from .renderer import ClinicianCockpitRenderer

__all__ = [
    "ChronosLab",
    "CaseBundle",
    "CanonicalLabRow",
    "ReferenceRange",
    "SourceTrace",
    "ValueType",
    "Flag",
    "DatetimePrecision",
    "LintResult",
    "ConfigLoader",
    "Constitution",
    "ChronosLabLinter",
    "ClinicianCockpitRenderer",
]
