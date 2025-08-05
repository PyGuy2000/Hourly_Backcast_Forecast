
import os
import sys
import re
import json
import pandas as pd
import importlib
import numpy as np

# Add the root directory to the system path
current_path = os.path.dirname(os.path.abspath(__file__))
root_path = os.path.dirname(current_path)
sys.path.append(root_path)

#########################
#MODULE IMPORTS
#########################
# NEW:
from pathlib import Path
from platform_config import platform_config


from library import globals as gbl
from library import initializer as init # this is an alias for initializer
from library.globals import setup_global_variables

from library.config import (
    create_electr_frcst_dicts_flag,
    check_integrity_of_input_data_flag,
    process_forecast_data_flag,
    stats_on_frcst_data_flag,
    generate_p_values_flag,
    calc_lcoe_flag,
    simulate_merit_order_flag,
    adjust_frcst_data_flag,
    enb_load_review_flag,
    create_trans_costs_flag,
    runpipe_all_flags_true
)

from library.class_objects.other_classes.classes import TrackedDict, ForecastFile
from library.class_objects.forecast_files.forecast_scenario_loader import load_forecast_scenarios
# old
#from library.class_objects.forecast_files.forecast_scenario_file_structure import build_forecast_file_structure
# new
from library.class_objects.forecast_files.forecast_scenario_file_structure import build_file_structure

from library.class_objects.output_files.output_file_loader import load_output_files
from library.class_objects.output_files.output_file_structure import build_output_file_structure
from library.test_code.test_merit_test import (
    calculate_lcoe, 
    #back_casted_capacity_factor_example,
    powergen_production_simulation 
)

from library.create_stats_visualizations import (
    calcStats_on_data, 
    calculate_percentile_data, 
    create_time_series_chart, 
    create_heat_map_chart, 
)

from library.historical_spot_buckets import adjust_forecast_data
from library.process_raw_files import process_data
from library.enb_load_calcluations import review_enb_load
from library.aeso_transmission_tariff import (
    create_transmission_cost,
    adjust_for_dst,
    adjust_processed_demand_data_for_dst
)

# New
#from new_build_file_structure import build_file_structure2

def load_full_json_to_global():
    """
    Load the dictionary from the JSON file and update the global variable.
    """
    
    temp_full_dict = {}
    with open(gbl.gbl_json_file_path_full, 'r') as json_file:
        temp_full_dict = json.load(json_file)
        gbl.gbl_tracked_dict_json_file_data = TrackedDict(temp_full_dict)
        gbl.gbl_tracked_dict_json_file_data.save_to_json(gbl.gbl_json_file_path_full)
        print(json.dumps(gbl.gbl_tracked_dict_json_file_data, indent=4))

def load_loaded_json_to_global():
    """Load the dictionary from the JSON file and update the global variable."""
    #global gbl_tracked_loaded_dict_json_file_data
    
    temp_loaded_dict = {}
    with open(gbl.gbl_json_file_path_loaded, 'r') as json_file:
        temp_loaded_dict = json.load(json_file)
        gbl.gbl_tracked_loaded_dict_json_file_data = TrackedDict(temp_loaded_dict)
        gbl.gbl_tracked_loaded_dict_json_file_data.save_to_json(gbl.gbl_json_file_path_loaded)
        #print(f" gbl.gbl_tracked_loaded_dict_json_file_data: {gbl.gbl_tracked_loaded_dict_json_file_data}")
        print(json.dumps(gbl.gbl_tracked_loaded_dict_json_file_data, indent=4))

'''
Create shortcut paths to dictionary to limit the amount of
code required
'''      
def create_global_dict_shortcut_path():
    global gbl_output_general_data

    
    gbl.gbl_input_general_data = gbl.gbl_tracked_loaded_dict_json_file_data ["Input_Data"]["General_Data"]
    print(f" gbl_input_general_data: {gbl.gbl_input_general_data}")

    gbl.gbl_price_forecast = gbl.gbl_tracked_loaded_dict_json_file_data ["Input_Data"]["Price_Forecast"]
    print(f" gbl.gbl_price_forecast: {gbl.gbl_price_forecast}")

    gbl.gbl_output_general_data =  gbl.gbl_tracked_loaded_dict_json_file_data ["Output_Data"]["General_Data"]
    print(f" gbl.gbl_output_general_data: {gbl.gbl_output_general_data}")

    gbl.gbl_processed_price_forecast = gbl.gbl_tracked_loaded_dict_json_file_data ['Output_Data']['Processed_Price_Forecast']
    print(f" gbl.gbl_processed_price_forecast : {gbl.gbl_processed_price_forecast }")

    gbl.gbl_output_template = gbl.gbl_tracked_loaded_dict_json_file_data ["Output_Data"]["Output_Template_Data"]
    print(f" gbl.gbl_output_template : {gbl.gbl_output_template }")


