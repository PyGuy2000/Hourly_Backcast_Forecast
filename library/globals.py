"""
Refactored globals.py with platform-aware path management
This shows how to properly integrate platform_config for all file paths
"""

from library.config import runpipe_all_flags_true
from library.class_objects.other_classes.classes import TrackedDict

import os
import pandas as pd
import json
import sys
from pathlib import Path

# Add parent directory to import platform_config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from platform_config import platform_config

# =============================================
# PLATFORM-AWARE PATH INITIALIZATION
# =============================================
# This replaces all hard-coded paths with dynamic, platform-aware paths

def initialize_platform_paths():
    """
    Initialize all global path variables using platform_config.
    This function should be called early in the module loading process.
    """
    global gbl_gbase_output_path, gbl_json_existing_powergen_folder_path_str
    global gbl_temp_path_str, gbl_hist_processed_price_data, gbl_hist_processed_nat_gas_price
    
    # Get the project root
    project_root = platform_config.get_path('project_root')
    
    # Set base paths using platform_config
    gbl_gbase_output_path = str(project_root)
    gbl_json_existing_powergen_folder_path_str = str(platform_config.get_path('json_data'))
    gbl_temp_path_str = str(platform_config.get_path('temp_data'))
    
    # Create directories if they don't exist
    Path(gbl_json_existing_powergen_folder_path_str).mkdir(parents=True, exist_ok=True)
    Path(gbl_temp_path_str).mkdir(parents=True, exist_ok=True)
    
    # Load historical data with error handling
    hist_price_path = platform_config.get_input_file_path(
        'merged_pool_price_data_2000_to_2024.csv',
        'AB_Historical_Prices'
    )
    hist_gas_path = platform_config.get_input_file_path(
        'merged_nat_gas_price_data_2000_to_2024.csv',
        'AB_Historical_Prices'
    )
    
    # Initialize as empty DataFrames first
    global gbl_hist_processed_price_data, gbl_hist_processed_nat_gas_price
    gbl_hist_processed_price_data = pd.DataFrame()
    gbl_hist_processed_nat_gas_price = pd.DataFrame()
    
    # Try to load the data if files exist
    if hist_price_path.exists():
        try:
            gbl_hist_processed_price_data = pd.read_csv(str(hist_price_path))
            print(f"✓ Loaded historical price data from {hist_price_path}")
        except Exception as e:
            print(f"✗ Error loading historical price data: {e}")
    else:
        print(f"⚠ Historical price data not found at {hist_price_path}")
    
    if hist_gas_path.exists():
        try:
            gbl_hist_processed_nat_gas_price = pd.read_csv(str(hist_gas_path))
            print(f"✓ Loaded historical gas price data from {hist_gas_path}")
        except Exception as e:
            print(f"✗ Error loading historical gas price data: {e}")
    else:
        print(f"⚠ Historical gas price data not found at {hist_gas_path}")

# =============================================
# CALL INITIALIZATION ON MODULE LOAD
# =============================================
# Initialize paths when module is imported
initialize_platform_paths()

# =============================================
# EXISTING GLOBAL VARIABLES (unchanged)
# =============================================
gbl_dateMPT_label_natural_gas = "DATE_BEGIN_LOCAL"
gbl_revised_date_col_gbl_dateMST_label_natural_gas = "DateTime"
gbl_pool_price_primary_data_col = 'pool_price'
gbl_natgas_primary_data_col = 'NAT_GAS_PRICE'

# =============================================
# PATH VARIABLES (now platform-aware)
# =============================================
# These are set by initialize_platform_paths() above
# gbl_gbase_output_path - set dynamically
# gbl_json_existing_powergen_folder_path_str - set dynamically
# gbl_temp_path_str - set dynamically

# Data columns
gbl_pool_price_primary_data_col = 'pool_price'
gbl_natgas_primary_data_col = 'NAT_GAS_PRICE'

# DataFrames loaded from files
# gbl_hist_processed_price_data - loaded dynamically
# gbl_hist_processed_nat_gas_price - loaded dynamically

# =============================================
# FOLDER NAMES (platform-independent)
# =============================================
gbl_csv_folder_name_str = 'csv_data'
gbl_image_folder_name_str = 'image_data'
gbl_json_folder_name_str = 'json_data'
gbl_excel_folder_name_str = 'excel_data'
gbl_excel_template_folder_name = 'template_excel_output_files'
gbl_processed_historical_folder_name_str = 'Processed Historical Data'
gbl_forecaster_folder_name_str = 'market_forecast_data_by_provider'

# =============================================
# FILE NAMES (platform-independent)
# =============================================
gbl_simulation_summary_tmplt_filename = 'simluation_annual_monthly_output_file_template.xlsx'
gbl_historical_data_filename_str = 'AB_Historical_Prices/merged_pool_price_data_2000_to_2024.csv'
gbl_full_file_data_name_str = 'full_file_data.json'
gbl_loaded_file_data_name_str = 'loaded_file_data.json'
gbl_output_file_name_str = 'output_data.json'
gbl_power_gen_dict_filename = 'power_generation_dict.json'
gbl_p50_output_file_var = 'p50_hourly_spot_electricity.csv'
gbl_power_p_template_filename = '_hourly_spot_electricity.csv'
gbl_natgas_p_template_filename = '_hourly_spot_natural_gas.csv'
gbl_updated_power_generation_json_file_str = 'updated_power_generation_dict.json'

# =============================================
# DYNAMIC PATH VARIABLES
# =============================================
# Created File Paths (now using platform_config)
gbl_json_power_generation_path = os.path.join(
    gbl_json_existing_powergen_folder_path_str, 
    gbl_updated_power_generation_json_file_str
)
gbl_csv_input_path = None

# Set during run time
gbl_frcst_output_excel_file_path = None
gbl_frcst_input_excel_file_path = None
gbl_frcst_output_csv_file_path = None

# Create global data frames
gbl_hist_processed_price_data = pd.DataFrame()
gbl_hist_processed_nat_gas_price = pd.DataFrame()

# Create dictionary shortcut paths to be used later
gbl_input_general_data = None
gbl_price_forecast = None
gbl_output_general_data = None
gbl_processed_price_forecast = None
gbl_output_template = None

#Carbon Tax
gbl_carbon_tax_annual_dict = {
    '2000': 0,
    '2001': 0,
    '2002': 0,
    '2003': 0,
    '2004': 0,
    '2005': 0,
    '2006': 0,
    '2007': 15,
    '2008': 15,
    '2009': 15,
    '2010': 15,
    '2011': 15,
    '2012': 15,
    '2013': 15,
    '2014': 15,
    '2015': 15,
    '2016': 20,
    '2017': 30,
    '2018': 30,
    '2019': 30,
    '2020': 30,
    '2021': 40,
    '2022': 50,
    '2023': 65,
    '2024': 80,
    '2025': 95,
    '2026': 110,
    '2027': 125,
    '2028': 140,
    '2029': 155,
    '2030': 170,
    '2031': 170,
    '2032': 170,
    '2033': 170,
    '2034': 170,
    '2035': 170,
    '2036': 170,
    '2037': 170,
    '2038': 170,
    '2039': 170,
    '2040': 170
}

# Electricity Grid Displacement Factors (EGDF)
# Electricity Grid Displacement Factor (tCO2e/MWh)
# Electricity grid displacement with renewable generation
gbl_edgf_renewable_generation_dict = {
    '2024': 0.49,
    '2025': 0.46,
    '2026': 0.43,
    '2027': 0.401,
    '2028': 0.371,
    '2029': 0.341,
    '2030': 0
}

gbl_increased_onsite_grid_electricity_use_dict = {
    '2024': 0.523,
    '2025': 0.491,
    '2026': 0.459,
    '2027': 0.427,
    '2028': 0.395,
    '2029': 0.363,
    '2030': 0
}
gbl_reduction_in_grid_electricity_usage_dict = {
    '2024': 0.523,
    '2025': 0.491,
    '2026': 0.459,
    '2027': 0.427,
    '2028': 0.395,
    '2029': 0.363,
    '2030': 0
}
gbl_distributed_renewable_displacement_at_pointofuse_dict = {
    '2024': 0.523,
    '2025': 0.491,
    '2026': 0.459,
    '2027': 0.427,
    '2028': 0.395,
    '2029': 0.363,
    '2030': 0
}

# Updated TIER High-Performance Benchmarks (CO2e tonnes per benchmark unit)
gbl_electrictity_hpb_dict = {
    #Units = MWh
    '2022' : 0.37,
    '2023' : 0.3626,
    '2024' : 0.3552,
    '2025' : 0.3478,
    '2026' : 0.3404,
    '2027' : 0.333,
    '2028' : 0.3256,
    '2029' : 0.3182,
    '2030' : 0.3108
}
gbl_electrictity_hpb_dict = {
    #Units = tonne
    '2022' : 9.068,
    '2023' : 8.993,
    '2024' : 8.919,
    '2025' : 8.844,
    '2026' : 8.769,
    '2027' : 8.694,
    '2028' : 8.619,
    '2029' : 8.545,
    '2030' : 8.47
}
gbl_industrial_heat_hpb_dict = {
    #Units = GJ
    '2022' : 0.0630,
    '2023' : 0.0617,
    '2024' : 0.0605,
    '2025' : 0.0592,
    '2026' : 0.0580,
    '2027' : 0.0567,
    '2028' : 0.0554,
    '2029' : 0.0542,
    '2030' : 0.0529
}

'''
Clean Electricity Regulations10 (CER)
The regulations limit the emissions intensity of fossil fired generation to 30 tCO2e per GWh, or 0.030 tCO2e/MWh,
which is 92% lower than the current TIER benchmark of 0.363 tCO2e/MWh. The regulations apply to units that
meet the following criteria (covered units):
~ Uses any amount of fossil fuels to generate electricity,
~ Has a capacity of 25 MW or greater, and
~ Is grid connected to a NERC-regulated electricity system.
The standard applies to all covered units starting January 1, 2035, with exceptions for units commissioned
between 2015 and 2024, which must meet the standard 20 years after their commissioning date. Covered units
include cogeneration units that are net exporters of electricity (in Alberta, cogeneration exports an average of
1,600 MW to the system). The regulations also include a peaking unit exemption, which allows for unabated
operation for up to 450 hours per year.
'''
gbl_cer_factor_dict = {
    '2030' : 0.030,
}
# =============================================
# Dictionaries transferred to tracked dictionary class
# =============================================
gbl_power_generation_dict = {}
glb_time_variable_dict = {}
gbl_general_data_variable_dict = {}
gbl_generator_specific_variable_dict = {}
gbl_run_variable_dict = {}
gbl_run_variable_dict_ideal = {}

# Define Tracked Dictionary Class Instances
gbl_tracked_powergen_dict = {}
gbl_tracked_dict_json_file_data = {}
gbl_tracked_loaded_dict_json_file_data = {}
gbl_tracked_dict_time_variables = {}
gbl_tracked_dict_general_data = {}
gbl_tracked_dict_generator_specific = {} 
gbl_tracked_dict_run_variables = {}
gbl_tracked_dict_run_variables_ideal = {} 

# New - Initialize these as TrackedDict instances
gbl_tracked_dict_json_file_data = TrackedDict()
gbl_tracked_loaded_dict_json_file_data = TrackedDict()

