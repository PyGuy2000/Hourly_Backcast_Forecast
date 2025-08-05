# Hourly Backcast Forecast Analysis System

A comprehensive Python-based system for analyzing hourly energy price forecasts and performing backcasting analysis on historical and forecasted energy market data.

## 🎯 Project Overview

This project loads and analyzes hourly energy market data to:
- Process historical hourly energy prices
- Analyze forecasted hourly energy prices from multiple providers
- Perform statistical analysis and generate visualizations
- Calculate capacity factors and capture prices for generation assets
- Support cross-platform deployment (Windows, WSL2, Linux)

### Key Features
- Multi-provider forecast data integration (EDC, Similan, etc.)
- Statistical analysis with P10/P25/P50/P75/P90 calculations
- LCOE (Levelized Cost of Energy) calculations
- Merit order dispatch simulation
- Transmission cost calculations
- Cross-platform compatibility

## 📁 Project Structure

```
Hourly_Backcast_Forecast/
├── .git/                           # Git repository
├── docs/                           # Documentation
│   └── CROSS_PLATFORM_USAGE.md    # Cross-platform usage guide
├── environment.yml                 # Conda environment configuration
├── platform_config.py             # Cross-platform configuration module
├── library/                       # Core library code
│   ├── run_pipeline.py           # Main entry point
│   ├── globals.py                # Global variables
│   ├── initializer.py            # Project initialization
│   ├── file_meta_data.py         # File metadata management (being refactored)
│   ├── config.py                 # Configuration flags
│   ├── class_objects/            # Object-oriented modules
│   │   ├── forecast_files/       # Forecast file classes
│   │   ├── output_files/         # Output file classes
│   │   └── other_classes/        # Utility classes
│   └── test_code/                # Test scripts
├── inputs/                       # Input data directory
│   ├── AB_Historical_Prices/     # Historical Alberta energy prices
│   ├── market_forecast_data_by_provider/  # Forecast data by provider
│   └── AESO_Tariff_Data/        # AESO tariff information
├── outputs/                      # Output data directory
│   ├── csv_data/                 # CSV outputs
│   ├── excel_data/               # Excel outputs
│   ├── image_data/               # Charts and visualizations
│   ├── json_data/                # JSON metadata
│   └── temp_data/                # Temporary files
└── template_excel_output_files/  # Excel templates
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Conda/Mamba (recommended) or pip
- Git

### Environment Setup

#### Option 1: Using Conda (Recommended)
```bash
# Clone the repository
git clone https://github.com/yourusername/Hourly_Backcast_Forecast.git
cd Hourly_Backcast_Forecast

# Create conda environment from yml file
conda env create -f environment.yml

# Activate the environment
conda activate hourly_backcast
```

#### Option 2: Using pip
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/WSL2:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## 🖥️ Cross-Platform Usage

The project now supports seamless operation across different platforms:

### Platform Detection
The system automatically detects your operating system and configures paths accordingly:
- **Windows**: Native Windows paths (C:\...)
- **WSL2**: Linux paths in Windows Subsystem for Linux
- **Linux**: Standard Unix paths

### Running the Project

#### Windows
```cmd
python library\run_pipeline.py
```

#### WSL2/Linux
```bash
python library/run_pipeline.py
```

### Platform Configuration
The `platform_config.py` module handles all platform-specific logic:

```python
from platform_config import platform_config

# Automatic platform detection
print(platform_config.platform)  # 'windows', 'wsl2', or 'linux'

# Get platform-specific paths
data_path = platform_config.get_data_file_path('historical_prices.csv')
```

## 🔧 Current Refactoring Tasks

### Task #1: File Metadata Refactoring
We are replacing hard-coded file paths in `file_meta_data.py` with object-oriented class modules:

**Before (Hard-coded):**
```python
# Old approach with hard-coded paths
Q2_2025_edc_basecase_data = 'Q2-2025 Hourly Data Base Case.xlsx'
edcq2_2025_path = "C:/Users/kaczanor/.../outputs/csv_data/edc/..."
```

**After (Class-based):**
```python
# New approach with class objects
forecast_scenarios = load_forecast_scenarios('forcast_scenarios.yaml')
list_of_structures = build_forecast_file_structure(forecast_scenarios, gbl)
```

### Task #2: Cross-Platform Integration
Integrating `platform_config.py` to work with existing global variable management:

**Integration Points:**
1. Update `initializer.py` to use platform_config
2. Modify `globals.py` to use dynamic paths
3. Ensure all file operations use platform-agnostic paths

## 📊 Usage

### Basic Pipeline Execution

1. **Configure Analysis Settings**
   Edit `library/config.py` to enable/disable analysis steps:
   ```python
   create_electr_frcst_dicts_flag = True
   process_forecast_data_flag = True
   stats_on_frcst_data_flag = True
   # ... etc
   ```

2. **Run the Main Pipeline**
   ```bash
   python library/run_pipeline.py
   ```

### Key Analysis Steps

1. **Data Processing**: Load and process forecast data from multiple providers
2. **Statistical Analysis**: Calculate percentile values (P10-P90)
3. **LCOE Calculation**: Determine levelized costs for generation assets
4. **Merit Order Simulation**: Simulate dispatch and calculate capacity factors
5. **Visualization**: Generate charts and heatmaps
6. **Report Generation**: Create Excel and CSV outputs

## 🔄 Git Workflow

### Initial Setup
```bash
# Set up git (if not already initialized)
git init
git remote add origin https://github.com/yourusername/Hourly_Backcast_Forecast.git

# Create .gitignore
echo "*.pyc" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "outputs/temp_data/" >> .gitignore
echo ".env" >> .gitignore
```

### Development Workflow
```bash
# 1. Create a feature branch for your work
git checkout -b feature/cross-platform-refactor

# 2. Make changes and commit
git add .
git commit -m "feat: integrate platform_config for cross-platform support"

# 3. Push to GitHub
git push origin feature/cross-platform-refactor

# 4. Create Pull Request on GitHub
```

### Best Practices
- Always work on feature branches
- Write descriptive commit messages
- Test on both Windows and WSL2 before pushing
- Keep sensitive data out of version control

## 📝 Configuration Files

### YAML Configuration Files
- `forcast_scenarios.yaml`: Defines forecast scenarios and parameters
- `output_file.yaml`: Specifies output file structures

### Global Configuration
- `library/config.py`: Runtime flags for pipeline steps
- `library/globals.py`: Global variables and paths
- `platform_config.py`: Cross-platform path management

## 🐛 Troubleshooting

### Common Issues

1. **Permission Errors (WSL2)**
   ```bash
   chmod +x library/run_pipeline.py
   ```

2. **Module Import Errors**
   Ensure you're running from the project root:
   ```bash
   cd /path/to/Hourly_Backcast_Forecast
   python library/run_pipeline.py
   ```

3. **Platform Path Issues**
   Check platform detection:
   ```python
   python platform_config.py
   ```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is proprietary. Please contact the project maintainers for licensing information.

## 👥 Contact

Rob Kaczanowski - rob_kaz@example.com

Project Link: [https://github.com/yourusername/Hourly_Backcast_Forecast](https://github.com/yourusername/Hourly_Backcast_Forecast)

---

## 🎯 Next Steps

### Immediate Actions
1. Complete the file_meta_data.py refactoring
2. Test platform_config integration
3. Update all hard-coded paths to use platform_config
4. Create unit tests for cross-platform functionality

### Future Enhancements
- Add Docker support for containerized deployment
- Implement automated testing across platforms
- Create web-based dashboard for results visualization
- Add support for additional forecast providers