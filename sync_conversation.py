#!/usr/bin/env python3
"""
Conversation Sync Script
========================

Purpose: Keep this conversation focused on coding/architecture
         Archive context to transcript for clean reconnection

Usage:
    python sync_conversation.py --action [archive|restore|status]

Actions:
    archive  - Save current context to transcript, clean conversation
    restore  - Load context from transcript for reconnection
    status   - Show current conversation state
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class ConversationSync:
    """Manages conversation context archival and restoration"""
    
    def __init__(self, transcript_dir: Path = Path("/mnt/transcripts")):
        self.transcript_dir = transcript_dir
        self.sync_file = Path("/mnt/user-data/outputs/conversation_sync.json")
        self.context_archive = Path("/mnt/user-data/outputs/context_archive.json")
    
    def archive_context(self) -> Dict:
        """
        Archive current conversation context.
        
        Returns:
            Archive metadata
        """
        # Get latest transcript
        transcripts = sorted(self.transcript_dir.glob("*.txt"))
        if not transcripts:
            print("❌ No transcripts found")
            return {}
        
        latest_transcript = transcripts[-1]
        
        # Create context snapshot
        context = {
            "timestamp": datetime.now().isoformat(),
            "transcript": str(latest_transcript),
            "version": "v1.6.0",
            "status": "CONSTITUTIONAL_AMENDMENT",
            "active_package": "chronoslab_v1.6.0_ARCHITECTURE_LOCKED.tar.gz",
            
            # Key decisions made
            "decisions": [
                "v1.5.0 had constitutional violations (interactive prompts, fallbacks)",
                "v1.5.1 restored compliance (HARD FAIL only, no interaction)",
                "v1.6.0 constitutional amendment (clinical panel order + UX improvements)",
                "ChatGPT session (2026-01-11) validated UX improvements",
                "Panel order: alphabetical → clinical priority (10 panels)",
                "Index banner, dark teal headers, unified dates, em-dash for missing",
                "YAML normalization kept (304 entries, FR/EN/DE)",
                "Fuzzy matching confidence-tagged (HIGH/LOW/UNKNOWN)",
                "All fallback logic removed (truth over completeness)"
            ],
            
            # Critical files
            "files": {
                "package": "chronoslab_v1.6.0_ARCHITECTURE_LOCKED.tar.gz",
                "amendment": "CONSTITUTIONAL_AMENDMENT_v1.6.0.md",
                "architecture_lock": "ARCHITECTURE_LOCK_v1.6.0.md",
                "html_spec": "docs/HTML_GENERATION_SPEC.md (v1.6.0)",
                "repository_lock": "REPOSITORY_LOCK.md (v1.6.0)",
                "quick_start": "QUICK_START.md (inside package)"
            },
            
            # What's locked
            "locked": {
                "panel_order": "Clinical (10 panels) - v1.6.0 amendment",
                "renal_membership": "7 analytes (frozen, unchanged)",
                "nfs_suborder": "12 analytes (frozen, unchanged)",
                "html_spec": "docs/HTML_GENERATION_SPEC.md (v1.6.0)",
                "architecture": "ARCHITECTURE_LOCK_v1.6.0.md (FROZEN)",
                "principles": [
                    "truth_over_completeness",
                    "silence_over_speculation",
                    "determinism_over_cleverness",
                    "clinician_first_readability",
                    "datenschutz_by_design"
                ]
            },
            
            # Quick reconnection
            "reconnect_context": {
                "task": "Medical lab PDF → HTML chronological table",
                "version": "v1.6.0 (constitutional amendment)",
                "languages": "French, English, German",
                "normalization": "304 YAML mappings",
                "compliance": "Constitutional v1.6.0",
                "panel_order": "Clinical priority (10 panels)",
                "ui_features": "Index banner, dark teal, unified dates, em-dash",
                "workflow": "PDF → OCR → Identity (HARD FAIL) → Extract → Normalize → Lint → HTML",
                "no_interaction": "All failures are HARD FAIL (deterministic)",
                "no_fallbacks": "Missing data = explicit error (truth over completeness)",
                "architecture": "LOCKED (v1.6.0)"
            }
        }
        
        # Save archive
        with open(self.context_archive, 'w') as f:
            json.dump(context, f, indent=2)
        
        # Create sync metadata
        sync_meta = {
            "last_archived": context["timestamp"],
            "transcript_file": str(latest_transcript),
            "archive_file": str(self.context_archive)
        }
        
        with open(self.sync_file, 'w') as f:
            json.dump(sync_meta, f, indent=2)
        
        print(f"✓ Context archived to: {self.context_archive}")
        print(f"✓ Transcript: {latest_transcript.name}")
        print(f"✓ Sync metadata: {self.sync_file}")
        
        return context
    
    def restore_context(self) -> Optional[Dict]:
        """
        Restore conversation context from archive.
        
        Returns:
            Archived context or None
        """
        if not self.context_archive.exists():
            print("❌ No archived context found")
            print(f"   Run: python sync_conversation.py --action archive")
            return None
        
        with open(self.context_archive, 'r') as f:
            context = json.load(f)
        
        print("="*60)
        print("CONVERSATION CONTEXT RESTORED")
        print("="*60)
        print(f"\nArchived: {context['timestamp']}")
        print(f"Version: {context['version']}")
        print(f"Status: {context['status']}")
        
        print("\n📦 ACTIVE PACKAGE:")
        print(f"   {context['active_package']}")
        
        print("\n🔒 LOCKED COMPONENTS:")
        for key, value in context['locked'].items():
            if isinstance(value, list):
                print(f"   {key}: {len(value)} items")
            else:
                print(f"   {key}: {value}")
        
        print("\n⚡ QUICK RECONNECT:")
        rc = context['reconnect_context']
        print(f"   Task: {rc['task']}")
        print(f"   Languages: {rc['languages']}")
        print(f"   Workflow: {rc['workflow']}")
        print(f"   Compliance: {rc['compliance']}")
        
        print("\n📋 KEY DECISIONS:")
        for i, decision in enumerate(context['decisions'], 1):
            print(f"   {i}. {decision}")
        
        print("\n📄 FILES:")
        for key, value in context['files'].items():
            print(f"   {key}: {value}")
        
        print("\n" + "="*60)
        print("Context restored. Ready to continue.")
        print("="*60)
        
        return context
    
    def show_status(self) -> None:
        """Show current conversation state"""
        print("="*60)
        print("CONVERSATION SYNC STATUS")
        print("="*60)
        
        # Check sync file
        if self.sync_file.exists():
            with open(self.sync_file, 'r') as f:
                sync_meta = json.load(f)
            
            print("\n✓ Sync metadata found")
            print(f"  Last archived: {sync_meta['last_archived']}")
            print(f"  Transcript: {Path(sync_meta['transcript_file']).name}")
        else:
            print("\n❌ No sync metadata")
            print("   Run: python sync_conversation.py --action archive")
        
        # Check archive
        if self.context_archive.exists():
            with open(self.context_archive, 'r') as f:
                context = json.load(f)
            
            print("\n✓ Context archive found")
            print(f"  Version: {context['version']}")
            print(f"  Status: {context['status']}")
            print(f"  Package: {context['active_package']}")
        else:
            print("\n❌ No context archive")
        
        # Check transcripts
        transcripts = sorted(self.transcript_dir.glob("*.txt"))
        print(f"\n📝 Available transcripts: {len(transcripts)}")
        if transcripts:
            latest = transcripts[-1]
            print(f"   Latest: {latest.name}")
        
        # Check journal
        journal = self.transcript_dir / "journal.txt"
        if journal.exists():
            print(f"\n📚 Journal: {journal}")
        
        print("\n" + "="*60)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Conversation sync for ChronosLab development"
    )
    parser.add_argument(
        '--action',
        choices=['archive', 'restore', 'status'],
        required=True,
        help="Action to perform"
    )
    
    args = parser.parse_args()
    
    sync = ConversationSync()
    
    if args.action == 'archive':
        context = sync.archive_context()
        if context:
            print("\n✓ Context archived successfully")
            print("\nTo restore in new conversation:")
            print("  python sync_conversation.py --action restore")
    
    elif args.action == 'restore':
        context = sync.restore_context()
        if context:
            print("\n✓ Ready to continue development")
        else:
            print("\n❌ No context to restore")
            sys.exit(1)
    
    elif args.action == 'status':
        sync.show_status()


if __name__ == "__main__":
    main()
