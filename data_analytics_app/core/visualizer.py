"""
visualizer.py - Data Visualization Module

This module provides chart generation using matplotlib and seaborn,
with support for embedding in wxPython applications.
"""

import matplotlib
matplotlib.use('WXAgg')  # Use wxPython backend

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Optional, Tuple, List, Dict, Any


class Visualizer:
    """
    Creates data visualizations using matplotlib and seaborn.
    
    Supported chart types:
        - Line chart
        - Bar chart
        - Histogram
        - Scatter plot
        - Box plot
        - Pie chart
        - Heatmap (correlation)
    
    All methods return matplotlib Figure objects for embedding in wxPython.
    """
    
    # Chart type constants
    CHART_LINE = 'line'
    CHART_BAR = 'bar'
    CHART_HISTOGRAM = 'histogram'
    CHART_SCATTER = 'scatter'
    CHART_BOX = 'box'
    CHART_PIE = 'pie'
    CHART_HEATMAP = 'heatmap'
    
    # Available chart types for UI
    CHART_TYPES = [
        ('Line Chart', CHART_LINE),
        ('Bar Chart', CHART_BAR),
        ('Histogram', CHART_HISTOGRAM),
        ('Scatter Plot', CHART_SCATTER),
        ('Box Plot', CHART_BOX),
        ('Pie Chart', CHART_PIE),
        ('Heatmap (Correlation)', CHART_HEATMAP),
    ]
    
    def __init__(self):
        """Initialize the Visualizer with default settings."""
        # Set seaborn style
        sns.set_style("whitegrid")
        sns.set_palette("husl")
        
        # Default figure size
        self.figsize = (10, 6)
        self.dpi = 100
    
    def create_figure(self, figsize: Optional[Tuple[int, int]] = None) -> Figure:
        """
        Create a new matplotlib Figure.
        
        Args:
            figsize: Optional (width, height) in inches
            
        Returns:
            matplotlib Figure object
        """
        size = figsize or self.figsize
        return Figure(figsize=size, dpi=self.dpi)
    
    def line_chart(
        self,
        df: pd.DataFrame,
        x_column: str,
        y_column: str,
        title: str = "Line Chart",
        x_label: Optional[str] = None,
        y_label: Optional[str] = None,
        figsize: Optional[Tuple[int, int]] = None
    ) -> Figure:
        """
        Create a line chart.
        
        Args:
            df: DataFrame with data
            x_column: Column for x-axis
            y_column: Column for y-axis
            title: Chart title
            x_label: X-axis label (defaults to column name)
            y_label: Y-axis label (defaults to column name)
            figsize: Optional figure size
            
        Returns:
            matplotlib Figure
        """
        fig = self.create_figure(figsize)
        ax = fig.add_subplot(111)
        
        # Sort by x if it's numeric or datetime
        data = df[[x_column, y_column]].dropna().copy()
        if pd.api.types.is_numeric_dtype(data[x_column]) or pd.api.types.is_datetime64_any_dtype(data[x_column]):
            data = data.sort_values(x_column)
        
        ax.plot(data[x_column], data[y_column], marker='o', markersize=3, linewidth=1.5)
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel(x_label or x_column, fontsize=11)
        ax.set_ylabel(y_label or y_column, fontsize=11)
        
        # Rotate x labels if needed
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        fig.tight_layout()
        return fig
    
    def bar_chart(
        self,
        df: pd.DataFrame,
        x_column: str,
        y_column: Optional[str] = None,
        title: str = "Bar Chart",
        x_label: Optional[str] = None,
        y_label: Optional[str] = None,
        figsize: Optional[Tuple[int, int]] = None,
        top_n: int = 20
    ) -> Figure:
        """
        Create a bar chart.
        
        Args:
            df: DataFrame with data
            x_column: Column for x-axis (categorical)
            y_column: Column for y-axis (if None, shows counts)
            title: Chart title
            x_label: X-axis label
            y_label: Y-axis label
            figsize: Optional figure size
            top_n: Limit to top N categories
            
        Returns:
            matplotlib Figure
        """
        fig = self.create_figure(figsize)
        ax = fig.add_subplot(111)
        
        if y_column is None or y_column == "(Count)":
            # Show value counts
            value_counts = df[x_column].value_counts().head(top_n)
            ax.bar(range(len(value_counts)), value_counts.values, color=sns.color_palette("husl", len(value_counts)))
            ax.set_xticks(range(len(value_counts)))
            ax.set_xticklabels(value_counts.index, rotation=45, ha='right')
            y_label = y_label or "Count"
        else:
            # Group by x and aggregate y
            grouped = df.groupby(x_column)[y_column].mean().head(top_n)
            ax.bar(range(len(grouped)), grouped.values, color=sns.color_palette("husl", len(grouped)))
            ax.set_xticks(range(len(grouped)))
            ax.set_xticklabels(grouped.index, rotation=45, ha='right')
            y_label = y_label or f"Mean {y_column}"
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel(x_label or x_column, fontsize=11)
        ax.set_ylabel(y_label, fontsize=11)
        
        fig.tight_layout()
        return fig
    
    def histogram(
        self,
        df: pd.DataFrame,
        column: str,
        bins: int = 30,
        title: str = "Histogram",
        x_label: Optional[str] = None,
        y_label: str = "Frequency",
        figsize: Optional[Tuple[int, int]] = None
    ) -> Figure:
        """
        Create a histogram.
        
        Args:
            df: DataFrame with data
            column: Column to plot
            bins: Number of bins
            title: Chart title
            x_label: X-axis label
            y_label: Y-axis label
            figsize: Optional figure size
            
        Returns:
            matplotlib Figure
        """
        fig = self.create_figure(figsize)
        ax = fig.add_subplot(111)
        
        data = df[column].dropna()
        
        ax.hist(data, bins=bins, edgecolor='white', alpha=0.7)
        
        # Add a kernel density estimate line
        if len(data) > 1:
            try:
                from scipy import stats
                kde_x = np.linspace(data.min(), data.max(), 100)
                kde = stats.gaussian_kde(data)
                ax2 = ax.twinx()
                ax2.plot(kde_x, kde(kde_x), 'r-', linewidth=2, label='KDE')
                ax2.set_ylabel('Density', fontsize=11)
                ax2.legend(loc='upper right')
            except:
                pass
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel(x_label or column, fontsize=11)
        ax.set_ylabel(y_label, fontsize=11)
        
        fig.tight_layout()
        return fig
    
    def scatter_plot(
        self,
        df: pd.DataFrame,
        x_column: str,
        y_column: str,
        hue_column: Optional[str] = None,
        title: str = "Scatter Plot",
        x_label: Optional[str] = None,
        y_label: Optional[str] = None,
        figsize: Optional[Tuple[int, int]] = None
    ) -> Figure:
        """
        Create a scatter plot.
        
        Args:
            df: DataFrame with data
            x_column: Column for x-axis
            y_column: Column for y-axis
            hue_column: Optional column for color coding
            title: Chart title
            x_label: X-axis label
            y_label: Y-axis label
            figsize: Optional figure size
            
        Returns:
            matplotlib Figure
        """
        fig = self.create_figure(figsize)
        ax = fig.add_subplot(111)
        
        data = df[[x_column, y_column]].dropna()
        
        if hue_column and hue_column in df.columns:
            # Add hue data
            hue_data = df.loc[data.index, hue_column]
            scatter = ax.scatter(data[x_column], data[y_column], c=pd.Categorical(hue_data).codes, 
                                alpha=0.6, cmap='viridis')
            # Add legend
            unique_hues = hue_data.unique()[:10]  # Limit legend entries
            handles = [plt.Line2D([0], [0], marker='o', color='w', 
                                  markerfacecolor=plt.cm.viridis(i/len(unique_hues)), 
                                  markersize=8, label=str(h)) 
                      for i, h in enumerate(unique_hues)]
            ax.legend(handles=handles, title=hue_column, loc='best')
        else:
            ax.scatter(data[x_column], data[y_column], alpha=0.6)
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel(x_label or x_column, fontsize=11)
        ax.set_ylabel(y_label or y_column, fontsize=11)
        
        fig.tight_layout()
        return fig
    
    def box_plot(
        self,
        df: pd.DataFrame,
        columns: List[str],
        title: str = "Box Plot",
        y_label: str = "Value",
        figsize: Optional[Tuple[int, int]] = None
    ) -> Figure:
        """
        Create a box plot for one or more columns.
        
        Args:
            df: DataFrame with data
            columns: List of columns to plot
            title: Chart title
            y_label: Y-axis label
            figsize: Optional figure size
            
        Returns:
            matplotlib Figure
        """
        fig = self.create_figure(figsize)
        ax = fig.add_subplot(111)
        
        # Filter to numeric columns
        numeric_cols = [c for c in columns if c in df.columns and pd.api.types.is_numeric_dtype(df[c])]
        
        if not numeric_cols:
            ax.text(0.5, 0.5, "No numeric columns selected", ha='center', va='center', fontsize=12)
            return fig
        
        data = df[numeric_cols].dropna()
        
        bp = ax.boxplot(data.values, patch_artist=True, labels=numeric_cols)
        
        # Color the boxes
        colors = sns.color_palette("husl", len(numeric_cols))
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_ylabel(y_label, fontsize=11)
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        fig.tight_layout()
        return fig
    
    def pie_chart(
        self,
        df: pd.DataFrame,
        column: str,
        title: str = "Pie Chart",
        figsize: Optional[Tuple[int, int]] = None,
        top_n: int = 10
    ) -> Figure:
        """
        Create a pie chart from categorical data.
        
        Args:
            df: DataFrame with data
            column: Column with categorical data
            title: Chart title
            figsize: Optional figure size
            top_n: Show top N categories (others grouped as "Other")
            
        Returns:
            matplotlib Figure
        """
        fig = self.create_figure(figsize)
        ax = fig.add_subplot(111)
        
        value_counts = df[column].value_counts()
        
        # Group smaller categories into "Other"
        if len(value_counts) > top_n:
            top_values = value_counts.head(top_n - 1)
            other_sum = value_counts.iloc[top_n - 1:].sum()
            value_counts = pd.concat([top_values, pd.Series({'Other': other_sum})])
        
        colors = sns.color_palette("husl", len(value_counts))
        
        wedges, texts, autotexts = ax.pie(
            value_counts.values,
            labels=value_counts.index,
            autopct='%1.1f%%',
            colors=colors,
            startangle=90,
            pctdistance=0.85
        )
        
        # Style the text
        for text in texts:
            text.set_fontsize(9)
        for autotext in autotexts:
            autotext.set_fontsize(8)
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        
        fig.tight_layout()
        return fig
    
    def heatmap(
        self,
        df: pd.DataFrame,
        title: str = "Correlation Heatmap",
        figsize: Optional[Tuple[int, int]] = None,
        method: str = 'pearson'
    ) -> Figure:
        """
        Create a correlation heatmap.
        
        Args:
            df: DataFrame with data
            title: Chart title
            figsize: Optional figure size
            method: Correlation method ('pearson', 'spearman', 'kendall')
            
        Returns:
            matplotlib Figure
        """
        fig = self.create_figure(figsize or (10, 8))
        ax = fig.add_subplot(111)
        
        # Get numeric columns only
        numeric_df = df.select_dtypes(include=[np.number])
        
        if numeric_df.empty or len(numeric_df.columns) < 2:
            ax.text(0.5, 0.5, "Need at least 2 numeric columns for correlation", 
                   ha='center', va='center', fontsize=12)
            return fig
        
        # Calculate correlation matrix
        corr = numeric_df.corr(method=method)
        
        # Create heatmap
        sns.heatmap(
            corr,
            annot=True,
            fmt='.2f',
            cmap='RdBu_r',
            center=0,
            square=True,
            linewidths=0.5,
            ax=ax,
            vmin=-1,
            vmax=1,
            annot_kws={'size': 8}
        )
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        plt.setp(ax.get_yticklabels(), rotation=0)
        
        fig.tight_layout()
        return fig
    
    def create_chart(
        self,
        df: pd.DataFrame,
        chart_type: str,
        x_column: Optional[str] = None,
        y_column: Optional[str] = None,
        title: Optional[str] = None,
        **kwargs
    ) -> Figure:
        """
        Create a chart based on the specified type.
        
        Args:
            df: DataFrame with data
            chart_type: Type of chart to create
            x_column: Column for x-axis (where applicable)
            y_column: Column for y-axis (where applicable)
            title: Chart title
            **kwargs: Additional arguments passed to the specific chart method
            
        Returns:
            matplotlib Figure
        """
        if df is None or df.empty:
            fig = self.create_figure()
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, "No data available", ha='center', va='center', fontsize=14)
            return fig
        
        # Generate default title if not provided
        if title is None:
            title = f"{chart_type.replace('_', ' ').title()}"
        
        try:
            if chart_type == self.CHART_LINE:
                return self.line_chart(df, x_column, y_column, title, **kwargs)
            elif chart_type == self.CHART_BAR:
                return self.bar_chart(df, x_column, y_column, title, **kwargs)
            elif chart_type == self.CHART_HISTOGRAM:
                return self.histogram(df, x_column, title=title, **kwargs)
            elif chart_type == self.CHART_SCATTER:
                return self.scatter_plot(df, x_column, y_column, title=title, **kwargs)
            elif chart_type == self.CHART_BOX:
                columns = [x_column] if y_column is None else [x_column, y_column]
                return self.box_plot(df, columns, title, **kwargs)
            elif chart_type == self.CHART_PIE:
                return self.pie_chart(df, x_column, title, **kwargs)
            elif chart_type == self.CHART_HEATMAP:
                return self.heatmap(df, title, **kwargs)
            else:
                fig = self.create_figure()
                ax = fig.add_subplot(111)
                ax.text(0.5, 0.5, f"Unknown chart type: {chart_type}", ha='center', va='center')
                return fig
        except Exception as e:
            fig = self.create_figure()
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, f"Error creating chart:\n{str(e)}", ha='center', va='center', fontsize=10)
            return fig
    
    @staticmethod
    def save_figure(fig: Figure, file_path: str, dpi: int = 150) -> bool:
        """
        Save a figure to a file.
        
        Args:
            fig: matplotlib Figure to save
            file_path: Path to save the image
            dpi: Resolution in dots per inch
            
        Returns:
            True if successful, False otherwise
        """
        try:
            fig.savefig(file_path, dpi=dpi, bbox_inches='tight', facecolor='white')
            return True
        except Exception as e:
            print(f"Error saving figure: {e}")
            return False