#=============================================
#Table Headers for Operating Costs Data Dicctionary
#=============================================
# Step 1a: Define the variables for the column headers
gbl_back_cast_opcosttbl_hdr_hour = 'hour'
gbl_back_cast_opcosttbl_hdr_year = 'year'
gbl_back_cast_opcosttbl_hdr_month = 'month'
gbl_back_cast_opcosttbl_hdr_starts = 'STARTS'
gbl_back_cast_opcosttbl_hdr_stops = 'STOPS'
gbl_back_cast_opcosttbl_hdr_startstatus = 'START_STATUS'
gbl_back_cast_opcosttbl_hdr_runhours = 'RUN_HOURS'# was isrunning and IS_RUNNING
gbl_back_cast_opcosttbl_hdr_currenthourstart = 'CURRENT_HOUR_START'
gbl_back_cast_opcosttbl_hdr_currenthourstop = 'CURRENT_HOUR_STOP'
gbl_back_cast_opcosttbl_hdr_previoushourstart = 'PREVIOUS_HOUR_START'
gbl_back_cast_opcosttbl_hdr_previoushourstop = 'PREVIOUS_HOUR_STOP'
gbl_back_cast_opcosttbl_hdr_uptimecount = 'UPTIME_COUNT'
gbl_back_cast_opcosttbl_hdr_downtimecount = 'DOWNTIME_COUNT'
gbl_back_cast_opcosttbl_hdr_contraintedrampup = 'CONSTRAINED_RAMP_UP'
gbl_back_cast_opcosttbl_hdr_constrainedrampdown = 'CONSTRAINED_RAMP_DOWN'
gbl_back_cast_opcosttbl_hdr_mwproduction = 'MW_PRODUCTION'
gbl_back_cast_opcosttbl_hdr_emissions = 'EMMISONS'
gbl_back_cast_opcosttbl_hdr_poolprice = 'POOL_PRICE'
gbl_back_cast_opcosttbl_hdr_natgasprice = 'NAT_GAS_PRICE'
gbl_back_cast_opcosttbl_hdr_natgascostmwh = 'NAT_GAS_COST_MWh'
gbl_back_cast_opcosttbl_hdr_natgascostdollars = 'NAT_GAS_COST_DOLLARS'
gbl_back_cast_opcosttbl_hdr_carbontax = 'CARBON_TAX'
gbl_back_cast_opcosttbl_hdr_varcost = 'VAR_COST'
gbl_back_cast_opcosttbl_hdr_startcosts = 'START_COST'
gbl_back_cast_opcosttbl_hdr_stscost = 'STS_COST'
gbl_back_cast_opcosttbl_hdr_fomcost = 'FOM_COST'
gbl_back_cast_opcosttbl_hdr_totalcostdollars = 'TOTAL_COST_DOLLARS'
gbl_back_cast_opcosttbl_hdr_receivedpoolprice = 'RECEIVED_POOL_PRICE'
gbl_back_cast_opcosttbl_hdr_operatingmargin = 'OPERATING_MARGIN'

# Step 1b: Pass variables to dictionary
gbl_opcosttbl_hdr_dict = {
    'gbl_back_cast_opcosttbl_hdr_hour': gbl_back_cast_opcosttbl_hdr_hour,
    'gbl_back_cast_opcosttbl_hdr_year': gbl_back_cast_opcosttbl_hdr_year,
    'gbl_back_cast_opcosttbl_hdr_month': gbl_back_cast_opcosttbl_hdr_month,
    'gbl_back_cast_opcosttbl_hdr_starts': gbl_back_cast_opcosttbl_hdr_starts,
    'gbl_back_cast_opcosttbl_hdr_stops': gbl_back_cast_opcosttbl_hdr_stops,
    'gbl_back_cast_opcosttbl_hdr_startstatus': gbl_back_cast_opcosttbl_hdr_startstatus,
    'gbl_back_cast_opcosttbl_hdr_runhours': gbl_back_cast_opcosttbl_hdr_runhours,
    'gbl_back_cast_opcosttbl_hdr_currenthourstart': gbl_back_cast_opcosttbl_hdr_currenthourstart,
    'gbl_back_cast_opcosttbl_hdr_currenthourstop': gbl_back_cast_opcosttbl_hdr_currenthourstop,
    'gbl_back_cast_opcosttbl_hdr_previoushourstart': gbl_back_cast_opcosttbl_hdr_previoushourstart,
    'gbl_back_cast_opcosttbl_hdr_previoushourstop': gbl_back_cast_opcosttbl_hdr_previoushourstop,
    'gbl_back_cast_opcosttbl_hdr_uptimecount': gbl_back_cast_opcosttbl_hdr_uptimecount,
    'gbl_back_cast_opcosttbl_hdr_downtimecount': gbl_back_cast_opcosttbl_hdr_downtimecount,
    'gbl_back_cast_opcosttbl_hdr_contraintedrampup': gbl_back_cast_opcosttbl_hdr_contraintedrampup,
    'gbl_back_cast_opcosttbl_hdr_constrainedrampdown': gbl_back_cast_opcosttbl_hdr_constrainedrampdown,
    'gbl_back_cast_opcosttbl_hdr_mwproduction': gbl_back_cast_opcosttbl_hdr_mwproduction,
    'gbl_back_cast_opcosttbl_hdr_emissions': gbl_back_cast_opcosttbl_hdr_emissions,
    'gbl_back_cast_opcosttbl_hdr_poolprice': gbl_back_cast_opcosttbl_hdr_poolprice,
    'gbl_back_cast_opcosttbl_hdr_natgasprice': gbl_back_cast_opcosttbl_hdr_natgasprice,
    'gbl_back_cast_opcosttbl_hdr_natgascostmwh': gbl_back_cast_opcosttbl_hdr_natgascostmwh,
    'gbl_back_cast_opcosttbl_hdr_natgascostdollars': gbl_back_cast_opcosttbl_hdr_natgascostdollars,
    'gbl_back_cast_opcosttbl_hdr_carbontax': gbl_back_cast_opcosttbl_hdr_carbontax,
    'gbl_back_cast_opcosttbl_hdr_varcost': gbl_back_cast_opcosttbl_hdr_varcost,
    'gbl_back_cast_opcosttbl_hdr_startcosts': gbl_back_cast_opcosttbl_hdr_startcosts,
    'gbl_back_cast_opcosttbl_hdr_stscost': gbl_back_cast_opcosttbl_hdr_stscost,
    'gbl_back_cast_opcosttbl_hdr_fomcost': gbl_back_cast_opcosttbl_hdr_fomcost,
    'gbl_back_cast_opcosttbl_hdr_totalcostdollars': gbl_back_cast_opcosttbl_hdr_totalcostdollars,
    'gbl_back_cast_opcosttbl_hdr_receivedpoolprice': gbl_back_cast_opcosttbl_hdr_receivedpoolprice,
    'gbl_back_cast_opcosttbl_hdr_operatingmargin': gbl_back_cast_opcosttbl_hdr_operatingmargin
}
# Step 1c: Pass variables to dictionary
gbl_opcosttbl_hdr_df = pd.DataFrame(columns=list(gbl_opcosttbl_hdr_dict.values()))

#column headers for annual_stats_data table
# Step 2a: Define the variables for the column headers
gbl_annual_stats_annualstattbl_hdr_startcost  ='START_COST',
gbl_annual_stats_annualstattbl_hdr_mwproduction  ='MW_PRODUCTION',
gbl_annual_stats_annualstattbl_hdr_capcaityfactor  ='CAPACITY_FACTOR',
gbl_annual_stats_annualstattbl_hdr_idealcapacityfactor  ='IDEAL_CAPACITY_FACTOR',
gbl_annual_stats_annualstattbl_hdr_capacityfactorefficiency  ='CAPACITY_FACTOR EFFICIENCY',
gbl_annual_stats_annualstattbl_hdr_runhours  ='RUN_HOURS',
gbl_annual_stats_annualstattbl_hdr_runrate  ='RUN_RATE',
gbl_annual_stats_annualstattbl_hdr_revenue  ='REVENUE',
gbl_annual_stats_annualstattbl_hdr_natgaspricegj  ='NAT_GAS_PRICE_GJ',
gbl_annual_stats_annualstattbl_hdr_natgascostdollars  ='NAT_GAS_COST_DOLLARS',
gbl_annual_stats_annualstattbl_hdr_natgascostmwh  ='NAT_GAS_COST_MWh',
gbl_annual_stats_annualstattbl_hdr_totalcostdollars   ='TOTAL_COST_DOLLARS',
gbl_annual_stats_annualstattbl_hdr_operatingmargin  ='OPERATING_MARGIN',
gbl_annual_stats_annualstattbl_hdr_receivedpoolprice  ='RECEIVED_POOL_PRICE',
gbl_annual_stats_annualstattbl_hdr_avgpoolprice  ='AVG_POOL_PRICE',
gbl_annual_stats_annualstattbl_hdr_receivedpoolpriceratiotospot  ='RECEIVED_POOL_PRICE_RATIO_TO_AVG_SPOT'

# Step 1b: Pass variables to dictionary
gbl_annualstattbl_hdr_dict = {
'gbl_annual_stats_annualstattbl_hdr_startcost'  : gbl_annual_stats_annualstattbl_hdr_startcost,
'gbl_annual_stats_annualstattbl_hdr_mwproduction'  : gbl_annual_stats_annualstattbl_hdr_mwproduction,
'gbl_annual_stats_annualstattbl_hdr_capcaityfactor'  : gbl_annual_stats_annualstattbl_hdr_capcaityfactor,
'gbl_annual_stats_annualstattbl_hdr_idealcapacityfactor'  : gbl_annual_stats_annualstattbl_hdr_idealcapacityfactor,
'gbl_annual_stats_annualstattbl_hdr_capacityfactorefficiency'  : gbl_annual_stats_annualstattbl_hdr_capacityfactorefficiency,
'gbl_annual_stats_annualstattbl_hdr_runhours'  : gbl_annual_stats_annualstattbl_hdr_runhours,
'gbl_annual_stats_annualstattbl_hdr_runrate'  : gbl_annual_stats_annualstattbl_hdr_runrate,
'gbl_annual_stats_annualstattbl_hdr_revenue'  : gbl_annual_stats_annualstattbl_hdr_revenue,
'gbl_annual_stats_annualstattbl_hdr_natgaspricegj'  : gbl_annual_stats_annualstattbl_hdr_natgaspricegj,
'gbl_annual_stats_annualstattbl_hdr_natgascostdollars'  : gbl_annual_stats_annualstattbl_hdr_natgascostdollars,
'gbl_annual_stats_annualstattbl_hdr_natgascostmwh'  : gbl_annual_stats_annualstattbl_hdr_natgascostmwh,
'gbl_annual_stats_annualstattbl_hdr_totalcostdollars'   : gbl_annual_stats_annualstattbl_hdr_totalcostdollars,
'gbl_annual_stats_annualstattbl_hdr_operatingmargin'  : gbl_annual_stats_annualstattbl_hdr_operatingmargin,
'gbl_annual_stats_annualstattbl_hdr_receivedpoolprice'  : gbl_annual_stats_annualstattbl_hdr_receivedpoolprice,
'gbl_annual_stats_annualstattbl_hdr_avgpoolprice'  : gbl_annual_stats_annualstattbl_hdr_avgpoolprice,
'gbl_annual_stats_annualstattbl_hdr_receivedpoolpriceratiotospot'  : gbl_annual_stats_annualstattbl_hdr_receivedpoolpriceratiotospot
}

gbl_annualstattbl_hdr_df = pd.DataFrame(columns=list(gbl_annualstattbl_hdr_dict .values()))

#=============================================
# LCOE Analysis
#=============================================
gbl_tracked_dict_json_file_data_path = None

#Set-up Generator Assumption Dictionary
gbl_lcoe_data_by_generator = {}
gbl_lcoe_total_by_generator = {}
gbl_gas_fired_peaker = None #!!!
gbl_generation_sources = None
gbl_power_generation_dict = {} #!!!


# =============================================
# HELPER FUNCTIONS
# =============================================
def remove_folder_contents2(folder):
    """Remove contents of a folder"""
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                remove_folder_contents2(file_path)
                os.rmdir(file_path)
        except Exception as e:
            print(e)

def create_path_2(input_dir, filename, subfolder_name=''):
    """Create path - now uses platform_config"""
    if subfolder_name:
        return str(platform_config.get_input_file_path(filename, subfolder_name))
    else:
        return os.path.normpath(os.path.join(input_dir, filename))

