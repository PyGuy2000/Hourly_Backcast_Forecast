import os
import sys
from pathlib import Path

# Add parent directory to path to import platform_config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from platform_config import platform_config

'''
Sets up directories and folder names using platform_config
This module initializes all path-related variables for the project
'''

# Folder Names (platform-independent)
init_csv_folder_name_str = 'csv_data'
init_image_folder_name_str = 'image_data'
init_json_folder_name_str = 'json_data'
init_excel_folder_name_str = 'excel_data'

# Global variables
init_ide_option = None
init_base_output_directory = None
init_base_input_directory = None


def initialize_global_variables(ide_option='auto'):
    """
    Initialize global variables with platform-aware paths.
    
    Args:
        ide_option: 'auto', 'vscode', 'kaggle', or 'jupyter_notebook'
                   'auto' will detect the environment automatically
    """
    global init_ide_option
    global init_base_output_directory, init_base_input_directory
    
    print("initialize_global_variables called")
    print(f"Platform detected: {platform_config.platform}")
    
    # Auto-detect IDE if requested
    if ide_option == 'auto':
        if 'KAGGLE_KERNEL_RUN_TYPE' in os.environ:
            ide_option = 'kaggle'
        elif 'VSCODE_PID' in os.environ or 'TERM_PROGRAM' in os.environ:
            ide_option = 'vscode'
        elif 'JPY_PARENT_PID' in os.environ:
            ide_option = 'jupyter_notebook'
        else:
            ide_option = 'vscode'  # Default
    
    init_ide_option = ide_option
    
    if init_ide_option == 'vscode':
        # Use platform_config to get the correct paths
        init_base_output_directory = str(platform_config.get_path('outputs'))
        init_base_input_directory = str(platform_config.get_path('inputs'))
        
    elif init_ide_option == 'kaggle':
        # Kaggle-specific paths
        init_base_output_directory = '/kaggle/working'
        init_base_input_directory = '/kaggle/input'
        
    elif init_ide_option == 'jupyter_notebook':
        # Use platform_config for Jupyter as well
        init_base_output_directory = str(platform_config.get_path('outputs'))
        init_base_input_directory = str(platform_config.get_path('inputs'))
    
    # Create directories if they don't exist
    Path(init_base_output_directory).mkdir(parents=True, exist_ok=True)
    Path(init_base_input_directory).mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories
    output_subdirs = [
        init_csv_folder_name_str,
        init_image_folder_name_str,
        init_json_folder_name_str,
        init_excel_folder_name_str,
        'temp_data'
    ]
    
    for subdir in output_subdirs:
        subdir_path = Path(init_base_output_directory) / subdir
        subdir_path.mkdir(parents=True, exist_ok=True)
    
    print(f"{init_ide_option} init_base_output_directory set: {init_base_output_directory}")
    print(f"{init_ide_option} init_base_input_directory set: {init_base_input_directory}")
    
    # Show platform-specific information if in debug mode
    if os.environ.get('DEBUG'):
        platform_config.print_platform_info()
    
    return


# Legacy support functions (for backward compatibility)
def get_init_home_dir():
    """Get home directory path (legacy support)"""
    if platform_config.is_windows:
        return 'C:/Users/Rob_Kaz/OneDrive/Documents/Rob Personal Documents/Python/EDC Hourly Capacity Factor Q2 2024'
    else:
        return str(platform_config.get_path('project_root'))


def get_init_office_dir():
    """Get office directory path (legacy support)"""
    if platform_config.is_windows:
        return 'C:/Users/kaczanor/OneDrive - Enbridge Inc/Documents/Python/EDC Hourly Capacity Factor Q2 2024'
    else:
        return str(platform_config.get_path('project_root'))


# For backward compatibility, set these after import
init_home_dir = None
init_office_dir = None

def _set_legacy_vars():
    """Set legacy variables for backward compatibility"""
    global init_home_dir, init_office_dir
    init_home_dir = get_init_home_dir()
    init_office_dir = get_init_office_dir()

# Call this when module is imported
_set_legacy_vars()








# import os
# '''
# Sets up directories and folder names
# '''


# init_home_dir = 'C:/Users/Rob_Kaz/OneDrive/Documents/Rob Personal Documents/Python/EDC Hourly Capacity Factor Q2 2024'
# init_office_dir = 'C:/Users/kaczanor/OneDrive - Enbridge Inc/Documents/Python/EDC Hourly Capacity Factor Q2 2024'

# #Folder Names
# init_csv_folder_name_str = 'csv_data'
# init_image_folder_name_str = 'image_data'
# init_json_folder_name_str = 'json_data'
# init_excel_folder_name_str = 'excel_data'

# init_ide_option = None
# init_base_output_directory = None
# init_base_input_directory = None



# def initialize_global_variables(ide_option):
#     global init_ide_option
#     global init_base_output_directory, init_base_input_directory, init_input_dir, init_output_dir
    
#     print("initialize_global_variables called")

#     init_ide_option = ide_option
    
#     if init_ide_option == 'vscode':
#         if os.path.exists(init_home_dir):
#             init_root_dir = init_home_dir
#         else:
#             init_root_dir = init_office_dir
#         init_output_dir = "outputs/"
#         init_input_dir = "inputs"  # removed the leading "/"
#     elif init_ide_option == 'kaggle':
#         init_root_dir = ''
#         init_output_dir = '/kaggle/working/CSV_Folder'  # retained the leading "/"
#         init_input_dir = '/kaggle/input/'  # retained the leading "/"

#     elif init_ide_option == 'jupyter_notebook':
#         init_root_dir = 'C:/Users/kaczanor/EDC Hourly Capacity Factor Q2 2024'
#         init_output_dir = 'NA'
#         init_input_dir = 'NA'

#     init_base_output_directory = os.path.normpath(os.path.join(init_root_dir, init_output_dir))
#     init_base_input_directory = os.path.normpath(os.path.join(init_root_dir, init_input_dir))
    
#     print(f"{init_ide_option} init_base_output_directory set: {init_base_output_directory}")
#     print(f"{init_ide_option} init_base_input_directory set: {init_base_input_directory}")
    
#     return 