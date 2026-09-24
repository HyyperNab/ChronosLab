"""
PDF OCR Module
Extracts text and structured data from lab result PDFs using Tesseract.
"""

import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

try:
    from .logging_config import get_logger
except ImportError:
    from logging_config import get_logger


@dataclass
class OCRBox:
    """Bounding box for OCR result"""
    x: int
    y: int
    width: int
    height: int
    confidence: float
    text: str
    page: int


@dataclass
class OCRPage:
    """OCR results for a single page"""
    page_num: int
    boxes: List[OCRBox]
    full_text: str
    confidence_avg: float


class OCRError(Exception):
    """Raised when OCR fails"""
    pass


class PDFOCREngine:
    """
    OCR engine for lab result PDFs.
    Uses Tesseract for text extraction.
    """
    
    def __init__(self, dpi: int = 300, lang: str = "eng+fra+deu"):
        """
        Initialize OCR engine.
        
        Args:
            dpi: Resolution for PDF rendering (300 recommended)
            lang: Tesseract language (eng+fra+deu for multilingual, fallback to available)
        """
        self.dpi = dpi
        self.logger = get_logger()  # Initialize logger FIRST
        self.lang = self._validate_languages(lang)
    
    def _validate_languages(self, lang: str) -> str:
        """
        Validate requested languages and fallback to available ones.
        
        Args:
            lang: Requested language string
            
        Returns:
            Valid language string with available languages only
        """
        try:
            # Get available languages
            import subprocess
            result = subprocess.run(
                ['tesseract', '--list-langs'],
                capture_output=True,
                text=True
            )
            available = set(result.stdout.strip().split('\n')[1:])  # Skip header
            
            # Parse requested languages
            requested = set(lang.split('+'))
            
            # Find intersection
            valid = requested & available
            
            if not valid:
                self.logger.warning(f"None of requested languages {requested} available, using 'eng'")
                return 'eng'
            
            final_lang = '+'.join(sorted(valid))
            if valid != requested:
                missing = requested - valid
                self.logger.warning(f"Languages not available: {missing}, using: {final_lang}")
            else:
                self.logger.info(f"Using languages: {final_lang}")
            
            return final_lang
            
        except Exception as e:
            self.logger.warning(f"Could not detect available languages: {e}, using 'eng'")
            return 'eng'
    
    def extract_from_pdf(self, pdf_path: Path) -> List[OCRPage]:
        """
        Extract text from PDF with OCR.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of OCRPage objects (one per page)
            
        Raises:
            OCRError: If OCR fails
        """
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            raise OCRError(f"PDF not found: {pdf_path}")
        
        self.logger.info(f"Starting OCR on: {pdf_path.name}")
        
        try:
            # Convert PDF to images
            images = convert_from_path(
                pdf_path,
                dpi=self.dpi,
                fmt='PNG'
            )
        except Exception as e:
            raise OCRError(f"PDF rendering failed: {e}")
        
        self.logger.info(f"Rendered {len(images)} pages at {self.dpi} DPI")
        
        # OCR each page
        pages = []
        for page_num, image in enumerate(images, start=1):
            self.logger.debug(f"OCR page {page_num}/{len(images)}")
            
            try:
                page_result = self._ocr_page(image, page_num)
                pages.append(page_result)
            except Exception as e:
                self.logger.error(f"OCR failed on page {page_num}: {e}")
                raise OCRError(f"OCR failed on page {page_num}: {e}")
        
        # Calculate overall confidence
        avg_conf = sum(p.confidence_avg for p in pages) / len(pages) if pages else 0
        self.logger.info(f"OCR complete. Avg confidence: {avg_conf:.1f}%")
        
        # Signal if confidence too low
        if avg_conf < 70:
            self.logger.warning(f"LOW OCR CONFIDENCE: {avg_conf:.1f}% (threshold: 70%)")
        
        return pages
    
    def _ocr_page(self, image: Image.Image, page_num: int) -> OCRPage:
        """
        OCR a single page image.
        
        Args:
            image: PIL Image
            page_num: Page number
            
        Returns:
            OCRPage with results
        """
        # Get full text
        full_text = pytesseract.image_to_string(
            image,
            lang=self.lang,
            config='--psm 6'  # Assume uniform text block
        )
        
        # Get detailed word-level data with bboxes
        data = pytesseract.image_to_data(
            image,
            lang=self.lang,
            output_type=pytesseract.Output.DICT,
            config='--psm 6'
        )
        
        # Extract boxes
        boxes = []
        confidences = []
        
        for i in range(len(data['text'])):
            text = data['text'][i].strip()
            if not text:
                continue
            
            conf = float(data['conf'][i])
            if conf < 0:  # Tesseract returns -1 for low confidence
                continue
            
            box = OCRBox(
                x=data['left'][i],
                y=data['top'][i],
                width=data['width'][i],
                height=data['height'][i],
                confidence=conf,
                text=text,
                page=page_num
            )
            boxes.append(box)
            confidences.append(conf)
        
        avg_conf = sum(confidences) / len(confidences) if confidences else 0
        
        return OCRPage(
            page_num=page_num,
            boxes=boxes,
            full_text=full_text,
            confidence_avg=avg_conf
        )
    
    def extract_text_only(self, pdf_path: Path) -> str:
        """
        Quick text extraction without boxes (faster).
        
        Args:
            pdf_path: Path to PDF
            
        Returns:
            Full text from all pages
        """
        pages = self.extract_from_pdf(pdf_path)
        return "\n\n".join(p.full_text for p in pages)


