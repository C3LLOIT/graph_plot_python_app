"""
panels.py - wxPython Panel Components

This module provides the main panel components for the Data Analytics application:
- DataPreviewPanel: Displays dataset preview in a grid
- StatisticsPanel: Shows descriptive statistics and column info
- VisualizationPanel: Handles chart type selection and rendering
"""

import wx
import wx.grid as gridlib
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as NavigationToolbar
from matplotlib.figure import Figure
import pandas as pd
import numpy as np
from typing import Optional, Callable

# Import core modules
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.visualizer import Visualizer
from core.data_analyzer import DataAnalyzer
from utils.helpers import TypeDetector, Formatter


class DataPreviewPanel(wx.Panel):
    """
    Panel for displaying a preview of the loaded dataset.
    
    Features:
        - Grid view of data (first N rows)
        - Dataset summary information
        - Column type indicators
    """
    
    def __init__(self, parent: wx.Window):
        """
        Initialize the DataPreviewPanel.
        
        Args:
            parent: Parent window
        """
        super().__init__(parent)
        
        self.df: Optional[pd.DataFrame] = None
        self.max_preview_rows = 100
        
        self._create_widgets()
        self._create_layout()
    
    def _create_widgets(self):
        """Create the panel widgets."""
        # Summary text at the top
        self.summary_label = wx.StaticText(self, label="No data loaded")
        self.summary_label.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        
        # Data grid
        self.grid = gridlib.Grid(self)
        self.grid.CreateGrid(0, 0)
        self.grid.EnableEditing(False)
        self.grid.SetDefaultCellAlignment(wx.ALIGN_LEFT, wx.ALIGN_CENTER)
        
        # Column info panel
        self.column_info_label = wx.StaticText(self, label="")
    
    def _create_layout(self):
        """Create the panel layout."""
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Summary section
        main_sizer.Add(self.summary_label, 0, wx.ALL | wx.EXPAND, 10)
        
        # Grid section
        main_sizer.Add(self.grid, 1, wx.ALL | wx.EXPAND, 5)
        
        # Column info section
        main_sizer.Add(self.column_info_label, 0, wx.ALL | wx.EXPAND, 10)
        
        self.SetSizer(main_sizer)
    
    def set_data(self, df: pd.DataFrame, file_info: dict = None):
        """
        Set the data to display.
        
        Args:
            df: pandas DataFrame to display
            file_info: Optional dictionary with file information
        """
        self.df = df
        
        if df is None or df.empty:
            self.summary_label.SetLabel("No data loaded")
            self._clear_grid()
            return
        
        # Update summary
        summary = Formatter.generate_summary_text(df)
        if file_info and 'file_path' in file_info:
            file_name = os.path.basename(file_info['file_path'])
            summary = f"File: {file_name}\n{summary}"
        self.summary_label.SetLabel(summary)
        
        # Update grid
        self._populate_grid(df)
        
        # Update column info
        types = TypeDetector.detect_all_column_types(df)
        type_info = ", ".join([f"{col}: {t}" for col, t in list(types.items())[:5]])
        if len(types) > 5:
            type_info += f"... and {len(types) - 5} more"
        self.column_info_label.SetLabel(f"Column Types: {type_info}")
        
        self.Layout()
    
    def _populate_grid(self, df: pd.DataFrame):
        """Populate the grid with DataFrame data."""
        # Clear existing grid
        self._clear_grid()
        
        # Get preview rows
        preview_df = df.head(self.max_preview_rows)
        n_rows, n_cols = preview_df.shape
        
        if n_rows == 0 or n_cols == 0:
            return
        
        # Disable grid updates for batch population
        self.grid.BeginBatch()
        
        try:
            # Resize grid
            self.grid.AppendRows(n_rows)
            self.grid.AppendCols(n_cols)

            # Set column labels
            for col_idx, col_name in enumerate(preview_df.columns):
                self.grid.SetColLabelValue(col_idx, str(col_name))

            # Populate cells
            for row_idx in range(n_rows):
                for col_idx in range(n_cols):
                    value = preview_df.iloc[row_idx, col_idx]
                    # Format value for display
                    if pd.isna(value):
                        display_value = ""
                    else:
                        display_value = Formatter.truncate_string(str(value), 50)
                    self.grid.SetCellValue(row_idx, col_idx, display_value)

            # Auto-size columns
            self.grid.AutoSizeColumns()
        finally:
            self.grid.EndBatch()
    
    def _clear_grid(self):
        """Clear all grid contents."""
        if self.grid.GetNumberRows() > 0:
            self.grid.DeleteRows(0, self.grid.GetNumberRows())
        if self.grid.GetNumberCols() > 0:
            self.grid.DeleteCols(0, self.grid.GetNumberCols())
    
    def clear(self):
        """Clear all data from the panel."""
        self.df = None
        self.summary_label.SetLabel("No data loaded")
        self._clear_grid()
        self.column_info_label.SetLabel("")


