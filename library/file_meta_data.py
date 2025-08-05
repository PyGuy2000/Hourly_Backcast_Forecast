

from library import globals as gbl          
from library.class_objects.other_classes.classes import TrackedDict, ForecastFile
from library.class_objects.output_files.output_file import create_file_from_string


import os
import re
import json


'''
This sets up the meta data for the various files that are held in the 
gbl_tracked_dict_json_file_data.  This dictionary object holds all relevant
file data in an object that can be accessed during run time.

'''

def create_final_dictionary(
        input_data_dict, 
        output_data_dict, 
        output_file_dict
):

        global gbl_tracked_dict_json_file_data, gbl_json_file_path_full, gbl_json_file_path_loaded, gbl_input_path, \
            gbl_historic_data_path, gbl_csv_output_path, gbl_image_data_path, gbl_json_power_generation_path, \
                gbl_frcst_output_excel_file_path, gbl_temp_path_str
        

        print("create_final_dictionary called")

        dict = {
            "Input_Data": {
                "General_Data": {
                    'json_data': [
                        gbl.gbl_json_file_path_full,
                        gbl.gbl_json_file_path_loaded
                    ],
                    'input_path' : gbl.gbl_input_path,
                    'historic_data_path' : gbl.gbl_historic_data_path,
                },
                "Price_Forecast": input_data_dict
            },
            "Output_Data" : {
                "General_Data" : {
                    'json_data': [
                        gbl.gbl_json_file_path_full,
                        gbl.gbl_json_file_path_loaded
                    ],
                    'csv_output_path' : gbl.gbl_csv_output_path,
                    'image_data_path' : gbl.gbl_image_data_path,
                    'json_power_generation_path' : gbl.gbl_json_power_generation_path,
                    'frcst_output_excel_file_path' : gbl.gbl_frcst_output_excel_file_path,
                    'temp_data_path': gbl.gbl_temp_path_str
                },
                "Processed_Price_Forecast" : output_data_dict,
                "Output_Template_Data": output_file_dict
            }
        }

        return dict
    
    
##################################################
def add_gen_list_post_loop(final_dict):
    print("add_gen_list_post_loop called")
    # Add generation list
    generation_sources_dict = gbl.gbl_tracked_powergen_dict["generation_sources"]
    generation_sources_keys_list = list(generation_sources_dict.keys())
    print(f" generation_sources_keys_list:{generation_sources_keys_list}")
    final_dict["Output_Data"]["Generator_Ouput_Data"] = generation_sources_keys_list


    return final_dict
##############################################
# This function takes all the input and output file dictionary items
# as parameters and the loops thorugh them them to populate a json file
# an input_data_dict{} and an output_data_dict{}.  These two dictionaries
# are then combined into a final dictionary called final_dict{}.

# Note that if these individual input dictionaries are converted to
# to a list of dictionaries rerpesenting the foredcast class objects, the 
# code below will have to loop through that list of dictionaries to extract the data

