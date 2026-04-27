"""
helpers.py - Helper Utilities for Data Analytics Application

This module provides utility functions for type detection, formatting, and data processing.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime


class TypeDetector:
    """
    Detects and classifies column data types in DataFrames.
    """
    
    # Column type constants
    TYPE_NUMERIC = 'numeric'
    TYPE_CATEGORICAL = 'categorical'
    TYPE_DATETIME = 'datetime'
    TYPE_TEXT = 'text'
    TYPE_BOOLEAN = 'boolean'
    TYPE_UNKNOWN = 'unknown'
    
    @classmethod
    def detect_column_type(cls, series: pd.Series) -> str:
        """
        Detect the semantic type of a pandas Series.
        
        Args:
            series: pandas Series to analyze
            
        Returns:
            Type string: 'numeric', 'categorical', 'datetime', 'text', 'boolean', or 'unknown'
        """
        if series is None or len(series) == 0:
            return cls.TYPE_UNKNOWN
        
        # Check for boolean
        if pd.api.types.is_bool_dtype(series):
            return cls.TYPE_BOOLEAN
        
        # Check for datetime
        if pd.api.types.is_datetime64_any_dtype(series):
            return cls.TYPE_DATETIME
        
        # Check for numeric
        if pd.api.types.is_numeric_dtype(series):
            return cls.TYPE_NUMERIC
        
        # Check for categorical or object type
        # In pandas 2.0+, is_categorical_dtype is deprecated, using isinstance or dtypes directly
        if isinstance(series.dtype, pd.CategoricalDtype):
            return cls.TYPE_CATEGORICAL
        
        # For object dtype, try to determine if it's categorical or text
        if series.dtype == 'object' or series.dtype == 'string':
            # Try to parse as datetime (only if column name suggests it or sample looks like it)
            # Sampling first 10 rows for quick check
            sample = series.dropna().head(10)
            if not sample.empty:
                try:
                    # Using a very restrictive check for speed
                    pd.to_datetime(sample, errors='raise')
                    return cls.TYPE_DATETIME
                except:
                    pass
            
            # Check unique ratio to determine if categorical
            # Optimization: for large series, only check unique ratio on a sample if it's very large
            if len(series) > 10000:
                # Sample for nunique if it's very large
                sample_for_unique = series.sample(n=10000, random_state=42)
                n_unique_sample = sample_for_unique.nunique()
                unique_ratio = n_unique_sample / 10000
                n_unique = n_unique_sample # Approximation for the check below
            else:
                n_unique = series.nunique()
                unique_ratio = n_unique / len(series) if len(series) > 0 else 1

            if unique_ratio < 0.5 or n_unique <= 20:
                return cls.TYPE_CATEGORICAL
            else:
                return cls.TYPE_TEXT
        
        return cls.TYPE_UNKNOWN
    
    @classmethod
    def detect_all_column_types(cls, df: pd.DataFrame) -> Dict[str, str]:
        """
        Detect types for all columns in a DataFrame.
        
        Args:
            df: pandas DataFrame
            
        Returns:
            Dictionary mapping column names to their detected types
        """
        return {col: cls.detect_column_type(df[col]) for col in df.columns}
    
    @classmethod
    def get_columns_by_type(cls, df: pd.DataFrame, col_type: str) -> List[str]:
        """
        Get all columns of a specific type.
        
        Args:
            df: pandas DataFrame
            col_type: Type to filter by ('numeric', 'categorical', 'datetime', etc.)
            
        Returns:
            List of column names matching the type
        """
        types = cls.detect_all_column_types(df)
        return [col for col, t in types.items() if t == col_type]
    
    @classmethod
    def get_numeric_columns(cls, df: pd.DataFrame) -> List[str]:
        """Get all numeric columns."""
        return cls.get_columns_by_type(df, cls.TYPE_NUMERIC)
    
    @classmethod
    def get_categorical_columns(cls, df: pd.DataFrame) -> List[str]:
        """Get all categorical columns."""
        return cls.get_columns_by_type(df, cls.TYPE_CATEGORICAL)
    
    @classmethod
    def get_datetime_columns(cls, df: pd.DataFrame) -> List[str]:
        """Get all datetime columns."""
        return cls.get_columns_by_type(df, cls.TYPE_DATETIME)


class Formatter:
    """
    Provides formatting utilities for displaying data.
    """
    
    @staticmethod
    def format_number(value: float, precision: int = 2) -> str:
        """
        Format a number for display.
        
        Args:
            value: Number to format
            precision: Decimal places (default 2)
            
        Returns:
            Formatted string
        """
        if pd.isna(value):
            return "N/A"
        
        if isinstance(value, (int, np.integer)):
            return f"{value:,}"
        
        if abs(value) >= 1e6:
            return f"{value:.{precision}e}"
        
        return f"{value:,.{precision}f}"
    
    @staticmethod
    def format_percentage(value: float, precision: int = 1) -> str:
        """
        Format a value as a percentage.
        
        Args:
            value: Value to format (0-1 scale)
            precision: Decimal places
            
        Returns:
            Formatted percentage string
        """
        if pd.isna(value):
            return "N/A"
        
        return f"{value * 100:.{precision}f}%"
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """
        Format file size in human-readable form.
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            Formatted string (e.g., "1.5 MB")
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} PB"
    
    @staticmethod
    def format_shape(rows: int, cols: int) -> str:
        """
        Format DataFrame shape for display.
        
        Args:
            rows: Number of rows
            cols: Number of columns
            
        Returns:
            Formatted string
        """
        return f"{rows:,} rows × {cols:,} columns"
    
    @staticmethod
    def truncate_string(text: str, max_length: int = 50) -> str:
        """
        Truncate a string if it exceeds max length.
        
        Args:
            text: String to truncate
            max_length: Maximum length
            
        Returns:
            Truncated string with ellipsis if needed
        """
        if not text:
            return ""
        
        text = str(text)
        if len(text) <= max_length:
            return text
        
        return text[:max_length - 3] + "..."
    
    @staticmethod
    def generate_summary_text(df: pd.DataFrame) -> str:
        """
        Generate a summary text for a DataFrame.
        
        Args:
            df: pandas DataFrame
            
        Returns:
            Multi-line summary string
        """
        if df is None or df.empty:
            return "No data loaded"
        
        lines = []
        lines.append(f"Dataset Shape: {Formatter.format_shape(len(df), len(df.columns))}")
        lines.append(f"Memory Usage: {Formatter.format_file_size(df.memory_usage(deep=True).sum())}")
        
        # Missing values
        missing = df.isnull().sum().sum()
        total = df.size
        missing_pct = (missing / total * 100) if total > 0 else 0
        lines.append(f"Missing Values: {missing:,} ({missing_pct:.1f}%)")
        
        # Column types summary
        types = TypeDetector.detect_all_column_types(df)
        type_counts = {}
        for t in types.values():
            type_counts[t] = type_counts.get(t, 0) + 1
        
        type_summary = ", ".join([f"{count} {t}" for t, count in type_counts.items()])
        lines.append(f"Column Types: {type_summary}")
        
        return "\n".join(lines)
