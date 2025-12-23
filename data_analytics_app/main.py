#!/usr/bin/env python3
"""
Data Analytics Tool - Main Entry Point

A standalone desktop application for intelligent CSV/JSON data analysis
and visualization using wxPython.

Author: Data Analytics Team
Version: 1.0.0

Usage:
    python main.py

Requirements:
    - Python 3.8+
    - wxPython >= 4.2.0
    - pandas >= 2.0.0
    - numpy >= 1.24.0
    - matplotlib >= 3.7.0
    - seaborn >= 0.12.0
"""

import sys
import os

# Add the application directory to Python path
APP_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, APP_DIR)

import wx

# Import the main frame
from gui.main_frame import MainFrame


class DataAnalyticsApp(wx.App):
    """
    Main application class for the Data Analytics Tool.
    
    Initializes the wxPython application and creates the main window.
    """
    
    def OnInit(self):
        """
        Initialize the application.
        
        Returns:
            True if initialization successful
        """
        # Set application name
        self.SetAppName("Data Analytics Tool")
        
        # Create and show the main frame
        self.frame = MainFrame()
        self.frame.Show()
        
        # Set as top window
        self.SetTopWindow(self.frame)
        
        return True
    
    def OnExit(self):
        """
        Clean up when the application exits.
        
        Returns:
            Exit code (0 for success)
        """
        return 0


def main():
    """
    Main entry point for the Data Analytics Tool.
    
    Creates and runs the wxPython application.
    """
    print("=" * 60)
    print("Data Analytics Tool v1.0.0")
    print("=" * 60)
    print()
    print("Starting application...")
    print()
    
    # Create the application
    app = DataAnalyticsApp(redirect=False)
    
    # Run the main event loop
    app.MainLoop()
    
    print()
    print("Application closed.")


if __name__ == "__main__":
    main()