def read_from_csv_input_folder_2(filename, subfolder_name=''):
    """Read CSV file using platform-aware paths"""
    # Use platform_config to get the correct path
    file_path = platform_config.get_input_file_path(filename, subfolder_name)
    
    print(f"Looking for file at: {file_path}")
    
    if not file_path.exists():
        print(f"Error: The file '{filename}' does not exist at {file_path}")
        return None
    
    try:
        df = pd.read_csv(str(file_path), low_memory=False)
        print(f"✓ Successfully loaded {filename} from {subfolder_name or 'input folder'}")
        print(f"  Columns: {list(df.columns)}")
        return df
        
    except PermissionError:
        print(f"✗ Permission denied: Cannot read {file_path}")
        if platform_config.is_linux:
            try:
                os.chmod(str(file_path), 0o644)
                df = pd.read_csv(str(file_path), low_memory=False)
                print(f"✓ Fixed permissions and loaded file successfully")
                return df
            except:
                print(f"✗ Could not fix permissions")
                return None
        return None
        
    except Exception as e:
        print(f"✗ Error reading file: {e}")
        return None

# =============================================
# SETUP FUNCTIONS
# =============================================
def setup_global_paths():
    """Set up all global path variables using platform_config"""
    from library.initializer import init_base_input_directory, init_base_output_directory
    
    global gbl_csv_output_path, gbl_input_path, gbl_excel_template_path
    global gbl_image_data_path, gbl_historic_data_path, gbl_processed_historic_data_path
    global gbl_json_file_path_full, gbl_json_file_path_loaded, gbl_input_forecast_data_path
    global gbl_input_data_path_str, gbl_output_data_path_str
    global gbl_json_folder_path, gbl_input_forecast_data_path_str
    
    # Use paths from initializer (which now uses platform_config)
    gbl_input_data_path_str = init_base_input_directory
    gbl_output_data_path_str = init_base_output_directory
    
    # Build all paths using platform_config
    #gbl_csv_output_path = str(platform_config.get_output_file_path('', gbl_csv_folder_name_str).parent)
    gbl_csv_output_path = str(platform_config.get_output_file_path('', gbl_csv_folder_name_str))
    print(f"gbl_csv_output_path: {gbl_csv_output_path}")
    gbl_input_path = gbl_input_data_path_str
    #gbl_image_data_path = str(platform_config.get_output_file_path('', gbl_image_folder_name_str).parent)
    gbl_image_data_path = str(platform_config.get_output_file_path('', gbl_image_folder_name_str))
    gbl_historic_data_path = str(platform_config.get_input_file_path(gbl_historical_data_filename_str))
    #gbl_processed_historic_data_path = str(platform_config.get_output_file_path('', gbl_processed_historical_folder_name_str).parent)
    gbl_processed_historic_data_path = str(platform_config.get_output_file_path('', gbl_processed_historical_folder_name_str))
    gbl_json_folder_path = str(platform_config.get_path('json_data'))
    gbl_json_file_path_full = str(platform_config.get_output_file_path(gbl_full_file_data_name_str, gbl_json_folder_name_str))
    gbl_json_file_path_loaded = str(platform_config.get_output_file_path(gbl_loaded_file_data_name_str, gbl_json_folder_name_str))
    
    # Template path
    gbl_excel_template_path = str(platform_config.get_path('templates') / gbl_simulation_summary_tmplt_filename)
    
    # Forecast data paths
    gbl_input_forecast_data_path_str = str(platform_config.get_path('market_forecast'))
    gbl_input_forecast_data_path = gbl_input_forecast_data_path_str
    
    # Create all necessary directories
    directories_to_create = [
        gbl_csv_output_path,
        gbl_image_data_path,
        gbl_processed_historic_data_path,
        gbl_json_folder_path,
        gbl_temp_path_str
    ]
    
    for dir_path in directories_to_create:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    print(f"Global paths initialized:")
    print(f"  Input path: {gbl_input_data_path_str}")
    print(f"  Output path: {gbl_output_data_path_str}")
    print(f"  Platform: {platform_config.platform}")
    
    return