class StatisticsPanel(wx.Panel):
    """
    Panel for displaying statistical analysis of the data.
    
    Features:
        - Descriptive statistics table
        - Correlation matrix display
        - Quick insights
    """
    
    def __init__(self, parent: wx.Window):
        """
        Initialize the StatisticsPanel.
        
        Args:
            parent: Parent window
        """
        super().__init__(parent)
        
        self.df: Optional[pd.DataFrame] = None
        self.analyzer = DataAnalyzer()
        
        self._create_widgets()
        self._create_layout()
    
    def _create_widgets(self):
        """Create the panel widgets."""
        # Notebook for different statistics views
        self.notebook = wx.Notebook(self)
        
        # Descriptive Statistics tab
        self.stats_panel = wx.Panel(self.notebook)
        self.stats_grid = gridlib.Grid(self.stats_panel)
        self.stats_grid.CreateGrid(0, 0)
        self.stats_grid.EnableEditing(False)
        
        stats_sizer = wx.BoxSizer(wx.VERTICAL)
        stats_sizer.Add(self.stats_grid, 1, wx.EXPAND | wx.ALL, 5)
        self.stats_panel.SetSizer(stats_sizer)
        
        # Column Info tab
        self.column_panel = wx.Panel(self.notebook)
        self.column_grid = gridlib.Grid(self.column_panel)
        self.column_grid.CreateGrid(0, 0)
        self.column_grid.EnableEditing(False)
        
        column_sizer = wx.BoxSizer(wx.VERTICAL)
        column_sizer.Add(self.column_grid, 1, wx.EXPAND | wx.ALL, 5)
        self.column_panel.SetSizer(column_sizer)
        
        # Insights tab
        self.insights_panel = wx.Panel(self.notebook)
        self.insights_text = wx.TextCtrl(
            self.insights_panel,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2
        )
        self.insights_text.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        
        insights_sizer = wx.BoxSizer(wx.VERTICAL)
        insights_sizer.Add(self.insights_text, 1, wx.EXPAND | wx.ALL, 5)
        self.insights_panel.SetSizer(insights_sizer)
        
        # Add tabs to notebook
        self.notebook.AddPage(self.stats_panel, "Descriptive Statistics")
        self.notebook.AddPage(self.column_panel, "Column Information")
        self.notebook.AddPage(self.insights_panel, "Insights")
    
    def _create_layout(self):
        """Create the panel layout."""
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(main_sizer)
    
    def set_data(self, df: pd.DataFrame):
        """
        Set the data to analyze.
        
        Args:
            df: pandas DataFrame to analyze
        """
        self.df = df
        self.analyzer.set_dataframe(df)
        
        if df is None or df.empty:
            self.clear()
            return
        
        self._update_stats_grid()
        self._update_column_grid()
        self._update_insights()
    
    def _update_stats_grid(self):
        """Update the descriptive statistics grid."""
        self._clear_grid(self.stats_grid)
        
        if self.df is None:
            return
        
        stats_df = self.analyzer.get_descriptive_stats()
        
        if stats_df.empty:
            return
        
        self.stats_grid.BeginBatch()
        try:
            # Populate grid
            n_rows, n_cols = stats_df.shape
            self.stats_grid.AppendRows(n_rows)
            self.stats_grid.AppendCols(n_cols + 1)  # +1 for index column

            # Set column labels
            self.stats_grid.SetColLabelValue(0, "Column")
            for col_idx, col_name in enumerate(stats_df.columns):
                self.stats_grid.SetColLabelValue(col_idx + 1, str(col_name))

            # Populate data
            for row_idx, (index, row) in enumerate(stats_df.iterrows()):
                self.stats_grid.SetCellValue(row_idx, 0, str(index))
                for col_idx, value in enumerate(row):
                    formatted = Formatter.format_number(value) if not pd.isna(value) else "N/A"
                    self.stats_grid.SetCellValue(row_idx, col_idx + 1, formatted)

            self.stats_grid.AutoSizeColumns()
        finally:
            self.stats_grid.EndBatch()
    
    def _update_column_grid(self):
        """Update the column information grid."""
        self._clear_grid(self.column_grid)
        
        if self.df is None:
            return
        
        column_info = self.analyzer.get_column_info()
        
        if column_info.empty:
            return
        
        self.column_grid.BeginBatch()
        try:
            # Populate grid
            n_rows, n_cols = column_info.shape
            self.column_grid.AppendRows(n_rows)
            self.column_grid.AppendCols(n_cols)

            # Set column labels
            for col_idx, col_name in enumerate(column_info.columns):
                self.column_grid.SetColLabelValue(col_idx, str(col_name))

            # Populate data
            for row_idx in range(n_rows):
                for col_idx in range(n_cols):
                    value = column_info.iloc[row_idx, col_idx]
                    if isinstance(value, float):
                        formatted = Formatter.format_number(value)
                    else:
                        formatted = str(value)
                    self.column_grid.SetCellValue(row_idx, col_idx, formatted)

            self.column_grid.AutoSizeColumns()
        finally:
            self.column_grid.EndBatch()
    
    def _update_insights(self):
        """Update the insights text."""
        if self.df is None:
            self.insights_text.SetValue("No data loaded")
            return
        
        insights = self.analyzer.get_quick_insights()
        
        # Format insights with bullet points
        formatted_insights = "\n".join([f"• {insight}" for insight in insights])
        
        self.insights_text.SetValue(f"Data Insights:\n\n{formatted_insights}")
    
    def _clear_grid(self, grid: gridlib.Grid):
        """Clear a grid."""
        if grid.GetNumberRows() > 0:
            grid.DeleteRows(0, grid.GetNumberRows())
        if grid.GetNumberCols() > 0:
            grid.DeleteCols(0, grid.GetNumberCols())
    
    def clear(self):
        """Clear all statistics data."""
        self.df = None
        self._clear_grid(self.stats_grid)
        self._clear_grid(self.column_grid)
        self.insights_text.SetValue("No data loaded")


