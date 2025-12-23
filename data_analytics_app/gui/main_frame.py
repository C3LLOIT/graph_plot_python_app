"""
main_frame.py - Main Application Window

This module provides the main wxPython Frame for the Data Analytics application,
including menu bar, notebook tabs, and event handling.
"""

import wx
import wx.adv
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.panels import DataPreviewPanel, StatisticsPanel, VisualizationPanel
from core.data_loader import DataLoader
from core.data_analyzer import DataAnalyzer


class MainFrame(wx.Frame):
    """
    Main application window for the Data Analytics Tool.
    
    Features:
        - Menu bar with File menu (Open, Exit)
        - Notebook with tabs: Data Preview, Statistics, Visualization
        - Status bar for messages
        - File dialog for opening CSV/JSON files
    """
    
    # Application constants
    APP_TITLE = "Data Analytics Tool"
    APP_SIZE = (1200, 800)
    
    def __init__(self, parent=None):
        """
        Initialize the MainFrame.
        
        Args:
            parent: Parent window (usually None for main frame)
        """
        super().__init__(
            parent,
            title=self.APP_TITLE,
            size=self.APP_SIZE,
            style=wx.DEFAULT_FRAME_STYLE
        )
        
        # Initialize data components
        self.data_loader = DataLoader()
        self.analyzer = DataAnalyzer()
        
        # Create UI components
        self._create_menu_bar()
        self._create_toolbar()
        self._create_main_panel()
        self._create_status_bar()
        
        # Bind events
        self._bind_events()
        
        # Center on screen
        self.Centre()
        
        # Set minimum size
        self.SetMinSize((800, 600))
        
        # Update status
        self._update_status("Ready. Click 'Open File' to load a CSV or JSON file.")
    
    def _create_menu_bar(self):
        """Create the application menu bar."""
        menu_bar = wx.MenuBar()
        
        # File menu
        file_menu = wx.Menu()
        
        open_item = file_menu.Append(wx.ID_OPEN, "&Open File\tCtrl+O", "Open a CSV or JSON file")
        file_menu.AppendSeparator()
        
        close_item = file_menu.Append(wx.ID_CLOSE, "&Close File", "Close current file")
        file_menu.AppendSeparator()
        
        exit_item = file_menu.Append(wx.ID_EXIT, "E&xit\tAlt+F4", "Exit the application")
        
        menu_bar.Append(file_menu, "&File")
        
        # View menu
        view_menu = wx.Menu()
        
        self.view_preview = view_menu.Append(wx.ID_ANY, "Show &Data Preview\tCtrl+1", "Switch to Data Preview tab")
        self.view_stats = view_menu.Append(wx.ID_ANY, "Show &Statistics\tCtrl+2", "Switch to Statistics tab")
        self.view_viz = view_menu.Append(wx.ID_ANY, "Show &Visualization\tCtrl+3", "Switch to Visualization tab")
        
        menu_bar.Append(view_menu, "&View")
        
        # Help menu
        help_menu = wx.Menu()
        
        about_item = help_menu.Append(wx.ID_ABOUT, "&About", "About this application")
        
        menu_bar.Append(help_menu, "&Help")
        
        self.SetMenuBar(menu_bar)
        
        # Bind menu events
        self.Bind(wx.EVT_MENU, self._on_open_file, open_item)
        self.Bind(wx.EVT_MENU, self._on_close_file, close_item)
        self.Bind(wx.EVT_MENU, self._on_exit, exit_item)
        self.Bind(wx.EVT_MENU, lambda e: self.notebook.SetSelection(0), self.view_preview)
        self.Bind(wx.EVT_MENU, lambda e: self.notebook.SetSelection(1), self.view_stats)
        self.Bind(wx.EVT_MENU, lambda e: self.notebook.SetSelection(2), self.view_viz)
        self.Bind(wx.EVT_MENU, self._on_about, about_item)
    
    def _create_toolbar(self):
        """Create the application toolbar."""
        toolbar = self.CreateToolBar(wx.TB_HORIZONTAL | wx.TB_TEXT | wx.TB_NOICONS)
        
        # Open file button
        self.open_btn = wx.Button(toolbar, label="📂 Open File")
        toolbar.AddControl(self.open_btn)
        
        toolbar.AddSeparator()
        
        # File info label
        self.file_info_label = wx.StaticText(toolbar, label="No file loaded")
        self.file_info_label.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL))
        toolbar.AddControl(self.file_info_label)
        
        toolbar.AddStretchableSpace()
        
        # Close file button
        self.close_btn = wx.Button(toolbar, label="Close File")
        self.close_btn.Enable(False)
        toolbar.AddControl(self.close_btn)
        
        toolbar.Realize()
        
        # Bind toolbar events
        self.open_btn.Bind(wx.EVT_BUTTON, self._on_open_file)
        self.close_btn.Bind(wx.EVT_BUTTON, self._on_close_file)
    
    def _create_main_panel(self):
        """Create the main panel with notebook."""
        # Main panel
        self.main_panel = wx.Panel(self)
        
        # Notebook for tabs
        self.notebook = wx.Notebook(self.main_panel)
        
        # Create tab panels
        self.preview_panel = DataPreviewPanel(self.notebook)
        self.stats_panel = StatisticsPanel(self.notebook)
        self.viz_panel = VisualizationPanel(self.notebook)
        
        # Add tabs
        self.notebook.AddPage(self.preview_panel, "📊 Data Preview")
        self.notebook.AddPage(self.stats_panel, "📈 Statistics")
        self.notebook.AddPage(self.viz_panel, "📉 Visualization")
        
        # Layout
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 5)
        self.main_panel.SetSizer(main_sizer)
    
    def _create_status_bar(self):
        """Create the status bar."""
        self.status_bar = self.CreateStatusBar(2)
        self.status_bar.SetStatusWidths([-2, -1])
    
    def _bind_events(self):
        """Bind additional event handlers."""
        self.Bind(wx.EVT_CLOSE, self._on_close)
    
    def _on_open_file(self, event):
        """Handle Open File action."""
        wildcard = "Data files (*.csv;*.json)|*.csv;*.json|CSV files (*.csv)|*.csv|JSON files (*.json)|*.json|All files (*.*)|*.*"
        
        with wx.FileDialog(
            self,
            "Open Data File",
            wildcard=wildcard,
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        ) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                file_path = dlg.GetPath()
                self._load_file(file_path)
    
    def _load_file(self, file_path: str):
        """
        Load a data file.
        
        Args:
            file_path: Path to the file to load
        """
        self._update_status(f"Loading file: {os.path.basename(file_path)}...")
        
        # Use a busy cursor
        wx.BeginBusyCursor()
        
        try:
            # Load the file
            success, message = self.data_loader.load_file(file_path)
            
            if success:
                df = self.data_loader.get_dataframe()
                file_info = self.data_loader.get_info()
                
                # Update all panels
                self.preview_panel.set_data(df, file_info)
                self.stats_panel.set_data(df)
                self.viz_panel.set_data(df)
                
                # Update file info label
                rows, cols = df.shape
                file_name = os.path.basename(file_path)
                self.file_info_label.SetLabel(f"📄 {file_name} ({rows:,} rows × {cols:,} columns)")
                
                # Enable close button
                self.close_btn.Enable(True)
                
                self._update_status(message)
                
                # Switch to preview tab
                self.notebook.SetSelection(0)
            else:
                wx.MessageBox(message, "Error Loading File", wx.OK | wx.ICON_ERROR)
                self._update_status(f"Error: {message}")
                
        except Exception as e:
            wx.MessageBox(f"Error loading file: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)
            self._update_status(f"Error: {str(e)}")
        
        finally:
            wx.EndBusyCursor()
    
    def _on_close_file(self, event):
        """Handle Close File action."""
        # Clear data
        self.data_loader.clear()
        
        # Clear all panels
        self.preview_panel.clear()
        self.stats_panel.clear()
        self.viz_panel.clear()
        
        # Update UI
        self.file_info_label.SetLabel("No file loaded")
        self.close_btn.Enable(False)
        
        self._update_status("File closed.")
    
    def _on_exit(self, event):
        """Handle Exit action."""
        self.Close()
    
    def _on_close(self, event):
        """Handle window close event."""
        dlg = wx.MessageDialog(
            self,
            "Are you sure you want to exit?",
            "Confirm Exit",
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION
        )
        
        if dlg.ShowModal() == wx.ID_YES:
            event.Skip()
        else:
            event.Veto()
    
    def _on_about(self, event):
        """Handle About action."""
        info = wx.adv.AboutDialogInfo()
        info.SetName("Data Analytics Tool")
        info.SetVersion("1.0.0")
        info.SetDescription(
            "A standalone desktop application for data analysis and visualization.\n\n"
            "Features:\n"
            "• Load CSV and JSON files\n"
            "• View data previews and statistics\n"
            "• Generate various chart types\n"
            "• Save visualizations as images"
        )
        info.SetCopyright("(C) 2024")
        info.AddDeveloper("Data Analytics Team")
        
        wx.adv.AboutBox(info)
    
    def _update_status(self, message: str):
        """
        Update the status bar.
        
        Args:
            message: Status message to display
        """
        self.status_bar.SetStatusText(message, 0)
        
        # Show memory usage in second field
        df = self.data_loader.get_dataframe()
        if df is not None:
            memory = df.memory_usage(deep=True).sum()
            memory_str = self._format_memory(memory)
            self.status_bar.SetStatusText(f"Memory: {memory_str}", 1)
        else:
            self.status_bar.SetStatusText("", 1)
    
    @staticmethod
    def _format_memory(bytes_size: int) -> str:
        """Format memory size for display."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024
        return f"{bytes_size:.1f} TB"