def setup_global_variables():
    """Setup global variables including power generation dictionary"""
    global gbl_power_generation_dict
    global gbl_tracked_powergen_dict
    global gbl_json_existing_powergen_folder_path_str
    global gbl_tracked_dict_time_variables 
    global gbl_tracked_dict_general_data 
    global gbl_tracked_dict_generator_specific 
    global gbl_tracked_dict_run_variables 
    global gbl_tracked_dict_run_variables_ideal 
    global gbl_json_file_data_dict 
    global gbl_json_loaded_file_data_dict
    global gbl_gas_fired_peaker
    global gbl_generation_sources

    print("setup_global_variables called")
    print(f"Running on platform: {platform_config.platform}")

    # Step 12: ENBRIDGE DATA
    gbl_enb_ab_station_consumption = read_from_csv_input_folder_2(
        'Power Consumption Consolidated D1&2.csv', 
        'ENB_Load'
    )
    print(f" gbl_enb_ab_station_consumption: {gbl_enb_ab_station_consumption}")

    # Step 13: Power Generation LCOE Inputs and Backcasting runs
    
    # Define gbl_power_generation_dict
    gbl_power_generation_dict = {
        "generation_sources": {
            "gas_fired_peaker_recip": {
                #------------------
                #technical
                #------------------
                "heat_rate": 8.71,  # GJ/MWh
                "plant_capacity_mw_gross": 5,  # MW
                "plant_capacity_mw_net": 5,  # MW
                "target_capacity_factor": 0.23,  # %
                "target_annual_production_mwh": 5 * 8760 * 0.23,  # MWh
                "min_down_time" : 1, # hrs
                "down_time_count" : 1, #frequency
                "min_up_time" : 1, # hrs
                "up_time_count" : 0, #frequency
                #------------------
                # Capital Costs
                #------------------
                "capital_cost_per_kw": 2152,  # $/kW
                "capital_cost_mm_dollars": 2152 * 5 / 1000,  # MM dollars
                #------------------
                # Operating Costs
                #------------------
                #................... 
                # Fuel Costs
                #................... 
                "target_nat_gas_price": 2.00,  # $/GJ
                #................... 
                # Variable O&M
                #................... 
                "vom_mwh": 11.92,  # $/MWh
                #................... 
                # Fixed O&M
                #................... 
                "fixed_operating_costs_fixed": 25 + 5,  # $/kW-year
                "fixed_operating_costs_mwh": 20 * 5 * 1000 / (5 * 8760 * 0.23),  # $/MWh
                "run_hour_maintenance_target" : 60000, #hrs
                "land_cost_per_acre": 1000,  # $/acre
                "number_acres": 10,
                "land_costs": 1000 * 10,  # $
                "ins_prop_tax": 2,  # $/kW-year
                #................... 
                # Start-up Costs
                #................... 
                #"start_up_cost" : 0, # $/start 
                "start_up_cost": {
                    'cold_start': {'cold_start_determination_hrs': 48, 'cold_ramp_up_time': 3, 'fuel_consumed_gj_mw' : 10*0, 'nonfuel_cost_dollar_start': 25000 * 0 + 2000, 'fixed_cost_recovery_dollar_start': 7000 * 0, 'emissions_tCO2e_start': 100},
                    'warm_start': {'warm_start_determination_hrs': 24, 'warm_ramp_up_time': 2, 'fuel_consumed_gj_mw': 6.65*0, 'nonfuel_cost_dollar_start': 16000 * 0 + 2000, 'fixed_cost_recovery_dollar_start': 5000 * 0, 'emissions_tCO2e_start': 70},
                    'hot_start': {'hot_start_determination_hrs': 8, 'hot_ramp_up_time': 1, 'fuel_consumed_gj_mw': 3.900*0, 'nonfuel_cost_dollar_start': 9000 * 0 + 2000, 'fixed_cost_recovery_dollar_start': 2000 * 0, 'emissions_tCO2e_start': 40},
                    'none_start': (0, 0, 0, 0, 0, 0)
                },
                #.................... 
                # Emission Costs
                #.................... 
                "carbon_costs_per_tCO2e": 130.55,  # $/tCO2e
                "emissions_intensity": 0.47,  # tonnes of CO2e per MWh for simple cycle
                "co2_reduction_target": 0.37, #tonnes of CO2e per MWh
                "env_costs_per_tCO2e": 0, #Caluclated in routine
                #.................... 
                # Transmission Costs
                #.................... 
                "sts_percentage": 0,  # %
                #------------------
                # Capital Recovery
                #------------------
                "term": 30,  # years
                "Ke": 0.10,  # %
                "Kd": 0.05,  # %
                "tax_rate": 0.25,  # %
                "equity_percent": 0.40,  # %
                "debt_percent": 0.60,  # %
                "annual_index_rate": 0.02,  # 2%
                "cf_limit": 0.35,  # 35% capacity factor limit
                #------------------
                #Investment Tax Credit Calculations,
                #------------------
                'eligibility_for_us_can_itc' : True,
                'itc_tax_credit_percent' : 0, # %
                #------------------
                #Production Tax Credit Calculations
                #------------------
                'eligibility_for_ptc' : False,
                'pc_term_yrs' : 10, # years
                'tax_credit_per_MWh_firstyear' : 0.00, #$/MWh
                #------------------
                #CCUS
                #------------------
                'lcoe_carbon_capture_capital' : 0
            },
            "gas_fired_peaker_aero": {
                #-------------------
                #technical
                #-------------------
                "heat_rate": 9.63,  # GJ/MWh
                "plant_capacity_mw_gross": 5,  # MW
                "plant_capacity_mw_net": 5,  # MW
                "target_capacity_factor": 0.23,  # %
                "target_annual_production_mwh": 5 * 8760 * 0.23,  # MWh
                "min_down_time" : 1, # hrs
                "down_time_count" : 1, #frequency
                "min_up_time" : 1, # hrs
                "up_time_count" : 0, #frequency
                #-------------------
                # Capital Costs
                #-------------------
                "capital_cost_per_kw": 1700,  # $/kW
                "capital_cost_mm_dollars": 1700 * 5 / 1000,  # MM dollars
                #-------------------
                # Operating Costs
                #-------------------
                #................... 
                # Fuel Costs
                #..................
                "target_nat_gas_price": 2.00,  # $/GJ
                #................... 
                # Variable O&M
                #................... 
                "vom_mwh": 6.73,  # $/MWh
                #................... 
                # Fixed O&M
                #...................
                "fixed_operating_costs_fixed": 24 + 5 ,  # $/kW-year
                "fixed_operating_costs_mwh": 24 * 5 * 1000 / (5 * 8760 * 0.23),  # $/MWh
                "run_hour_maintenance_target" : 60000, #hrs
                "land_cost_per_acre": 1000,  # $/acre
                "number_acres": 10,
                "land_costs": 1000 * 10,  # $
                "ins_prop_tax": 2,  # $/kW-year
                #................... 
                # Start-up Costs
                #................... 
                #"start_up_cost" : 0, # $/start 
                "start_up_cost": {
                    'cold_start': {'cold_start_determination_hrs': 48, 'cold_ramp_up_time': 3, 'fuel_consumed_gj_mw' : 10, 'nonfuel_cost_dollar_start': 25000*0+2000, 'fixed_cost_recovery_dollar_start': 7000*0, 'emissions_tCO2e_start': 100},
                    'warm_start': {'warm_start_determination_hrs': 24, 'warm_ramp_up_time': 2, 'fuel_consumed_gj_mw': 6.65, 'nonfuel_cost_dollar_start': 16000*0+2000, 'fixed_cost_recovery_dollar_start': 5000*0, 'emissions_tCO2e_start': 70},
                    'hot_start': {'hot_start_determination_hrs': 0, 'hot_ramp_up_time': 1, 'fuel_consumed_gj_mw': 3.900, 'nonfuel_cost_dollar_start': 9000*0+2000, 'fixed_cost_recovery_dollar_start': 2000*0, 'emissions_tCO2e_start': 40},
                    'none_start': (0, 0, 0, 0, 0, 0)
                },
                #.................... 
                # Emission Costs
                #.................... 
                "carbon_costs_per_tCO2e": 130.55,  # $/tCO2e
                "emissions_intensity": 0.47,  # tonnes of CO2e per MWh for simple cycle
                "co2_reduction_target": 0.37, #tonnes of CO2e per MWh
                "env_costs_per_tCO2e": 0, #Caluclated in routine
                #.................... 
                # Transmission Costs
                #....................
                "sts_percentage": 0,  # %
                # Capital Recovery
                "term": 30,  # years
                "Ke": 0.10,  # %
                "Kd": 0.05,  # %
                "tax_rate": 0.25,  # %
                "equity_percent": 0.40,  # %
                "debt_percent": 0.60,  # %
                "annual_index_rate": 0.02,  # 2%
                "cf_limit": 0.35,  # 35% capacity factor limit
                #-------------------
                #Investment Tax Credit Calculations,
                #-------------------
                'eligibility_for_us_can_itc' : True,
                'itc_tax_credit_percent' : 0, # %
                #-------------------
                #Production Tax Credit Calculations
                #-------------------
                'eligibility_for_ptc' : False,
                'pc_term_yrs' : 10, # years
                'tax_credit_per_MWh_firstyear' : 0.00, #$/MWh
                #-------------------
                #CCUS
                #-------------------
                'lcoe_carbon_capture_capital' : 0
            },
            "gas_fired_peaker_frame": {
                #-------------------
                #technical
                #-------------------
                "heat_rate": 10.45,  # GJ/MWh
                "plant_capacity_mw_gross": 5,  # MW
                "plant_capacity_mw_net": 5,  # MW
                "target_capacity_factor": 0.23,  # %
                "target_annual_production_mwh": 5 * 8760 * 0.23,  # MWh
                "min_down_time" : 1, # hrs
                "down_time_count" : 1, #frequency
                "min_up_time" : 1, # hrs
                "up_time_count" : 0, #frequency
                #-------------------
                # Capital Costs
                #-------------------
                "capital_cost_per_kw": 1800,  # $/kW
                "capital_cost_mm_dollars": 1800 * 5 / 1000,  # MM dollars
                #-------------------
                # Operating Costs
                #-------------------
                #................... 
                # Fuel Costs
                #................... 
                "target_nat_gas_price": 2.00,  # $/GJ
                #................... 
                # Variable O&M
                #................... 
                "vom_mwh": 6.45,  # $/MWh
                #................... 
                # Fixed O&M
                #................... 
                "fixed_operating_costs_fixed": 10 * 0 + 40,  # $/kW-year
                "fixed_operating_costs_mwh": 10 * 5 * 1000 / (5 * 8760 * 0.23),  # $/MWh
                "run_hour_maintenance_target" : 60000, #hrs
                "land_cost_per_acre": 1000,  # $/acre
                "number_acres": 10,
                "land_costs": 1000 * 10,  # $
                "ins_prop_tax": 2,  # $/kW-year
                #................... 
                # Start-up Costs
                #................... 
                #"start_up_cost" : 0, # $/start 
                "start_up_cost": {
                    'cold_start': {'cold_start_determination_hrs': 48, 'cold_ramp_up_time': 3, 'fuel_consumed_gj_mw' : 10, 'nonfuel_cost_dollar_start': 25000*0+2000, 'fixed_cost_recovery_dollar_start': 7000*0, 'emissions_tCO2e_start': 100},
                    'warm_start': {'warm_start_determination_hrs': 24, 'warm_ramp_up_time': 2, 'fuel_consumed_gj_mw': 6.65, 'nonfuel_cost_dollar_start': 16000*0+2000, 'fixed_cost_recovery_dollar_start': 5000*0, 'emissions_tCO2e_start': 70},
                    'hot_start': {'hot_start_determination_hrs': 0, 'hot_ramp_up_time': 1, 'fuel_consumed_gj_mw': 3.900, 'nonfuel_cost_dollar_start': 9000*0+2000, 'fixed_cost_recovery_dollar_start': 2000*0, 'emissions_tCO2e_start': 40},
                    'none_start': (0, 0, 0, 0, 0, 0)
                },
                #.................... 
                # Emission Costs
                #.................... 
                "carbon_costs_per_tCO2e": 130.55,  # $/tCO2e
                "emissions_intensity": 0.47,  # tonnes of CO2e per MWh for simple cycle
                "co2_reduction_target": 0.37, #tonnes of CO2e per MWh
                "env_costs_per_tCO2e": 0, #Caluclated in routine
                #.................... 
                # Transmission Costs
                #....................
                "sts_percentage": 0,  # %
                #-------------------
                # Capital Recovery
                #-------------------
                "term": 30,  # years
                "Ke": 0.10,  # %
                "Kd": 0.05,  # %
                "tax_rate": 0.25,  # %
                "equity_percent": 0.40,  # %
                "debt_percent": 0.60,  # %
                "annual_index_rate": 0.02,  # 2%
                "cf_limit": 0.35,  # 35% capacity factor limit
                #-------------------
                #Investment Tax Credit Calculations,
                #-------------------
                'eligibility_for_us_can_itc' : True,
                'itc_tax_credit_percent' : 0, # %
                #-------------------
                #Production Tax Credit Calculations
                #-------------------
                'eligibility_for_ptc' : False,
                'pc_term_yrs' : 10, # years
                'tax_credit_per_MWh_firstyear' : 0.00, #$/MWh
                #-------------------
                #CCUS
                #-------------------
                'lcoe_carbon_capture_capital' : 0
            },
            "combined_cycle_gas_turbine": {
                #-------------------
                #technical
                #-------------------
                "heat_rate": 6.9,  # GJ/MWh
                "plant_capacity_mw_gross": 5,  # MW
                "plant_capacity_mw_net": 5,  # MW
                "target_capacity_factor": 0.6,  # %
                "target_annual_production_mwh": 5 * 8760 * 0.6,  # MWh
                "min_down_time" : 2, # hrs
                "down_time_count" : 1, #frequency
                "min_up_time" : 4, # hrs
                "up_time_count" : 0, #frequency
                #-------------------
                # Capital Costs
                #-------------------
                "capital_cost_per_kw": 2100,  # $/kW
                "capital_cost_mm_dollars": 2100 * 5 / 1000,  # MM dollars
                #-------------------
                # Operating Costs
                #-------------------
                #................... 
                # Fuel Costs
                #................... 
                "target_nat_gas_price": 2.00,  # $/GJ
                #................... 
                # Variable O&M
                #................... 
                "vom_mwh": 3,  # $/MWh
                #................... 
                # Fixed O&M
                #................... 
                "fixed_operating_costs_fixed": 24,  # $/kW-year
                "fixed_operating_costs_mwh": 24 * 5 * 1000 / (5 * 8760 * 0.23),  # $/MWh
                "run_hour_maintenance_target" : 60000, #hrs
                "land_cost_per_acre": 1000,  # $/acre
                "number_acres": 10,
                "land_costs": 1000 * 10,  # $
                "ins_prop_tax": 2,  # $/kW-year
                #................... 
                # Start-up Costs
                #...................
                #"start_up_cost" : 0, # $/start 
                "start_up_cost": {
                    'cold_start': {'cold_start_determination_hrs': 72, 'cold_ramp_up_time': 3, 'fuel_consumed_gj_mw' : 15.0, 'nonfuel_cost_dollar_start': 42000*0+2000, 'fixed_cost_recovery_dollar_start': 10000*0, 'emissions_tCO2e_start': 200},
                    'warm_start': {'warm_start_determination_hrs': 48, 'warm_ramp_up_time': 2, 'fuel_consumed_gj_mw': 10.0, 'nonfuel_cost_dollar_start': 30000*0+2000, 'fixed_cost_recovery_dollar_start': 6500*0, 'emissions_tCO2e_start': 135},
                    'hot_start': {'hot_start_determination_hrs': 24, 'hot_ramp_up_time': 1, 'fuel_consumed_gj_mw': 6.00, 'nonfuel_cost_dollar_start': 18000*0+2000, 'fixed_cost_recovery_dollar_start': 3000*0, 'emissions_tCO2e_start': 70},
                    'none_start': (0, 0, 0, 0, 0, 0)
                },
                #.................... 
                # Emission Costs
                #...................
                "carbon_costs_per_tCO2e": 130.55,  # $/tCO2e
                "emissions_intensity": 0.47,  # tonnes of CO2e per MWh for simple cycle
                "co2_reduction_target": 0.37, #tonnes of CO2e per MWh
                "env_costs_per_tCO2e": 0, #Caluclated in routine
                #.................... 
                # Transmission Costs
                #....................
                "sts_percentage": 0,  # %
                #-------------------
                # Capital Recovery
                #-------------------
                "term": 30,  # years
                "Ke": 0.10,  # %
                "Kd": 0.05,  # %
                "tax_rate": 0.25,  # %
                "equity_percent": 0.40,  # %
                "debt_percent": 0.60,  # %
                "annual_index_rate": 0.02,  # 2%
                "cf_limit": 0.35,  # 35% capacity factor limit
                #-------------------
                #Investment Tax Credit Calculations,
                #-------------------
                'eligibility_for_us_can_itc' : True,
                'itc_tax_credit_percent' : 0, # %
                #-------------------
                #Production Tax Credit Calculations
                #-------------------
                'eligibility_for_ptc' : False,
                'pc_term_yrs' : 10, # years
                'tax_credit_per_MWh_firstyear' : 0.00, #$/MWh
                #-------------------
                #CCUS
                #-------------------
                'lcoe_carbon_capture_capital' : 0
            }
        }
    }

    print(f" gbl_json_power_generation_path: {gbl_json_power_generation_path}")

    # Create classes instance of TrackedDict class object
    # LCOE Variables use for LCOE analysis
    gbl_tracked_powergen_dict = TrackedDict(gbl_power_generation_dict)
    print(type(gbl_tracked_powergen_dict['generation_sources']))
    
    # Dispatch variables used for the backcasting runs
    gbl_tracked_dict_time_variables = TrackedDict(glb_time_variable_dict)
    gbl_tracked_dict_general_data = TrackedDict(gbl_general_data_variable_dict) 
    gbl_tracked_dict_generator_specific = TrackedDict(gbl_generator_specific_variable_dict)
    gbl_tracked_dict_run_variables = TrackedDict(gbl_run_variable_dict)
    gbl_tracked_dict_run_variables_ideal = TrackedDict(gbl_run_variable_dict_ideal)

    return


# =============================================
# HELPER FUNCTIONS FOR PATH ACCESS
# =============================================
def get_forecast_data_path(provider, filename):
    """
    Get the path for a forecast data file.
    
    Args:
        provider: Provider name (e.g., 'edc', 'similan')
        filename: Name of the file
    
    Returns:
        Path object for the forecast file
    """
    return platform_config.get_input_file_path(
        filename,
        f'market_forecast_data_by_provider/{provider}'
    )

def get_output_path(output_type, filename, subfolder=None):
    """
    Get the path for an output file.
    
    Args:
        output_type: Type of output ('csv', 'excel', 'image', 'json')
        filename: Name of the file
        subfolder: Optional subfolder within the output type
    
    Returns:
        Path object for the output file
    """
    type_map = {
        'csv': gbl_csv_folder_name_str,
        'excel': gbl_excel_folder_name_str,
        'image': gbl_image_folder_name_str,
        'json': gbl_json_folder_name_str,
        'temp': 'temp_data'
    }
    
    base_folder = type_map.get(output_type, output_type)
    if subfolder:
        full_subfolder = f"{base_folder}/{subfolder}"
    else:
        full_subfolder = base_folder
    
    return platform_config.get_output_file_path(filename, full_subfolder)

# =============================================
# REMAINING GLOBALS (unchanged)
# =============================================
# [Rest of your globals remain the same - carbon tax dicts, table headers, etc.]

############################################################
############################################################
############################################################
# moved up top
# from library.config import runpipe_all_flags_true
# from library.class_objects.other_classes.classes import TrackedDict

