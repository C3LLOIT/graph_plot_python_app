# Data Analytics Tool

A standalone desktop application for intelligent CSV/JSON data analysis and visualization using wxPython.

## Features

- **File Support**: Load CSV and JSON files with automatic format detection
- **Data Preview**: View dataset with shape, column types, and first 100 rows
- **Statistical Analysis**: Descriptive statistics, correlation matrix, and quick insights
- **Visualization**: 7 chart types with embedded matplotlib canvas
  - Line Chart
  - Bar Chart
  - Histogram
  - Scatter Plot
  - Box Plot
  - Pie Chart
  - Heatmap (Correlation)
- **Save Plots**: Export visualizations as PNG, JPEG, or PDF

## Requirements

- Python 3.8+
- wxPython >= 4.2.0
- pandas >= 2.0.0
- numpy >= 1.24.0
- matplotlib >= 3.7.0
- seaborn >= 0.12.0

## Installation

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

```bash
cd data_analytics_app
python main.py
```

## Project Structure

```
data_analytics_app/
├── main.py                 # Application entry point
├── requirements.txt        # Dependencies
├── README.md              # This file
├── sample_data.csv        # Sample data for testing
├── gui/
│   ├── __init__.py
│   ├── main_frame.py      # Main window with menu and tabs
│   └── panels.py          # Data, Statistics, Visualization panels
├── core/
│   ├── __init__.py
│   ├── data_loader.py     # CSV/JSON loading
│   ├── data_analyzer.py   # Statistical analysis
│   └── visualizer.py      # Chart generation
└── utils/
    ├── __init__.py
    ├── validators.py      # File and data validation
    └── helpers.py         # Type detection, formatting
```

## Architecture

### Data Flow

1. **File Selection** → User selects CSV/JSON via File Dialog
2. **Data Loading** → `DataLoader` parses file into pandas DataFrame
3. **Distribution** → DataFrame passed to all 3 panels
4. **Analysis** → `DataAnalyzer` computes statistics
5. **Visualization** → `Visualizer` generates matplotlib figures
6. **Display** → Charts embedded in wxPython canvas

### Design Pattern

The application follows an MVC-inspired architecture:
- **Model**: `DataLoader`, `DataAnalyzer` (core/)
- **View**: `panels.py` (gui/)
- **Controller**: `MainFrame` event handlers (gui/)

## Packaging for Distribution

### Using PyInstaller

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "DataAnalyticsTool" main.py
```

### Using cx_Freeze

```python
# setup.py
from cx_Freeze import setup, Executable

setup(
    name="DataAnalyticsTool",
    version="1.0",
    executables=[Executable("main.py", base="Win32GUI")]
)
```

```bash
pip install cx_Freeze
python setup.py build
```

## Future Improvements

- **Auto Insights**: Statistical significance tests, anomaly detection
- **ML Integration**: Regression, clustering, classification models
- **Dashboard Export**: Export visualizations to PDF/HTML reports
- **Plugin System**: Custom visualization and analysis plugins
- **Data Transformation**: Pipeline editor for data cleaning
- **Multi-Dataset**: Compare and merge multiple datasets

## License

MIT License
