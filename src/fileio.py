"""
Robust file I/O operations with atomic writes and proper error handling.
"""

import os
import tempfile
from pathlib import Path
from typing import Union, Optional
import json


class FileIOError(Exception):
    """Raised when file operations fail"""
    pass


def atomic_write(
    path: Path,
    content: Union[str, bytes],
    encoding: Optional[str] = 'utf-8'
) -> None:
    """
    Write file atomically (write to temp, then move).
    Prevents partial writes if process is killed.
    
    Args:
        path: Target file path
        content: Content to write
        encoding: Text encoding (None for binary)
        
    Raises:
        FileIOError: If write fails
    """
    path = Path(path)
    
    # Create parent directory if needed
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise FileIOError(f"Cannot create directory {path.parent}: {e}")
    
    # Write to temporary file in same directory
    # (must be same filesystem for atomic move)
    try:
        fd, temp_path = tempfile.mkstemp(
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp"
        )
        
        try:
            if isinstance(content, str):
                if encoding is None:
                    raise FileIOError("String content requires encoding")
                os.write(fd, content.encode(encoding))
            else:
                os.write(fd, content)
        finally:
            os.close(fd)
        
        # Atomic move (overwrites existing file)
        os.replace(temp_path, path)
        
    except OSError as e:
        # Clean up temp file if it exists
        try:
            if 'temp_path' in locals():
                os.unlink(temp_path)
        except:
            pass
        raise FileIOError(f"Failed to write {path}: {e}")


def safe_read_text(path: Path, encoding: str = 'utf-8') -> str:
    """
    Safely read text file with proper error handling.
    
    Args:
        path: File path
        encoding: Text encoding
        
    Returns:
        File contents
        
    Raises:
        FileIOError: If read fails
    """
    path = Path(path)
    
    if not path.exists():
        raise FileIOError(f"File not found: {path}")
    
    if not path.is_file():
        raise FileIOError(f"Not a file: {path}")
    
    try:
        return path.read_text(encoding=encoding)
    except UnicodeDecodeError as e:
        raise FileIOError(f"Encoding error in {path}: {e}")
    except OSError as e:
        raise FileIOError(f"Cannot read {path}: {e}")


def safe_read_json(path: Path) -> dict:
    """
    Safely read and parse JSON file.
    
    Args:
        path: JSON file path
        
    Returns:
        Parsed JSON data
        
    Raises:
        FileIOError: If read or parse fails
    """
    content = safe_read_text(path)
    
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        raise FileIOError(f"Invalid JSON in {path}: {e}")


def safe_write_json(path: Path, data: dict, indent: int = 2) -> None:
    """
    Safely write JSON file atomically.
    
    Args:
        path: Target file path
        data: Data to serialize
        indent: JSON indentation
        
    Raises:
        FileIOError: If write fails
    """
    try:
        content = json.dumps(data, indent=indent, ensure_ascii=False)
    except (TypeError, ValueError) as e:
        raise FileIOError(f"Cannot serialize data: {e}")
    
    atomic_write(path, content, encoding='utf-8')