# import os
# import pandas as pd
# import json


# moved up top
# gbl_dateMPT_label_natural_gas = "DATE_BEGIN_LOCAL"
# gbl_revised_date_col_gbl_dateMST_label_natural_gas = "DateTime"
# gbl_pool_price_primary_data_col = 'pool_price'
# gbl_natgas_primary_data_col = 'NAT_GAS_PRICE'

# =============================================
# PATH VARIABLES (now platform-aware)
# =============================================
# moved up toip
# gbl_gbase_output_path = r'C:\Users\kaczanor\OneDrive - Enbridge Inc\Documents\Python\EDC Hourly Capacity Factor Q2 2024'
# gbl_json_existing_powergen_folder_path_str = r'C:\Users\kaczanor\OneDrive - Enbridge Inc\Documents\Python\EDC Hourly Capacity Factor Q2 2024\outputs\json_data'
# gbl_temp_path_str = r'C:\Users\kaczanor\OneDrive - Enbridge Inc\Documents\Python\EDC Hourly Capacity Factor Q2 2024\outputs\temp_data'

#moved up top
# Data columns
# gbl_pool_price_primary_data_col = 'pool_price'
# gbl_natgas_primary_data_col = 'NAT_GAS_PRICE'

# # DataFrames loaded from files
# gbl_hist_processed_price_data = pd.read_csv(r'C:\Users\kaczanor\OneDrive - Enbridge Inc\Documents\Python\EDC Hourly Capacity Factor Q2 2024\inputs\AB_Historical_Prices\merged_pool_price_data_2000_to_2024.csv')
# gbl_hist_processed_nat_gas_price = pd.read_csv(r'C:\Users\kaczanor\OneDrive - Enbridge Inc\Documents\Python\EDC Hourly Capacity Factor Q2 2024\inputs\AB_Historical_Prices\merged_nat_gas_price_data_2000_to_2024.csv')
#----------------------------------------

# Moved up top
#Folder Names
# gbl_csv_folder_name_str = 'csv_data'
# gbl_image_folder_name_str = 'image_data'
# gbl_json_folder_name_str = 'json_data'
# gbl_excel_folder_name_str = 'excel_data'
# gbl_excel_template_folder_name = 'template_excel_output_files'
# gbl_processed_historical_folder_name_str = 'Processed Historical Data'
# gbl_forecaster_folder_name_str = 'market_forecast_data_by_provider'
#----------------------------------------
# File Names
# gbl_simulation_summary_tmplt_filename = 'simluation_annual_monthly_output_file_template.xlsx'
# gbl_historical_data_filename_str = 'AB_Historical_Prices/merged_pool_price_data_2000_to_2024.csv'
# #gbl_active_price_run_file_name_str = 'file_data.json'
# gbl_full_file_data_name_str = 'full_file_data.json'
# gbl_loaded_file_data_name_str = 'loaded_file_data.json'
# gbl_output_file_name_str = 'output_data.json'
# gbl_power_gen_dict_filename = 'power_generation_dict.json'
# gbl_p50_output_file_var = 'p50_hourly_spot_electricity.csv'
# gbl_power_p_template_filename = '_hourly_spot_electricity.csv'
# gbl_natgas_p_template_filename = '_hourly_spot_natural_gas.csv'
# gbl_updated_power_generation_json_file_str = 'updated_power_generation_dict.json'


# =============================================
# DYNAMIC PATH VARIABLES
# =============================================
# old
#gbl_json_power_generation_path = os.path.join(gbl_json_existing_powergen_folder_path_str, gbl_updated_power_generation_json_file_str)

# # These will be set dynamically using platform_config
# gbl_json_power_generation_path = os.path.join(
#     gbl_json_existing_powergen_folder_path_str, 
#     gbl_updated_power_generation_json_file_str
# )
# gbl_csv_input_path = None


# Set during run time
# gbl_frcst_output_excel_file_path = None
# gbl_frcst_input_excel_file_path = None
# gbl_frcst_output_csv_file_path = None


#----------------------------------------
# Create global data frames
#gbl_hist_processed_price_data
#gbl_hist_processed_price_data = pd.DataFrame()

#gbl_hist_processed_nat_gas_price
#gbl_hist_processed_nat_gas_price = pd.DataFrame()

#----------------------------------------
# Create dictionary shortcut paths to be used later
# when looping through the json file that holds all 
# file meta data for inputs and outputs
# gbl_input_general_data = None
# gbl_price_forecast = None
# gbl_output_general_data = None
# gbl_processed_price_forecast = None
# gbl_output_template = None

#----------------------------------------

# #Carbon Tax
# gbl_carbon_tax_annual_dict = {
#     '2000': 0,
#     '2001': 0,
#     '2002': 0,
#     '2003': 0,
#     '2004': 0,
#     '2005': 0,
#     '2006': 0,
#     '2007': 15,
#     '2008': 15,
#     '2009': 15,
#     '2010': 15,
#     '2011': 15,
#     '2012': 15,
#     '2013': 15,
#     '2014': 15,
#     '2015': 15,
#     '2016': 20,
#     '2017': 30,
#     '2018': 30,
#     '2019': 30,
#     '2020': 30,
#     '2021': 40,
#     '2022': 50,
#     '2023': 65,
#     '2024': 80,
#     '2025': 95,
#     '2026': 110,
#     '2027': 125,
#     '2028': 140,
#     '2029': 155,
#     '2030': 170,
#     '2031': 170,
#     '2032': 170,
#     '2033': 170,
#     '2034': 170,
#     '2035': 170,
#     '2036': 170,
#     '2037': 170,
#     '2038': 170,
#     '2039': 170,
#     '2040': 170
# }

# # Electricity Grid Displacement Factors (EGDF)
# # Electricity Grid Displacement Factor (tCO2e/MWh)
# # Electricity grid displacement with renewable generation
# gbl_edgf_renewable_generation_dict = {
#     '2024': 0.49,
#     '2025': 0.46,
#     '2026': 0.43,
#     '2027': 0.401,
#     '2028': 0.371,
#     '2029': 0.341,
#     '2030': 0
# }

# gbl_increased_onsite_grid_electricity_use_dict = {
#     '2024': 0.523,
#     '2025': 0.491,
#     '2026': 0.459,
#     '2027': 0.427,
#     '2028': 0.395,
#     '2029': 0.363,
#     '2030': 0
# }
# gbl_reduction_in_grid_electricity_usage_dict = {
#     '2024': 0.523,
#     '2025': 0.491,
#     '2026': 0.459,
#     '2027': 0.427,
#     '2028': 0.395,
#     '2029': 0.363,
#     '2030': 0
# }
# gbl_distributed_renewable_displacement_at_pointofuse_dict = {
#     '2024': 0.523,
#     '2025': 0.491,
#     '2026': 0.459,
#     '2027': 0.427,
#     '2028': 0.395,
#     '2029': 0.363,
#     '2030': 0
# }

# # Updated TIER High-Performance Benchmarks (CO2e tonnes per benchmark unit)
# gbl_electrictity_hpb_dict = {
#     #Units = MWh
#     '2022' : 0.37,
#     '2023' : 0.3626,
#     '2024' : 0.3552,
#     '2025' : 0.3478,
#     '2026' : 0.3404,
#     '2027' : 0.333,
#     '2028' : 0.3256,
#     '2029' : 0.3182,
#     '2030' : 0.3108
# }
# gbl_electrictity_hpb_dict = {
#     #Units = tonne
#     '2022' : 9.068,
#     '2023' : 8.993,
#     '2024' : 8.919,
#     '2025' : 8.844,
#     '2026' : 8.769,
#     '2027' : 8.694,
#     '2028' : 8.619,
#     '2029' : 8.545,
#     '2030' : 8.47
# }
# gbl_industrial_heat_hpb_dict = {
#     #Units = GJ
#     '2022' : 0.0630,
#     '2023' : 0.0617,
#     '2024' : 0.0605,
#     '2025' : 0.0592,
#     '2026' : 0.0580,
#     '2027' : 0.0567,
#     '2028' : 0.0554,
#     '2029' : 0.0542,
#     '2030' : 0.0529
# }

# '''
# Clean Electricity Regulations10 (CER)
# The regulations limit the emissions intensity of fossil fired generation to 30 tCO2e per GWh, or 0.030 tCO2e/MWh,
# which is 92% lower than the current TIER benchmark of 0.363 tCO2e/MWh. The regulations apply to units that
# meet the following criteria (covered units):
# ~ Uses any amount of fossil fuels to generate electricity,
# ~ Has a capacity of 25 MW or greater, and
# ~ Is grid connected to a NERC-regulated electricity system.
# The standard applies to all covered units starting January 1, 2035, with exceptions for units commissioned
# between 2015 and 2024, which must meet the standard 20 years after their commissioning date. Covered units
# include cogeneration units that are net exporters of electricity (in Alberta, cogeneration exports an average of
# 1,600 MW to the system). The regulations also include a peaking unit exemption, which allows for unabated
# operation for up to 450 hours per year.
# '''
# gbl_cer_factor_dict = {
#     '2030' : 0.030,
# }
#----------------------------------------
#########################################
# Step XX:
# # LCOE Analysis
# #########################################
# gbl_tracked_dict_json_file_data_path = None

# #Set-up Generator Assumption Dictionary
# gbl_lcoe_data_by_generator = {}
# gbl_lcoe_total_by_generator = {}
# gbl_gas_fired_peaker = None #!!!
# gbl_generation_sources = None
# gbl_power_generation_dict = {} #!!!

# Dictionaries transferred to tracked dictionary class
#if runpipe_all_flags_true:
# gbl_power_generation_dict = {}
# glb_time_variable_dict = {}
# gbl_general_data_variable_dict = {}
# gbl_generator_specific_variable_dict = {}
# gbl_run_variable_dict = {}
# gbl_run_variable_dict_ideal = {}

# Define Tracked Dictionary Class Instances
# Only create these two dictionaries if you are running the 
# the entire code on the run_pipeline.py. Otherwise these do not needs
# to be created again as the code in run_pipline is only running snippets of
# code that uses the saved version of these dictionaries in the outputs/json folder.
# That data is loaded back into the gbl_general_data_variable_dict and gbl_generator_specific_variable_dict
# at start-up.  When doing that you need to bypass these intilization statements for those 
# 2x dictionaries as this code runs first in all scenarios and these initlization statements
# will clear the 2x dictionaries 

# gbl_tracked_powergen_dict = {}
# gbl_tracked_dict_json_file_data = {}
# gbl_tracked_loaded_dict_json_file_data = {}
# gbl_tracked_dict_time_variables = {}
# gbl_tracked_dict_general_data = {}
# gbl_tracked_dict_generator_specific = {} 
# gbl_tracked_dict_run_variables = {}
# gbl_tracked_dict_run_variables_ideal = {} 

#New 
# Note the other class instances are set up in the setup_global_variables below
#if runpipe_all_flags_true:
# gbl_tracked_dict_json_file_data = TrackedDict()
# gbl_tracked_loaded_dict_json_file_data = TrackedDict()

# #Table Headers for Operating Costs Data Dicctionary
# # Step 1a: Define the variables for the column headers

