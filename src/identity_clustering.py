"""
Patient Identity Clustering
Verifies that multiple PDFs belong to the same patient.
HARD STOP if identity mismatch detected.
"""

import re
from pathlib import Path
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from datetime import datetime

try:
    from .logging_config import get_logger
except ImportError:
    from logging_config import get_logger


@dataclass
class PatientIdentity:
    """Patient identity signals extracted from document"""
    name: Optional[str] = None
    dob: Optional[str] = None  # YYYY-MM-DD format
    patient_id: Optional[str] = None
    source_doc: Optional[str] = None
    confidence: float = 0.0


class IdentityMismatchError(Exception):
    """Raised when identity signals conflict across documents"""
    pass


class PatientIdentityClusterer:
    """
    Clusters documents by patient identity.
    Uses: Name + DOB ± Patient ID
    """
    
    # Patterns for French lab results.
    # The negative lookahead (?!Né|Née?|le|la|de) stops the name capture from
    # greedily eating the DOB marker ("Né le <date>"); without it, re.IGNORECASE
    # lets "Né"/"Le" match the repeated [A-Z][a-z]+ group.
    NAME_PATTERNS = [
        r"(?:Nom|Patient|Identité)\s*:?\s*([A-ZÀ-ÖØ-Þ][a-zà-öø-ÿ]+(?:\s+(?!Né\b|Née?\b|le\b|la\b|de\b)[A-ZÀ-ÖØ-Þ][a-zà-öø-ÿ]+)+)",
        r"(?:M\.|Mme|Mr\.?|Madame|Monsieur)\s+([A-ZÀ-ÖØ-Þ][a-zà-öø-ÿ]+(?:\s+(?!Né\b|Née?\b|le\b|la\b|de\b)[A-ZÀ-ÖØ-Þ][a-zà-öø-ÿ]+)*)",
    ]
    
    DOB_PATTERNS = [
        r"(?:Né(?:e)?\s+le|Date\s+de\s+naissance|DDN)\s*:?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})",
        r"(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})",  # Generic date
    ]
    
    # Sample date patterns (different from DOB)
    SAMPLE_DATE_PATTERNS = [
        r"(?:Date\s+(?:du\s+)?prélèvement|Date\s+d['''e]\s*analyse|Prélevé\s+le)\s*:?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})",
        r"(?:Le)\s+(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})",
    ]
    
    PATIENT_ID_PATTERNS = [
        r"(?:N°|Numéro|ID)\s*(?:patient|dossier)?\s*:?\s*([A-Z0-9\-]+)",
        r"(?:Patient\s+ID|Dossier)\s*:?\s*([A-Z0-9\-]+)",
    ]
    
    def __init__(self):
        self.logger = get_logger()
    
    def extract_identity(self, text: str, source_doc: str) -> PatientIdentity:
        """
        Extract patient identity signals from OCR text.
        
        Args:
            text: Full OCR text from document
            source_doc: Source document identifier
            
        Returns:
            PatientIdentity object
        """
        identity = PatientIdentity(source_doc=source_doc)
        
        # Extract name
        for pattern in self.NAME_PATTERNS:
            match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
            if match:
                identity.name = self._normalize_name(match.group(1))
                break
        
        # Extract DOB
        for pattern in self.DOB_PATTERNS:
            match = re.search(pattern, text, re.MULTILINE)
            if match:
                dob_raw = match.group(1)
                identity.dob = self._normalize_date(dob_raw)
                if identity.dob:
                    break
        
        # Extract Patient ID
        for pattern in self.PATIENT_ID_PATTERNS:
            match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
            if match:
                identity.patient_id = match.group(1).strip()
                break
        
        # Calculate confidence
        confidence = 0.0
        if identity.name:
            confidence += 0.4
        if identity.dob:
            confidence += 0.4
        if identity.patient_id:
            confidence += 0.2
        
        identity.confidence = confidence
        
        return identity
    
    def verify_same_patient(
        self,
        identities: List[PatientIdentity]
    ) -> bool:
        """
        Verify all documents belong to same patient.
        
        Args:
            identities: List of extracted identities
            
        Returns:
            True if same patient
            
        Raises:
            IdentityMismatchError: If mismatch detected (HARD FAIL)
        """
        if len(identities) < 2:
            return True  # Single document, no clustering needed
        
        # Extract unique values
        names = set(i.name for i in identities if i.name)
        dobs = set(i.dob for i in identities if i.dob)
        patient_ids = set(i.patient_id for i in identities if i.patient_id)
        
        # Check for conflicts
        conflicts = []
        
        if len(names) > 1:
            conflicts.append(f"Names: {', '.join(names)}")
        
        if len(dobs) > 1:
            conflicts.append(f"DOBs: {', '.join(dobs)}")
        
        if len(patient_ids) > 1:
            conflicts.append(f"Patient IDs: {', '.join(patient_ids)}")
        
        if not conflicts:
            self.logger.info("✓ Identity verified: All documents match")
            return True
        
        # Mismatch detected → HARD FAIL (no user interaction)
        self.logger.error("⚠️  IDENTITY MISMATCH DETECTED")
        for conflict in conflicts:
            self.logger.error(f"  - {conflict}")
        
        self.logger.error("Documents:")
        for i, identity in enumerate(identities, 1):
            self.logger.error(f"  {i}. {identity.source_doc}")
            self.logger.error(f"     Name: {identity.name or 'MISSING'}")
            self.logger.error(f"     DOB: {identity.dob or 'MISSING'}")
            self.logger.error(f"     Patient ID: {identity.patient_id or 'MISSING'}")
        
        # HARD FAIL - no user interaction allowed
        raise IdentityMismatchError(
            f"Identity mismatch detected: {'; '.join(conflicts)}. "
            "Processing stopped. Documents do NOT belong to same patient."
        )
    
    @staticmethod
    def _normalize_name(name: str) -> str:
        """Normalize name for comparison"""
        # Remove extra whitespace, convert to uppercase
        name = re.sub(r'\s+', ' ', name.strip())
        return name.upper()
    
    @staticmethod
    def _normalize_date(date_str: str) -> Optional[str]:
        """
        Normalize date to YYYY-MM-DD.
        
        Args:
            date_str: Date in various formats (DD/MM/YYYY, DD-MM-YYYY, etc.)
            
        Returns:
            Date in YYYY-MM-DD format, or None if parsing fails
        """
        # Try common French formats
        formats = [
            "%d/%m/%Y",
            "%d-%m-%Y",
            "%d.%m.%Y",
            "%d/%m/%y",
            "%d-%m-%y",
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        return None
    
    @classmethod
    def extract_sample_date(cls, text: str) -> Optional[str]:
        """
        Extract sample/collection date from document.
        
        Args:
            text: Full OCR text
            
        Returns:
            Date in YYYY-MM-DD format, or None
        """
        for pattern in cls.SAMPLE_DATE_PATTERNS:
            match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
            if match:
                date_raw = match.group(1)
                normalized = cls._normalize_date(date_raw)
                if normalized:
                    return normalized
        
        return None


def test_identity_extraction():
    """Test identity extraction"""
    
    sample_text = """
    Laboratoire XYZ
    
    Patient: DUPONT Jean
    Né le 15/03/1975
    N° dossier: PAT-12345
    
    Résultats d'analyses
    """
    
    clusterer = PatientIdentityClusterer()
    identity = clusterer.extract_identity(sample_text, "DOC-001")
    
    print("Extracted Identity:")
    print(f"  Name: {identity.name}")
    print(f"  DOB: {identity.dob}")
    print(f"  Patient ID: {identity.patient_id}")
    print(f"  Confidence: {identity.confidence:.1%}")


if __name__ == "__main__":
    test_identity_extraction()
