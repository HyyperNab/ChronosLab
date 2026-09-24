"""
ChronosLab Configuration System
Loads and validates constitution, policies, and analyte dictionaries.
Implements hash-based immutability checks.
"""

import hashlib
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

try:
    from .fileio import safe_read_text, safe_read_json, safe_write_json, FileIOError
    from .validation import ConfigValidator, ValidationError
    from .logging_config import get_logger
except ImportError:
    from fileio import safe_read_text, safe_read_json, safe_write_json, FileIOError
    from validation import ConfigValidator, ValidationError
    from logging_config import get_logger


class ConfigurationError(Exception):
    """Raised when configuration is invalid or tampered"""
    pass


@dataclass
class Constitution:
    """ChronosLab constitutional settings"""
    name: str
    version: str
    core_principles: List[str]
    panel_order: List[str]
    panel_labels: Dict[str, str]
    nfs_suborder: List[str]
    renal_membership_locked: List[str]
    reference_policy: Dict[str, Any]
    canonical_row_required_fields: List[str]
    clinician_cockpit: Dict[str, Any]
    linting: Dict[str, List[str]]
    privacy: Dict[str, Any]
    identity_policy: Dict[str, Any]
    
    @property
    def colors(self) -> Dict[str, str]:
        return self.clinician_cockpit.get("colors", {})
    
    @property
    def reference_triggers(self) -> Dict[str, List[str]]:
        return self.reference_policy.get("reference_triggers", {})


class ConfigLoader:
    """
    Loads and validates ChronosLab configuration.
    Implements determinism through hash verification.
    """
    
    def __init__(self, config_dir: Path):
        self.config_dir = Path(config_dir)
        self._constitution: Optional[Constitution] = None
        self._analyte_dict: Optional[Dict[str, Any]] = None
        
    def load_constitution(self, verify_hash: bool = False) -> Constitution:
        """
        Load constitution from JSON.
        
        Args:
            verify_hash: If True, verify constitution hasn't been modified
            
        Returns:
            Constitution object
            
        Raises:
            ConfigurationError: If constitution is invalid or hash mismatch
        """
        logger = get_logger()
        constitution_path = self.config_dir / "constitution.json"
        
        if not constitution_path.exists():
            raise ConfigurationError(f"Constitution not found: {constitution_path}")
        
        # Safe read with error handling
        try:
            data = safe_read_json(constitution_path)
        except FileIOError as e:
            raise ConfigurationError(f"Cannot load constitution: {e}")
        
        # Validate structure
        try:
            ConfigValidator.validate_constitution(data)
        except ValidationError as e:
            raise ConfigurationError(f"Invalid constitution: {e}")
        
        # Compute hash if requested
        if verify_hash:
            computed_hash = self._compute_file_hash(constitution_path)
            stored_hash = data.get("constitution_hash")
            if stored_hash and stored_hash != "TO_BE_COMPUTED" and computed_hash != stored_hash:
                raise ConfigurationError(
                    f"Constitution hash mismatch! "
                    f"Expected: {stored_hash}, Got: {computed_hash}"
                )
        
        logger.debug(f"Loaded constitution v{data['version']}")
        
        self._constitution = Constitution(
            name=data["name"],
            version=data["version"],
            core_principles=data["core_principles"],
            panel_order=data["panel_order"],
            panel_labels=data.get("panel_labels", {}),
            nfs_suborder=data.get("nfs_suborder", []),
            renal_membership_locked=data.get("renal_membership_locked", []),
            reference_policy=data.get("reference_policy", {}),
            canonical_row_required_fields=data.get("canonical_row_required_fields", []),
            clinician_cockpit=data.get("clinician_cockpit", {}),
            linting=data.get("linting", {}),
            privacy=data.get("privacy", {}),
            identity_policy=data.get("identity_policy", {})
        )
        
        return self._constitution
    
    def load_analyte_dictionary(self) -> Dict[str, Any]:
        """
        Load analyte dictionary from YAML.
        
        Returns:
            Parsed analyte dictionary
            
        Raises:
            ConfigurationError: If dictionary is invalid
        """
        logger = get_logger()
        dict_path = self.config_dir / "analyte_dictionary.yaml"
        
        if not dict_path.exists():
            raise ConfigurationError(f"Analyte dictionary not found: {dict_path}")
        
        try:
            content = safe_read_text(dict_path)
            data = yaml.safe_load(content)
        except FileIOError as e:
            raise ConfigurationError(f"Cannot load analyte dictionary: {e}")
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in analyte dictionary: {e}")
        
        # Validate structure
        try:
            ConfigValidator.validate_analyte_dict(data)
        except ValidationError as e:
            raise ConfigurationError(f"Invalid analyte dictionary: {e}")
        
        # Build lookup index for fast analyte resolution
        lookup = {}
        for analyte in data["analytes"]:
            canonical = analyte["canonical"]
            
            # Add canonical name
            lookup[canonical.lower()] = {
                "canonical": canonical,
                "panel": analyte["panel"],
                "order": analyte["order"]
            }
            
            # Add all synonyms
            for lang, synonyms in analyte.get("synonyms", {}).items():
                for syn in synonyms:
                    lookup[syn.lower()] = {
                        "canonical": canonical,
                        "panel": analyte["panel"],
                        "order": analyte["order"]
                    }
        
        logger.debug(f"Loaded {len(data['analytes'])} analytes with {len(lookup)} synonyms")
        
        self._analyte_dict = {
            "raw": data,
            "lookup": lookup
        }
        
        return self._analyte_dict
    
    def resolve_analyte(self, raw_name: str) -> Optional[Dict[str, Any]]:
        """
        Resolve raw analyte name to canonical form.
        
        Args:
            raw_name: Raw analyte name from lab report
            
        Returns:
            Dict with canonical, panel, order or None if not found
        """
        if not self._analyte_dict:
            self.load_analyte_dictionary()
        
        return self._analyte_dict["lookup"].get(raw_name.lower())
    
    def get_constitution(self) -> Constitution:
        """Get loaded constitution (loads if not already loaded)"""
        if not self._constitution:
            self.load_constitution()
        return self._constitution
    
    @staticmethod
    def _compute_file_hash(filepath: Path) -> str:
        """Compute SHA256 hash of file content"""
        sha256 = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def save_constitution_hash(self) -> None:
        """Compute and save constitution hash"""
        constitution_path = self.config_dir / "constitution.json"
        
        # Load current constitution
        try:
            data = safe_read_json(constitution_path)
        except FileIOError as e:
            raise ConfigurationError(f"Cannot load constitution: {e}")
        
        # Temporarily remove hash field for computation
        data.pop("constitution_hash", None)
        
        # Compute hash of normalized JSON
        import json
        normalized = json.dumps(data, sort_keys=True, indent=2)
        hash_value = hashlib.sha256(normalized.encode('utf-8')).hexdigest()
        
        # Save hash back
        data["constitution_hash"] = hash_value
        
        try:
            safe_write_json(constitution_path, data)
            print(f"Constitution hash saved: {hash_value[:16]}...")
        except FileIOError as e:
            raise ConfigurationError(f"Cannot save constitution hash: {e}")
