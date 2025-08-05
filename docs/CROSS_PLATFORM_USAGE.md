# Cross-Platform Usage Guide

The Geospatial Dashboard is designed to work seamlessly across Windows, WSL2, and Linux environments. This guide explains how the cross-platform support works and how to use it effectively.

## 🖥️ Platform Detection

The dashboard automatically detects your operating system and configures itself accordingly. No manual configuration is required!

### Supported Platforms
- **Windows** (Windows 10/11)
- **WSL2** (Windows Subsystem for Linux 2)
- **Linux** (Ubuntu, Debian, etc.)
- **macOS** (experimental)

## 🚀 Starting the Dashboard

### Quick Start by Platform

#### Windows
```cmd
start_dashboard.bat
```

#### Linux/WSL2
```bash
./scripts/start_crossplatform.sh
```

#### Any Platform (Python)
```bash
python scripts/start_dashboard.py
```

### Understanding the Startup Scripts

We provide multiple startup scripts for different use cases:

| Script | Platform | Purpose | Features |
|--------|----------|---------|----------|
| **`start_dashboard.bat`** | Windows | Primary Windows launcher | • Starts both servers<br>• Opens browser<br>• Windows-native |
| **`start_crossplatform.sh`** | Linux/WSL2 | Primary Linux/WSL2 launcher | • Conda environment support<br>• Calls Python script<br>• Shell environment setup |
| **`start_simple.sh`** | Linux/WSL2 | Alternative simple launcher | • Direct server startup<br>• No conda required<br>• Basic but reliable |
| **`start_dashboard.py`** | All | Universal Python launcher | • OS auto-detection<br>• Cross-platform<br>• Programmatic control |
| ~~`start_dashboard.sh`~~ | Linux/WSL2 | Deprecated | ⚠️ Only starts backend! |

### Recommended Scripts

- **Windows Users**: Always use `start_dashboard.bat`
- **WSL2/Linux Users**: Use `start_crossplatform.sh` (supports conda environments)
- **Docker/Containers**: Use `start_dashboard.py` directly
- **Development/Testing**: Any script based on your needs

### Script Details

#### `start_dashboard.bat` (Windows)
```batch
@echo off
echo Starting Geospatial Dashboard on Windows...
python scripts\start_dashboard.py
```
- Simple wrapper for Windows
- Handles Windows path conventions
- Launches the Python script

#### `start_crossplatform.sh` (Linux/WSL2)
```bash
#!/bin/bash
# Features:
# - Detects WSL2 environment
# - Activates conda environment if available
# - Sets up Python path
# - Calls the universal Python script
```
- Best for users with conda/mamba
- Handles environment activation
- Provides clean shutdown handling

#### `start_simple.sh` (Linux/WSL2)
```bash
#!/bin/bash
# Features:
# - Starts backend API server
# - Starts frontend HTTP server
# - Simple process management
```
- No dependencies on conda
- Direct server startup
- Good for production/deployment

#### `start_dashboard.py` (Universal)
```python
# Features:
# - Automatic OS detection
# - Platform-specific configurations
# - Integrated frontend/backend startup
# - Browser auto-launch
```
- Pure Python solution
- Most flexible option
- Used by other scripts

## 🔧 How It Works

### Platform Configuration Module

The `backend/core/platform_config.py` module handles all platform-specific logic:

```python
from backend.core.platform_config import platform_config

# Automatic platform detection
print(platform_config.platform)  # 'windows', 'wsl2', or 'linux'

# Get platform-specific paths
data_path = platform_config.get_data_file_path('cities.geojson')
config_path = platform_config.get_config_path()
cache_path = platform_config.get_cache_path('results.json')
```

### Path Resolution

All paths are automatically converted to the correct format:

| Platform | Path Example |
|----------|--------------|
| Windows | `C:\Users\username\geospatial-dashboard\data\file.json` |
| WSL2 | `/home/username/geospatial-dashboard/data/file.json` |
| Linux | `/home/username/geospatial-dashboard/data/file.json` |

### Network Configuration

The system automatically configures network settings:

| Platform | Host Binding | Access |
|----------|--------------|--------|
| Windows | `127.0.0.1` | Local only (security) |
| WSL2 | `0.0.0.0` | Network accessible |
| Linux | `0.0.0.0` | Network accessible |

## 📁 File Path Best Practices

### In Configuration Files
Always use forward slashes and relative paths:
```yaml
# layer_registry.yaml - works on all platforms
layer_files:
  cities:
    path: "geospatial_data/cities.geojson"  # ✅ Correct
    # path: "C:\\data\\cities.geojson"      # ❌ Wrong
```

