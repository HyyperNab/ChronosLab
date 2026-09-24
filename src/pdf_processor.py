"""
Multi-PDF Lab Results Processor
Ingests multiple PDFs, verifies identity, extracts data, merges chronologically.

Harmonization fixes:
- S3: assign panel_key / analyte_order / case_id via the analyte dictionary
  (was never done -> every PDF row kept panel_key="" and fell into MISC).
  The linter only CHECKS panels; it never assigns them.
"""

from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
import json

try:
    from .ocr_engine import PDFOCREngine, OCRPage, FrenchReferenceParser
    from .identity_clustering import PatientIdentityClusterer, PatientIdentity, IdentityMismatchError
    from .table_extraction import TableExtractor, LabDataParser
    from .datatypes import CanonicalLabRow, ValueType, Flag, ReferenceRange, SourceTrace
    from .config import ConfigLoader
    from .logging_config import get_logger
except ImportError:
    from ocr_engine import PDFOCREngine, OCRPage, FrenchReferenceParser
    from identity_clustering import PatientIdentityClusterer, PatientIdentity, IdentityMismatchError
    from table_extraction import TableExtractor, LabDataParser
    from datatypes import CanonicalLabRow, ValueType, Flag, ReferenceRange, SourceTrace
    from config import ConfigLoader
    from logging_config import get_logger


@dataclass
class PDFDocument:
    """Represents a single PDF document"""
    path: Path
    doc_id: str
    ocr_pages: List[OCRPage]
    identity: PatientIdentity
    text_full: str


class PDFProcessingError(Exception):
    """Raised when PDF processing fails"""
    pass


