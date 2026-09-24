#!/usr/bin/env python3
"""
OCR Demo Script
Demonstrates PDF ingestion workflow with identity verification.

Usage:
    python demo_ocr.py pdf1.pdf pdf2.pdf pdf3.pdf
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pdf_processor import MultiPDFProcessor, IdentityMismatchError, PDFProcessingError
from chronoslab import ChronosLab
from config import ConfigLoader


def main():
    """
    Main OCR demo workflow.
    
    Workflow:
    1. Ingest multiple PDFs with OCR
    2. Extract identity from each
    3. Verify same patient (ask user if mismatch)
    4. Extract lab data
    5. Merge chronologically
    6. Generate HTML cockpit
    """
    
    print("="*60)
    print("ChronosLab OCR Demo")
    print("="*60)
    print()
    
    # Check for PDF arguments
    if len(sys.argv) < 2:
        print("Usage: python demo_ocr.py <pdf1> <pdf2> ...")
        print()
        print("Example:")
        print("  python demo_ocr.py data/pdfs/lab_jan.pdf data/pdfs/lab_feb.pdf")
        print()
        sys.exit(1)
    
    # Parse PDF paths
    pdf_paths = [Path(arg) for arg in sys.argv[1:]]
    
    # Validate paths
    for pdf_path in pdf_paths:
        if not pdf_path.exists():
            print(f"✗ File not found: {pdf_path}")
            sys.exit(1)
    
    print(f"Processing {len(pdf_paths)} PDFs:")
    for i, pdf_path in enumerate(pdf_paths, 1):
        print(f"  {i}. {pdf_path.name}")
    print()
    
    # Initialize processor WITH a ConfigLoader so panels get assigned (S3).
    # Without it, extracted rows keep panel_key="" and all fall into MISC.
    config_dir = Path(__file__).parent / "config"
    processor = MultiPDFProcessor(
        ocr_dpi=300,
        lang="fra",
        config_loader=ConfigLoader(config_dir),
    )
    
    # Process PDFs (identity mismatch -> HARD FAIL, no interactive prompt)
    try:
        result = processor.process_multiple_pdfs(
            pdf_paths,
            output_dir=Path(__file__).parent / "data" / "output",
        )
    except IdentityMismatchError as e:
        print()
        print("="*60)
        print("✗ PROCESSING STOPPED")
        print("="*60)
        print(f"Reason: {e}")
        sys.exit(1)
    except PDFProcessingError as e:
        print()
        print("="*60)
        print("✗ PROCESSING FAILED")
        print("="*60)
        print(f"Error: {e}")
        sys.exit(1)
    
    print()
    print("="*60)
    print("✓ PDF PROCESSING COMPLETE")
    print("="*60)
    print(f"Case ID: {result['case_id']}")
    print(f"Documents processed: {result['documents_processed']}")
    print(f"Rows extracted: {result['rows_extracted']}")
    print(f"Case JSON: {result['case_json_path']}")
    print()
    
    # Now render HTML cockpit
    print("="*60)
    print("Generating HTML Cockpit")
    print("="*60)
    print()
    
    lab = ChronosLab(config_dir=config_dir)
    
    cockpit_result = lab.process_case_from_json(
        case_json_path=Path(result['case_json_path']),
        output_dir=Path("data/output"),
        verify_integrity=True
    )
    
    print()
    print("="*60)
    print(f"✓ STATUS: {cockpit_result['status']}")
    print("="*60)
    print()
    
    if cockpit_result['status'] == 'SUCCESS':
        print("Outputs:")
        for key, path in cockpit_result.get('outputs', {}).items():
            print(f"  • {key}: {path}")
        print()
        print(f"✓ Open the clinician cockpit in your browser:")
        print(f"  {cockpit_result['outputs']['clinician_cockpit']}")
    else:
        print(f"Status: {cockpit_result['status']}")
        if 'error' in cockpit_result:
            print(f"Error: {cockpit_result['error']}")


if __name__ == "__main__":
    main()
