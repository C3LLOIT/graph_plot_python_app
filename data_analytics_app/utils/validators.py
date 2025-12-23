"""
validators.py - File and Data Validation Utilities

This module provides validation functions for file handling and data integrity checks.
"""

import os
from typing import Tuple, Optional


class FileValidator:
    """
    Validates file existence, accessibility, and format requirements.
    """
    
    # Supported file extensions
    SUPPORTED_EXTENSIONS = {'.csv', '.json'}
    
    @classmethod
    def validate_file_path(cls, file_path: str) -> Tuple[bool, str]:
        """
        Validate that a file exists and is accessible.
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not file_path:
            return False, "No file path provided"
        
        if not os.path.exists(file_path):
            return False, f"File does not exist: {file_path}"
        
        if not os.path.isfile(file_path):
            return False, f"Path is not a file: {file_path}"
        
        if not os.access(file_path, os.R_OK):
            return False, f"File is not readable: {file_path}"
        
        return True, ""
    
    @classmethod
    def validate_extension(cls, file_path: str) -> Tuple[bool, str]:
        """
        Validate that a file has a supported extension.
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not file_path:
            return False, "No file path provided"
        
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        if ext not in cls.SUPPORTED_EXTENSIONS:
            supported = ", ".join(cls.SUPPORTED_EXTENSIONS)
            return False, f"Unsupported file type: {ext}. Supported types: {supported}"
        
        return True, ""
    
    @classmethod
    def get_file_type(cls, file_path: str) -> Optional[str]:
        """
        Get the file type from extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File type ('csv' or 'json') or None if unsupported
        """
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        if ext == '.csv':
            return 'csv'
        elif ext == '.json':
            return 'json'
        return None
    
    @classmethod
    def validate_file(cls, file_path: str) -> Tuple[bool, str]:
        """
        Perform complete file validation.
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check file path
        is_valid, error = cls.validate_file_path(file_path)
        if not is_valid:
            return False, error
        
        # Check extension
        is_valid, error = cls.validate_extension(file_path)
        if not is_valid:
            return False, error
        
        return True, ""


class DataValidator:
    """
    Validates DataFrame contents and structure.
    """
    
    @staticmethod
    def validate_dataframe(df) -> Tuple[bool, str]:
        """
        Validate that a DataFrame is valid for analysis.
        
        Args:
            df: pandas DataFrame to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if df is None:
            return False, "DataFrame is None"
        
        if df.empty:
            return False, "DataFrame is empty"
        
        if len(df.columns) == 0:
            return False, "DataFrame has no columns"
        
        return True, ""
    
    @staticmethod
    def validate_columns_exist(df, columns: list) -> Tuple[bool, str]:
        """
        Validate that specified columns exist in the DataFrame.
        
        Args:
            df: pandas DataFrame
            columns: List of column names to check
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if df is None:
            return False, "DataFrame is None"
        
        missing = [col for col in columns if col not in df.columns]
        
        if missing:
            return False, f"Missing columns: {', '.join(missing)}"
        
        return True, ""
    
    @staticmethod
    def validate_numeric_column(df, column: str) -> Tuple[bool, str]:
        """
        Validate that a column contains numeric data.
        
        Args:
            df: pandas DataFrame
            column: Column name to check
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        import pandas as pd
        
        if column not in df.columns:
            return False, f"Column '{column}' not found"
        
        if not pd.api.types.is_numeric_dtype(df[column]):
            return False, f"Column '{column}' is not numeric"
        
        return True, ""