# gbl_back_cast_opcosttbl_hdr_hour = 'hour'
# gbl_back_cast_opcosttbl_hdr_year = 'year'
# gbl_back_cast_opcosttbl_hdr_month = 'month'
# gbl_back_cast_opcosttbl_hdr_starts = 'STARTS'
# gbl_back_cast_opcosttbl_hdr_stops = 'STOPS'
# gbl_back_cast_opcosttbl_hdr_startstatus = 'START_STATUS'
# gbl_back_cast_opcosttbl_hdr_runhours = 'RUN_HOURS'# was isrunning and IS_RUNNING
# gbl_back_cast_opcosttbl_hdr_currenthourstart = 'CURRENT_HOUR_START'
# gbl_back_cast_opcosttbl_hdr_currenthourstop = 'CURRENT_HOUR_STOP'
# gbl_back_cast_opcosttbl_hdr_previoushourstart = 'PREVIOUS_HOUR_START'
# gbl_back_cast_opcosttbl_hdr_previoushourstop = 'PREVIOUS_HOUR_STOP'
# gbl_back_cast_opcosttbl_hdr_uptimecount = 'UPTIME_COUNT'
# gbl_back_cast_opcosttbl_hdr_downtimecount = 'DOWNTIME_COUNT'
# gbl_back_cast_opcosttbl_hdr_contraintedrampup = 'CONSTRAINED_RAMP_UP'
# gbl_back_cast_opcosttbl_hdr_constrainedrampdown = 'CONSTRAINED_RAMP_DOWN'
# gbl_back_cast_opcosttbl_hdr_mwproduction = 'MW_PRODUCTION'
# gbl_back_cast_opcosttbl_hdr_emissions = 'EMMISONS'
# gbl_back_cast_opcosttbl_hdr_poolprice = 'POOL_PRICE'
# gbl_back_cast_opcosttbl_hdr_natgasprice = 'NAT_GAS_PRICE'
# gbl_back_cast_opcosttbl_hdr_natgascostmwh = 'NAT_GAS_COST_MWh'
# gbl_back_cast_opcosttbl_hdr_natgascostdollars = 'NAT_GAS_COST_DOLLARS'
# gbl_back_cast_opcosttbl_hdr_carbontax = 'CARBON_TAX'
# gbl_back_cast_opcosttbl_hdr_varcost = 'VAR_COST'
# gbl_back_cast_opcosttbl_hdr_startcosts = 'START_COST'
# gbl_back_cast_opcosttbl_hdr_stscost = 'STS_COST'
# gbl_back_cast_opcosttbl_hdr_fomcost = 'FOM_COST'
# gbl_back_cast_opcosttbl_hdr_totalcostdollars = 'TOTAL_COST_DOLLARS'
# gbl_back_cast_opcosttbl_hdr_receivedpoolprice = 'RECEIVED_POOL_PRICE'
# gbl_back_cast_opcosttbl_hdr_operatingmargin = 'OPERATING_MARGIN'

# # Step 1b: Pass variables to dictionary
# gbl_opcosttbl_hdr_dict = {
#     'gbl_back_cast_opcosttbl_hdr_hour': gbl_back_cast_opcosttbl_hdr_hour,
#     'gbl_back_cast_opcosttbl_hdr_year': gbl_back_cast_opcosttbl_hdr_year,
#     'gbl_back_cast_opcosttbl_hdr_month': gbl_back_cast_opcosttbl_hdr_month,
#     'gbl_back_cast_opcosttbl_hdr_starts': gbl_back_cast_opcosttbl_hdr_starts,
#     'gbl_back_cast_opcosttbl_hdr_stops': gbl_back_cast_opcosttbl_hdr_stops,
#     'gbl_back_cast_opcosttbl_hdr_startstatus': gbl_back_cast_opcosttbl_hdr_startstatus,
#     'gbl_back_cast_opcosttbl_hdr_runhours': gbl_back_cast_opcosttbl_hdr_runhours,
#     'gbl_back_cast_opcosttbl_hdr_currenthourstart': gbl_back_cast_opcosttbl_hdr_currenthourstart,
#     'gbl_back_cast_opcosttbl_hdr_currenthourstop': gbl_back_cast_opcosttbl_hdr_currenthourstop,
#     'gbl_back_cast_opcosttbl_hdr_previoushourstart': gbl_back_cast_opcosttbl_hdr_previoushourstart,
#     'gbl_back_cast_opcosttbl_hdr_previoushourstop': gbl_back_cast_opcosttbl_hdr_previoushourstop,
#     'gbl_back_cast_opcosttbl_hdr_uptimecount': gbl_back_cast_opcosttbl_hdr_uptimecount,
#     'gbl_back_cast_opcosttbl_hdr_downtimecount': gbl_back_cast_opcosttbl_hdr_downtimecount,
#     'gbl_back_cast_opcosttbl_hdr_contraintedrampup': gbl_back_cast_opcosttbl_hdr_contraintedrampup,
#     'gbl_back_cast_opcosttbl_hdr_constrainedrampdown': gbl_back_cast_opcosttbl_hdr_constrainedrampdown,
#     'gbl_back_cast_opcosttbl_hdr_mwproduction': gbl_back_cast_opcosttbl_hdr_mwproduction,
#     'gbl_back_cast_opcosttbl_hdr_emissions': gbl_back_cast_opcosttbl_hdr_emissions,
#     'gbl_back_cast_opcosttbl_hdr_poolprice': gbl_back_cast_opcosttbl_hdr_poolprice,
#     'gbl_back_cast_opcosttbl_hdr_natgasprice': gbl_back_cast_opcosttbl_hdr_natgasprice,
#     'gbl_back_cast_opcosttbl_hdr_natgascostmwh': gbl_back_cast_opcosttbl_hdr_natgascostmwh,
#     'gbl_back_cast_opcosttbl_hdr_natgascostdollars': gbl_back_cast_opcosttbl_hdr_natgascostdollars,
#     'gbl_back_cast_opcosttbl_hdr_carbontax': gbl_back_cast_opcosttbl_hdr_carbontax,
#     'gbl_back_cast_opcosttbl_hdr_varcost': gbl_back_cast_opcosttbl_hdr_varcost,
#     'gbl_back_cast_opcosttbl_hdr_startcosts': gbl_back_cast_opcosttbl_hdr_startcosts,
#     'gbl_back_cast_opcosttbl_hdr_stscost': gbl_back_cast_opcosttbl_hdr_stscost,
#     'gbl_back_cast_opcosttbl_hdr_fomcost': gbl_back_cast_opcosttbl_hdr_fomcost,
#     'gbl_back_cast_opcosttbl_hdr_totalcostdollars': gbl_back_cast_opcosttbl_hdr_totalcostdollars,
#     'gbl_back_cast_opcosttbl_hdr_receivedpoolprice': gbl_back_cast_opcosttbl_hdr_receivedpoolprice,
#     'gbl_back_cast_opcosttbl_hdr_operatingmargin': gbl_back_cast_opcosttbl_hdr_operatingmargin
# }
# # Step 1c: Pass variables to dictionary
# gbl_opcosttbl_hdr_df = pd.DataFrame(columns=list(gbl_opcosttbl_hdr_dict.values()))

# #column headers for annual_stats_data table
# # Step 2a: Define the variables for the column headers
# gbl_annual_stats_annualstattbl_hdr_startcost  ='START_COST',
# gbl_annual_stats_annualstattbl_hdr_mwproduction  ='MW_PRODUCTION',
# gbl_annual_stats_annualstattbl_hdr_capcaityfactor  ='CAPACITY_FACTOR',
# gbl_annual_stats_annualstattbl_hdr_idealcapacityfactor  ='IDEAL_CAPACITY_FACTOR',
# gbl_annual_stats_annualstattbl_hdr_capacityfactorefficiency  ='CAPACITY_FACTOR EFFICIENCY',
# gbl_annual_stats_annualstattbl_hdr_runhours  ='RUN_HOURS',
# gbl_annual_stats_annualstattbl_hdr_runrate  ='RUN_RATE',
# gbl_annual_stats_annualstattbl_hdr_revenue  ='REVENUE',
# gbl_annual_stats_annualstattbl_hdr_natgaspricegj  ='NAT_GAS_PRICE_GJ',
# gbl_annual_stats_annualstattbl_hdr_natgascostdollars  ='NAT_GAS_COST_DOLLARS',
# gbl_annual_stats_annualstattbl_hdr_natgascostmwh  ='NAT_GAS_COST_MWh',
# gbl_annual_stats_annualstattbl_hdr_totalcostdollars   ='TOTAL_COST_DOLLARS',
# gbl_annual_stats_annualstattbl_hdr_operatingmargin  ='OPERATING_MARGIN',
# gbl_annual_stats_annualstattbl_hdr_receivedpoolprice  ='RECEIVED_POOL_PRICE',
# gbl_annual_stats_annualstattbl_hdr_avgpoolprice  ='AVG_POOL_PRICE',
# gbl_annual_stats_annualstattbl_hdr_receivedpoolpriceratiotospot  ='RECEIVED_POOL_PRICE_RATIO_TO_AVG_SPOT'

# # Step 1b: Pass variables to dictionary
# gbl_annualstattbl_hdr_dict = {
# 'gbl_annual_stats_annualstattbl_hdr_startcost'  : gbl_annual_stats_annualstattbl_hdr_startcost,
# 'gbl_annual_stats_annualstattbl_hdr_mwproduction'  : gbl_annual_stats_annualstattbl_hdr_mwproduction,
# 'gbl_annual_stats_annualstattbl_hdr_capcaityfactor'  : gbl_annual_stats_annualstattbl_hdr_capcaityfactor,
# 'gbl_annual_stats_annualstattbl_hdr_idealcapacityfactor'  : gbl_annual_stats_annualstattbl_hdr_idealcapacityfactor,
# 'gbl_annual_stats_annualstattbl_hdr_capacityfactorefficiency'  : gbl_annual_stats_annualstattbl_hdr_capacityfactorefficiency,
# 'gbl_annual_stats_annualstattbl_hdr_runhours'  : gbl_annual_stats_annualstattbl_hdr_runhours,
# 'gbl_annual_stats_annualstattbl_hdr_runrate'  : gbl_annual_stats_annualstattbl_hdr_runrate,
# 'gbl_annual_stats_annualstattbl_hdr_revenue'  : gbl_annual_stats_annualstattbl_hdr_revenue,
# 'gbl_annual_stats_annualstattbl_hdr_natgaspricegj'  : gbl_annual_stats_annualstattbl_hdr_natgaspricegj,
# 'gbl_annual_stats_annualstattbl_hdr_natgascostdollars'  : gbl_annual_stats_annualstattbl_hdr_natgascostdollars,
# 'gbl_annual_stats_annualstattbl_hdr_natgascostmwh'  : gbl_annual_stats_annualstattbl_hdr_natgascostmwh,
# 'gbl_annual_stats_annualstattbl_hdr_totalcostdollars'   : gbl_annual_stats_annualstattbl_hdr_totalcostdollars,
# 'gbl_annual_stats_annualstattbl_hdr_operatingmargin'  : gbl_annual_stats_annualstattbl_hdr_operatingmargin,
# 'gbl_annual_stats_annualstattbl_hdr_receivedpoolprice'  : gbl_annual_stats_annualstattbl_hdr_receivedpoolprice,
# 'gbl_annual_stats_annualstattbl_hdr_avgpoolprice'  : gbl_annual_stats_annualstattbl_hdr_avgpoolprice,
# 'gbl_annual_stats_annualstattbl_hdr_receivedpoolpriceratiotospot'  : gbl_annual_stats_annualstattbl_hdr_receivedpoolpriceratiotospot
# }

# Step 2c: Pass variables to dictionary
# gbl_annualstattbl_hdr_df = pd.DataFrame(columns=list(gbl_annualstattbl_hdr_dict .values()))
  
  
#Deleted     
# #########################################
# # Functions()
# #########################################

# def remove_folder_contents2(folder):
#     for the_file in os.listdir(folder):
#         file_path = os.path.join(folder, the_file)
#         try:
#             if os.path.isfile(file_path):
#                 os.unlink(file_path)
#             elif os.path.isdir(file_path):
#                 remove_folder_contents2(file_path)
#                 os.rmdir(file_path)
#         except Exception as e:
#             print(e)
# def create_path_2(input_dir, filename, subfolder_name=''):
#     full_path = os.path.normpath(os.path.join(input_dir, subfolder_name, filename))
#     return full_path

# def read_from_csv_input_folder_2(filename, subfolder_name=''):
#     from library.initializer import init_ide_option, init_base_input_directory
    