# new
def create_forecast_metadata(file_structure_data):
    """
    Process forecast metadata from file structure data
    
    Args:
        file_structure_data: Dictionary containing all the forecast-related dictionaries
    """
    print("create_forecast_metadata called")
    
    # Extract all dictionaries from file_structure_data
    forecaster_name_dict = file_structure_data['forecaster_name_dict']
    sto_seed_dict = file_structure_data['sto_seed_dict']
    dst_type_dict = file_structure_data['dst_type_dict']
    forecaster_data_structure_dict = file_structure_data['forecaster_data_structure_dict']
    input_filename_dict = file_structure_data['input_filename_dict']
    forecast_years_dict = file_structure_data['forecast_years_dict']
    forecast_folder_dict = file_structure_data['forecast_folder_dict']
    forecast_data_flag_dict = file_structure_data['forecast_data_flag_dict']
    output_file_dict = file_structure_data['output_file_dict']
    output_file_attributes_dict = file_structure_data['output_file_attributes_dict']
    
    input_data_dict = {}
    output_data_dict = {}

    # Rest of your existing code remains the same...
    for key in input_filename_dict.keys():
        print(f"Key: {key}")

        # Extract Forecaster Name
        forecaster_acronym = key.split('_')[2]  # This extracts 'edc', 'similan'
        # Get the corresponding forecaster name from forecaster_name_dict
        forecaster_name = forecaster_name_dict.get(forecaster_acronym)
        
        # Check that forecaster name exists
        if forecaster_name:
            print(f"Forecaster name for {key}: {forecaster_name}")
        else:
            print(f"No forecaster name found for {key}")

        # Extract the base part of the key
        base_key = key.replace('_data', '')
        print(f" base_key: {base_key}")

        # Extract the year part from the key for dynamic naming
        year_part = key.split('_')[1]
        
        #Extract sto seed values from dict
        key1_revised = forecaster_name +'_stochastic_seeds'
        key2_revised = forecaster_name +'_stochastic_seeds_used'
        stochastic_seeds = sto_seed_dict[key1_revised]
        stochastic_seeds_used = sto_seed_dict[key2_revised]
        print(stochastic_seeds, stochastic_seeds_used)
        
        
        
        # Extract start and end years
        #start_year, end_year = forecast_years_dict[f"{key}_years"]
        start_year, end_year = forecast_years_dict[key]

        # Folder name
        #folder_name = forecast_folder_dict[f"{key}_folder_name"]
        folder_name = forecast_folder_dict[key]
        print(f" folder_name: {folder_name}")
        
        # Raw data file path
        quarter_part = key.split('_')[0][1:]  # Extract the quarter part
        
        case_part = key.split('_')[3][0:]  # Extract the 'basecase'
        
        raw_data_file_path = f"{forecaster_name.lower()}q{quarter_part}_{year_part}_base_path_processed_data"
        
        #file_data_structure = forecaster_data_structure_dict[f'{forecaster_name}_data_structure']
        file_data_structure = forecaster_data_structure_dict[forecaster_name]
        
        #dst_type = dst_type_dict[f'{forecaster_name}_dst_type']
        dst_type = dst_type_dict[forecaster_name]
        
        input_sub_folder = folder_name 
        output_sub_folder = folder_name
        filename = input_filename_dict[key]  # Fix: Get specific filename for this key
        
        print(input_sub_folder)
        print(output_sub_folder)
        print(filename)
        
        input_raw_data_path = os.path.join(gbl.gbl_input_path, input_sub_folder, filename)

        # Create input folder that has existing data
        gbl.gbl_frcst_input_excel_file_path = os.path.join(gbl.gbl_input_path, forecaster_name, filename)
        
        # Create output folder that has existing data
        gbl.gbl_frcst_output_excel_file_path = os.path.join(gbl.gbl_input_path, forecaster_name, filename)
        
        # Create output folder that does not yet have any data
        gbl.gbl_frcst_output_csv_file_path = os.path.join(gbl.gbl_csv_output_path, forecaster_name, output_sub_folder)

        # Construct input_data_dict metadata for each forecast
        input_data_dict[f"{forecaster_name} Q{quarter_part} {year_part} {case_part}"] = {
            "Input_File_Attributes": {
                'forecaster_name' : forecaster_name,
                'input_sub_folder' : input_sub_folder,
                'filename': filename,
                'file_structure' : file_data_structure,
                'dst_type' : dst_type,
                'frcst_input_excel_file_path' : gbl.gbl_frcst_input_excel_file_path,
                'frcst_output_csv_file_path' : "",
                'datetime_column': 'begin_datetime_mpt',
                'price_column': 'price',
                'start_year': start_year,
                'end_year': end_year,
                'stochastic_seeds': stochastic_seeds,
                'stochastic_seeds_used': stochastic_seeds_used,
                'input_raw_data_path' : input_raw_data_path,
                'base_path_processed_data': raw_data_file_path,
                'pwr_file_name_p50': f"Date-{start_year}-{end_year}_p50_hourly_spot_electricity.csv",
                'natgas_file_name_p50': f"Date-{start_year}-{end_year}_p50_hourly_spot_natural_gas.csv",
                #'Data_Active': forecast_data_flag_dict[f"{key}_flag"]
                'Data_Active': forecast_data_flag_dict[key]
            }
        }

        # Construct output_data_dict metadata for each forecast
        output_data_dict[f"{forecaster_name} Q{quarter_part} {year_part} {case_part}"] = {
            "Output_File_Attributes": {
                'forecaster_name' : forecaster_name,
                'output_sub_folder': output_sub_folder,
                'filename' : None,
                'frcst_output_excel_file_path' : gbl.gbl_frcst_output_excel_file_path, 
                'frcst_output_csv_file_path' : gbl.gbl_frcst_output_csv_file_path,
                'start_year': start_year,
                'end_year': end_year,
                'stochastic_seeds': stochastic_seeds,
                'stochastic_seeds_used': stochastic_seeds_used,
                'pwr_file_name_p50': f"Date-{start_year}-{end_year}_p50_hourly_spot_electricity.csv",
                'natgas_file_name_p50': f"Date-{start_year}-{end_year}_p50_hourly_spot_natural_gas.csv",
                #'Data_Active': forecast_data_flag_dict[f"{key}_flag"]
                'Data_Active': forecast_data_flag_dict[key]
            }
        }

        # Add additional data to "Output_File_Attributes"
        output_data_dict[f"{forecaster_name} Q{quarter_part} {year_part} {case_part}"]["Output_File_Attributes"].update(output_file_attributes_dict)
        
        # Create the final dictionary by combining the input/ouput dictionaries
        final_dict = create_final_dictionary(input_data_dict, output_data_dict, output_file_dict)
    
    # Add the generation list outside of the loop as it only needs to be added once
    print(gbl.gbl_tracked_powergen_dict)
    if final_dict is not None:
        final_dict = add_gen_list_post_loop(final_dict)
        print(final_dict)
    else:
        print("Final dictionary is None, skipping generation list addition.")

    # Create instance of TrackedDict class by passing the final dictionary
    # to the gbl.gbl_tracked_dict_json_file_data
    gbl.gbl_tracked_dict_json_file_data = TrackedDict(final_dict)
    
    ######################
    # Speical Note:
    ######################
    
    # This is saves the first versiopn of the gbl_tracked_dict_json_file_data to the 
    # json output file.  This holds all the data CAN be used in the analysis.
    # However the use may not want to use ALL the forecast data and may want to choose
    # specific forecasts.  This can be achieved by adjusting the "is_active" key
    # in the forcast_scenarios.yaml file

    gbl.gbl_tracked_dict_json_file_data.save_to_json(gbl.gbl_json_file_path_full)
    print("gbl_tracked_dict_json_file_data", type(gbl.gbl_tracked_dict_json_file_data))
    
    

    print("Printing gbl_tracked_dict_json_file_data data..")
    print(json.dumps(gbl.gbl_tracked_dict_json_file_data, indent=4))
    print("Exiting create_forecast_metadata function...") 

    return



##############################################
def function(output_data_path_str, csv_folder_name_str, gbl_p50_output_file_var, data_years, folder_name):
    # Extracting the start and end year from the tuple
    start_year, end_year = data_years
    
    # Constructing the file name
    file_name = f"Date-{start_year}-{end_year}_{gbl_p50_output_file_var}"
    
    # Constructing the full file path
    full_path = os.path.join(output_data_path_str.replace("/", "//"), csv_folder_name_str, folder_name, file_name)
    
    return full_path

#