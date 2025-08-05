from library.class_objects.forecast_files.forecast_scenario import ForecastScenario
from library import globals as gbl
import re

def create_file_from_string(filename_tuple):
    filename_str, extension = filename_tuple

    # Define allowed extensions
    allowed_extensions = ['csv', 'xlsx', 'png', 'json']
    if extension not in allowed_extensions:
        raise ValueError(f"Extension {extension} is not supported. Allowed extensions are {allowed_extensions}.")

    # Check for problematic characters in the filename
    # the pattern r'^[/w/-]+$' is intended to match alphanumeric characters, underscores, and hyphens, but it doesn't 
    # work due to the incorrect escape sequence. The forward slash (/) and backslash (\) are incorrect her
    # if not re.match(r'^[/w/-]+$', filename_str):
    # The correct pattern should use \w to match word characters (alphanumeric plus underscore) and allow for hyphens (-). 
    # Here's the corrected pattern and function:
    if not re.match(r'^[\w-]+$', filename_str):
        raise ValueError("Filename contains problematic characters. Only alphanumeric characters, underscores, and hyphens are allowed.")

    # Create the filename with the extension
    full_filename = f"{filename_str}.{extension}"
    
    # Write to the file (for demonstration purposes, we'll just create an empty file)
    # with open(full_filename, 'w') as file:
    #     file.write("")

    return full_filename

#def create_output_file_dicts():
def create_output_file_dicts(list_of_output_file_structures=None):
    """Create output file dictionaries"""
    # If you have the structure from YAML, use it
    if list_of_output_file_structures:
        output_file_dict = {}
        for key, value in list_of_output_file_structures.items():
            output_file_dict[f"{key}_filename_str"] = create_file_from_string((key, 'csv'))
    else:
        # Otherwise use default configuration
        OUTPUT_FILE_CONFIGS = {
            'consolidated_hourly':'csv',
            'hourly_electricity':'csv',
            'hourly_natural_gas':'csv',
            # ... all other files
            'hourly_market_heat_rate':'csv',

            'monthly_generator_bid_output':'csv',
            'monthly_cf_output':'csv',
            'monthly_avg_electricity':'csv',
            'monthly_avg_natural_gas':'csv',
            'monthly_market_heat_rate':'csv',
            'monthly_power_recievedratio_output':'csv',
            'monthly_natgas_recievedratio_output':'csv',

            'annual_generator_bid_output':'csv',
            'annual_cf_output':'csv',
            'annual_power_recievedratio_output':'csv',
            'annual_natgas_recievedratio_output':'csv',
            'annual_avg_electricity':'csv',
            'annual_avg_natural_gas':'csv',
            'annual_market_heat_rate':'csv',
            'annual_allhour_electricity_heatmap':'csv',
            'annual_offpeak_electricity_heatmap':'csv',
            'annual_onpeak_electricity_heatmap':'csv',
            'annual_heatmap_data_market_electricity':'csv',
            'annual_heatmap_data_market_naturalgas':'csv',
            'annual_market_heat_rate_std_avg_heatmap_data':'csv'
        }
    
        output_file_dict = {}
    
    
        for file_key, extension in OUTPUT_FILE_CONFIGS.items():
            filename = create_file_from_string((file_key, extension))
            output_file_dict[f"{file_key}_filename_str"] = filename

    # Add template files
    output_file_dict['combined_forecast_filename_str'] = "combined_forecast_{}_with_{}.csv"
    output_file_dict['combined_forecast_with_Top_Percent_Price_filename_str'] = "combined_forecast_{}_with_{}.csv"
    
    # Create output_file_attributes_dict (empty for now, to be filled as needed)
    output_file_attributes_dict = {key.replace('_filename_str', ''): "" for key in output_file_dict.keys()}
    
    return output_file_dict, output_file_attributes_dict

