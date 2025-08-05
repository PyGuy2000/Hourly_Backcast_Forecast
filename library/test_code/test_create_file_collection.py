import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from library.class_objects.forecast_files.other_classes.classes import TrackedDict, ForecastFile


from functions import create_file_from_string



def function(output_data_path_str, csv_folder_name_str, p50_output_file_var, data_years, folder_name):
    # Extracting the start and end year from the tuple
    start_year, end_year = data_years
    
    # Constructing the file name
    file_name = f"Date-{start_year}-{end_year}_{p50_output_file_var}"
    
    # Constructing the full file path
    full_path = os.path.join(output_data_path_str.replace("/", "//"), csv_folder_name_str, folder_name, file_name)
    
    return full_path


# Create a dictionary to hold ForecastFile objects for easy lookup by key

input_data_path_str =  r'C:\Users\kaczanor\OneDrive - Enbridge Inc\Documents\Python\EDC Hourly Capacity Factor Q2 2024\inputs'
output_data_path_str = r'C:\Users\kaczanor\OneDrive - Enbridge Inc\Documents\Python\EDC Hourly Capacity Factor Q2 2024\outputs'
csv_folder_name_str = 'csv_data'
image_folder_name_str = 'image_data'
json_folder_name_str = 'json_data'
excel_folder_name_str = 'excel_data'
excel_template_folder_name = 'template_excel_output_files'
simulation_summary_tmplt_filename = 'simluation_annual_monthly_output_file_template.xlsx'
processed_historical_folder_name_str = 'Processed Historical Data'
historical_data_filename_str = 'AB_Historical_Prices/merged_pool_price_data_2000_to_2024.csv'
active_price_run_file_name_str = 'file_data.json'
output_file_name_str = 'output_data.json'

gbase_output_path = r'C:\Users\kaczanor\OneDrive - Enbridge Inc\Documents\Python\EDC Hourly Capacity Factor Q2 2024'
csv_output_path = os.path.join(output_data_path_str, csv_folder_name_str)
print(csv_output_path)
excel_output_path = os.path.join(output_data_path_str, excel_folder_name_str)
input_path = os.path.join(input_data_path_str)
image_data_path = os.path.join(output_data_path_str,image_folder_name_str)
historic_data_path = os.path.join(output_data_path_str, historical_data_filename_str)
processed_historic_data_path = os.path.join(output_data_path_str, processed_historical_folder_name_str)
excel_template_path = os.path.join(gbase_output_path, excel_template_folder_name, simulation_summary_tmplt_filename )

# json folder path for saved input dictionary objects
json_folder_path = os.path.join(output_data_path_str, json_folder_name_str)

# temp folder path
temp_path = r'C:\Users\kaczanor\OneDrive - Enbridge Inc\Documents\Python\EDC Hourly Capacity Factor Q2 2024\outputs\csv_data\temp_data'

# File Template Names
power_gen_dict_filename = 'power_generation_dict.json'

# Create json path
json_file_path_data_json = os.path.join(json_folder_path, active_price_run_file_name_str)

#-------------------------------------------------
# Forecast Input/Output File Attributes
#-------------------------------------------------
# INPUT FILE ATTRIBUTES

#Create name for the p50_hourly_spot_electricity.csv file
p50_output_file_var = 'p50_hourly_spot_electricity.csv'
p_template_filename = '_hourly_spot_electricity.csv'

p10_label = 'P10'
p25_label = 'P25'
p50_label = 'P50'
p75_label = 'P75'
p90_label = 'P90'

historical_top_percent_summary_filename_str = 'Historical_top_hour_percentage_summary.csv'

# Function #1
# Create electricity foreacst dictionaries
power_generation_dict = {}


#-------------------------------------------------
# Special Note on file names:

#-------------------------------------------------
# EDC Price Forecasting Data
#-------------------------------------------------
# Forecaster Name
edc_forecaster_name = 'EDC'
#..........................
#Inputs
#..........................
# Use prefix on variables 'edc_'
edc_stochastic_seeds = 50
edc_stochastic_seeds_used = 3

 # Price Forecasts Active Flag
