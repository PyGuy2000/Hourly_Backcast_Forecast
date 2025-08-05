import os
import re
import json
import sys

# Add the root directory to the system path
current_path = os.path.dirname(os.path.abspath(__file__))
root_path = os.path.dirname(current_path)
sys.path.append(root_path)

from library import globals as gbl   
from library import initializer as init # this is an alias for initializer
from library.globals import setup_global_variables

from library.file_meta_data import create_file_from_string, create_forecast_metadata

def load_forecaster_config(config_path):
    with open(config_path, 'r') as f:
        lines = f.readlines()
        # json file can have certain sections commented out if you don't want to run them
        # but the comments need to be stripped out beforeloading
        # Remove comments
        json_str = ''.join(line for line in lines if not line.strip().startswith('//'))
        return json.loads(json_str)
        #return json.load(f)
    
def update_file_name(file_name):
    # Replace the first hyphen with an underscore
    updated_file_name = file_name.replace('-', '_', 1)
    return updated_file_name

def discover_files(base_path):
    forecaster_files = {}
    for forecaster_dir in os.listdir(base_path):
        forecaster_path = os.path.join(base_path, forecaster_dir)
        if os.path.isdir(forecaster_path):
            files = os.listdir(forecaster_path)
            forecaster_files[forecaster_dir] = [os.path.join(forecaster_path, f) for f in files if f.endswith('.xlsx')]
    return forecaster_files

def parse_file_name(file_path):
    file_name = os.path.basename(file_path)
    print(f" file_name: {file_name}")
    match = re.match(r'(Q\d-\d{4}) Hourly Data (\w+) Case\.xlsx', file_name)
    if match:

        # Replace the hyphen with an underscore in the quarter_year field
        quarter_year = match.group(1).replace('-', '_')

        return {
            "quarter_year": quarter_year,
            "data_type": match.group(2),
            "file_name": file_name
        }
    return None