class MultiPDFProcessor:
    """
    Processes multiple PDF lab results.

    Workflow:
    1. OCR each PDF
    2. Extract identity from each
    3. Verify same patient (HARD STOP if mismatch)
    4. Extract lab data
    5. Merge chronologically
    6. Assign panels / orders / case_id (S3)
    """

    def __init__(
        self,
        ocr_dpi: int = 300,
        lang: str = "eng+fra+deu",
        config_loader: Optional[ConfigLoader] = None,
    ):
        """
        Initialize processor.

        Args:
            ocr_dpi: OCR resolution (300 recommended)
            lang: Tesseract languages (eng+fra+deu for multilingual, auto-fallback)
            config_loader: Optional ConfigLoader for panel/order assignment (S3).
                If None, rows are left with panel_key="" and fall into MISC.
        """
        self.ocr_engine = PDFOCREngine(dpi=ocr_dpi, lang=lang)
        self.identity_clusterer = PatientIdentityClusterer()
        self.config_loader = config_loader
        self.logger = get_logger()

    def process_multiple_pdfs(
        self,
        pdf_paths: List[Path],
        output_dir: Path
    ) -> Dict:
        """
        Process multiple PDFs into unified case.

        Args:
            pdf_paths: List of PDF file paths
            output_dir: Where to save outputs

        Returns:
            Processing result dict

        Raises:
            IdentityMismatchError: If identity mismatch detected (HARD FAIL)
            PDFProcessingError: If processing fails
        """
        self.logger.info(f"Processing {len(pdf_paths)} PDFs")

        # Step 1: OCR all PDFs
        documents = []
        for pdf_path in pdf_paths:
            doc = self._process_single_pdf(pdf_path)
            documents.append(doc)

        # Step 2: Extract identities
        identities = [doc.identity for doc in documents]

        # Step 3: Verify same patient (HARD FAIL on mismatch - no interaction)
        try:
            same_patient = self.identity_clusterer.verify_same_patient(identities)
        except IdentityMismatchError as e:
            self.logger.error(f"Identity verification failed: {e}")
            raise

        if not same_patient:
            raise IdentityMismatchError("Documents do not belong to same patient")

        # Step 4: Extract lab data from all documents
        all_rows = []
        for doc in documents:
            rows = self._extract_lab_rows(doc)
            all_rows.extend(rows)

        # Step 5: Sort chronologically
        all_rows_sorted = sorted(all_rows, key=lambda r: r.datetime)

        # Build case bundle
        # Use first non-None patient ID or generate one
        case_id = next(
            (i.patient_id for i in identities if i.patient_id),
            f"CASE-{identities[0].dob or 'UNKNOWN'}"
        )

        # S3: Assign panel_key / analyte_order / case_id (was MISSING).
        # Without this every row kept panel_key="" and the renderer dumped
        # everything into MISC.
        all_rows_sorted = self._assign_panels(all_rows_sorted, case_id)

        self.logger.info(f"Extracted {len(all_rows_sorted)} total lab results")

        case_bundle = {
            "case_id": case_id,
            "patient_name": identities[0].name,
            "patient_dob": identities[0].dob,
            "source_documents": [doc.doc_id for doc in documents],
            "canonical_rows_long": [row.to_dict() for row in all_rows_sorted]
        }

        # Save intermediate JSON
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        case_json_path = output_dir / f"{case_id}_extracted.json"
        with open(case_json_path, 'w', encoding='utf-8') as f:
            json.dump(case_bundle, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Saved case bundle: {case_json_path}")

        return {
            "status": "SUCCESS",
            "case_id": case_id,
            "documents_processed": len(documents),
            "rows_extracted": len(all_rows_sorted),
            "case_json_path": str(case_json_path)
        }

    def _assign_panels(
        self,
        rows: List[CanonicalLabRow],
        case_id: str,
    ) -> List[CanonicalLabRow]:
        """
        Assign panel_key, analyte_order, and case_id to every row using the
        analyte dictionary (ConfigLoader.resolve_analyte). This is the step
        that was MISSING (S3): table_extraction sets panel_key="" / order=0 /
        case_id="" and the linter only checks, never assigns.

        Unknown analytes -> MISC, order 999, with an info log (matches
        QUICK_START's documented behaviour).
        """
        for r in rows:
            r.case_id = case_id

        if not self.config_loader:
            self.logger.warning(
                "No config_loader provided -> panel assignment skipped; "
                "rows keep panel_key='' and will fall into MISC."
            )
            for r in rows:
                r.panel_key = "MISC"
                r.analyte_order = 999
            return rows

        # Ensure dictionary loaded
        try:
            self.config_loader.load_analyte_dictionary()
        except Exception as e:
            self.logger.error(f"Cannot load analyte dictionary: {e}")
            for r in rows:
                r.panel_key = "MISC"
                r.analyte_order = 999
            return rows

        for r in rows:
            resolved = self.config_loader.resolve_analyte(r.analyte_canonical)
            if resolved:
                r.panel_key = resolved["panel"]
                r.analyte_order = resolved["order"]
            else:
                r.panel_key = "MISC"
                r.analyte_order = 999
                self.logger.info(f"Unknown analyte '{r.analyte_canonical}' -> MISC")

        return rows

    def _process_single_pdf(self, pdf_path: Path) -> PDFDocument:
        """
        Process single PDF: OCR + identity extraction.

        Args:
            pdf_path: Path to PDF

        Returns:
            PDFDocument object
        """
        pdf_path = Path(pdf_path)
        doc_id = pdf_path.stem

        self.logger.info(f"Processing: {pdf_path.name}")

        # OCR
        try:
            ocr_pages = self.ocr_engine.extract_from_pdf(pdf_path)
        except Exception as e:
            raise PDFProcessingError(f"OCR failed for {pdf_path.name}: {e}")

        # Combine all page text
        text_full = "\n\n".join(p.full_text for p in ocr_pages)

        # Extract identity
        identity = self.identity_clusterer.extract_identity(text_full, doc_id)

        self.logger.info(f"  Identity: {identity.name or 'UNKNOWN'} / {identity.dob or 'UNKNOWN'}")

        return PDFDocument(
            path=pdf_path,
            doc_id=doc_id,
            ocr_pages=ocr_pages,
            identity=identity,
            text_full=text_full
        )

    def _extract_lab_rows(self, doc: PDFDocument) -> List[CanonicalLabRow]:
        """
        Extract lab result rows from document.

        Args:
            doc: PDFDocument

        Returns:
            List of CanonicalLabRow objects

        Raises:
            PDFProcessingError: If sample date not found
        """
        # Extract sample date from document
        from .identity_clustering import PatientIdentityClusterer
        sample_date = PatientIdentityClusterer.extract_sample_date(doc.text_full)

        if not sample_date:
            # HARD FAIL - no fallback allowed (constitutional requirement)
            raise PDFProcessingError(
                f"No sample date found in {doc.doc_id}. "
                "Cannot process without explicit collection date. "
                "Document must contain: 'Date du prélèvement', 'Prélevé le', or similar."
            )

        self.logger.info(f"Sample date: {sample_date}")

        table_extractor = TableExtractor()
        lab_parser = LabDataParser(default_date=sample_date)

        all_rows = []

        for page in doc.ocr_pages:
            # Extract tables from page
            tables = table_extractor.extract_tables(page)

            self.logger.debug(f"{doc.doc_id} page {page.page_num}: {len(tables)} tables detected")

            # Parse each table
            for table_idx, table in enumerate(tables):
                rows = lab_parser.parse_table(table, doc.doc_id, page.page_num)
                all_rows.extend(rows)

                self.logger.debug(f"  Table {table_idx + 1}: {len(rows)} extracted")

        self.logger.info(f"Extracted {len(all_rows)} total rows from {doc.doc_id}")

        return all_rows


def test_multi_pdf():
    """Test multi-PDF processing"""
    processor = MultiPDFProcessor()

    # Example usage (would need real PDFs)
    # pdf_paths = [
    #     Path("lab_results_2024_01.pdf"),
    #     Path("lab_results_2024_02.pdf"),
    # ]
    #
    # result = processor.process_multiple_pdfs(
    #     pdf_paths,
    #     output_dir=Path("output"),
    # )
    #
    # print(f"Status: {result['status']}")
    # print(f"Case ID: {result['case_id']}")
    # print(f"Rows extracted: {result['rows_extracted']}")

    print("Multi-PDF processor initialized")


if __name__ == "__main__":
    test_multi_pdf()