Q2_2023_EDC_data_flag = False
Q2_2024_EDC_data_flag = False
Q3_2024_EDC_data_flag = False
Q4_2024_EDC_data_flag = True
Q5_2024_EDC_data_flag = False

# Input File Names
Q2_2023_EDC_data = 'Q2-2023 Hourly Data.xlsx'
Q2_2024_EDC_data = 'Q2-2024 Hourly Data.xlsx'
Q3_2024_EDC_data = 'Q3-2024 Hourly Data.xlsx'
Q4_2024_EDC_data = 'Q4-2024 Hourly Data.xlsx'
Q5_2024_EDC_data = 'Q5-2024 Hourly Data.xlsx'
#Add more with same format

# Forecast Term (years)
Q2_2023_EDC_data_years = (2023,2037)
Q2_2024_EDC_data_years = (2024,2038)
Q3_2024_EDC_data_years = (2024,2038)
Q4_2024_EDC_data_years = (2024,2038)
Q5_2024_EDC_data_years = (2024,2038)
#Add more with same format


# Input Folder Name
Q2_2023_EDC_folder_name = "EDC Q2 2023 Forecast Data"
Q2_2024_EDC_folder_name = "EDC Q2 2024 Forecast Data"
Q3_2024_EDC_folder_name = "EDC Q3 2024 Forecast Data"
Q4_2024_EDC_folder_name = "EDC Q4 2024 Forecast Data"
Q5_2024_EDC_folder_name = "EDC Q5 2024 Forecast Data"
#Add more with same format


# Input File Path
edcq2_2023_base_path_processed_data = os.path.join(csv_output_path,edc_forecaster_name, Q2_2023_EDC_folder_name)
edcq2_2024_base_path_processed_data = os.path.join(csv_output_path,edc_forecaster_name, Q2_2024_EDC_folder_name)
edcq3_2024_base_path_processed_data = os.path.join(csv_output_path,edc_forecaster_name, Q3_2024_EDC_folder_name)
edcq4_2024_base_path_processed_data = os.path.join(csv_output_path,edc_forecaster_name, Q4_2024_EDC_folder_name)
edcq5_2024_base_path_processed_data = os.path.join(csv_output_path,edc_forecaster_name, Q5_2024_EDC_folder_name)
#Add more with same format


# Processed P50 File Path
edcq2_2023_path = function(output_data_path_str, csv_folder_name_str, p50_output_file_var, Q2_2023_EDC_data_years, Q2_2023_EDC_folder_name)
edcq2_2024_path = function(output_data_path_str, csv_folder_name_str, p50_output_file_var, Q2_2024_EDC_data_years, Q2_2024_EDC_folder_name)
edcq3_2024_path = function(output_data_path_str, csv_folder_name_str, p50_output_file_var, Q3_2024_EDC_data_years, Q3_2024_EDC_folder_name)
edcq4_2024_path = function(output_data_path_str, csv_folder_name_str, p50_output_file_var, Q4_2024_EDC_data_years, Q4_2024_EDC_folder_name)
edcq5_2024_path = function(output_data_path_str, csv_folder_name_str, p50_output_file_var, Q5_2024_EDC_data_years, Q5_2024_EDC_folder_name)
#Add more with same format

#Create Dictionaries

forecaster_name_dict = {
    'EDC': edc_forecaster_name  # Using the acronym 'EDC' as the key
}

# Input File Names
input_filename_dict = {
    'Q2_2023_EDC_data' : Q2_2023_EDC_data,
    'Q2_2024_EDC_data' : Q2_2024_EDC_data,
    'Q3_2024_EDC_data':  Q3_2024_EDC_data,
    'Q4_2024_EDC_data':  Q4_2024_EDC_data, 
    'Q5_2024_EDC_data':  Q5_2024_EDC_data
    } 

# Forecast Term (years)
forecast_years_dict = {
    'Q2_2023_EDC_data_years' : Q2_2023_EDC_data_years, 
    'Q2_2024_EDC_data_years' : Q2_2024_EDC_data_years, 
    'Q3_2024_EDC_data_years' : Q3_2024_EDC_data_years, 
    'Q4_2024_EDC_data_years' : Q4_2024_EDC_data_years, 
    'Q5_2024_EDC_data_years' : Q5_2024_EDC_data_years
    }