def build_file_structure2(config):
    base_path = gbl.gbl_input_forecast_data_path
    forecaster_files = discover_files(base_path)
    
    # Initialize dictionaries
    output_file_attributes_dict = {}
    output_file_dict = {}
    
    forecaster_name_dict = {}
    input_filename_dict = {}
    forecast_years_dict = {}
    forecast_folder_dict = {}
    forecast_data_flag_dict = {}
    
    sto_seed_dict = {}
    dst_type_dict = {}
    forecaster_data_structure_dict ={}
    
    # Loop through files
    for forecaster, files in forecaster_files.items():
        forecaster_name_dict[forecaster] = forecaster
        sto_seed_dict[forecaster] = config[forecaster]['sto_seed']
        dst_type_dict[forecaster] = config[forecaster]['dst_type']
        forecaster_data_structure_dict[forecaster] = config[forecaster]['data_structure']

        for file_path in files:
            file_info = parse_file_name(file_path)
            if file_info:
                file_name = file_info['file_name']
                quarter_year = file_info['quarter_year']
                data_type = file_info['data_type']
                
                flag_name = f"{quarter_year}_{forecaster}_{data_type}_data_flag"
                
                # Initialize the flag dynamically, could be set based on more complex logic
                forecast_data_flag_dict[flag_name] = False  # Default or based on some condition

                # Update dictionaries
                forecast_data_flag_dict[flag_name] = False  # Default or based on some condition
                input_filename_dict[flag_name] = file_name
                forecast_years_dict[flag_name] = (int(quarter_year.split('_')[1]), int(quarter_year.split('_')[1]) + 14)
                forecast_folder_dict[flag_name] = f"{forecaster.upper()} {quarter_year} Forecast {data_type} Data"
    

    output_file_attributes_dict = {
        "consolidated_hourly": "",
        "hourly_electricity": "",
        "hourly_natural_gas": "",
        "hourly_market_heat_rate": "",
        "monthly_avg_electricity": "",
        "monthly_avg_natural_gas": "",
        "monthly_market_heat_rate": "",
        "annual_avg_electricity": "",
        "annual_avg_natural_gas": "",
        "annual_market_heat_rate": "",
        "annual_allhour_electricity_heatmap": "",
        "annual_offpeak_electricity_heatmap": "",
        "annual_onpeak_electricity_heatmap": "",
        "annual_heatmap_data_market_electricity": "",
        "annual_heatmap_data_market_naturalgas": "",
        "annual_market_heat_rate_std_avg_heatmap_data": "",
        "annual_generator_bid_output_file_var": "",
        "annual_cf_output_file_var": "",
        "annual_power_recievedratio_output_file_var": "",
        "annual_natgas_recievedratio_output_file_var": "",
        "monthly_generator_bid_output_file_var": "",
        "monthly_cf_output_file_var": "",
        "monthly_power_recievedratio_output_file_var": "",
        "monthly_natgas_recievedratio_output_file_var": "",
        "P10_hourly_spot_electricity": "",
        "P25_hourly_spot_electricity": "",
        "P50_hourly_spot_electricity": "",
        "P75_hourly_spot_electricity": "",
        "P90_hourly_spot_electricity": "",
        "top_hour_percentage_summary": "",
        "P10_hourly_spot_natural_gas": "",
        "P25_hourly_spot_natural_gas": "",
        "P50_hourly_spot_natural_gas": "",
        "P75_hourly_spot_natural_gas": "",
        "P90_hourly_spot_natural_gas": "",
        "combined_forecast_" : "",
        "combined_forecast_with_Top_Percent_Price": ""
    }

    # INPUT FILE ATTRIBUTES
    # Output File Names
    consolidated_hourly_filename_str = create_file_from_string(('consolidated_hourly', 'csv'))
    
    hourly_electricity_filename_str = create_file_from_string(('hourly_electricity', 'csv'))
    hourly_natural_gas_filename_str  = create_file_from_string(('hourly_natural_gas', 'csv'))
    hourly_market_heat_rate_filename_str  = create_file_from_string(('hourly_market_heat_rate', 'csv'))

    monthly_generator_bid_output_file_name_str  = create_file_from_string(('monthly_generator_bid_output', 'csv'))
    monthly_cf_output_file_name_str  = create_file_from_string(('monthly_cf_output', 'csv'))
    monthly_avg_electricity_filename_str  = create_file_from_string(('monthly_avg_electricity', 'csv'))
    monthly_avg_natural_gas_filename_str  = create_file_from_string(('monthly_avg_natural_gas', 'csv'))
    monthly_market_heat_rate_filename_str  = create_file_from_string(('monthly_market_heat_rate', 'csv'))
    monthly_power_recievedratio_output_file_name_str  = create_file_from_string(('monthly_power_recievedratio_output', 'csv'))
    monthly_natgas_recievedratio_output_file_name_str  = create_file_from_string(('monthly_natgas_recievedratio_output', 'csv'))

    annual_generator_bid_output_file_name_str  = create_file_from_string(('annual_generator_bid_output', 'csv'))
    annual_cf_output_file_name_str  = create_file_from_string(('annual_cf_output', 'csv'))
    annual_power_recievedratio_output_file_name_str  = create_file_from_string(('annual_power_recievedratio_output', 'csv'))
    annual_natgas_recievedratio_output_file_name_str  = create_file_from_string(('annual_natgas_recievedratio_output', 'csv'))
    annual_avg_electricity_filename_str  = create_file_from_string(('annual_avg_electricity', 'csv'))
    annual_avg_natural_gas_filename_str  = create_file_from_string(('annual_avg_natural_gas', 'csv'))
    annual_market_heat_rate_filename_str  = create_file_from_string(('annual_market_heat_rate', 'csv'))
    annual_allhour_electricity_heatmap_filename_str  = create_file_from_string(('annual_allhour_electricity_heatmap', 'csv'))
    annual_offpeak_electricity_heatmap_filename_str  = create_file_from_string(('annual_offpeak_electricity_heatmap', 'csv'))
    annual_onpeak_electricity_heatmap_filename_str  = create_file_from_string(('annual_onpeak_electricity_heatmap', 'csv'))
    annual_heatmap_data_market_electricity_filename_str  = create_file_from_string(('annual_heatmap_data_market_electricity', 'csv'))
    annual_heatmap_data_market_naturalgas_filename_str  = create_file_from_string(('annual_heatmap_data_market_naturalgas', 'csv'))
    annual_market_heat_rate_std_avg_heatmap_data_filename_str  = create_file_from_string(('annual_market_heat_rate_std_avg_heatmap_data', 'csv'))
    top_hour_percentage_summary_filename_str = create_file_from_string(('top_hour_percentage_summary', 'csv'))
    combined_forecast_filename_str = "combined_forecast_{}_with_{}.csv" #template file
    combined_forecast_with_Top_Percent_Price_filename_str = "combined_forecast_{}_with_{}.csv" #template file

    #Create Output File Name Dictionary

    output_file_dict['consolidated_hourly_filename_str'] = consolidated_hourly_filename_str
    output_file_dict['hourly_electricity_filename_str'] = hourly_electricity_filename_str 
    output_file_dict['hourly_natural_gas_filename_str'] =hourly_natural_gas_filename_str 
    output_file_dict['hourly_market_heat_rate_filename_str'] =hourly_market_heat_rate_filename_str
    output_file_dict['monthly_avg_electricity_filename_str'] =monthly_avg_electricity_filename_str
    output_file_dict['monthly_avg_natural_gas_filename_str'] =monthly_avg_natural_gas_filename_str
    output_file_dict['monthly_market_heat_rate_filename_str'] =monthly_market_heat_rate_filename_str
    output_file_dict['annual_avg_electricity_filename_str'] =annual_avg_electricity_filename_str 
    output_file_dict['annual_avg_natural_gas_filename_str'] =annual_avg_natural_gas_filename_str 
    output_file_dict['annual_market_heat_rate_filename_str'] =annual_market_heat_rate_filename_str
    output_file_dict['annual_allhour_electricity_heatmap_filename_str'] =annual_allhour_electricity_heatmap_filename_str
    output_file_dict['annual_offpeak_electricity_heatmap_filename_str'] =annual_offpeak_electricity_heatmap_filename_str
    output_file_dict['annual_onpeak_electricity_heatmap_filename_str'] =annual_onpeak_electricity_heatmap_filename_str
    output_file_dict['annual_heatmap_data_market_electricity_filename_str'] =annual_heatmap_data_market_electricity_filename_str
    output_file_dict['annual_heatmap_data_market_naturalgas_filename_str'] =annual_heatmap_data_market_naturalgas_filename_str
    output_file_dict['annual_market_heat_rate_std_avg_heatmap_data_filename_str'] =annual_market_heat_rate_std_avg_heatmap_data_filename_str

    output_file_dict['annual_generator_bid_output_file_var'] = annual_generator_bid_output_file_name_str
    output_file_dict['annual_cf_output_file_var'] = annual_cf_output_file_name_str
    output_file_dict['annual_power_recievedratio_output_file_var'] = annual_power_recievedratio_output_file_name_str
    output_file_dict['annual_natgas_recievedratio_output_file_var'] = annual_natgas_recievedratio_output_file_name_str
    output_file_dict['monthly_generator_bid_output_file_var'] = monthly_generator_bid_output_file_name_str
    output_file_dict['monthly_cf_output_file_var'] = monthly_cf_output_file_name_str
    output_file_dict['monthly_power_recievedratio_output_file_var'] = monthly_power_recievedratio_output_file_name_str
    output_file_dict['monthly_natgas_recievedratio_output_file_var'] = monthly_natgas_recievedratio_output_file_name_str
    
    output_file_dict['top_hour_percentage_summary_filename_str'] = top_hour_percentage_summary_filename_str
    output_file_dict['combined_forecast_filename_str'] = combined_forecast_filename_str
    output_file_dict['combined_forecast_with_Top_Percent_Price_filename_str'] = combined_forecast_with_Top_Percent_Price_filename_str 

    print("build_file_structure called")
    return forecast_data_flag_dict, forecaster_name_dict, input_filename_dict, \
            forecast_years_dict, forecast_folder_dict, sto_seed_dict, dst_type_dict, \
                forecaster_data_structure_dict, output_file_dict, output_file_attributes_dict