class FrenchReferenceParser:
    """
    Parses French lab reference ranges from OCR text.
    Handles: "Réf: 12-16", "Valeurs usuelles: 0.5 - 1.5", etc.
    """
    
    # Common French reference indicators
    REF_PATTERNS = [
        r"(?:Réf\.?|Référence|Ref\.?)\s*:?\s*([0-9.,]+)\s*[-–—]\s*([0-9.,]+)",
        r"(?:Valeurs?\s+usuelles?|Normes?)\s*:?\s*([0-9.,]+)\s*[-–—]\s*([0-9.,]+)",
        r"(?:Intervalle\s+de\s+référence)\s*:?\s*([0-9.,]+)\s*[-–—]\s*([0-9.,]+)",
        r"<\s*([0-9.,]+)",  # "< 5"
        r">\s*([0-9.,]+)",  # "> 10"
    ]
    
    @classmethod
    def parse(cls, text: str) -> Tuple[Optional[float], Optional[float], str]:
        """
        Parse reference range from text.
        
        Args:
            text: Text containing reference range
            
        Returns:
            (low, high, confidence) where confidence is "HIGH" or "LOW"
        """
        text = text.strip()
        
        # Try range patterns first
        for pattern in cls.REF_PATTERNS[:3]:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    low = cls._parse_number(match.group(1))
                    high = cls._parse_number(match.group(2))
                    return (low, high, "HIGH")
                except (ValueError, TypeError):
                    continue
        
        # Try inequality patterns (< or >)
        # "<5" pattern
        match = re.search(cls.REF_PATTERNS[3], text)
        if match:
            try:
                val = cls._parse_number(match.group(1))
                return (None, val, "LOW")  # Upper bound only
            except (ValueError, TypeError):
                pass
        
        # ">10" pattern
        match = re.search(cls.REF_PATTERNS[4], text)
        if match:
            try:
                val = cls._parse_number(match.group(1))
                return (val, None, "LOW")  # Lower bound only
            except (ValueError, TypeError):
                pass
        
        return (None, None, "LOW")
    
    @staticmethod
    def _parse_number(s: str) -> float:
        """Parse French number format (comma as decimal)"""
        s = s.strip().replace(',', '.')
        return float(s)


def test_ocr():
    """Test OCR on sample PDF"""
    engine = PDFOCREngine(dpi=300, lang="fra")
    
    # This would be a real PDF path
    # pages = engine.extract_from_pdf(Path("sample.pdf"))
    # for page in pages:
    #     print(f"Page {page.page_num}: {page.confidence_avg:.1f}% confidence")
    
    # Test reference parsing
    test_cases = [
        "Réf: 12.0 - 16.0",
        "Valeurs usuelles: 135-145",
        "< 5",
        "> 10",
        "Référence : 4,5 - 5,5"
    ]
    
    for text in test_cases:
        low, high, conf = FrenchReferenceParser.parse(text)
        print(f"{text:30} → low={low}, high={high}, confidence={conf}")


if __name__ == "__main__":
    test_ocr()
