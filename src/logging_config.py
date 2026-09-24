"""
Structured logging for ChronosLab.
Replaces print statements with proper logging.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


class ChronosLabLogger:
    """Centralized logging for ChronosLab"""
    
    def __init__(
        self,
        name: str = "chronoslab",
        log_file: Optional[Path] = None,
        level: int = logging.INFO
    ):
        """
        Initialize logger.
        
        Args:
            name: Logger name
            log_file: Optional log file path
            level: Logging level
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler if specified
        if log_file:
            log_file = Path(log_file)
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)  # More verbose in file
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
    
    def info(self, msg: str, **kwargs) -> None:
        """Log info message"""
        self.logger.info(msg, extra=kwargs)
    
    def warning(self, msg: str, **kwargs) -> None:
        """Log warning message"""
        self.logger.warning(msg, extra=kwargs)
    
    def error(self, msg: str, **kwargs) -> None:
        """Log error message"""
        self.logger.error(msg, extra=kwargs)
    
    def debug(self, msg: str, **kwargs) -> None:
        """Log debug message"""
        self.logger.debug(msg, extra=kwargs)
    
    def critical(self, msg: str, **kwargs) -> None:
        """Log critical message"""
        self.logger.critical(msg, extra=kwargs)
    
    def log_case_processing(
        self,
        case_id: str,
        status: str,
        details: Optional[str] = None
    ) -> None:
        """Log case processing event"""
        msg = f"Case {case_id}: {status}"
        if details:
            msg += f" - {details}"
        self.info(msg)
    
    def log_lint_result(
        self,
        case_id: str,
        passed: bool,
        errors: int = 0,
        warnings: int = 0
    ) -> None:
        """Log linting result"""
        if passed:
            self.info(f"Lint passed for {case_id} ({warnings} warnings)")
        else:
            self.error(f"Lint FAILED for {case_id} ({errors} errors, {warnings} warnings)")
    
    def log_export(
        self,
        case_id: str,
        export_type: str,
        path: Path,
        success: bool = True
    ) -> None:
        """Log export operation"""
        if success:
            self.info(f"Exported {export_type} for {case_id} to {path}")
        else:
            self.error(f"Failed to export {export_type} for {case_id}")
    
    def log_error_with_context(
        self,
        error: Exception,
        context: str,
        case_id: Optional[str] = None
    ) -> None:
        """Log error with full context"""
        msg = f"Error in {context}"
        if case_id:
            msg += f" (case {case_id})"
        msg += f": {type(error).__name__}: {str(error)}"
        self.error(msg)


# Global logger instance
_logger: Optional[ChronosLabLogger] = None


def get_logger(
    log_file: Optional[Path] = None,
    level: int = logging.INFO
) -> ChronosLabLogger:
    """
    Get or create global logger instance.
    
    Args:
        log_file: Optional log file path
        level: Logging level
        
    Returns:
        Logger instance
    """
    global _logger
    
    if _logger is None:
        _logger = ChronosLabLogger(log_file=log_file, level=level)
    
    return _logger