############################
def main():
    # Dynamically build the file structure
    init.initialize_global_variables('vscode')

    # Setup global variables that depend on initialization and file paths from the previous step
    # to load input files
    gbl.setup_global_paths()
    gbl.setup_global_variables()


    #Moved this form above as it needs to occur AFTER the global variable are set
    from library.file_meta_data import (
        create_forecast_metadata,
        create_final_dictionary,
        add_gen_list_post_loop
    )

    foreaster_config_path = r'C:\Users\kaczanor\OneDrive - Enbridge Inc\Documents\Python\EDC Hourly Capacity Factor Q2 2024\forecaster_config.json'
    forecaster_config = load_forecaster_config(foreaster_config_path)
    forecast_data_flag_dict, forecaster_name_dict, input_filename_dict, \
            forecast_years_dict, forecast_folder_dict, sto_seed_dict, dst_type_dict, \
                forecaster_data_structure_dict, output_file_dict, output_file_attributes_dict = build_file_structure2(forecaster_config)

    create_forecast_metadata(
                                forecaster_name_dict,
                                sto_seed_dict,
                                dst_type_dict,
                                forecaster_data_structure_dict,
                                input_filename_dict, 
                                forecast_years_dict, 
                                forecast_folder_dict,
                                forecast_data_flag_dict,
                                output_file_dict,
                                output_file_attributes_dict,
                            )

    print("gbl.gbl_tracked_dict_json_file_data", type(gbl.gbl_tracked_dict_json_file_data))
    print("Printing gbl.gbl_tracked_dict_json_file_data data..")
    print(json.dumps(gbl.gbl_tracked_dict_json_file_data, indent=4))

if __name__ == "__main__":
    main()