#     if init_ide_option == 'vscode':
#         full_path = create_path_2(init_base_input_directory, filename, subfolder_name)
#     elif init_ide_option == 'jupyter_notebook':
#         # Additional code for Jupyter environment
#         pass
#     elif init_ide_option == 'kaggle':
#         full_path = create_path_2(init_base_input_directory, filename, subfolder_name)

#     print(f" full_path: {full_path}")

#     # Somtime this function generates an permission error. This is a workaround to handle that error.
#     if not os.path.exists(full_path):
#         print("Error: The file does not exist at the specified path.")
#         return None

#     try:
#         if os.path.exists(full_path):

#             os.chmod(full_path, 0o666)
#             print("File permissions modified successfully!")
#             df = pd.read_csv(full_path, low_memory=False)
#             print(f"{filename} loaded from input folder...")
#             print(f" df.columns: {df.columns}")
#             return df
#         else:
#             print("File not found:", full_path)
#     except PermissionError:
#         print("Permission denied: You don't have the necessary permissions to change the permissions of this file.")
#         return None

# moved uo top
# def setup_global_paths():
#     from  library.initializer import init_base_input_directory, init_base_output_directory
#     global gbl_csv_output_path, gbl_input_path, gbl_excel_template_path
#     global gbl_image_data_path, gbl_historic_data_path, gbl_processed_historic_data_path, gbl_json_file_path_full, gbl_json_file_path_loaded, gbl_input_forecast_data_path
#     global gbl_input_data_path_str, gbl_output_data_path_str
#     global gbl_csv_folder_name_str, gbl_image_folder_name_str, gbl_historical_data_filename_str, gbl_processed_historical_folder_name_str, \
#         gbl_json_folder_name_str, gbl_full_file_data_name_str, gbl_loaded_file_data_name_str, gbl_forecaster_folder_name_str
#     #----------------------------------------

#     #Revised FilePaths
#     gbl_input_data_path_str =  init_base_input_directory
#     gbl_output_data_path_str = init_base_output_directory
    
#     gbl_csv_output_path = os.path.join(gbl_output_data_path_str, gbl_csv_folder_name_str)
#     gbl_input_path = os.path.join(gbl_input_data_path_str)
    
#     gbl_image_data_path = os.path.join(gbl_output_data_path_str, gbl_image_folder_name_str)
#     gbl_historic_data_path = os.path.join(gbl_input_data_path_str, gbl_historical_data_filename_str)
    
#     gbl_processed_historic_data_path = os.path.join(gbl_output_data_path_str, gbl_processed_historical_folder_name_str)
#     gbl_json_folder_path = os.path.join(gbl_output_data_path_str, gbl_json_folder_name_str)
    
#     gbl_json_file_path_full = os.path.join(gbl_json_folder_path, gbl_full_file_data_name_str)
#     gbl_json_file_path_loaded = os.path.join(gbl_json_folder_path, gbl_loaded_file_data_name_str)

#     gbl_excel_template_path = os.path.join(gbl_gbase_output_path, gbl_excel_template_folder_name, gbl_simulation_summary_tmplt_filename )
    
#     gbl_input_forecast_data_path_str = os.path.join(gbl_input_path, gbl_forecaster_folder_name_str)
#     gbl_input_forecast_data_path = os.path.join(gbl_input_forecast_data_path_str)

#     print(f"Global input path: {gbl_input_data_path_str}")
#     print(f"Global output path: {gbl_output_data_path_str}")
#     return
# ###########################################
# def setup_global_variables():

#     global gbl_power_generation_dict
#     global gbl_tracked_powergen_dict
#     global gbl_json_existing_powergen_folder_path_str

#     global gbl_tracked_dict_time_variables 
#     global gbl_tracked_dict_general_data 
#     global gbl_tracked_dict_generator_specific 
#     global gbl_tracked_dict_run_variables 
#     global gbl_tracked_dict_run_variables_ideal 

#     global gbl_json_file_data_dict 
#     global gbl_json_loaded_file_data_dict

#     global gbl_gas_fired_peaker #!!!
#     global gbl_generation_sources

#     print("setup_global_variables called")

#      # Step 12: ENBRIDGE DATA
#     #______________________________________________________________________________
#     gbl_enb_ab_station_consumption = read_from_csv_input_folder_2('Power Consumption Consolidated D1&2.csv', 'ENB_Load')
#     print(f" gbl_enb_ab_station_consumption: {gbl_enb_ab_station_consumption}")

#     #_____________________________________________________________________________
#     # Step 13: Power Generation LCOE Inputs and Backcasting runs
    
#     # Delete the existing power generation json file
#     #path =  r'C:\Users\kaczanor\OneDrive - Enbridge Inc\Documents\Python\AB Electricity Sector Stats\input_data\power_generation_json_data'
#     #remove_folder_contents2(path)
#     #remove_folder_contents2(gbl_json_existing_powergen_folder_path)


#     # Save the generator input dictionary to a JSON file
#     # Set base value of cacpacity factor 

