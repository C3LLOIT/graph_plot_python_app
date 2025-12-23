# GUI module for the Data Analytics Application
# Contains wxPython GUI components

from .main_frame import MainFrame
from .panels import DataPreviewPanel, StatisticsPanel, VisualizationPanel

__all__ = ['MainFrame', 'DataPreviewPanel', 'StatisticsPanel', 'VisualizationPanel']
