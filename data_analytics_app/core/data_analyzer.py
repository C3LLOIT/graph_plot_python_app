"""
data_analyzer.py - Data Analysis Module

This module provides statistical analysis and data insights for pandas DataFrames.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from utils.helpers import TypeDetector


class DataAnalyzer:
    """
    Provides statistical analysis and data insights for DataFrames.
    
    Features:
        - Descriptive statistics (mean, median, mode, std, min, max)
        - Correlation analysis
        - Column-wise summaries
        - Missing value analysis
    """
    
    def __init__(self, df: Optional[pd.DataFrame] = None):
        """
        Initialize the DataAnalyzer.
        
        Args:
            df: Optional DataFrame to analyze
        """
        self.df = df
        self._column_types = None
    
    def set_dataframe(self, df: pd.DataFrame):
        """
        Set the DataFrame to analyze.
        
        Args:
            df: pandas DataFrame
        """
        self.df = df
        self._column_types = None  # Reset cache

    def _get_column_types(self) -> Dict[str, str]:
        """Get or compute cached column types."""
        if self._column_types is None and self.df is not None:
            self._column_types = TypeDetector.detect_all_column_types(self.df)
        return self._column_types or {}
    
    def get_descriptive_stats(self, columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Get descriptive statistics for numeric columns.
        
        Args:
            columns: Optional list of columns to analyze. If None, analyzes all numeric columns.
            
        Returns:
            DataFrame with statistics (mean, median, mode, std, min, max, etc.)
        """
        if self.df is None:
            return pd.DataFrame()
        
        # Get numeric columns
        if columns is None:
            col_types = self._get_column_types()
            numeric_cols = [c for c, t in col_types.items() if t == TypeDetector.TYPE_NUMERIC]
        else:
            numeric_cols = [c for c in columns if c in self.df.columns and 
                          pd.api.types.is_numeric_dtype(self.df[c])]
        
        if not numeric_cols:
            return pd.DataFrame()
        
        # Use pandas describe() which is highly optimized
        desc = self.df[numeric_cols].describe(percentiles=[.25, .5, .75]).T
        
        # Rename columns to match the expected format
        desc = desc.rename(columns={
            '50%': 'median',
            '25%': 'q1',
            '75%': 'q3'
        })

        # Add missing stats that describe() doesn't provide by default
        desc['missing'] = self.df[numeric_cols].isnull().sum()
        
        # Calculate mode for each column (pandas mode can return multiple values, take first)
        desc['mode'] = [self.df[col].mode().iloc[0] if not self.df[col].mode().empty else np.nan for col in numeric_cols]

        # Reorder columns to match original expected format
        cols_to_return = ['count', 'missing', 'mean', 'median', 'mode', 'std', 'min', 'max', 'q1', 'q3']
        return desc[cols_to_return]
    
    def get_categorical_summary(self, columns: Optional[List[str]] = None) -> Dict[str, pd.Series]:
        """
        Get summary for categorical columns.
        
        Args:
            columns: Optional list of columns. If None, analyzes all categorical columns.
            
        Returns:
            Dictionary mapping column names to value counts
        """
        if self.df is None:
            return {}
        
        if columns is None:
            col_types = self._get_column_types()
            cat_cols = [c for c, t in col_types.items() if t == TypeDetector.TYPE_CATEGORICAL]
        else:
            cat_cols = [c for c in columns if c in self.df.columns]
        
        result = {}
        for col in cat_cols:
            result[col] = self.df[col].value_counts()
        
        return result
    
    def get_correlation_matrix(self, method: str = 'pearson') -> pd.DataFrame:
        """
        Get correlation matrix for numeric columns.
        
        Args:
            method: Correlation method ('pearson', 'spearman', 'kendall')
            
        Returns:
            Correlation matrix as DataFrame
        """
        if self.df is None:
            return pd.DataFrame()
        
        col_types = self._get_column_types()
        numeric_cols = [c for c, t in col_types.items() if t == TypeDetector.TYPE_NUMERIC]
        
        if len(numeric_cols) < 2:
            return pd.DataFrame()
        
        return self.df[numeric_cols].corr(method=method)
    
    def get_column_info(self) -> pd.DataFrame:
        """
        Get detailed information about each column.
        
        Returns:
            DataFrame with column information
        """
        if self.df is None:
            return pd.DataFrame()
        
        types = self._get_column_types()
        
        # Batch calculations for efficiency
        null_counts = self.df.isnull().sum()
        non_null_counts = self.df.count()
        unique_counts = self.df.nunique()
        total_rows = len(self.df)

        info_list = []
        for col in self.df.columns:
            null_count = null_counts[col]
            info = {
                'column': col,
                'dtype': str(self.df[col].dtype),
                'semantic_type': types.get(col, 'unknown'),
                'non_null_count': non_null_counts[col],
                'null_count': null_count,
                'null_percentage': (null_count / total_rows * 100) if total_rows > 0 else 0,
                'unique_count': unique_counts[col],
            }
            info_list.append(info)
        
        return pd.DataFrame(info_list)
    
    def get_missing_value_analysis(self) -> pd.DataFrame:
        """
        Analyze missing values in the dataset.
        
        Returns:
            DataFrame with missing value statistics
        """
        if self.df is None:
            return pd.DataFrame()
        
        total_rows = len(self.df)
        null_counts = self.df.isnull().sum()
        
        missing_info = []
        for col in self.df.columns:
            null_count = null_counts[col]
            missing_info.append({
                'column': col,
                'missing_count': null_count,
                'missing_percentage': (null_count / total_rows * 100) if total_rows > 0 else 0,
                'present_count': total_rows - null_count,
            })
        
        return pd.DataFrame(missing_info).sort_values('missing_count', ascending=False)
    
    def get_quick_insights(self) -> List[str]:
        """
        Generate quick insights about the data.
        
        Returns:
            List of insight strings
        """
        if self.df is None:
            return ["No data loaded"]
        
        insights = []
        col_types = self._get_column_types()
        
        # Shape insight
        rows, cols = self.df.shape
        insights.append(f"Dataset contains {rows:,} rows and {cols:,} columns")
        
        # Missing values insight
        null_counts_series = self.df.isnull().sum()
        total_missing = null_counts_series.sum()
        total_cells = self.df.size
        if total_missing > 0:
            pct = (total_missing / total_cells) * 100
            insights.append(f"Missing values: {total_missing:,} ({pct:.1f}% of all data)")
        else:
            insights.append("No missing values in the dataset")
        
        # Column types
        type_counts = {}
        for t in col_types.values():
            type_counts[t] = type_counts.get(t, 0) + 1
        
        type_str = ", ".join([f"{v} {k}" for k, v in type_counts.items()])
        insights.append(f"Column types: {type_str}")
        
        # Numeric column insights
        numeric_cols = [c for c, t in col_types.items() if t == TypeDetector.TYPE_NUMERIC]
        if numeric_cols:
            # Check for potential outliers using IQR
            for col in numeric_cols[:3]:  # Limit to first 3 numeric columns
                # Only check for outliers if we have enough data
                if len(self.df[col].dropna()) < 4:
                    continue
                q1 = self.df[col].quantile(0.25)
                q3 = self.df[col].quantile(0.75)
                iqr = q3 - q1
                outliers = ((self.df[col] < (q1 - 1.5 * iqr)) | (self.df[col] > (q3 + 1.5 * iqr))).sum()
                if outliers > 0:
                    insights.append(f"Column '{col}' has {outliers} potential outliers")
        
        # Correlation insights
        # Pass pre-calculated numeric columns to avoid re-detection
        if len(numeric_cols) < 2:
            corr = pd.DataFrame()
        else:
            corr = self.df[numeric_cols].corr()

        if not corr.empty and len(corr) > 1:
            # Find highly correlated pairs
            high_corr_pairs = []
            for i in range(len(corr.columns)):
                for j in range(i+1, len(corr.columns)):
                    val = corr.iloc[i, j]
                    if abs(val) > 0.7 and not pd.isna(val):
                        high_corr_pairs.append((corr.columns[i], corr.columns[j], val))
            
            if high_corr_pairs:
                pair = high_corr_pairs[0]
                insights.append(f"High correlation ({pair[2]:.2f}) found between '{pair[0]}' and '{pair[1]}'")
        
        return insights