def build_file_structure(forecast_scenarios, list_of_output_file_structures):
    print("build_file_structure called")
    
    # Initialize aggregated dictionaries
    forecaster_name_dict = {}
    forecaster_data_structure_dict = {}
    sto_seed_dict = {}
    #sto_seed_used_dict = {}
    dst_type_dict = {}
    forecast_years_dict = {}
    input_filename_dict = {}
    forecast_folder_dict = {}
    forecast_raw_data_filepath_dict = {}
    forecast_p50_filepath_dict = {}
    forecast_data_flag_dict = {}
    
        
    for scenario in forecast_scenarios:
        # Use scenario.name + "_years" and scenario.name + "_folder_name" etc. 
        # to match the expected format in create_forecast_metadata
        
        forecast_years_dict[scenario.name] = scenario.year_range
        input_filename_dict[scenario.name] = scenario.file_name
        forecast_folder_dict[scenario.name] = scenario.folder_name
        forecast_raw_data_filepath_dict[scenario.name] = scenario.raw_data_path(gbl.gbl_csv_output_path)
        forecast_p50_filepath_dict[scenario.name] = scenario.processed_p50_path(
            gbl.gbl_output_data_path_str,
            gbl.gbl_csv_folder_name_str,
            gbl.gbl_p50_output_file_var
        )
        forecast_data_flag_dict[scenario.name] = scenario.is_active
        
        # Forecaster-specific data
        forecaster_name_dict[scenario.forecaster] = scenario.forecaster
        forecaster_data_structure_dict[scenario.forecaster] = scenario.data_structure
        dst_type_dict[scenario.forecaster] = scenario.dst_type
        print(scenario.stochastic_seeds)
        sto_seed_dict[f"{scenario.forecaster}_stochastic_seeds"] = scenario.stochastic_seeds
        # new
        sto_seed_dict[f"{scenario.forecaster}_stochastic_seeds_used"] = scenario.stochastic_seeds_used
        print(scenario.stochastic_seeds_used)
        # old
        #sto_seed_used_dict[f"{scenario.forecaster}_stochastic_seeds_used"] = scenario.stochastic_seeds_used
    
    # Create output files (only once, outside the loop)
    #output_file_dict, output_file_attributes_dict = create_output_file_dicts()
    output_file_dict, output_file_attributes_dict = create_output_file_dicts(list_of_output_file_structures)
    
    # P-labels
    p10_label, p25_label, p50_label, p75_label, p90_label = 'P10', 'P25', 'P50', 'P75', 'P90'
    
    # RETURN A DICTIONARY, NOT A TUPLE!
    # return (forecaster_name_dict, sto_seed_dict, dst_type_dict, 
    #         forecaster_data_structure_dict, input_filename_dict, forecast_years_dict,
    #         forecast_folder_dict, forecast_raw_data_filepath_dict, forecast_p50_filepath_dict, 
    #         forecast_data_flag_dict, output_file_dict, output_file_attributes_dict,
    #         p10_label, p25_label, p50_label, p75_label, p90_label)
    return {
        'forecaster_name_dict': forecaster_name_dict,
        'sto_seed_dict': sto_seed_dict,
        'dst_type_dict': dst_type_dict,
        'forecaster_data_structure_dict': forecaster_data_structure_dict,
        'input_filename_dict': input_filename_dict,
        'forecast_years_dict': forecast_years_dict,
        'forecast_folder_dict': forecast_folder_dict,
        'forecast_raw_data_filepath_dict': forecast_raw_data_filepath_dict,
        'forecast_p50_filepath_dict': forecast_p50_filepath_dict,
        'forecast_data_flag_dict': forecast_data_flag_dict,
        'output_file_dict': output_file_dict,
        'output_file_attributes_dict': output_file_attributes_dict,
        'p_labels': {
            'p10': 'P10',
            'p25': 'P25',
            'p50': 'P50',
            'p75': 'P75',
            'p90': 'P90'
        }
    }
    