def load_powergen_json_to_global():
    """Load the poewrgen dictionary from the JSON file and update the global variable."""
    global gbl_tracked_powergen_dict
    temp_powergen_dict = {}
    with open(gbl.gbl_json_power_generation_path, 'r') as json_file:
        temp_powergen_dict = json.load(json_file)
        gbl.gbl_tracked_powergen_dict = TrackedDict(temp_powergen_dict)
        gbl.gbl_tracked_powergen_dict.save_to_json(gbl.gbl_json_power_generation_path)
        #print(f" gbl.gbl_tracked_powergen_dict: {gbl.gbl_tracked_powergen_dict}")
        print(json.dumps(gbl.gbl_tracked_powergen_dict, indent=4))


# Define file paths both input and output files
# This has been replaced by the code in the file_meta_data.py file
init.initialize_global_variables('vscode')

# Setup global variables that depend on initialization and file paths from the previous step
# to load input files
gbl.setup_global_paths()
gbl.setup_global_variables()


#Moved this form above as it needs to occur AFTER the global variable are set
from library.file_meta_data import (
    #build_file_structure,
    create_forecast_metadata,
    create_final_dictionary,
    add_gen_list_post_loop
)


'''
Main routine that calls various functions to analyze the price curves
that are stored in the project
'''
##################################################
def main():

    print("main called")
    ##################################################
    # Main Inputs
    ##################################################
    
    
    # new
    # Create file path
    output_file_path = str(platform_config.get_library_path(
    'output_file.yaml',
    'class_objects/output_files'    
    ))
    print("*" *90)
    print(f"output_file_path: {output_file_path}")
    
    # Load output files from the YAML file
    output_files = load_output_files(output_file_path)
    print("*" *90)
    print(f"output_files: {output_files}")
    
    # Pass output structured output files to object
    list_of_output_file_structures = build_output_file_structure(output_files)
    print("*" *90)
    print(f"list_of_output_file_structures: {list_of_output_file_structures}")
    
    input_frcst_file_path = str(platform_config.get_library_path(
        'forcast_scenarios.yaml', 
        'class_objects/forecast_files'
    ))
    # Define forecast file paths from YAML file
    forecast_scenarios = load_forecast_scenarios(input_frcst_file_path)
    print("*" *90)
    print(f"forecast_scenarios: {forecast_scenarios}")

    ##################################################
    #Set-up directories and input file paths
    ##################################################
    #-------------------------------------------------
    # General File Paths and General File Names
    #-------------------------------------------------
    
    '''
    Build the DNA of file dictionary that holds all the relevant input/ouput
    file meta data that needs to be accessed during model run time
  
    
    Important Note
    The file_structure_data is a dictionary that holds all the relevant input/output file meta data.
    These exist in various diciontaries that are held in the file_structure_data dictionary.
    The contencw of that file looks like this: 
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
    
    Examples on how to reference the data in the file_structure_data dictionary:
    
    #######################################################
    # Example 1: Pass just one dictionary to a function
    #######################################################
    def process_output_files(output_dict):
        for key, value in output_dict.items():
            print(f"Processing {key}: {value}")

    # Call it with just the output_file_dict
    process_output_files(file_structure_data['output_file_dict'])

    #######################################################
    # Example 2: Extract multiple dictionaries at once
    #######################################################
    output_dict = file_structure_data['output_file_dict']
    forecast_years = file_structure_data['forecast_years_dict']
    p_labels = file_structure_data['p_labels']

    #######################################################
    # Example 3: Use in a conditional 
    #######################################################
    if file_structure_data['forecast_data_flag_dict'].get('Q2_2025_edc_basecase_flag'):
        print("Q2 2025 EDC basecase is active")

    #######################################################
    # Example 4: Pass specific dictionaries to another function
    #######################################################
    def analyze_forecasts(years_dict, flags_dict):
        for key, is_active in flags_dict.items():
            if is_active:
                scenario_name = key.replace('_flag', '')
                years = years_dict.get(f"{scenario_name}_years")
                print(f"Active scenario: {scenario_name}, Years: {years}")

    analyze_forecasts(
        file_structure_data['forecast_years_dict'],
        file_structure_data['forecast_data_flag_dict']
    )
    
    
    '''
    
    file_structure_data  = build_file_structure(forecast_scenarios, list_of_output_file_structures)
    

   

    #####################################################################
    Active = create_electr_frcst_dicts_flag

    if Active:
        '''
        Creates meta data structure in gbl_tracked_dict_json_file_data
        '''
        
        # new
        create_forecast_metadata(file_structure_data)
        
        print("gbl.gbl_tracked_dict_json_file_data", type(gbl.gbl_tracked_dict_json_file_data))
        print("Printing gbl.gbl_tracked_dict_json_file_data data..")
        print(json.dumps(gbl.gbl_tracked_dict_json_file_data, indent=4))

    else:
        pass


    #-------------------------------------------------


    ##################################################
    # Step 1: Check integrity of input data
    ##################################################
    # Historical Data
    # Forecast Data

    Active = check_integrity_of_input_data_flag

    if Active:
        #Do something
        pass
    else:
        pass
    
    ##################################################
    # Step 2: Process the Forecast Data to test assumptions on capacity factor and capture price
    # The Purpose of this step is to use an houlry forecasted data set from a third party and test their assumptions 
    # on capacity factor and capture price for a given generator.  This routine creates new standalone files for spot power spot nat gas, 
    # market heat rate, and then varies them by hour, month, annual so that they can be used to put back in a capital 
    # budgetting model for sensitivy analysis.  Some models use monthly data, some use annual data, some use hourly data. 
    ##################################################

    Active = process_forecast_data_flag

    if Active:
        if not runpipe_all_flags_true:
            #load_full_json_to_global()
            load_loaded_json_to_global()
            create_global_dict_shortcut_path()
            load_powergen_json_to_global()

        ######################################
        # Filter the Runs you want to analyze 
        ######################################
        # Filter the Price_Forecast input entries
        filtered_input_file_list = {
            key: value for key, value in gbl.gbl_tracked_dict_json_file_data["Input_Data"]["Price_Forecast"].items()
            if value["Input_File_Attributes"].get('Data_Active', True)

        }
        print(f" filtered_input_file_list: {filtered_input_file_list}")

        # Construct the new input dictionary
        filtered_input_file_dict = {}
        for key, value in filtered_input_file_list.items():
            filtered_input_file_dict[key] = {
                "Input_File_Attributes": value["Input_File_Attributes"]
            }

        # Also filter the Price_Forecast output data
        filtered_output_file_list = {
            key: value for key, value in gbl.gbl_tracked_dict_json_file_data["Output_Data"]["Processed_Price_Forecast"].items()
             if value["Output_File_Attributes"].get('Data_Active', True)

        }

        print(f" filtered_output_file_list: {filtered_output_file_list}")

        
        # Construct the new output dictionary
        filtered_output_file_dict = {}
        for key, value in filtered_output_file_list.items():
            filtered_output_file_dict[key] = {
                "Output_File_Attributes": value["Output_File_Attributes"]
            
            }
            print(key)

        ######################################
        # Create the final dictionary based on revised/filtered file lists
        ######################################
        # Step 1: Create regular dictionary using local dict object
        output_file_dict = file_structure_data['output_file_dict']
        loaded_dict = create_final_dictionary(
            filtered_input_file_dict, 
            filtered_output_file_dict, 
            output_file_dict
            )
        loaded_dict = add_gen_list_post_loop(loaded_dict)
        print(loaded_dict.keys())

        # Step 2: Create Tracked Dict instance for loaded_dict and pass local dict object
        # to this class object
        gbl.gbl_tracked_loaded_dict_json_file_data = TrackedDict(loaded_dict)
        #Step 3: Save class instances to file
        gbl.gbl_tracked_loaded_dict_json_file_data.save_to_json(gbl.gbl_json_file_path_loaded)

        # Step 4: Also create Update global shortcut variables for json file to make accessing data
        #create_global_dict_shortcut_path()


        ##############################
        # process_data Function
        ##############################

        process_data()

    else:
        pass
   
    ##################################################
    # Step 3: Calculates Stats and Create Visuualizations for the data
    # The purpose of this step is to calculate the statistics for the data and create visualizations to help understand the data.
    # This code also processes the hourly data to create P10, P25, P50, P75, and P90 values for the data.
    # The P50 value will then be used to calculate determine the capacity factor and capture price for a given generator.
    # This step will also calculate the LCOE and Variable Costs for the Merit Test. 
    # The Merit Test is a test that is used to determine the capacity factor and capture price for a given generator.

    ##################################################

    #-------------------------------------------------
    # PART A: Separate Electricity Prices and Natuaral Gas Prices and Perform Stats on the Electricity and Natural Gas Prices
    #-------------------------------------------------
  
    #******************************************************************************************        
    Active = stats_on_frcst_data_flag

    if Active:
        if not runpipe_all_flags_true:
            load_loaded_json_to_global()
            create_global_dict_shortcut_path()
            load_powergen_json_to_global()
            # Pretty-print the JSON data
            print(json.dumps(gbl.gbl_tracked_loaded_dict_json_file_data, indent=4))

        ##############################
        # calcStats Function
        ##############################
        '''
        Analyze price curves and extract statistics
        '''
        df_consolidated_elec_natgas, electricity_cols, natural_gas_cols = calcStats_on_data()
        

    else:
        pass
   

        
    #-------------------------------------------------
    # PART B: Generate P10/P25/P50/P75/P90 Values and Create Visualizations
    # Some of the forecast data is provided as a collection of stochastic seeds.
    # This routine calculates the P-Values so that you don't have to manage all
    # the seed data in your final analysis. For example the EDC data is provided
    # as 50x seeds of hourly data over 15 years.  This function provides a P_Value
    # for the hourly data, monthly data, and/or annual data so that you don't have to
    # load all 50 seeds of data into your spreadsheet.
    #-------------------------------------------------
    
    Active = generate_p_values_flag

    if Active:
        if not runpipe_all_flags_true:
            load_loaded_json_to_global()
            create_global_dict_shortcut_path()
            load_powergen_json_to_global()
        
        pwr_percentiles_df, pwr_P10, pwr_P25, pwr_P50, pwr_P75, pwr_P90, natgas_percentiles_df, natgas_P10, natgas_P25, \
            natgas_P50, natgas_P75, natgas_P90 = calculate_percentile_data()


        chart_title_txt = 'Hourly Power Prices Forecast Percentiles',
        file_ext_txt = ' Spot Electricity Percentile Time Series Chart'
        create_time_series_chart(        
                        pwr_P10, 
                        pwr_P25, 
                        pwr_P50, 
                        pwr_P75, 
                        pwr_P90, 
                        pwr_percentiles_df, 
                        chart_title_txt,
                        file_ext_txt
                        )

        chart_title_txt = 'Hourly Natural Gas Prices Forecast Percentiles',
        file_ext_txt = ' Spot Natural Gas Percentile Time Series Chart'
        create_time_series_chart(
                        natgas_P10, 
                        natgas_P25, 
                        natgas_P50, 
                        natgas_P75, 
                        natgas_P90, 
                        natgas_percentiles_df, 
                        chart_title_txt,
                        file_ext_txt
                        )
        
        create_heat_map_chart(
                        pwr_percentiles_df, 
                        )
        create_heat_map_chart(
                        natgas_percentiles_df, 
                        )

    else:
        pass


        

    #-------------------------------------------------
    # PART C: Calculated LCOE and Variable Costs for Merit Test
    #-------------------------------------------------
    '''
    Calculates LCOE for list of facilities loaded into gbl_generation_sources
    '''

    Active = calc_lcoe_flag

    if Active:
        if not runpipe_all_flags_true:
            # Re-load the file and generator files you created from above
            load_loaded_json_to_global()
            create_global_dict_shortcut_path()
            load_powergen_json_to_global()
            # Load the generator assumption file you created from above
        
        generator_list = ['gas_fired_peaker_recip']

        ##############################
        # Calculate_LCOE Function
        ##############################

        #NEW Function
        # "years" variable used to pull historical natural gas data for LCOE
        years = [2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021,2022,2023]
        
        # First Run of Routine
        capacity_factor_range = [i / 10.0 for i in range(1, 11)]  # Creates a list [0.0, 0.1, 0.2, ..., 1.0]
        year_title = calculate_lcoe(
                    gbl.gbl_generation_sources,
                    years,
                    capacity_factor_range,
        )

    else:
        pass


    #-------------------------------------------------
    #Part D: Conduct Merit Test and Create Visualizations
    #-------------------------------------------------
    '''
    Analyzes the run time of a particular generation source rleative to
    annual spot price forecasts. This is effectively a dispatch analysis
    '''
    Active = simulate_merit_order_flag
    print(F" gbl.gbl_json_file_path_loaded: {gbl.gbl_json_file_path_loaded}")
    if Active:
        if not runpipe_all_flags_true:
            load_loaded_json_to_global()
            create_global_dict_shortcut_path()
            load_powergen_json_to_global()
        
        generator_list = ['gas_fired_peaker_recip']
        gstarting_index = 1.0
        gcurrent_annual_index = None
        gannual_index_rate = 0.02 #2%
        gnox_emissons = 0.140 #kg/GJ of energy output
        gcf_limit = 1 #0.35 

        # Select strategy
        gSTRATEGY_CF_CAP = 1
        gSTRATEGY_PERFECT_FORESIGHT = 2
        gSTRATEGY_PREDICTIVE_BIDDING = 3
        gstrategy = gSTRATEGY_CF_CAP #STRATEGY_CF_CAP/STRATEGY_PERFECT_FORESIGHT/STRATEGY_PREDICTIVE_BIDDING  # Change this to STRATEGY_PERFECT_FORESIGHT or STRATEGY_PREDICTIVE_BIDDING as needed
    

        ##############################
        # Calculate_Merit_Test Function
        ##############################

        run_type = "Actuals" # "Actuals", "P-Value" or "Stochastic Seeds"
        
        if run_type == 'Actuals':
        # "years" variable used to pull historical natural gas and power data when using historical data
            years = [2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021,2022,2024]
        elif run_type == "P-Value":
            # Range defined witin function
            years = None
        elif run_type == "Stochastic Seeds":
            # Range defined witin function
            years = None

        
        
        
        generator_list = ['gas_fired_peaker_recip']
        year_title = ""

        

        #new
        powergen_production_simulation(
            generator_list,
            years,
            run_type
            )
    else:
        pass
        #******************************************************************************************
        # Reload Json Path in the even that the python routine starts from this point in the code
        # json_file_path_data_json = os.path.join(json_folder_path, active_price_run_file_name_str)
        # Load the dictionary from the JSON file
        # with open(gbl.gbl_json_file_path_data_json, 'r') as json_file:
        #     gbl.gbl_tracked_loaded_dict_json_file_data = json.load(json_file)


    #-------------------------------------------------
    #Part E: Make Adjustments to the forecast data based on historical data and/or other factors
    #-------------------------------------------------
    ##################################################
    # The purpose of this step is to make adjustments to the forecast data based on historical data and/or other factors.
    # This step will also calculate the Top % Hour Pricing for both Historical and Forecast Data.
    # The code creates the top % hour pricing for both historical and forecast data.
    # The top % hour pricing is the price that is paid for the top % of hours in a given year.
    # The buckets create are as follows: Top 10% Hours Top 25%, Top 50%, Top 75%, and Top 90%.
    # The code then gives the user the opportuntity to adjust a specific tier of the forecast data based on the Top X% buckets above
    # The user can chose between using a fixed $/MWh price cap in the top X% Hours of the forecast OR they can use the historical capture
    # price in the top X% Hours from the historicla data as an adjsutment to the forecast data. 
    
    ##################################################
    # Reload Json Path in the even that the python routine starts from this point in the code
    # json_file_path_data_json = os.path.join(json_folder_path, active_price_run_file_name_str)
    # Load the dictionary from the JSON file
    # with open(gbl.gbl_json_file_path_data_json, 'r') as json_file:
    #      gbl.gbl_tracked_loaded_dict_json_file_data = json.load(json_file)

    
    #****************************************************************************************** 
    Active = adjust_frcst_data_flag

    if Active:
        if not runpipe_all_flags_true:
            load_loaded_json_to_global()
            create_global_dict_shortcut_path()
            load_powergen_json_to_global()


        gvariable_cost = 40 # $/MWh
        input_filename_template =  "combined_forecast_*.csv"
        output_filename_template = f'combined_forecast_with_Top_10%_Price_'
        datetime_column = 'DateTime'
    
    
        adjust_forecast_data(
            gvariable_cost, 
            input_filename_template, 
            output_filename_template, 
            datetime_column,
            p50_label
            )  
    else:
        pass
    
    #-------------------------------------------------
    #Part F: Review ENB Load
    #-------------------------------------------------
    # Reload Json Path in the even that the python routine starts from this point in the code
    # json_file_path_data_json = os.path.join(json_folder_path, active_price_run_file_name_str)
    # Load the dictionary from the JSON file
    # with open(gbl.gbl_json_file_path_data_json, 'r') as json_file:
    #      gbl.gbl_tracked_loaded_dict_json_file_data = json.load(json_file)
    #****************************************************************************************** 

    Active = enb_load_review_flag
    
    if Active:
        if not runpipe_all_flags_true:
            load_loaded_json_to_global()
        
        peak_demand_methodology = 'twelve_cp_peak_demand' #twelve_cp_peak_demand, five_cp_peak_demand, highest_in_month_each_month
        timeseries_format1 =  '%Y-%m-%d %H:%M:%S'
        timeseries_format2 =  '%m/%d/%Y %H:%M'
        processed_demand_data = pd.DataFrame()
        
        # new
        processed_demand_path = platform_config.get_input_file_path(
            'processed_demand_data.csv',
            'AESO_Tariff_Data'  # or another appropriate subfolder
        )
        if processed_demand_path.exists():
            processed_demand_data = pd.read_csv(str(processed_demand_path))
        else:
            print(f"Warning: Processed demand data not found. Please ensure it's in {processed_demand_path}")
        ##################################
        # old
        #processed_demand_data = pd.read_csv(r"C:\Users\kaczanor\OneDrive - Enbridge Inc\Documents\Python\AB Electricity Sector Stats\output_data\CSV_Folder\processed_demand_data.csv")

        # Initialize and set parameters
        # Step 1: Initialize and set parameters
        # Step 1.1 Load Alberta system load data

        # Convert the "Date_Begin_Local" column to datetime if it's not already
        processed_demand_data['Date'] = pd.to_datetime(processed_demand_data['DateTime'], format=timeseries_format1)
        print(f" processed_demand_data_upload before format change: {processed_demand_data}")

        processed_demand_data.set_index('Date', inplace=True)
        print(f"processed_demand_data after setting index: {processed_demand_data.head()}")

        # Step 1.2 Load ENB load data
        #Load enb demand data
        # Adjust the `skiprows` parameter based on your actual data structure
        # I only need the hourly data from the 16th row onwards
        # I dont need the summay statistics at the top of the file

        '''
        2021,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
        AVG,,"24,443","22,044","18,685","29,355","31,262","13,404","25,335","24,089","21,842","1,465","23,339","25,525","24,265","10,381","2,609","12,390","1,341","21,906","26,048","19,136",,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
        MAX,,"75,399","80,915","69,298","68,616","99,263","94,288","38,789","99,173","95,335","9,981","83,232","67,851","85,658","63,686","9,901","32,905","9,647","87,183","77,798","73,586",,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
        Load Factor %,,32%,27%,27%,43%,31%,14%,65%,24%,23%,15%,28%,38%,28%,16%,26%,38%,14%,25%,33%,26%,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
        ,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
        2022,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
        AVG,,"24,448","22,024","18,691","29,357","31,263","13,416","25,336","24,091","21,839","1,465","23,341","25,528","24,270","10,381","2,613","12,387","1,341","21,907","26,050","19,137",,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
        MAX,,"75,399","80,915","69,298","68,616","99,263","94,288","38,789","99,173","95,335","9,981","83,232","67,851","85,658","63,686","9,901","32,905","9,647","87,183","77,798","73,586",,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
        Load Factor %,,32%,27%,27%,43%,31%,14%,65%,24%,23%,15%,28%,38%,28%,16%,26%,38%,14%,25%,33%,26%,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
        ,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
        2023,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
        AVG,,"24,447","21,997","18,687","29,359","31,263","13,418","25,338","24,094","21,837","1,465","23,344","25,533","24,276","10,380","2,618","12,388","1,340","21,909","26,053","19,139",,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
        MAX,,"75,399","80,915","69,298","68,616","99,263","94,288","38,789","99,173","95,335","9,981","83,232","67,851","85,658","63,686","9,901","32,905","9,647","87,183","77,798","73,586",,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
        Load Factor %,,32%,27%,27%,43%,31%,14%,65%,24%,23%,15%,28%,38%,28%,16%,26%,38%,14%,25%,33%,26%,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
        ,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
        ,,District 1,,,,,District 2,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
        ,Year,EP,KG,ST,YP,ME,CC,KB,HR,MI,IL-93,ZP,CK,BU,RT-67,RQ-93,QU,WC,OD,AP,LB,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
        01-Jan-21 00:00:00,2021,9990.5,47842.0,6245.5,31534.9,30802.8,2755.4,23365.1,22789.1,22176.3,913.0717572,24808.0,20462.84257,20512.88242,10745.44476,1422.240462,14873.46192,161.7291616,21022.3941,25957.76316,17086.08622,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
        '''

        skiprows = 16  # 20 Example: Skip the first 16 rows, adjust as needed
        enb_demand_data = pd.read_csv(r"C:\Users\kaczanor\OneDrive - Enbridge Inc\Documents\Python\AB Electricity Sector Stats\input_data\ENB_Load\Power Consumption Consolidated D1&2.csv", skiprows=skiprows)

        enb_demand_data['Date'] = pd.to_datetime(enb_demand_data['Date'], format=timeseries_format2) 
        enb_demand_data.set_index('Date', inplace=True)
        print(f"enb_demand_data after setting index: {enb_demand_data.head()}")

        # Step 1.3 Filter Load Data
        # Asset data can be filtered as follows:
        # district_names = ["District 1", "District 2"]
        # district_1_stations = ["EP","KG","ST","YP","ME"]
        # district_2_stations = ["CC","KB","HR","MI","IL-93","ZP","CK","BU","RT-67","RQ-93","QU","WC","OD","AP","LB"]
        # all stations = ["EP","KG","ST","YP","ME","CC","KB","HR","MI","IL-93","ZP","CK","BU","RT-67","RQ-93","QU","WC","OD","AP","LB"]
        #line_3-af (AF) - Edmonton																	
        # line_93_ = ["YP", "ME", "CC", "KB", "HR", "IL", "ZP", "CK", "BU", "RQ", "OD", "AP", "LB"]
        # line_67_f = ["EP", "KG", "ST", "YP", "ME", "CC", "KB", "HR", "MI", "ZP", "CK", "BU", "RT", "OD", "AP", "LB"]
        # line_1_f = ["EP", "ST", "YP", "CC", "KB", "MI", "ZP", "BU", "QU", "WC", "OD", "AP", "LB"]
        # line_2_f = ["EP", "KG", "ST", "YP", "ME", "CC", "KB", "HR", "MI", "ZP", "CK", "BU", "QU", "WC", "OD", "AP", "LB"]
        # line_13_4_d = ["KG", "YP", "ME", "KB", "HR", "ZP", "CK", "QU", "OD", "AP", "LB"]
        # line_4_f = ["EP", "KG", "ST", "YP", "ME", "CC", "KB", "HR", "MI", "ZP", "CK", "BU", "QU", "OD", "AP", "LB"]

        asset_group = ['EP', 'KG', 'ST', 'YP'] 

        # Step 1.4 Make DST adjustments to load data

        # Adjust enfor DST changes
        enb_demand_data = adjust_for_dst(enb_demand_data)
        print(f"enb_demand_data after DST adjustment: {enb_demand_data.index}")

        # Adjust processed_demand_data for DST changes
        processed_demand_data = adjust_processed_demand_data_for_dst(processed_demand_data)
        print(f"processed_demand_data after DST adjustment: {processed_demand_data.index}")

        # Debugging: Print initial date ranges before filtering
        print(f"enb_demand_data min/max dates pre filter: {enb_demand_data.index.min()}, and {enb_demand_data.index.max()}")
        print(f"processed_demand_data min/max dates pre filter: {processed_demand_data.index.min()}, and {processed_demand_data.index.max()}")
        # Set date range in system data to match the ENB data
        start_date = enb_demand_data.index.min()
        end_date = enb_demand_data.index.max()
        processed_demand_data = processed_demand_data.loc[start_date:end_date]

        # Debugging: Print date ranges after filtering
        print(f"enb_demand_data min/max dates post filter: {enb_demand_data.index.min()}, and {enb_demand_data.index.max()}")
        print(f"processed_demand_data min/max dates post filter: {processed_demand_data.index.min()}, and {processed_demand_data.index.max()}")


        # Ensure that the indices are aligned
        if not processed_demand_data.index.equals(enb_demand_data.index):
            print("Mismatched dates between the two datasets:")
            mismatched_dates = processed_demand_data.index.difference(enb_demand_data.index)
            if not mismatched_dates.empty:
                print(f"Dates in processed_demand_data not in enb_demand_data: {mismatched_dates}")
            mismatched_dates = enb_demand_data.index.difference(processed_demand_data.index)
            if not mismatched_dates.empty:
                print(f"Dates in enb_demand_data not in processed_demand_data: {mismatched_dates}")
            raise ValueError("The date indices in the two datasets do not match")


        # Convert the datetime objects to the desired format (timeseries_format2)
        processed_demand_data.index = processed_demand_data.index.strftime(timeseries_format2)
        print(f"processed_demand_data after format change: {processed_demand_data.head()}")

        review_enb_load(
            processed_demand_data,
            enb_demand_data,
            timeseries_format2,
            asset_group,
            peak_demand_methodology,
            gbl.gbl_tracked_loaded_dict_json_file_data)
    else:
        pass
        #-------------------------------------------------
        #Part G: Calculate DTS/STS Transmission Costs
        #-------------------------------------------------
        # Reload Json Path in the even that the python routine starts from this point in the code
        # json_file_path_data_json = os.path.join(json_folder_path, active_price_run_file_name_str)
        # Load the dictionary from the JSON file
        # with open(gbl.gbl_json_file_path_data_json, 'r') as json_file:
        #     gbl.gbl_tracked_loaded_dict_json_file_data = json.load(json_file)
        #****************************************************************************************** 
        Active = create_trans_costs_flag

        if Active:
            if not runpipe_all_flags_true:
                load_loaded_json_to_global()
                create_global_dict_shortcut_path()
                load_powergen_json_to_global()
            
            # File Attributes
            csv_file = r'C:\Users\kaczanor\OneDrive - Enbridge Inc\Documents\Python\EDC Hourly Capacity Factor Q2 2024\inputs\AESO_Tariff_Data\aeso_tariff_appendix_one_bill_estimator.csv'
            aeso_tariff = 'AESO 2024'

            # ESTIMATES
            EstimateType = 'DTS Only'  # 'DTS Only, STS Only, DTS and STS' (a) Is estimate for Rate DTS, Rate STS or both?
            OtherParticipant = False # (b) Any other market participant at substation?
            PrimaryServiceCredit = False  # (c) Does Primary Service Credit apply to service?
            is_this_regulated_generating_unit = False  # (d) Is this a regulated generating unit within its base life?
            RiderC = False  # (e) Include Deferral Account Adjustment Rider C?
            RiderE = False  # (f) Include Losses Calibration Factor Rider E?
            RiderF = False  # (g) Include Balancing Pool Consumer Allocation Rider F?
            RiderJ = False  # (h) Include Wind Forecasting Service Cost Recovery Rider J?
            contract_capacity_dts = 20.0
            estimate_for_rate_sts = 0.0
            contract_capacity_other = 0.0 

            create_transmission_cost(
                        csv_file, 
                        aeso_tariff,
                        EstimateType,
                        OtherParticipant,
                        PrimaryServiceCredit,
                        is_this_regulated_generating_unit,
                        RiderC,
                        RiderE,
                        RiderF,
                        RiderJ,
                        contract_capacity_dts,
                        estimate_for_rate_sts,
                        contract_capacity_other
                    )
        else:
            pass

        #-------------------------------------------------
        #Part H: Optimize Power Generation Capacity Sizing
        #-----------------------------------------------


        #-------------------------------------------------
        # PART B: Define method for ajusting forecast data
        #-------------------------------------------------

        #-------------------------------------------------
        # PART B(i): Calculate Top % Hour Pricing for both Historical and Forecast Data
        #-------------------------------------------------

        #-------------------------------------------------
        # PART C: Make adjustments to forecast data
        #-------------------------------------------------
        '''
        This code adjustes the forecast data by applying different options for adjustment

        Option 1:  Hard Price Caps in Top X% hours 

        Option 2:  Impute Historical Data Buckets on Forecast in Top X% hours 

        Option 3:  Other

        Option 4:  Other

        Option 5:  Other
        '''
        ##################################################
        # Step 5: View adjusted data
        ##################################################

if __name__ == "__main__":
    main()