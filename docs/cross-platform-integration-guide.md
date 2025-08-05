# Cross-Platform Integration Guide

## Step-by-Step Integration Process

### Step 1: Test Platform Config
First, verify that platform_config.py works correctly:

```bash
# From your project root
cd /home/rob_kaz/python/projects/Hourly_Backcast_Forecast
python platform_config.py
```

You should see output showing your detected platform and paths.

### Step 2: Update run_pipeline.py
Add platform config import at the top of run_pipeline.py:

```python
# Add after other imports
from platform_config import platform_config

# Update the initialization call
init.initialize_global_variables('auto')  # Use 'auto' for automatic detection
```

### Step 3: Update File References in file_meta_data.py
Replace hard-coded paths with dynamic ones:

```python
# Old way (remove):
forecast_path = r"C:\Users\kaczanor\OneDrive - Enbridge Inc\Documents\Python\..."

# New way (use):
from platform_config import platform_config
forecast_path = platform_config.get_data_file_path(
    'forcast_scenarios.yaml', 
    'library/class_objects/forecast_files'
)
```

### Step 4: Update YAML Loading Paths
In your run_pipeline.py, update the YAML file loading:

```python
# Old:
frcst_path = r"C:\Users\kaczanor\OneDrive - Enbridge Inc\Documents\Python\EDC Hourly Capacity Factor Q2 2024\library\class_objects\forecast_files\forcast_scenarios.yaml"

# New:
from pathlib import Path
project_root = platform_config.get_path('project_root')
if (project_root / 'Hourly_Backcast_Forecast').exists():
    base_dir = project_root / 'Hourly_Backcast_Forecast'
else:
    base_dir = project_root
    
frcst_path = str(base_dir / 'library' / 'class_objects' / 'forecast_files' / 'forcast_scenarios.yaml')
```

### Step 5: Create a Test Script
Create `test_platform_integration.py`:

```python
#!/usr/bin/env python3
"""Test script to verify platform integration"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from platform_config import platform_config
from library import initializer as init
from library import globals as gbl

def test_platform_integration():
    """Test that all platform-specific paths work correctly"""
    
    print("=== Testing Platform Integration ===\n")
    
    # Test 1: Platform detection
    print(f"1. Platform detected: {platform_config.platform}")
    
    # Test 2: Initialize project
    print("\n2. Initializing project...")
    init.initialize_global_variables('auto')
    
    # Test 3: Setup global paths
    print("\n3. Setting up global paths...")
    gbl.setup_global_paths()
    
    # Test 4: Verify key paths exist or can be created
    print("\n4. Verifying paths:")
    paths_to_check = {
        'Input directory': gbl.gbl_input_path,
        'Output directory': gbl.gbl_output_data_path_str,
        'CSV output': gbl.gbl_csv_output_path,
        'JSON output': gbl.gbl_json_folder_path,
    }
    
    for name, path_str in paths_to_check.items():
        path = Path(path_str)
        exists = path.exists()
        print(f"   {name}: {'✓' if exists else '✗'} {path}")
        if not exists and 'output' in name.lower():
            path.mkdir(parents=True, exist_ok=True)
            print(f"      → Created directory")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_platform_integration()
```

### Step 6: Update Git Configuration
Create/update `.gitignore`:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.env

# Project-specific
outputs/temp_data/
outputs/json_data/*.json
outputs/csv_data/
outputs/excel_data/
outputs/image_data/
*.log

# Platform-specific
.DS_Store
Thumbs.db
.vscode/
.idea/

# Jupyter
.ipynb_checkpoints/
```

### Step 7: Create Platform-Specific Scripts
Create helper scripts for different platforms:

**For Windows**: `run_windows.bat`
```batch
@echo off
echo Starting Hourly Backcast Forecast on Windows...
cd /d "%~dp0"
python library\run_pipeline.py
pause
```

**For Linux/WSL2**: `run_linux.sh`
```bash
#!/bin/bash
echo "Starting Hourly Backcast Forecast on Linux/WSL2..."
cd "$(dirname "$0")"
python library/run_pipeline.py
```

Make the Linux script executable:
```bash
chmod +x run_linux.sh
```

## Testing Cross-Platform Compatibility

### Test on WSL2
```bash
# In WSL2 terminal
cd /home/rob_kaz/python/projects/Hourly_Backcast_Forecast
python test_platform_integration.py
```

### Test on Windows
```cmd
# In Windows Command Prompt
cd C:\path\to\project\on\windows
python test_platform_integration.py
```

## Troubleshooting

### Common Issues and Solutions

1. **Import Error for platform_config**
   - Ensure platform_config.py is in the project root
   - Check that sys.path includes the project root

2. **Path Not Found Errors**
   - Run the test script to verify path creation
   - Check file permissions on Linux/WSL2

3. **Different Path Separators**
   - Always use Path objects or os.path.join()
   - Never hard-code path separators

## Next Steps

1. **Complete File Metadata Refactoring**
   - Continue converting hard-coded paths in file_meta_data.py
   - Test each forecast scenario with new class structure

2. **Update Documentation**
   - Document any platform-specific behaviors
   - Update docstrings to reflect cross-platform support

3. **Create Unit Tests**
   - Test path resolution on each platform
   - Test file operations across platforms

4. **Git Workflow**
   ```bash
   git add .
   git commit -m "feat: add cross-platform support with platform_config"
   git push origin feature/cross-platform-support
   ```