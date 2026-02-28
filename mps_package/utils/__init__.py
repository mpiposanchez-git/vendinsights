"""Utility functions."""

import logging
from pathlib import Path


def setup_logger(name: str, log_file: str = None) -> logging.Logger:
    """
    Setup logger for the project.
    
    Args:
        name: Logger name
        log_file: Optional log file path
    
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_data_path(subdir: str = None) -> Path:
    """Get path to data directory."""
    base_path = Path(__file__).parent.parent.parent / 'data'
    if subdir:
        return base_path / subdir
    return base_path
