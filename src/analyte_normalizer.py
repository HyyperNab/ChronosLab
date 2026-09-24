"""
Simple Analyte Normalizer
Maps OCR variants to canonical names using fuzzy matching + lookup table.
"""

import yaml
from pathlib import Path
from typing import Optional, Dict
import re

try:
    from .logging_config import get_logger
except ImportError:
    from logging_config import get_logger


class AnalyteNormalizer:
    """
    Normalizes analyte names from OCR text.
    Simple lookup + fuzzy matching.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize normalizer.
        
        Args:
            config_path: Path to analyte_normalization.yaml
        """
        self.logger = get_logger()
        
        # Load normalization map
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "analyte_normalization.yaml"
        
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                self.mapping = yaml.safe_load(f) or {}
        else:
            self.mapping = {}
            self.logger.warning(f"Normalization map not found: {config_path}")
    
    def normalize(self, ocr_text: str) -> tuple[str, str]:
        """
        Normalize OCR text to canonical analyte name.
        
        Args:
            ocr_text: Raw OCR text
            
        Returns:
            Tuple of (canonical_name, confidence)
            - confidence: "HIGH" (exact/synonym) or "LOW" (fuzzy)
        """
        # Clean text
        cleaned = self._clean_text(ocr_text)
        
        # Exact match (case-insensitive) → HIGH confidence
        for variant, canonical in self.mapping.items():
            if self._clean_text(variant) == cleaned:
                self.logger.debug(f"Normalized '{ocr_text}' → '{canonical}' (exact, HIGH)")
                return (canonical, "HIGH")
        
        # Fuzzy match (remove accents, spaces, case) → LOW confidence + LOGGED
        ocr_normalized = self._remove_accents(cleaned)
        
        for variant, canonical in self.mapping.items():
            variant_normalized = self._remove_accents(self._clean_text(variant))
            if ocr_normalized == variant_normalized:
                self.logger.warning(f"Fuzzy match: '{ocr_text}' → '{canonical}' (confidence: LOW)")
                return (canonical, "LOW")
        
        # Partial match (contains) → LOW confidence + LOGGED
        for variant, canonical in self.mapping.items():
            variant_normalized = self._remove_accents(self._clean_text(variant))
            if variant_normalized in ocr_normalized or ocr_normalized in variant_normalized:
                # Only if similarity is high
                if len(variant_normalized) > 5:  # Avoid short spurious matches
                    self.logger.warning(f"Partial match: '{ocr_text}' → '{canonical}' (confidence: LOW)")
                    return (canonical, "LOW")
        
        # No match - return original with UNKNOWN tag
        self.logger.info(f"Unknown analyte: '{ocr_text}' (no normalization)")
        return (ocr_text.strip(), "UNKNOWN")
    
    def _clean_text(self, text: str) -> str:
        """Remove extra whitespace, lowercase"""
        return re.sub(r'\s+', ' ', text.strip()).lower()
    
    def _remove_accents(self, text: str) -> str:
        """
        Remove accents from text for fuzzy matching.
        Simple approach: replace common accented characters.
        """
        replacements = {
            'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
            'à': 'a', 'â': 'a', 'ä': 'a',
            'ô': 'o', 'ö': 'o',
            'û': 'u', 'ü': 'u',
            'ç': 'c',
            'î': 'i', 'ï': 'i',
            'ñ': 'n',
            'ß': 'ss',
        }
        
        result = text
        for accented, plain in replacements.items():
            result = result.replace(accented, plain)
        
        return result


def test_normalizer():
    """Test normalization"""
    normalizer = AnalyteNormalizer()
    
    test_cases = [
        "Hémoglobine glyquée",
        "Hemoglobine glyquee",
        "HbA1c",
        "Hemoglobin A1c",
        "Glykiertes Hämoglobin",
        "Créatinine",
        "Kreatinin",
        "Unknown Analyte",
    ]
    
    print("Analyte Normalization Tests:")
    print("="*60)
    for text in test_cases:
        canonical = normalizer.normalize(text)
        print(f"{text:30} → {canonical}")


if __name__ == "__main__":
    test_normalizer()