# Input Folder Name
forecast_folder_dict = {
    'Q2_2023_EDC_folder_name' : Q2_2023_EDC_folder_name, 
    'Q2_2024_EDC_folder_name' : Q2_2024_EDC_folder_name, 
    'Q3_2024_EDC_folder_name' : Q3_2024_EDC_folder_name, 
    'Q4_2024_EDC_folder_name' : Q4_2024_EDC_folder_name, 
    'Q5_2024_EDC_folder_name' : Q5_2024_EDC_folder_name
    }

# Input File Path
forecast_raw_data_filepath_dict = {
    'edcq2_2023_base_path_processed_data' : edcq2_2023_base_path_processed_data, 
    'edcq2_2024_base_path_processed_data': edcq2_2024_base_path_processed_data, 
    'edcq3_2024_base_path_processed_data' : edcq3_2024_base_path_processed_data, 
    'edcq4_2024_base_path_processed_data' : edcq4_2024_base_path_processed_data,
    'edcq5_2024_base_path_processed_data' : edcq5_2024_base_path_processed_data
    }

# Processed P50 File Path
forecast_p50_filepath_dict = {
    'edcq2_2023_path' : edcq2_2023_path, 
    'edcq2_2024_path' : edcq2_2024_path, 
    'edcq3_2024_path' : edcq3_2024_path, 
    'edcq4_2024_path' : edcq4_2024_path, 
    'edcq5_2024_path' : edcq5_2024_path
    } 

forecast_data_flag_dict = {
    'Q2_2023_EDC_data_flag' : Q2_2023_EDC_data_flag,
    'Q2_2024_EDC_data_flag' : Q2_2024_EDC_data_flag,
    'Q3_2024_EDC_data_flag' : Q3_2024_EDC_data_flag,
    'Q4_2024_EDC_data_flag' : Q4_2024_EDC_data_flag,
    'Q5_2024_EDC_data_flag' : Q5_2024_EDC_data_flag
}

output_file_attributes_dict = {
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
    "monthly_natgas_recievedratio_output_file_var": ""
}

# INPUT FILE ATTRIBUTES

# Output File Names
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

#Create Output File Name Dictionary
output_file_dict = {}

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


# Creation dictionary of files
forecast_files_dict = {}

for key, filename in input_filename_dict.items():
    forecaster_acronym = key.split('_')[2]
    forecaster_name = forecaster_name_dict.get(forecaster_acronym)

    if forecaster_name:
        start_year, end_year = forecast_years_dict[f"{key}_years"]
        folder_name = forecast_folder_dict[f"{key}_folder_name"]

        # Create the ForecastFile object
        forecast_file = ForecastFile(
            forecaster_name=forecaster_name,
            key=key,
            filename=filename,
            start_year=start_year,
            end_year=end_year,
            folder_name=folder_name,
            input_path=input_path,
            csv_output_path=csv_output_path
        )

        # Add it to the dictionary using a meaningful key
        forecast_files_dict[key] = forecast_file


# #####################################
# Access a specific file by key
file_key = 'Q2_2024_EDC_data'
forecast_file = forecast_files_dict[file_key]

print(f"Forecaster: {forecast_file.forecaster_name}")
print(f"Input Path: {forecast_file.frcst_input_excel_file_path}")

# Update an attribute
#forecast_file.filename = "NewFilename.xlsx"

# ################################
# def update_forecast_files(forecast_files, new_filename):
#     for forecast_file in forecast_files:
#         # Update the filename attribute
#         forecast_file.filename = new_filename
#         print(f"Updated filename for {forecast_file.key} to {forecast_file.filename}")

# # Call the function
# update_forecast_files(forecast_files, "UpdatedFilename.xlsx")
################################
# def update_specific_file(forecast_files_dict, key, new_filename):
#     if key in forecast_files_dict:
#         forecast_files_dict[key].filename = new_filename
#         print(f"Updated filename for {key} to {forecast_files_dict[key].filename}")

# # Update a specific file
# update_specific_file(forecast_files_dict, 'Q2_2024_EDC_data', 'UpdatedFileForQ2_2024.xlsx')

