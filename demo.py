#!/usr/bin/env python3
"""
ChronosLab Demo Script
Demonstrates the complete pipeline with example data.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from chronoslab import ChronosLab


def main():
    """Run ChronosLab demo"""
    
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   ChronosLab v1.6.0 (ALLSTARDS)                          ║
║   Medical Laboratory Document Intelligence System         ║
║                                                           ║
║   Truth over completeness.                                ║
║   Silence over speculation.                               ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Initialize ChronosLab
    config_dir = Path(__file__).parent / "config"
    output_dir = Path(__file__).parent / "data" / "output"
    
    chronoslab = ChronosLab(config_dir)
    
    # Save constitution hash for integrity verification
    print("\n[1/3] Computing constitution hash...")
    chronoslab.save_constitution_hash()
    print("✓ Constitution hash computed and saved")
    
    # Process example case
    print("\n[2/3] Processing example case...")
    case_json = Path(__file__).parent / "data" / "input" / "case_demo.json"
    
    if not case_json.exists():
        print(f"✗ Example case not found: {case_json}")
        return 1
    
    results = chronoslab.process_case_from_json(
        case_json_path=case_json,
        output_dir=output_dir,
        verify_integrity=True
    )
    
    # Display results
    print("\n" + "="*60)
    print("RESULTS SUMMARY")
    print("="*60)
    print(f"Status: {results['status']}")
    print(f"\nOutputs:")
    for name, path in results['outputs'].items():
        print(f"  • {name}: {path}")
    
    if results.get('stats'):
        print(f"\nStatistics:")
        for key, value in results['stats'].items():
            print(f"  • {key}: {value}")
    
    if results['status'] == 'SUCCESS':
        print(f"\n✓ Success! Open the clinician cockpit in your browser:")
        print(f"  file://{results['outputs']['clinician_cockpit']}")
        return 0
    else:
        print(f"\n✗ Processing failed with status: {results['status']}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