class VisualizationPanel(wx.Panel):
    """
    Panel for creating and displaying data visualizations.
    
    Features:
        - Chart type selection
        - Column selection for axes
        - Embedded matplotlib canvas
        - Save plot functionality
    """
    
    def __init__(self, parent: wx.Window):
        """
        Initialize the VisualizationPanel.
        
        Args:
            parent: Parent window
        """
        super().__init__(parent)
        
        self.df: Optional[pd.DataFrame] = None
        self.visualizer = Visualizer()
        self.current_figure: Optional[Figure] = None
        
        self._create_widgets()
        self._create_layout()
        self._bind_events()
    
    def _create_widgets(self):
        """Create the panel widgets."""
        # Controls panel
        self.controls_panel = wx.Panel(self)
        
        # Chart type selection
        self.chart_type_label = wx.StaticText(self.controls_panel, label="Chart Type:")
        chart_types = [name for name, _ in Visualizer.CHART_TYPES]
        self.chart_type_combo = wx.ComboBox(
            self.controls_panel,
            choices=chart_types,
            style=wx.CB_READONLY
        )
        self.chart_type_combo.SetSelection(0)
        
        # X-axis column selection
        self.x_column_label = wx.StaticText(self.controls_panel, label="X-Axis Column:")
        self.x_column_combo = wx.ComboBox(self.controls_panel, style=wx.CB_READONLY)
        
        # Y-axis column selection
        self.y_column_label = wx.StaticText(self.controls_panel, label="Y-Axis Column:")
        self.y_column_combo = wx.ComboBox(self.controls_panel, style=wx.CB_READONLY)
        
        # Generate button
        self.generate_btn = wx.Button(self.controls_panel, label="Generate Plot")
        self.generate_btn.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        
        # Save button
        self.save_btn = wx.Button(self.controls_panel, label="Save Plot")
        self.save_btn.Enable(False)
        
        # Clear button
        self.clear_btn = wx.Button(self.controls_panel, label="Clear")
        
        # Matplotlib canvas
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvas(self, -1, self.figure)
        
        # Navigation toolbar
        self.toolbar = NavigationToolbar(self.canvas)
        self.toolbar.Realize()
        
        # Status label
        self.status_label = wx.StaticText(self, label="Select a chart type and columns, then click Generate Plot")
    
    def _create_layout(self):
        """Create the panel layout."""
        # Controls layout
        controls_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Chart type
        controls_sizer.Add(self.chart_type_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        controls_sizer.Add(self.chart_type_combo, 0, wx.RIGHT, 15)
        
        # X-axis
        controls_sizer.Add(self.x_column_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        controls_sizer.Add(self.x_column_combo, 1, wx.RIGHT, 15)
        
        # Y-axis
        controls_sizer.Add(self.y_column_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        controls_sizer.Add(self.y_column_combo, 1, wx.RIGHT, 15)
        
        # Buttons
        controls_sizer.Add(self.generate_btn, 0, wx.RIGHT, 5)
        controls_sizer.Add(self.save_btn, 0, wx.RIGHT, 5)
        controls_sizer.Add(self.clear_btn, 0)
        
        self.controls_panel.SetSizer(controls_sizer)
        
        # Main layout
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.controls_panel, 0, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(self.toolbar, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        main_sizer.Add(self.canvas, 1, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(self.status_label, 0, wx.ALL, 10)
        
        self.SetSizer(main_sizer)
    
    def _bind_events(self):
        """Bind event handlers."""
        self.generate_btn.Bind(wx.EVT_BUTTON, self._on_generate)
        self.save_btn.Bind(wx.EVT_BUTTON, self._on_save)
        self.clear_btn.Bind(wx.EVT_BUTTON, self._on_clear)
        self.chart_type_combo.Bind(wx.EVT_COMBOBOX, self._on_chart_type_change)
    
    def set_data(self, df: pd.DataFrame):
        """
        Set the data for visualization.
        
        Args:
            df: pandas DataFrame
        """
        self.df = df
        
        if df is None or df.empty:
            self.x_column_combo.Clear()
            self.y_column_combo.Clear()
            self.status_label.SetLabel("No data loaded")
            return
        
        # Populate column dropdowns
        columns = list(df.columns)
        
        self.x_column_combo.Clear()
        self.y_column_combo.Clear()
        
        self.x_column_combo.AppendItems(columns)
        self.y_column_combo.AppendItems(["(None)"] + columns)
        
        if columns:
            self.x_column_combo.SetSelection(0)
            # Default Y to second column if available (index 1 in the (None) + columns list = index 2)
            if len(columns) > 1:
                self.y_column_combo.SetSelection(2)  # Second data column
            else:
                self.y_column_combo.SetSelection(0)  # (None)
        
        self._on_chart_type_change(None)
        self.status_label.SetLabel("Data loaded. Select chart type and columns, then click Generate Plot.")
    
    def _on_chart_type_change(self, event):
        """Handle chart type selection change."""
        chart_idx = self.chart_type_combo.GetSelection()
        if chart_idx < 0:
            return
        
        _, chart_type = Visualizer.CHART_TYPES[chart_idx]
        
        # Update Y-axis visibility based on chart type
        needs_y_axis = chart_type in [
            Visualizer.CHART_LINE,
            Visualizer.CHART_SCATTER,
            Visualizer.CHART_BAR
        ]
        
        self.y_column_label.Enable(needs_y_axis)
        self.y_column_combo.Enable(needs_y_axis)
        
        # Update labels based on chart type
        if chart_type == Visualizer.CHART_HISTOGRAM:
            self.x_column_label.SetLabel("Column:")
        elif chart_type == Visualizer.CHART_PIE:
            self.x_column_label.SetLabel("Category Column:")
        elif chart_type == Visualizer.CHART_HEATMAP:
            self.x_column_label.SetLabel("(Uses all numeric columns)")
            self.x_column_combo.Enable(False)
            self.y_column_combo.Enable(False)
        elif chart_type == Visualizer.CHART_BOX:
            self.x_column_label.SetLabel("Column(s):")
            self.y_column_label.SetLabel("Additional Column:")
        else:
            self.x_column_label.SetLabel("X-Axis Column:")
            self.x_column_combo.Enable(True)

    def _on_generate(self, event):
        """Handle Generate Plot button click."""
        if self.df is None or self.df.empty:
            wx.MessageBox("No data loaded. Please load a file first.", "Error", wx.OK | wx.ICON_ERROR)
            return
        
        chart_idx = self.chart_type_combo.GetSelection()
        if chart_idx < 0:
            wx.MessageBox("Please select a chart type.", "Error", wx.OK | wx.ICON_ERROR)
            return
        
        _, chart_type = Visualizer.CHART_TYPES[chart_idx]
        
        # Get selected columns
        x_col = self.x_column_combo.GetValue() if self.x_column_combo.IsEnabled() else None
        y_col_raw = self.y_column_combo.GetValue()
        y_col = None if y_col_raw in ["(None)", ""] else y_col_raw
        
        # Validate column selection
        if chart_type != Visualizer.CHART_HEATMAP and not x_col:
            wx.MessageBox("Please select a column.", "Error", wx.OK | wx.ICON_ERROR)
            return
        
        # Validate Y column for charts that require it
        needs_y_col = chart_type in [Visualizer.CHART_LINE, Visualizer.CHART_SCATTER]
        if needs_y_col and not y_col:
            wx.MessageBox("Please select a Y-axis column for this chart type.", "Error", wx.OK | wx.ICON_ERROR)
            return
        
        try:
            wx.BeginBusyCursor()
            
            chart_name = Visualizer.CHART_TYPES[chart_idx][0]
            title = f"{chart_name}"
            if x_col:
                title += f" - {x_col}"
                if y_col:
                    title += f" vs {y_col}"
            
            # Use the visualizer to create the figure (it has sampling logic)
            self.current_figure = self.visualizer.create_chart(self.df, chart_type, x_col, y_col, title)
            
            # Update the canvas with the new figure
            self.canvas.figure = self.current_figure
            self.current_figure.set_canvas(self.canvas)
            
            self.canvas.draw()
            
            self.save_btn.Enable(True)
            self.status_label.SetLabel(f"Generated: {chart_name}")
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            wx.MessageBox(f"Error generating chart: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)
            self.status_label.SetLabel(f"Error: {str(e)}")
        finally:
            wx.EndBusyCursor()
    
    def _on_save(self, event):
        """Handle Save Plot button click."""
        if self.current_figure is None:
            wx.MessageBox("No plot to save. Generate a plot first.", "Error", wx.OK | wx.ICON_ERROR)
            return
        
        with wx.FileDialog(
            self,
            "Save Plot As",
            wildcard="PNG files (*.png)|*.png|JPEG files (*.jpg)|*.jpg|PDF files (*.pdf)|*.pdf",
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
        ) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                file_path = dlg.GetPath()
                
                try:
                    Visualizer.save_figure(self.current_figure, file_path)
                    self.status_label.SetLabel(f"Plot saved to: {file_path}")
                    wx.MessageBox(f"Plot saved successfully to:\n{file_path}", "Success", wx.OK | wx.ICON_INFORMATION)
                except Exception as e:
                    wx.MessageBox(f"Error saving plot: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)
    
    def _on_clear(self, event):
        """Handle Clear button click."""
        self.figure.clear()
        self.canvas.draw()
        self.current_figure = None
        self.save_btn.Enable(False)
        self.status_label.SetLabel("Plot cleared")
    
    def clear(self):
        """Clear the visualization panel."""
        self.df = None
        self.x_column_combo.Clear()
        self.y_column_combo.Clear()
        self.figure.clear()
        self.canvas.draw()
        self.current_figure = None
        self.save_btn.Enable(False)
        self.status_label.SetLabel("No data loaded")