#     #if runpipe_all_flags_true:
#     # Define gbl_power_generation_dict
#     gbl_power_generation_dict = {
#         "generation_sources": {
#             "gas_fired_peaker_recip": {
#                 #------------------
#                 #technical
#                 #------------------
#                 "heat_rate": 8.71,  # GJ/MWh
#                 "plant_capacity_mw_gross": 5,  # MW
#                 "plant_capacity_mw_net": 5,  # MW
#                 "target_capacity_factor": 0.23,  # %
#                 "target_annual_production_mwh": 5 * 8760 * 0.23,  # MWh
#                 "min_down_time" : 1, # hrs
#                 "down_time_count" : 1, #frequency
#                 "min_up_time" : 1, # hrs
#                 "up_time_count" : 0, #frequency
#                 #------------------
#                 # Capital Costs
#                 #------------------
#                 "capital_cost_per_kw": 2152,  # $/kW
#                 "capital_cost_mm_dollars": 2152 * 5 / 1000,  # MM dollars
#                 #------------------
#                 # Operating Costs
#                 #------------------
#                 #................... 
#                 # Fuel Costs
#                 #................... 
#                 "target_nat_gas_price": 2.00,  # $/GJ
#                 #................... 
#                 # Variable O&M
#                 #................... 
#                 "vom_mwh": 11.92,  # $/MWh
#                 #................... 
#                 # Fixed O&M
#                 #................... 
#                 "fixed_operating_costs_fixed": 25 + 5,  # $/kW-year
#                 "fixed_operating_costs_mwh": 20 * 5 * 1000 / (5 * 8760 * 0.23),  # $/MWh
#                 "run_hour_maintenance_target" : 60000, #hrs
#                 "land_cost_per_acre": 1000,  # $/acre
#                 "number_acres": 10,
#                 "land_costs": 1000 * 10,  # $
#                 "ins_prop_tax": 2,  # $/kW-year
#                 #................... 
#                 # Start-up Costs
#                 #................... 
#                 #"start_up_cost" : 0, # $/start 
#                 "start_up_cost": {
#                     'cold_start': {'cold_start_determination_hrs': 48, 'cold_ramp_up_time': 3, 'fuel_consumed_gj_mw' : 10*0, 'nonfuel_cost_dollar_start': 25000 * 0 + 2000, 'fixed_cost_recovery_dollar_start': 7000 * 0, 'emissions_tCO2e_start': 100},
#                     'warm_start': {'warm_start_determination_hrs': 24, 'warm_ramp_up_time': 2, 'fuel_consumed_gj_mw': 6.65*0, 'nonfuel_cost_dollar_start': 16000 * 0 + 2000, 'fixed_cost_recovery_dollar_start': 5000 * 0, 'emissions_tCO2e_start': 70},
#                     'hot_start': {'hot_start_determination_hrs': 8, 'hot_ramp_up_time': 1, 'fuel_consumed_gj_mw': 3.900*0, 'nonfuel_cost_dollar_start': 9000 * 0 + 2000, 'fixed_cost_recovery_dollar_start': 2000 * 0, 'emissions_tCO2e_start': 40},
#                     'none_start': (0, 0, 0, 0, 0, 0)
#                 },
#                 #.................... 
#                 # Emission Costs
#                 #.................... 
#                 "carbon_costs_per_tCO2e": 130.55,  # $/tCO2e
#                 "emissions_intensity": 0.47,  # tonnes of CO2e per MWh for simple cycle
#                 "co2_reduction_target": 0.37, #tonnes of CO2e per MWh
#                 "env_costs_per_tCO2e": 0, #Caluclated in routine
#                 #.................... 
#                 # Transmission Costs
#                 #.................... 
#                 "sts_percentage": 0,  # %
#                 #------------------
#                 # Capital Recovery
#                 #------------------
#                 "term": 30,  # years
#                 "Ke": 0.10,  # %
#                 "Kd": 0.05,  # %
#                 "tax_rate": 0.25,  # %
#                 "equity_percent": 0.40,  # %
#                 "debt_percent": 0.60,  # %
#                 "annual_index_rate": 0.02,  # 2%
#                 "cf_limit": 0.35,  # 35% capacity factor limit
#                 #------------------
#                 #Investment Tax Credit Calculations,
#                 #------------------
#                 'eligibility_for_us_can_itc' : True,
#                 'itc_tax_credit_percent' : 0, # %
#                 #------------------
#                 #Production Tax Credit Calculations
#                 #------------------
#                 'eligibility_for_ptc' : False,
#                 'pc_term_yrs' : 10, # years
#                 'tax_credit_per_MWh_firstyear' : 0.00, #$/MWh
#                 #------------------
#                 #CCUS
#                 #------------------
#                 'lcoe_carbon_capture_capital' : 0
#             },
#             "gas_fired_peaker_aero": {
#                 #-------------------
#                 #technical
#                 #-------------------
#                 "heat_rate": 9.63,  # GJ/MWh
#                 "plant_capacity_mw_gross": 5,  # MW
#                 "plant_capacity_mw_net": 5,  # MW
#                 "target_capacity_factor": 0.23,  # %
#                 "target_annual_production_mwh": 5 * 8760 * 0.23,  # MWh
#                 "min_down_time" : 1, # hrs
#                 "down_time_count" : 1, #frequency
#                 "min_up_time" : 1, # hrs
#                 "up_time_count" : 0, #frequency
#                 #-------------------
#                 # Capital Costs
#                 #-------------------
#                 "capital_cost_per_kw": 1700,  # $/kW
#                 "capital_cost_mm_dollars": 1700 * 5 / 1000,  # MM dollars
#                 #-------------------
#                 # Operating Costs
#                 #-------------------
#                 #................... 
#                 # Fuel Costs
#                 #..................
#                 "target_nat_gas_price": 2.00,  # $/GJ
#                 #................... 
#                 # Variable O&M
#                 #................... 
#                 "vom_mwh": 6.73,  # $/MWh
#                 #................... 
#                 # Fixed O&M
#                 #...................
#                 "fixed_operating_costs_fixed": 24 + 5 ,  # $/kW-year
#                 "fixed_operating_costs_mwh": 24 * 5 * 1000 / (5 * 8760 * 0.23),  # $/MWh
#                 "run_hour_maintenance_target" : 60000, #hrs
#                 "land_cost_per_acre": 1000,  # $/acre
#                 "number_acres": 10,
#                 "land_costs": 1000 * 10,  # $
#                 "ins_prop_tax": 2,  # $/kW-year
#                 #................... 
#                 # Start-up Costs
#                 #................... 
#                 #"start_up_cost" : 0, # $/start 
#                 "start_up_cost": {
#                     'cold_start': {'cold_start_determination_hrs': 48, 'cold_ramp_up_time': 3, 'fuel_consumed_gj_mw' : 10, 'nonfuel_cost_dollar_start': 25000*0+2000, 'fixed_cost_recovery_dollar_start': 7000*0, 'emissions_tCO2e_start': 100},
#                     'warm_start': {'warm_start_determination_hrs': 24, 'warm_ramp_up_time': 2, 'fuel_consumed_gj_mw': 6.65, 'nonfuel_cost_dollar_start': 16000*0+2000, 'fixed_cost_recovery_dollar_start': 5000*0, 'emissions_tCO2e_start': 70},
#                     'hot_start': {'hot_start_determination_hrs': 0, 'hot_ramp_up_time': 1, 'fuel_consumed_gj_mw': 3.900, 'nonfuel_cost_dollar_start': 9000*0+2000, 'fixed_cost_recovery_dollar_start': 2000*0, 'emissions_tCO2e_start': 40},
#                     'none_start': (0, 0, 0, 0, 0, 0)
#                 },
#                 #.................... 
#                 # Emission Costs
#                 #.................... 
#                 "carbon_costs_per_tCO2e": 130.55,  # $/tCO2e
#                 "emissions_intensity": 0.47,  # tonnes of CO2e per MWh for simple cycle
#                 "co2_reduction_target": 0.37, #tonnes of CO2e per MWh
#                 "env_costs_per_tCO2e": 0, #Caluclated in routine
#                 #.................... 
#                 # Transmission Costs
#                 #....................
#                 "sts_percentage": 0,  # %
#                 # Capital Recovery
#                 "term": 30,  # years
#                 "Ke": 0.10,  # %
#                 "Kd": 0.05,  # %
#                 "tax_rate": 0.25,  # %
#                 "equity_percent": 0.40,  # %
#                 "debt_percent": 0.60,  # %
#                 "annual_index_rate": 0.02,  # 2%
#                 "cf_limit": 0.35,  # 35% capacity factor limit
#                 #-------------------
#                 #Investment Tax Credit Calculations,
#                 #-------------------
#                 'eligibility_for_us_can_itc' : True,
#                 'itc_tax_credit_percent' : 0, # %
#                 #-------------------
#                 #Production Tax Credit Calculations
#                 #-------------------
#                 'eligibility_for_ptc' : False,
#                 'pc_term_yrs' : 10, # years
#                 'tax_credit_per_MWh_firstyear' : 0.00, #$/MWh
#                 #-------------------
#                 #CCUS
#                 #-------------------
#                 'lcoe_carbon_capture_capital' : 0
#             },
#             "gas_fired_peaker_frame": {
#                 #-------------------
#                 #technical
#                 #-------------------
#                 "heat_rate": 10.45,  # GJ/MWh
#                 "plant_capacity_mw_gross": 5,  # MW
#                 "plant_capacity_mw_net": 5,  # MW
#                 "target_capacity_factor": 0.23,  # %
#                 "target_annual_production_mwh": 5 * 8760 * 0.23,  # MWh
#                 "min_down_time" : 1, # hrs
#                 "down_time_count" : 1, #frequency
#                 "min_up_time" : 1, # hrs
#                 "up_time_count" : 0, #frequency
#                 #-------------------
#                 # Capital Costs
#                 #-------------------
#                 "capital_cost_per_kw": 1800,  # $/kW
#                 "capital_cost_mm_dollars": 1800 * 5 / 1000,  # MM dollars
#                 #-------------------
#                 # Operating Costs
#                 #-------------------
#                 #................... 
#                 # Fuel Costs
#                 #................... 
#                 "target_nat_gas_price": 2.00,  # $/GJ
#                 #................... 
#                 # Variable O&M
#                 #................... 
#                 "vom_mwh": 6.45,  # $/MWh
#                 #................... 
#                 # Fixed O&M
#                 #................... 
#                 "fixed_operating_costs_fixed": 10 * 0 + 40,  # $/kW-year
#                 "fixed_operating_costs_mwh": 10 * 5 * 1000 / (5 * 8760 * 0.23),  # $/MWh
#                 "run_hour_maintenance_target" : 60000, #hrs
#                 "land_cost_per_acre": 1000,  # $/acre
#                 "number_acres": 10,
#                 "land_costs": 1000 * 10,  # $
#                 "ins_prop_tax": 2,  # $/kW-year
#                 #................... 
#                 # Start-up Costs
#                 #................... 
#                 #"start_up_cost" : 0, # $/start 
#                 "start_up_cost": {
#                     'cold_start': {'cold_start_determination_hrs': 48, 'cold_ramp_up_time': 3, 'fuel_consumed_gj_mw' : 10, 'nonfuel_cost_dollar_start': 25000*0+2000, 'fixed_cost_recovery_dollar_start': 7000*0, 'emissions_tCO2e_start': 100},
#                     'warm_start': {'warm_start_determination_hrs': 24, 'warm_ramp_up_time': 2, 'fuel_consumed_gj_mw': 6.65, 'nonfuel_cost_dollar_start': 16000*0+2000, 'fixed_cost_recovery_dollar_start': 5000*0, 'emissions_tCO2e_start': 70},
#                     'hot_start': {'hot_start_determination_hrs': 0, 'hot_ramp_up_time': 1, 'fuel_consumed_gj_mw': 3.900, 'nonfuel_cost_dollar_start': 9000*0+2000, 'fixed_cost_recovery_dollar_start': 2000*0, 'emissions_tCO2e_start': 40},
#                     'none_start': (0, 0, 0, 0, 0, 0)
#                 },
#                 #.................... 
#                 # Emission Costs
#                 #.................... 
#                 "carbon_costs_per_tCO2e": 130.55,  # $/tCO2e
#                 "emissions_intensity": 0.47,  # tonnes of CO2e per MWh for simple cycle
#                 "co2_reduction_target": 0.37, #tonnes of CO2e per MWh
#                 "env_costs_per_tCO2e": 0, #Caluclated in routine
#                 #.................... 
#                 # Transmission Costs
#                 #....................
#                 "sts_percentage": 0,  # %
#                 #-------------------
#                 # Capital Recovery
#                 #-------------------
#                 "term": 30,  # years
#                 "Ke": 0.10,  # %
#                 "Kd": 0.05,  # %
#                 "tax_rate": 0.25,  # %
#                 "equity_percent": 0.40,  # %
#                 "debt_percent": 0.60,  # %
#                 "annual_index_rate": 0.02,  # 2%
#                 "cf_limit": 0.35,  # 35% capacity factor limit
#                 #-------------------
#                 #Investment Tax Credit Calculations,
#                 #-------------------
#                 'eligibility_for_us_can_itc' : True,
#                 'itc_tax_credit_percent' : 0, # %
#                 #-------------------
#                 #Production Tax Credit Calculations
#                 #-------------------
#                 'eligibility_for_ptc' : False,
#                 'pc_term_yrs' : 10, # years
#                 'tax_credit_per_MWh_firstyear' : 0.00, #$/MWh
#                 #-------------------
#                 #CCUS
#                 #-------------------
#                 'lcoe_carbon_capture_capital' : 0
#             },
#             "combined_cycle_gas_turbine": {
#                 #-------------------
#                 #technical
#                 #-------------------
#                 "heat_rate": 6.9,  # GJ/MWh
#                 "plant_capacity_mw_gross": 5,  # MW
#                 "plant_capacity_mw_net": 5,  # MW
#                 "target_capacity_factor": 0.6,  # %
#                 "target_annual_production_mwh": 5 * 8760 * 0.6,  # MWh
#                 "min_down_time" : 2, # hrs
#                 "down_time_count" : 1, #frequency
#                 "min_up_time" : 4, # hrs
#                 "up_time_count" : 0, #frequency
#                 #-------------------
#                 # Capital Costs
#                 #-------------------
#                 "capital_cost_per_kw": 2100,  # $/kW
#                 "capital_cost_mm_dollars": 2100 * 5 / 1000,  # MM dollars
#                 #-------------------
#                 # Operating Costs
#                 #-------------------
#                 #................... 
#                 # Fuel Costs
#                 #................... 
#                 "target_nat_gas_price": 2.00,  # $/GJ
#                 #................... 
#                 # Variable O&M
#                 #................... 
#                 "vom_mwh": 3,  # $/MWh
#                 #................... 
#                 # Fixed O&M
#                 #................... 
#                 "fixed_operating_costs_fixed": 24,  # $/kW-year
#                 "fixed_operating_costs_mwh": 24 * 5 * 1000 / (5 * 8760 * 0.23),  # $/MWh
#                 "run_hour_maintenance_target" : 60000, #hrs
#                 "land_cost_per_acre": 1000,  # $/acre
#                 "number_acres": 10,
#                 "land_costs": 1000 * 10,  # $
#                 "ins_prop_tax": 2,  # $/kW-year
#                 #................... 
#                 # Start-up Costs
#                 #...................
#                 #"start_up_cost" : 0, # $/start 
#                 "start_up_cost": {
#                     'cold_start': {'cold_start_determination_hrs': 72, 'cold_ramp_up_time': 3, 'fuel_consumed_gj_mw' : 15.0, 'nonfuel_cost_dollar_start': 42000*0+2000, 'fixed_cost_recovery_dollar_start': 10000*0, 'emissions_tCO2e_start': 200},
#                     'warm_start': {'warm_start_determination_hrs': 48, 'warm_ramp_up_time': 2, 'fuel_consumed_gj_mw': 10.0, 'nonfuel_cost_dollar_start': 30000*0+2000, 'fixed_cost_recovery_dollar_start': 6500*0, 'emissions_tCO2e_start': 135},
#                     'hot_start': {'hot_start_determination_hrs': 24, 'hot_ramp_up_time': 1, 'fuel_consumed_gj_mw': 6.00, 'nonfuel_cost_dollar_start': 18000*0+2000, 'fixed_cost_recovery_dollar_start': 3000*0, 'emissions_tCO2e_start': 70},
#                     'none_start': (0, 0, 0, 0, 0, 0)
#                 },
#                 #.................... 
#                 # Emission Costs
#                 #...................
#                 "carbon_costs_per_tCO2e": 130.55,  # $/tCO2e
#                 "emissions_intensity": 0.47,  # tonnes of CO2e per MWh for simple cycle
#                 "co2_reduction_target": 0.37, #tonnes of CO2e per MWh
#                 "env_costs_per_tCO2e": 0, #Caluclated in routine
#                 #.................... 
#                 # Transmission Costs
#                 #....................
#                 "sts_percentage": 0,  # %
#                 #-------------------
#                 # Capital Recovery
#                 #-------------------
#                 "term": 30,  # years
#                 "Ke": 0.10,  # %
#                 "Kd": 0.05,  # %
#                 "tax_rate": 0.25,  # %
#                 "equity_percent": 0.40,  # %
#                 "debt_percent": 0.60,  # %
#                 "annual_index_rate": 0.02,  # 2%
#                 "cf_limit": 0.35,  # 35% capacity factor limit
#                 #-------------------
#                 #Investment Tax Credit Calculations,
#                 #-------------------
#                 'eligibility_for_us_can_itc' : True,
#                 'itc_tax_credit_percent' : 0, # %
#                 #-------------------
#                 #Production Tax Credit Calculations
#                 #-------------------
#                 'eligibility_for_ptc' : False,
#                 'pc_term_yrs' : 10, # years
#                 'tax_credit_per_MWh_firstyear' : 0.00, #$/MWh
#                 #-------------------
#                 #CCUS
#                 #-------------------
#                 'lcoe_carbon_capture_capital' : 0
#             }
#         }
#     }

#     print(f" gbl_json_power_generation_path: {gbl_json_power_generation_path}")

#     # Create classes instance of TrackedDict class object
#     # LCOE Variables use for LCOE analysios
#     gbl_tracked_powergen_dict = TrackedDict(gbl_power_generation_dict)
#     print(type(gbl_tracked_powergen_dict['generation_sources']))
        
    
#     # Dispatch variables used for the backcasting runs
#     gbl_tracked_dict_time_variables = TrackedDict(glb_time_variable_dict)

#     gbl_tracked_dict_general_data = TrackedDict(gbl_general_data_variable_dict) 

#     gbl_tracked_dict_generator_specific = TrackedDict(gbl_generator_specific_variable_dict)

#     gbl_tracked_dict_run_variables = TrackedDict(gbl_run_variable_dict)

#     gbl_tracked_dict_run_variables_ideal = TrackedDict(gbl_run_variable_dict_ideal)


#     return