### In Python Code
Use the platform config module:
```python
# ✅ Correct - platform independent
from backend.core.platform_config import platform_config
file_path = platform_config.get_data_file_path('cities.geojson')

# ❌ Wrong - platform specific
file_path = "C:\\data\\cities.geojson"
```

## 🐛 Debugging Platform Issues

### Check Platform Detection
```bash
python backend/core/platform_config.py
```

Output example:
```
=== Platform Configuration ===
Detected Platform: wsl2
System: Linux
Python Version: 3.11.0
Current Directory: /home/user/geospatial-dashboard
Project Root: /home/user/geospatial-dashboard

Configured Paths:
  ✓ project_root: /home/user/geospatial-dashboard
  ✓ geospatial_data: /home/user/geospatial-dashboard/geospatial_data
  ✓ backend: /home/user/geospatial-dashboard/backend
  ✓ config: /home/user/geospatial-dashboard/backend/core/config
  ✓ cache: /home/user/geospatial-dashboard/modern_dashboard/cache
==============================
```

### Test Platform Paths
```bash
python scripts/test_platform.py
```

This will verify all paths are correctly resolved for your platform.

## 🌐 Environment-Specific Features

### Windows
- **Pros**: Native performance, easy installation
- **Cons**: Path length limitations (260 chars)
- **Tips**: 
  - Use `start_dashboard.bat`
  - Enable long path support in Windows 10+
  - Use short project paths

### WSL2
- **Pros**: Linux tools on Windows, great for development
- **Cons**: File I/O slower across OS boundaries
- **Tips**: 
  - Use `./scripts/start_crossplatform.sh`
  - Keep project files in WSL filesystem (`/home/...`)
  - Access via `\\wsl$` from Windows Explorer

### Linux
- **Pros**: Native performance, no path limitations
- **Cons**: May need additional dependencies
- **Tips**: 
  - Use `./scripts/start_crossplatform.sh`
  - Use system package manager for dependencies
  - Check file permissions

## 📝 Common Issues and Solutions

### Issue: "Permission denied" when running shell scripts
**Solution**: Make scripts executable:
```bash
chmod +x scripts/start_crossplatform.sh
chmod +x scripts/start_simple.sh
chmod +x scripts/start_dashboard.py
```

### Issue: "Module not found" errors
**Solution**: Ensure you're running from the project root and have activated your virtual environment.

### Issue: Conda environment not found
**Solution**: The scripts work with or without conda. If you don't have conda, use `start_simple.sh` instead.

### Issue: Can't access from network on Windows
**Solution**: Windows binds to localhost by default for security. To allow network access:
1. Edit `scripts/start_dashboard.py`
2. Change `host = "127.0.0.1"` to `host = "0.0.0.0"`
3. Configure Windows Firewall if needed

### Issue: Wrong startup script used
**Solution**: 
- Windows: Use `start_dashboard.bat`
- Linux/WSL2: Use `start_crossplatform.sh`
- Avoid `start_dashboard.sh` (deprecated, backend only)

## 🔄 Migrating Between Platforms

### From Windows to WSL2
1. Copy project folder to WSL2: `/home/username/`
2. Install Python in WSL2
3. Create new virtual environment
4. Install dependencies
5. Run with `./scripts/start_crossplatform.sh`

### From WSL2 to Windows
1. Copy from `\\wsl$\Ubuntu\home\username\` to `C:\`
2. Create Windows virtual environment
3. Install dependencies
4. Run with `start_dashboard.bat`

## 🚪 Advanced Configuration

### Custom Path Configuration
Edit `platform_config.py` to add custom paths:
```python
# In _initialize_base_paths()
paths['custom'] = project_root / 'my_custom_folder'
```

### Override Platform Detection
```python
# Force specific platform (for testing)
import os
os.environ['FORCE_PLATFORM'] = 'windows'  # or 'wsl2', 'linux'
```

### Manual Server Startup
If you need fine control, start servers manually:

**Backend API:**
```bash
cd modern_dashboard
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd modern_dashboard
python -m http.server 3000
```

## 📚 Additional Resources

- [Architecture Overview](architecture-overview.md) - System design details
- [API Documentation](http://localhost:8000/docs) - When server is running
- [Adding Components](ADDING_COMPONENTS.md) - Extending the system

---

For questions about cross-platform support, please open an issue on GitHub!