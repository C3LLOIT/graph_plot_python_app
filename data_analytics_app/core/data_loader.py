"""
data_loader.py - Data Loading Module

This module handles loading data from CSV and JSON files into pandas DataFrames,
with proper error handling and file type detection.
"""

import pandas as pd
import os
from typing import Tuple, Optional, Dict, Any
from utils.validators import FileValidator


class DataLoader:
    """
    Handles loading data from various file formats into pandas DataFrames.
    
    Supports:
        - CSV files (.csv)
        - JSON files (.json)
    
    Features:
        - Automatic file type detection
        - Error handling for malformed data
        - Missing value handling
        - Large file support
    """
    
    def __init__(self):
        """Initialize the DataLoader."""
        self.current_df: Optional[pd.DataFrame] = None
        self.file_path: Optional[str] = None
        self.file_type: Optional[str] = None
        self.load_errors: list = []
    
    def load_file(self, file_path: str) -> Tuple[bool, str]:
        """
        Load data from a file into a DataFrame.
        
        Args:
            file_path: Path to the file to load
            
        Returns:
            Tuple of (success, message)
        """
        self.load_errors = []
        
        # Validate file
        is_valid, error = FileValidator.validate_file(file_path)
        if not is_valid:
            return False, error
        
        # Detect file type
        self.file_type = FileValidator.get_file_type(file_path)
        self.file_path = file_path
        
        try:
            if self.file_type == 'csv':
                success, message = self._load_csv(file_path)
            elif self.file_type == 'json':
                success, message = self._load_json(file_path)
            else:
                return False, f"Unsupported file type: {self.file_type}"
            
            if success:
                self._post_process()
            
            return success, message
            
        except Exception as e:
            self.current_df = None
            return False, f"Error loading file: {str(e)}"
    
    def _load_csv(self, file_path: str) -> Tuple[bool, str]:
        """
        Load a CSV file.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            
            for encoding in encodings:
                try:
                    self.current_df = pd.read_csv(
                        file_path,
                        encoding=encoding,
                        low_memory=False,
                        on_bad_lines='warn'
                    )
                    break
                except UnicodeDecodeError:
                    continue
            else:
                # If all encodings fail, try with error handling
                self.current_df = pd.read_csv(
                    file_path,
                    encoding='utf-8',
                    errors='replace',
                    low_memory=False
                )
            
            rows, cols = self.current_df.shape
            return True, f"Successfully loaded CSV: {rows:,} rows × {cols:,} columns"
            
        except pd.errors.EmptyDataError:
            return False, "The CSV file is empty"
        except pd.errors.ParserError as e:
            return False, f"Error parsing CSV: {str(e)}"
    
    def _load_json(self, file_path: str) -> Tuple[bool, str]:
        """
        Load a JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Try loading as different JSON structures
            try:
                # First, try as standard JSON (records or columns orientation)
                self.current_df = pd.read_json(file_path)
            except ValueError:
                # Try loading as lines (newline-delimited JSON)
                self.current_df = pd.read_json(file_path, lines=True)
            
            rows, cols = self.current_df.shape
            return True, f"Successfully loaded JSON: {rows:,} rows × {cols:,} columns"
            
        except ValueError as e:
            return False, f"Error parsing JSON: {str(e)}"
    
    def _post_process(self):
        """
        Post-process the loaded DataFrame.
        
        - Attempts to detect and convert datetime columns
        - Handles common data issues
        """
        if self.current_df is None:
            return
        
        # Try to parse date columns
        for col in self.current_df.columns:
            if self.current_df[col].dtype == 'object':
                # Check if column name suggests datetime
                date_keywords = ['date', 'time', 'timestamp', 'created', 'updated', 'datetime']
                if any(kw in col.lower() for kw in date_keywords):
                    try:
                        self.current_df[col] = pd.to_datetime(
                            self.current_df[col],
                            infer_datetime_format=True,
                            errors='coerce'
                        )
                    except:
                        pass
    
    def get_dataframe(self) -> Optional[pd.DataFrame]:
        """
        Get the currently loaded DataFrame.
        
        Returns:
            The loaded DataFrame or None if no data is loaded
        """
        return self.current_df
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded data.
        
        Returns:
            Dictionary with data information
        """
        if self.current_df is None:
            return {
                'loaded': False,
                'file_path': None,
                'file_type': None,
                'shape': (0, 0),
                'columns': [],
                'dtypes': {},
                'memory_usage': 0
            }
        
        return {
            'loaded': True,
            'file_path': self.file_path,
            'file_type': self.file_type,
            'shape': self.current_df.shape,
            'columns': list(self.current_df.columns),
            'dtypes': {col: str(dtype) for col, dtype in self.current_df.dtypes.items()},
            'memory_usage': self.current_df.memory_usage(deep=True).sum(),
            'missing_values': self.current_df.isnull().sum().to_dict()
        }
    
    def get_preview(self, n_rows: int = 100) -> Optional[pd.DataFrame]:
        """
        Get a preview of the first N rows.
        
        Args:
            n_rows: Number of rows to return
            
        Returns:
            DataFrame with first N rows or None
        """
        if self.current_df is None:
            return None
        return self.current_df.head(n_rows)
    
    def clear(self):
        """Clear the currently loaded data."""
        self.current_df = None
        self.file_path = None
        self.file_type = None
        self.load_errors = []
