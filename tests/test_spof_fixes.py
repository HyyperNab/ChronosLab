"""
Test suite for SPOF elimination.
Tests atomic writes, validation, error handling.
"""

import pytest
import tempfile
import os
from pathlib import Path
import json

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fileio import atomic_write, safe_read_text, safe_read_json, safe_write_json, FileIOError
from validation import CaseValidator, ConfigValidator, ValidationError
from logging_config import get_logger


class TestAtomicWrites:
    """Test atomic file operations"""
    
    def test_atomic_write_success(self):
        """Test successful atomic write"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.txt"
            content = "test content"
            
            atomic_write(path, content)
            
            assert path.exists()
            assert path.read_text() == content
    
    def test_atomic_write_creates_parent_dir(self):
        """Test atomic write creates parent directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "subdir" / "test.txt"
            content = "test"
            
            atomic_write(path, content)
            
            assert path.exists()
            assert path.read_text() == content
    
    def test_atomic_write_overwrites_existing(self):
        """Test atomic write overwrites existing file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.txt"
            path.write_text("old content")
            
            atomic_write(path, "new content")
            
            assert path.read_text() == "new content"
    
    def test_safe_read_missing_file(self):
        """Test safe read raises FileIOError for missing file"""
        with pytest.raises(FileIOError, match="not found"):
            safe_read_text(Path("/nonexistent/file.txt"))


class TestCaseValidation:
    """Test case data validation"""
    
    def test_valid_case(self):
        """Test validation passes for valid case"""
        data = {
            "case_id": "CASE-001",
            "canonical_rows_long": [
                {
                    "case_id": "CASE-001",
                    "doc_id": "DOC-001",
                    "page": 1,
                    "datetime": "2024-01-15T09:30:00",
                    "analyte_canonical": "Hemoglobin",
                    "panel_key": "NFS"
                }
            ]
        }
        
        # Should not raise
        CaseValidator.validate(data)
    
    def test_missing_case_id(self):
        """Test validation fails for missing case_id"""
        data = {
            "canonical_rows_long": []
        }
        
        with pytest.raises(ValidationError, match="case_id"):
            CaseValidator.validate(data)
    
    def test_empty_rows(self):
        """Test validation fails for empty rows"""
        data = {
            "case_id": "CASE-001",
            "canonical_rows_long": []
        }
        
        with pytest.raises(ValidationError, match="cannot be empty"):
            CaseValidator.validate(data)
    
    def test_invalid_datetime(self):
        """Test validation fails for invalid datetime"""
        data = {
            "case_id": "CASE-001",
            "canonical_rows_long": [
                {
                    "case_id": "CASE-001",
                    "doc_id": "DOC-001",
                    "page": 1,
                    "datetime": "not-a-date",
                    "analyte_canonical": "Hemoglobin",
                    "panel_key": "NFS"
                }
            ]
        }
        
        with pytest.raises(ValidationError, match="ISO 8601"):
            CaseValidator.validate(data)
    
    def test_negative_page_number(self):
        """Test validation fails for negative page"""
        data = {
            "case_id": "CASE-001",
            "canonical_rows_long": [
                {
                    "case_id": "CASE-001",
                    "doc_id": "DOC-001",
                    "page": -1,
                    "datetime": "2024-01-15T09:30:00",
                    "analyte_canonical": "Hemoglobin",
                    "panel_key": "NFS"
                }
            ]
        }
        
        with pytest.raises(ValidationError, match="non-negative"):
            CaseValidator.validate(data)


class TestConfigValidation:
    """Test configuration validation"""
    
    def test_valid_constitution(self):
        """Test validation passes for valid constitution"""
        data = {
            "name": "ChronosLab",
            "version": "1.4.3",
            "panel_order": ["NFS", "RENAL"],
            "core_principles": ["truth_over_completeness"]
        }
        
        # Should not raise
        ConfigValidator.validate_constitution(data)
    
    def test_missing_panel_order(self):
        """Test validation fails for missing panel_order"""
        data = {
            "name": "ChronosLab",
            "version": "1.4.3",
            "core_principles": []
        }
        
        with pytest.raises(ValidationError, match="panel_order"):
            ConfigValidator.validate_constitution(data)
    
    def test_valid_analyte_dict(self):
        """Test validation passes for valid analyte dictionary"""
        data = {
            "analytes": [
                {
                    "canonical": "Hemoglobin",
                    "panel": "NFS",
                    "order": 0
                }
            ]
        }
        
        # Should not raise
        ConfigValidator.validate_analyte_dict(data)
    
    def test_empty_analytes(self):
        """Test validation fails for empty analytes list"""
        data = {
            "analytes": []
        }
        
        with pytest.raises(ValidationError, match="cannot be empty"):
            ConfigValidator.validate_analyte_dict(data)


class TestLogging:
    """Test logging functionality"""
    
    def test_logger_initialization(self):
        """Test logger can be initialized"""
        logger = get_logger()
        assert logger is not None
    
    def test_logger_with_file(self):
        """Test logger with file output"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            logger = get_logger(log_file=log_file)
            
            logger.info("test message")
            
            assert log_file.exists()
            content = log_file.read_text()
            assert "test message" in content


class TestJSONSafety:
    """Test JSON operations are safe"""
    
    def test_safe_write_json(self):
        """Test JSON writing with proper encoding"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.json"
            data = {"key": "value with émojis 🎉"}
            
            safe_write_json(path, data)
            
            loaded = safe_read_json(path)
            assert loaded == data
    
    def test_safe_read_invalid_json(self):
        """Test safe read raises error for invalid JSON"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "invalid.json"
            path.write_text("not valid json{")
            
            with pytest.raises(FileIOError, match="Invalid JSON"):
                safe_read_json(path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
