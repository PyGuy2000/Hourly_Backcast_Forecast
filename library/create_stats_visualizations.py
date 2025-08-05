from library import config
from library import globals as gbl

from library.functions import (
    save_plot, 
    show_visualizations_func, 
    remove_folder_contents, 
    #csv_save_function, 
    print_lcoe_table, 
    paste_csv_to_excel,
    adjust_excel_ranges,
    #create_excel_output_table
)

from library.class_objects.other_classes.classes import TrackedDict, ForecastFile

import pandas as pd
import os
import json
import seaborn as sns
import matplotlib.pyplot as plt
from joypy import joyplot  # Make sure to import joyplot
import matplotlib.cm as cm
from matplotlib.ticker import FuncFormatter
from matplotlib.dates import DateFormatter
from tqdm import tqdm
import numpy as np
import calendar
from openpyxl import load_workbook
from pandas.tseries.holiday import AbstractHolidayCalendar, Holiday, USFederalHolidayCalendar
from datetime import time

'''
Manages visualizations for the project
'''



###############################################
# Helper Functions for Calculating Capacity Factors and Recieved/Capture Price 
###############################################

def plant_running(
    plant_capacity_mw_net, 
    startcost_amort_hours, 
    electricity_price, 
    natural_gas_price, 
    heat_rate, 
    co2_tax, 
    start_up_cost_per_start, 
    non_fuel_vom, 
    running_status_count, 
    cf_limit_reached
    ):
    

        threshold_price = heat_rate * natural_gas_price + co2_tax + (start_up_cost_per_start/plant_capacity_mw_net/startcost_amort_hours) + non_fuel_vom
        
        if cf_limit_reached:
            running_status = False
        else:
            running_status = electricity_price >= threshold_price
            running_status_count =+ 1
            #print(f"running_status: {running_status}, electricity_price: {electricity_price}, threshold_price: {threshold_price}")
            #transfer running_status, electricity_price, threshold_price to csv file

        return running_status, threshold_price
###############################################
def plant_capture_price(electricity_price, running_status):
    
    capture_price = np.where(running_status, electricity_price, np.nan)
    market_power_price = electricity_price  # Keep all values, no NaNs here

    # The data being returned is in hourly strips

    return capture_price, market_power_price
###############################################
#new
def natgas_capture_price(natural_gas_price, running_status):
    natgas_capture_price = np.where(running_status, natural_gas_price, np.nan)
    market_natgas_price = natural_gas_price  # Keep all values, no NaNs here
    return natgas_capture_price, market_natgas_price
###############################################
# Function to calculate running status based on strategy
def calculate_running_status(
                strategy, 
                STRATEGY_CF_CAP, 
                STRATEGY_PERFECT_FORESIGHT, 
                STRATEGY_PREDICTIVE_BIDDING, 
                df, 
                year_data, 
                seed, 
                month, 
                year, 
                plant_capacity_mw_net, 
                startcost_amort_hours, 
                cf_limit,
                monthly_index_rate, 
                adj_non_fuel_variable_bid_costs, 
                start_up_cost_per_start, 
                #carbon_dict, 
                heat_rate, 
                emissions_intensity, 
                base_line, 
                start_year
                ):
    
    '''
    This is the heart of the merit test logic and measures whether the power plant
    is in merit in a give hour subject to its, cost, power prices, and its bidding strategy.

    Data for the current

    It returns a list of hourly stats for the current month and sends them back to the 
    '''


    running_status_count = 0
    
    #Calc Max energy during month in MWh
    days_in_month = calendar.monthrange(year, month)[1]
    total_possible_capacity = plant_capacity_mw_net * days_in_month * 24
    
    #Filter the annual data to get the specific month
    month_data = year_data[year_data.index.month == month]
    #print(f"month_data: {month_data}")
    
    # Capacity Factor Limit Threshold
    # Plant will run as much as it can within this limit hourly
    if strategy == STRATEGY_CF_CAP:
        current_month_cum_energy = 0

        #Create lists to hold hourly data
        monthly_running_status = []
        threshold_price_list = []

        # This loop is monthly.  The month is an hourly strip (744 or 720 hours).
        # The calculations for the hours are done using the np.array functions on the entire month.
        for i in range(len(month_data)):
            # Test current month cumulative energy against the capacity factor limit
            if current_month_cum_energy / total_possible_capacity > cf_limit:
                cf_limit_reached = True
                #print(f" cf_limit: {cf_limit}, and cf_limit_reached: {cf_limit_reached}")
                break
            else:
                cf_limit_reached = False
                #print(f" cf_limit: {cf_limit}, and cf_limit_reached: {cf_limit_reached}")

            # Extract power price, gas price, carbon cost, and non_fuel_om
            # for the current hour
            power_price = month_data[f'Seed {seed}_Power'].iloc[i]
            gas_price = month_data[f'Seed {seed}_Gas'].iloc[i]
            carbon_cost = gbl.gbl_carbon_tax_annual_dict[str(year)] * (emissions_intensity - base_line)
            non_fuel_vom = adj_non_fuel_variable_bid_costs * (1 + monthly_index_rate) ** ((year - start_year) * 12 + month)

            # Pass current hour data to function which tests whether 
            # the power plant is in merit based on a comparison of its
            # variable operating costs to the current hour spot power price
            running_status, threshold_price = plant_running(

                plant_capacity_mw_net, 
                startcost_amort_hours, 
                power_price, 
                gas_price, 
                heat_rate, 
                carbon_cost, 
                start_up_cost_per_start, 
                non_fuel_vom * (1 + monthly_index_rate) ** ((year - start_year) * 12 + month),
                running_status_count, 
                cf_limit_reached
            )

            # Pass current hour results to monthly data object
            monthly_running_status.append(running_status)
            threshold_price_list.append(threshold_price)

            if running_status:
                current_month_cum_energy += plant_capacity_mw_net

        # Convert list data to array data using np.array to pass back to the 
        # Calculate_Merit_Test() function which is a monthly function
        monthly_running_status = np.array(monthly_running_status)
        threshold_price_list = np.array(threshold_price_list)
        
        # The data being returned is a collection of hours for the month
        return monthly_running_status, threshold_price_list, days_in_month

    elif strategy == STRATEGY_PERFECT_FORESIGHT:
        year_data_sorted = year_data.sort_values(by=f'Seed {seed}_Power', ascending=False)
        month_data_sorted = year_data_sorted[year_data_sorted.index.month == month]

        month_capacity_limit = plant_capacity_mw_net * days_in_month * 24 * cf_limit
        cumulative_energy = 0
        monthly_running_status = np.zeros(len(month_data), dtype=bool)
        threshold_price_list = np.zeros(len(month_data))

        # This loop is monthly.  The month is an hourly strip (744 or 720 hours).
        # The calculations for the hours are done using the np.array functions on the entire month.
        for i in range(len(month_data_sorted)):
            if cumulative_energy >= month_capacity_limit:
                break
            
            power_price = month_data_sorted[f'Seed {seed}_Power'].iloc[i]
            gas_price = month_data_sorted[f'Seed {seed}_Gas'].iloc[i]
            carbon_cost = gbl.gbl_carbon_tax_annual_dict[str(year)] * (emissions_intensity - base_line)
            bid_cost = adj_non_fuel_variable_bid_costs * (1 + monthly_index_rate) ** ((year - start_year) * 12 + month)
            
            #Check for if the power price is greater than the bid cost
            if power_price >= bid_cost:
                running_status = True
                threshold_price = plant_running(
                    plant_capacity_mw_net, 
                    startcost_amort_hours, 
                    power_price, 
                    gas_price, 
                    heat_rate, 
                    carbon_cost, 
                    start_up_cost_per_start,
                    non_fuel_vom * (1 + monthly_index_rate) ** ((year - start_year) * 12 + month),
                    running_status_count,
                    False
                )[1]

                month_index = month_data.index.get_loc(month_data_sorted.index[i])
                monthly_running_status[month_index] = running_status
                threshold_price_list[month_index] = threshold_price
                cumulative_energy += plant_capacity_mw_net

        monthly_running_status = np.array(monthly_running_status)
        threshold_price_list = np.array(threshold_price_list)

        return monthly_running_status, threshold_price_list, days_in_month

    elif strategy == STRATEGY_PREDICTIVE_BIDDING:
        current_month_cum_energy = 0
        monthly_running_status = []
        threshold_price_list = []

        for i in range(len(month_data)):
            if current_month_cum_energy / total_possible_capacity > cf_limit:
                cf_limit_reached = True
            else:
                cf_limit_reached = False

            # Example metric: On-peak hours
            is_on_peak = month_data.index[i].hour >= 7 and month_data.index[i].hour <= 23

            running_status = is_on_peak and not cf_limit_reached
            threshold_price = plant_running(
                plant_capacity_mw_net, 
                startcost_amort_hours, 
                month_data[f'Seed {seed}_Power'].iloc[i], 
                month_data[f'Seed {seed}_Gas'].iloc[i], 
                heat_rate, 
                gbl.gbl_carbon_tax_annual_dict[str(year)] * (emissions_intensity - base_line), 
                non_fuel_vom * (1 + monthly_index_rate) ** ((year - start_year) * 12 + month),
                cf_limit_reached
            )[1]

            monthly_running_status.append(running_status)
            threshold_price_list.append(threshold_price)

            if running_status:
                current_month_cum_energy += plant_capacity_mw_net

        monthly_running_status = np.array(monthly_running_status)
        threshold_price_list = np.array(threshold_price_list)
    
    return monthly_running_status, threshold_price_list, days_in_month

###############################################
# Helper Class and Functions for Creating Visualizations
###############################################

# Define Canadian holidays
class CanadianHolidayCalendar(AbstractHolidayCalendar):
    rules = [
        Holiday('New Year', month=1, day=1),
        # Add other Canadian holidays here
    ]
###############################################
# Function to label peak hours
def label_peak_hours(data):
    # Ensure that 'date' column is in datetime format
    #data['date'] = pd.to_datetime(data['begin_datetime_mpt'])

    # Get holidays for Canada
    calendar = CanadianHolidayCalendar()
    holidays = calendar.holidays(start=data['DateTime'].min(), end=data['DateTime'].max())

    # Initialize columns
    data['peak_status'] = 'Off-Peak'  # Default value

    # Define on-peak hours (example: 7 AM to 11 PM)
    on_peak_hours = [time(7, 0), time(23, 0)]

    # Label hours as On-Peak or Off-Peak
    for index, row in data.iterrows():
        if row['DateTime'].time() >= on_peak_hours[0] and row['DateTime'].time() <= on_peak_hours[1] and row['DateTime'].date() not in holidays:
            data.at[index, 'peak_status'] = 'On-Peak'

    return data

###############################################
# Function to generate heatmaps
def generate_heatmap(data, title, image_data_path, image_file_name_adder,date_ext):
    
    # Adjust the size of the plot (especially the height)
    plt.figure(figsize=(18, 5))  # Adjust the height here

    # Format the data for annotations with thousand separator
    formatted_data = data.map(lambda x: '{:,}'.format(x) if pd.notnull(x) else '')

    # Create the heatmap with formatted annotations
    ax = sns.heatmap(data, cmap='coolwarm', annot=True, fmt='d')

    # Add labels and title
    ax.set_ylabel('Year')
    ax.set_xlabel('Price Buckets')
    ax.set_title(title)

    # Rotate y-tick labels
    plt.yticks(rotation=45)

#     filename_img = f'{title}.png'
#     save_figure(plt.gcf(), filename_img)  # Assuming 'plt.gcf()' gets the current figure

    #Save image
    #"C:/Users/kaczanor/OneDrive - Enbridge Inc/Documents/Python/EDC Hourly Capacity Factor Q2 2024/outputs/image_data"
    #output_file_var = image_file_name_adder + title + '.png'
    image_output_path = gbl.gbl_output_general_data['image_data_path']
    #output_file = os.path.join(image_output_path, date_ext + output_file_var)
    title = title + date_ext
    save_plot(plt, title, image_output_path)

    # Display the plot
    show_visualizations_func() 
    #plt.show()


# Function to categorize pool prices into buckets
def categorize_price(price):
    if price == 0:
        return "=$0"
    elif 0 < price <= 10:
        return ">0<=10"
    elif 10 < price <= 25:
        return ">10<=25"
    elif 25 < price <= 50:
        return ">25<=50"
    elif 50 < price <= 100:
        return ">50<=100"
    elif 100 < price <= 250:
        return ">100<=250"
    elif 250 < price <= 500:
        return ">250<=500"
    elif 500 < price <= 999:
        return ">500<=999"
    else:
        return ">999"



###############################################
# Helper Functions for Generating P10/P25/P50/P75/P90 Values
###############################################

#-----------------------------------------------------
# Generate P10/P25/P50/P75/P90 Values
#-----------------------------------------------------
def calculate_hourly_percentiles(data):
    """Calculate the P10, P25, P50, P75, P90 percentiles for each hour."""
    percentiles = {
        'P10': np.percentile(data, 10, axis=1),
        'P25': np.percentile(data, 25, axis=1),
        'P50': np.percentile(data, 50, axis=1),
        'P75': np.percentile(data, 75, axis=1),
        'P90': np.percentile(data, 90, axis=1)
    }
    return percentiles
#-----------------------------------------------------
def categorize_hourly_forecast(df, start_year, end_year, stochastic_seeds_used, col_header):
#-----------------------------------------------------
    hourly_data = []

    #Ensure the df has a DateTime index and preserve the date column header
    df['DateTime'] = pd.to_datetime(df['DateTime'])
    df.set_index('DateTime', inplace=True)

    # Collect all hourly data for each seed across all years
    #for seed in tqdm(range(1, 51)):
    for seed in tqdm(range(1, stochastic_seeds_used + 1)): 
        seed_hourly_data = []
        for year in tqdm(range(start_year, end_year + 1)):
            year_data = df[df.index.year == year]
            #seed_hourly_data.append(year_data[f'Seed {seed}_Power'])
            seed_hourly_data.append(year_data[f'Seed {seed}{col_header}'])
        hourly_data.append(pd.concat(seed_hourly_data))

    # Convert the list of Series to a DataFrame
    hourly_data_df = pd.concat(hourly_data, axis=1)

    # Calculate percentiles across seeds for each hour
    percentiles = calculate_hourly_percentiles(hourly_data_df.values)

    # Create a DataFrame to hold the percentile data
    percentiles_df = pd.DataFrame(percentiles, index=hourly_data_df.index)

    return percentiles_df
#-----------------------------------------------------
def calculate_annual_P50(hourly_percentiles_df, start_year, end_year):
#-----------------------------------------------------
    annual_P50 = {}
    for year in range(start_year, end_year + 1):
        # Extract data for the current year
        year_data = hourly_percentiles_df[hourly_percentiles_df.index.year == year]
        # Calculate the annual P50 as the average of hourly P50 values for the year
        annual_P50[year] = year_data['P50'].mean()
    return annual_P50
#-----------------------------------------------------
def calculate_monthly_P50_profiles(df, start_year, end_year,stochastic_seeds_used, col_header):
#-----------------------------------------------------
    monthly_P50_profiles = {}
    for year in range(start_year, end_year + 1):
        print(f"Processing year: {year}")
        # Initialize a DataFrame to store monthly P50 profiles
        monthly_data = {month: [] for month in range(1, 13)}
        
        #for seed in range(1, 51):
        for seed in range(1, stochastic_seeds_used):
            #seed_year_data = df[df.index.year == year][f'Seed {seed}_Power']
            seed_year_data = df[df.index.year == year][f'Seed {seed}{col_header}']
            for month in range(1, 13):
                monthly_data[month].append(seed_year_data[seed_year_data.index.month == month].mean())
        
        # Calculate P50 for each month
        monthly_P50 = {month: np.median(monthly_data[month]) for month in monthly_data}
        monthly_P50_profiles[year] = monthly_P50
    return monthly_P50_profiles
#-----------------------------------------------------
def calculate_annual_percentiles(hourly_percentiles_df, start_year, end_year):
#-----------------------------------------------------    
    annual_percentiles = {}
    for year in range(start_year, end_year + 1):
        # Extract data for the current year
        year_data = hourly_percentiles_df[hourly_percentiles_df.index.year == year]
        # Calculate the annual percentiles directly from hourly percentiles
        annual_percentiles[year] = {
            'P10': np.percentile(year_data['P50'], 10),
            'P25': np.percentile(year_data['P50'], 25),
            'P50': np.percentile(year_data['P50'], 50),
            'P75': np.percentile(year_data['P50'], 75),
            'P90': np.percentile(year_data['P50'], 90)
        }
    return annual_percentiles
#-----------------------------------------------------
def normalize_hourly_percentiles(hourly_percentiles_df, annual_percentiles, start_year, end_year):
#-----------------------------------------------------
    normalized_hourly_percentiles = hourly_percentiles_df.copy()
    
    for year in range(start_year, end_year + 1):
        year_data = normalized_hourly_percentiles[normalized_hourly_percentiles.index.year == year]
        annual_data = annual_percentiles[year]
        
        for col in ['P10', 'P25', 'P50', 'P75', 'P90']:
            normalized_hourly_percentiles.loc[year_data.index, col] = (
                year_data[col] * (annual_data[col] / year_data['P50'].mean())
            )
    
    return normalized_hourly_percentiles

#-----------------------------------------------------
def normalize_monthly_profiles(monthly_profiles, annual_P50):
#-----------------------------------------------------
    normalized_profiles = {}
    for year in monthly_profiles:
        print(f"Normalizing year: {year}")
        monthly_profile = pd.Series(monthly_profiles[year])
        annual_avg = monthly_profile.mean()
        normalization_factor = annual_P50[year] / annual_avg
        normalized_profiles[year] = monthly_profile * normalization_factor
    return normalized_profiles

#-------------------------------------------------
def calcStats_on_data(
    #gbl_tracked_loaded_dict_json_file_data
     ):
#-------------------------------------------------
    print("calcStats_on_data called")
    for key1, value1 in gbl.gbl_tracked_loaded_dict_json_file_data["Output_Data"]['Processed_Price_Forecast'].items():
        print(f"key: {key1}, value: {value1}")
    
        ### Steps
        '''
        1. **Load the CSV file into a DataFrame.**
        2. **Create a Boolean test for each hour to determine if the proxy power-generating asset would run.**
        3. **Calculate the capacity for each hour based on the Boolean test and the plant's capacity.**
        4. **Calculate the annual capacity factor for each seed and year.**
        5. **Create a summary DataFrame with the results for each seed and year.**
        6. **Visualize the results with ridgeline charts.**

        '''
        # Set up shortcut paths to the json file

        # This is short cut variable so that I do not need to keep hard-coding
        # 'Source_Attributes' when I want to pull an item underneath it.  I am doing this 
        # becuase the loop only goes down to the loaded_dict["Input_Data"]["Price_Forecast"] level but
        # the variables I need are 1 more layer down loaded_dict["Input_Data"]["Price_Forecast"]['Source_Attributes'].
        # source_attributes = value['Source_Attributes']
        # target_attributes = value['Target_Attributes']
        # general_data = value['Input_Data']['General_Data'] 

       
        output_file_attributes = value1['Output_File_Attributes']

        frcst_output_csv_file_path = output_file_attributes['frcst_output_csv_file_path']
        output_file_var = output_file_attributes['consolidated_hourly']
        output_data_path = os.path.join(frcst_output_csv_file_path, output_file_var)
        print(f" output_data_path: {output_data_path}")

        for key2, value2 in gbl.gbl_tracked_loaded_dict_json_file_data["Input_Data"]['Price_Forecast'].items():
                
            input_file_attributes = value2['Input_File_Attributes']

            g_start_year = input_file_attributes['start_year']
            g_end_year = input_file_attributes['end_year']
            date_ext = f'Date-{g_start_year}-{g_end_year}_'
            stochastic_seeds = input_file_attributes['stochastic_seeds']
            stochastic_seeds_used = input_file_attributes['stochastic_seeds_used']

        ##############################
        #PART A: Separate Electricity Prices and Natuaral Gas Prices
        ##############################
        #-----------------------------------------------
        '''
        This code was written around reformatting the existing format that the EDC data is provided
        in for their 15-year hourly forecasts. That data is an excel file that has the following workskeets:
        
        'Summary' worksheet
        15x worksheets with hourly data named based on the 4 digit years they represent (eg. 2024, 2025, 2026, 2027).

        They layout of these annual worksheets look as follows:
        1)  starting in row 6 column header Date (Column A), HE (Column B) and 50x columns for 20 seeds of electricity data which are named
        as Seed 1, Seed 2, ....Seed 50. This spans from column A to AZ or 52 columns

        I then delete the first 5 rows as they are not used.
        
        Example
        Date	HE	Seed 1	Seed 2	Seed 3 ....seed 50

        There are 2x empty columns (Columns BA an BB or columns 53 and 54), and
        2) 50x columns for 50 seeds of natural gas data which are named 
        as Seed 1, Seed 2, ....Seed 50. This spans from column BC to CZ or an additiona 50 columns which take us from column 55 to 104

        As such the number of column are in determined in the EDC data by the number of seeds of data for both electricity and natural gas,
        as well as two additional columns for the Date and HE columns and the 2x empty columns between the electricity and natural gas data.

        If hourly data is provided by another vendour then that data will have to be set up in a similar format to be able to be processed by this code.
        If that data is only 1x run (1x stochastic seed) then that data needs to be set up as follows

        Date	HE	Seed 1	blank_column_1, blank_colunm_2, Seed_1

        '''

        start_year = g_start_year
        end_year = g_end_year

        #### 1. Load the CSV file
        df_consolidated_elec_natgas = pd.read_csv(output_data_path)

        # Define column start and end indices
        electricity_col_start = 2
        electricity_col_end = stochastic_seeds + electricity_col_start
        electricity_col_end_used = stochastic_seeds_used + electricity_col_start

        nat_gas_col_start = electricity_col_end + 2
        nat_gas_col_end = electricity_col_end + stochastic_seeds + 2
        nat_gas_col_end_used = electricity_col_end + stochastic_seeds_used + 2

        #print(f" electricity columns: {df_consolidated_elec_natgas .columns[2: 52]}")
        print(f" electricity columns: {df_consolidated_elec_natgas .columns[electricity_col_start: electricity_col_end_used]}")

        #print(f" nat gas columns: {df_consolidated_elec_natgas .columns[54:104]}")
        print(f" nat gas columns: {df_consolidated_elec_natgas .columns[nat_gas_col_start:nat_gas_col_end_used]}")

        # Optionally, set the DateTime column as the index and drop the old Date column if not needed
        df_consolidated_elec_natgas ['DateTime'] = pd.to_datetime(df_consolidated_elec_natgas ['DateTime'])
        df_consolidated_elec_natgas .set_index('DateTime', inplace=True)

        # Print the original columns before renaming to verify
        print("Columns before renaming:", df_consolidated_elec_natgas .columns)

        # Ensure unique column names by removing any '.1' or other suffixes
        cols=pd.Series(df_consolidated_elec_natgas .columns)
        for dup in cols[cols.duplicated()].unique(): 
            cols[cols[cols == dup].index.values.tolist()] = [dup + '_' + str(i) if i != 0 else dup for i in range(sum(cols == dup))]
        df_consolidated_elec_natgas .columns=cols

        # Print the columns after ensuring uniqueness
        print("Columns after ensuring uniqueness:", df_consolidated_elec_natgas .columns)

        # Define the column renaming for electricity and natural gas data
        #electricity_columns = {df_consolidated_elec_natgas .columns[i]: f'Seed {i-1}_Power' for i in range(2, 52)}  # Adjusted for 50 seeds
        #natural_gas_columns = {df_consolidated_elec_natgas .columns[i]: f'Seed {i-53}_Gas' for i in range(54, 104)}

        electricity_columns = {df_consolidated_elec_natgas .columns[i]: f'Seed {i-electricity_col_start + 1}_Power' for i in range(electricity_col_start, electricity_col_end_used)}  # Adjusted for 50 seeds
        natural_gas_columns = {df_consolidated_elec_natgas .columns[i]: f'Seed {i-(electricity_col_end + 1)}_Gas' for i in range(nat_gas_col_start, nat_gas_col_end_used)}

        # Print the renaming mappings for debugging
        print("Electricity columns renaming map:", electricity_columns)
        print("Natural gas columns renaming map:", natural_gas_columns)

        # Rename columns
        df_consolidated_elec_natgas .rename(columns={**electricity_columns, **natural_gas_columns}, inplace=True)

        # Print the columns after renaming to verify
        print("Columns after renaming:", df_consolidated_elec_natgas .columns)

        print(f" df_consolidated_elec_natgas : {df_consolidated_elec_natgas }")

        # Note this needed to be revised when altering the # seeds as df.columns might actually have 50x seed columns
        # But you may have chosen to only use 5x or 10x during testing.
        # The general syntax for slicing is sequence[start:stop:step], where:
        #   start is the index to start the slice (inclusive, default is 0).
        #   stop is the index to end the slice (exclusive).
        #   step is the step size (default is 1).
        # For example, if df_consolidated_elec_natgas .columns is an Index object containing ['A', 'B', 'C', 'D'] and 
        # X is 2, then df_consolidated_elec_natgas .columns[:X] will return an Index object containing ['A', 'B'].
        # So if we choose 5x seeds we need to reference:
        # Date	HE	Seed 1	Seed 2	Seed 3 Seed 4 Seed 5 or the first 7 columns of electrcity
        # and from columns 53 to 57 to account for the first 5x seeds of natural gas 

        print(f"for {stochastic_seeds_used} electricity seeds, take first {electricity_col_end_used} columns")
        print(f"for {stochastic_seeds_used} natural gas seeds, take column {nat_gas_col_start + 1} to {nat_gas_col_end_used}")

        # Check for any potential missing or incorrectly named columns
        expected_power_columns = [f'Seed {i}_Power' for i in range(1, stochastic_seeds_used + 1)]
        expected_gas_columns = [f'Seed {i}_Gas' for i in range(1, stochastic_seeds_used + 1)]

        missing_power_columns = [col for col in expected_power_columns if col not in df_consolidated_elec_natgas .columns]
        missing_gas_columns = [col for col in expected_gas_columns if col not in df_consolidated_elec_natgas .columns]

        # Print missing columns warnings
        if missing_power_columns:
            print(f"Warning: Missing power columns: {missing_power_columns}")
        if missing_gas_columns:
            print(f"Warning: Missing gas columns: {missing_gas_columns}")

        print(f" output_data_path: {output_data_path}")
        df_consolidated_elec_natgas .to_csv(output_data_path, header=True, index=True)


        ##############################
        #PART B: Perform Stats on the Electricity and Natural Gas Prices
        ##############################

        # Separate the tables into two DataFrames using the renamed columns
        electricity_cols = list(electricity_columns.values())
        print(f" electricity_cols: {electricity_cols}")
        natural_gas_cols = list(natural_gas_columns.values())
        print(f" natural_gas_cols: {natural_gas_cols}")

        df_electricity = df_consolidated_elec_natgas[electricity_cols].copy()
        df_natural_gas = df_consolidated_elec_natgas[natural_gas_cols].copy()

        # Debugging step: Print the first few rows of the DataFrames to check if data is loaded correctly
        # print("Electricity DataFrame head:/n", df_electricity.head(10))
        # print("Natural Gas DataFrame head:\n", df_natural_gas.head(10))

        # Ensure the DataFrames are aligned
        df_electricity = df_electricity.sort_index()
        df_natural_gas = df_natural_gas.sort_index()

        # Handle division by zero by replacing zeros in df_natural_gas with NaN
        df_natural_gas.replace(0, pd.NA, inplace=True)

        # Convert columns to float to ensure proper division
        df_electricity = df_electricity.astype(float)
        df_natural_gas = df_natural_gas.astype(float)

        # Align the DataFrames to ensure they are correctly matched for division
        df_electricity, df_natural_gas = df_electricity.align(df_natural_gas, join='inner', axis=0)

        # Perform manual division for market heat rate calculation using a loop
        hourly_market_heat_rate_data = {}
        for col_power, col_gas in zip(df_electricity.columns, df_natural_gas.columns):
            hourly_market_heat_rate_data[col_power] = df_electricity[col_power] / df_natural_gas[col_gas]

        hourly_market_heat_rate = pd.DataFrame(hourly_market_heat_rate_data, index=df_electricity.index)

        #---------------------------------------------
        # Calculate the monthly and annual averages
        #---------------------------------------------
        monthly_avg_electricity = df_electricity.resample('M').mean()
        annual_avg_electricity = df_electricity.resample('Y').mean()

        monthly_avg_natural_gas = df_natural_gas.resample('M').mean()
        annual_avg_natural_gas = df_natural_gas.resample('Y').mean()

        # Perform manual division using a loop for monthly market heat rate calculation 
        monthly_market_heat_rate_data = {}
        for col_power, col_gas in zip(monthly_avg_electricity.columns, monthly_avg_natural_gas.columns):
            monthly_market_heat_rate_data[col_power] = monthly_avg_electricity[col_power] / monthly_avg_natural_gas[col_gas]

        monthly_market_heat_rate = pd.DataFrame(monthly_market_heat_rate_data, index=monthly_avg_electricity.index)

        # Perform manual division using a loop for annual market heat rate calculation 
        annual_market_heat_rate_data = {}
        for col_power, col_gas in zip(annual_avg_electricity.columns, annual_avg_natural_gas.columns):
            annual_market_heat_rate_data[col_power] = annual_avg_electricity[col_power] / annual_avg_natural_gas[col_gas]

        annual_market_heat_rate = pd.DataFrame(annual_market_heat_rate_data, index=annual_avg_electricity.index)

        # Save the results to CSV files if needed
        date_ext = f'Date-{g_start_year}-{g_end_year}_'
        print(f" date_ext: {date_ext}")

        #---------------------------------------------
        #Hourly Market Heat Rate Volatility
        #---------------------------------------------

        output_file_var = gbl.gbl_output_template['hourly_electricity_filename_str']
        output_file = os.path.join(frcst_output_csv_file_path, date_ext + output_file_var)
        print(len(output_file))  # Should be less than 260
        print(f" output_file: {output_file}")
        df_electricity.to_csv(output_file, header=True, index=True)
        output_file_attributes['hourly_electricity'] = output_file


        output_file_var = gbl.gbl_output_template['hourly_natural_gas_filename_str']
        output_file = os.path.join(frcst_output_csv_file_path, date_ext + output_file_var)
        print(len(output_file))  # Should be less than 260
        print(f" output_file: {output_file}")
        df_natural_gas.to_csv(output_file, header=True, index=True)
        output_file_attributes['hourly_natural_gas'] = output_file
        #print(gbl.gbl_tracked_loaded_dict_json_file_data)

        #Check data
        print(hourly_market_heat_rate.head())  # Inspect the first few rows
        print(hourly_market_heat_rate.info())  # Get an overview of the DataFrame
        
        #output_file_var = 'hourly_market_heat_rate.csv'
        output_file_var = gbl.gbl_output_template['hourly_market_heat_rate_filename_str']
        output_file = os.path.join(frcst_output_csv_file_path, date_ext + output_file_var)
        print(len(output_file))  # Should be less than 260
        print(f" output_file: {output_file}")
        hourly_market_heat_rate.to_csv(output_file, header=True, index=True)
        output_file_attributes['hourly_market_heat_rate'] = output_file

        #---------------------------------------------
        #Monthly  Market Heat Rate Volatility
        #---------------------------------------------

        output_file_var = gbl.gbl_output_template['monthly_avg_electricity_filename_str']
        output_file = os.path.join(frcst_output_csv_file_path, date_ext + output_file_var)
        print(f" output_file: {output_file}")
        monthly_avg_electricity.to_csv(output_file, header=True, index=True)
        output_file_attributes['monthly_avg_electricity'] = output_file


        output_file_var = gbl.gbl_output_template['monthly_avg_natural_gas_filename_str']
        output_file = os.path.join(frcst_output_csv_file_path, date_ext + output_file_var)
        print(f" output_file: {output_file}")
        monthly_avg_natural_gas.to_csv(output_file, header=True, index=True)
        output_file_attributes['monthly_avg_natural_gas'] = output_file


        output_file_var = gbl.gbl_output_template['monthly_market_heat_rate_filename_str']
        output_file = os.path.join(frcst_output_csv_file_path, date_ext + output_file_var)
        print(f" output_file: {output_file}")
        monthly_market_heat_rate.to_csv(output_file, header=True, index=True)
        output_file_attributes['monthly_market_heat_rate'] = output_file

        #---------------------------------------------
        #Annual  Market Heat Rate Volatility
        #---------------------------------------------

        output_file_var = gbl.gbl_output_template['annual_avg_electricity_filename_str']
        output_file = os.path.join(frcst_output_csv_file_path, date_ext + output_file_var)
        print(f" output_file: {output_file}")
        annual_avg_electricity.to_csv(output_file, header=True, index=True)
        output_file_attributes['annual_avg_electricity'] = output_file


        output_file_var = gbl.gbl_output_template['annual_avg_natural_gas_filename_str']
        output_file = os.path.join(frcst_output_csv_file_path, date_ext + output_file_var)
        print(f" output_file: {output_file}")
        annual_avg_natural_gas.to_csv(output_file, header=True, index=True)
        output_file_attributes['annual_avg_natural_gas'] = output_file


        output_file_var = gbl.gbl_output_template['annual_market_heat_rate_filename_str']
        output_file = os.path.join(frcst_output_csv_file_path, date_ext + output_file_var)
        print(f" output_file: {output_file}")
        annual_market_heat_rate.to_csv(output_file, header=True, index=True)
        output_file_attributes['annual_market_heat_rate'] = output_file


        #######################
        # Testing code
        print("Loaded dictionary keys:", gbl.gbl_tracked_loaded_dict_json_file_data["Output_Data"]['Processed_Price_Forecast'].keys())
        if gbl.gbl_tracked_loaded_dict_json_file_data["Output_Data"]['Processed_Price_Forecast']:
            first_key = next(iter(gbl.gbl_tracked_loaded_dict_json_file_data["Output_Data"]['Processed_Price_Forecast']))
            print("First key:", first_key)
            print("First key dictionary:", gbl.gbl_tracked_loaded_dict_json_file_data["Output_Data"]['Processed_Price_Forecast'][first_key])
        #######################
    

    gbl.gbl_tracked_loaded_dict_json_file_data.save_to_json(gbl.gbl_json_file_path_loaded)
    
    # Pretty-print the JSON data
    print(json.dumps(gbl.gbl_tracked_loaded_dict_json_file_data, indent=4))

    return df_consolidated_elec_natgas, electricity_cols, natural_gas_cols

#-------------------------------------------------
def calculate_percentile_data():
#-------------------------------------------------
        print("calculate_percentile_data called")
        changes = {}
        
        # Load the dictionary from the JSON file
        # And loop through the various price forecasts
        for key1, value1 in gbl.gbl_tracked_loaded_dict_json_file_data["Input_Data"]["Price_Forecast"].items():

            key_name1 = key1
            print(f"key: {key1}, value: {value1}")
            input_file_attributes =value1['Input_File_Attributes']

            #Load the consolidated file saved in Step 2 and pass it to the next function
            #filename = gbl.gbl_output_template['hourly_electricity_filename_str']
            input_data_path = input_file_attributes['base_path_processed_data']
            print(f" input_data_path: {input_data_path}")

            # Moved below
            #df = pd.read_csv(os.path.join(input_data_path, filename))
        
            # Assuming df is your DataFrame containing the data
            start_year = input_file_attributes['start_year']
            end_year = input_file_attributes['end_year']
            date_ext = f'Date-{start_year}-{end_year}_'
            stochastic_seeds = input_file_attributes['stochastic_seeds']
            stochastic_seeds_used = input_file_attributes['stochastic_seeds_used']
        
            for key2, value2 in gbl.gbl_tracked_loaded_dict_json_file_data["Output_Data"]["Processed_Price_Forecast"].items():
                #Define power and natural gas file paths/names
                output_file_attributes =value2['Output_File_Attributes']

                # Power
                hrly_pwr_filename = output_file_attributes['hourly_electricity']
                hrly_pwr_frcst_output_csv_file_path = output_file_attributes['frcst_output_csv_file_path']
                hrly_pwr_output_data_path = os.path.join(hrly_pwr_frcst_output_csv_file_path)
                hrly_pwr_df = pd.read_csv(os.path.join(hrly_pwr_output_data_path, hrly_pwr_filename))
                print(f" hrly_pwr_df: {hrly_pwr_df}")

                #Nat Gas
                hrly_natgas_filename = output_file_attributes['hourly_natural_gas']
                hrly_natgas_frcst_output_csv_file_path = output_file_attributes['frcst_output_csv_file_path']
                hrly_natgas_output_data_path = os.path.join(hrly_natgas_frcst_output_csv_file_path)
                hrly_natgas_df = pd.read_csv(os.path.join(hrly_natgas_output_data_path, hrly_natgas_filename))
                print(f" hrly_natgas_df: {hrly_natgas_df}")
                
                # Categorize Power and Nat Gas Data
                # Power 
                col_header = '_Power'
                hrly_pwr_percentiles_df = categorize_hourly_forecast(hrly_pwr_df, start_year, end_year, stochastic_seeds_used, col_header)
                print(f" percentiles_df: {hrly_pwr_percentiles_df}")

                col_header = '_Gas'
                hrly_natgas_percentiles_df = categorize_hourly_forecast(hrly_natgas_df, start_year, end_year, stochastic_seeds_used, col_header)
                print(f" hrly_natgas_percentiles_df: {hrly_natgas_percentiles_df}")
                #---------------------------------------------

                # Calculate the annual percentiles
                # Power
                hrly_pwr_annual_percentiles = calculate_annual_percentiles(hrly_pwr_percentiles_df, start_year, end_year)
                # Nat Gas
                hrly_natgas_annual_percentiles = calculate_annual_percentiles(hrly_natgas_percentiles_df, start_year, end_year)

                # Normalize the hourly percentiles
                # Power
                hrly_pwr_normalized_hourly_percentiles_df = normalize_hourly_percentiles(hrly_pwr_percentiles_df, hrly_pwr_annual_percentiles, start_year, end_year)
                print(hrly_pwr_normalized_hourly_percentiles_df)

                # Nat Gas
                hrly_natgas_normalized_hourly_percentiles_df = normalize_hourly_percentiles(hrly_natgas_percentiles_df, hrly_natgas_annual_percentiles, start_year, end_year)
                print(hrly_natgas_normalized_hourly_percentiles_df)

                #---------------------------------------------
                # Calculate the annual P50 values
                # Power
                pwr_annual_P50 = calculate_annual_P50(hrly_pwr_percentiles_df, start_year, end_year)
                # NatGas
                natgas_annual_P50 = calculate_annual_P50(hrly_natgas_percentiles_df, start_year, end_year)

                # Calculate monthly P50 profiles
                # Power
                col_header = '_Power'
                pwr_monthly_P50_profiles = calculate_monthly_P50_profiles(hrly_pwr_df, start_year, end_year, stochastic_seeds_used, col_header)
                # Nat Gas
                col_header = '_Gas'
                natgas_monthly_P50_profiles = calculate_monthly_P50_profiles(hrly_natgas_df, start_year, end_year, stochastic_seeds_used, col_header)

                # Check if the monthly profiles were calculated correctly
                if pwr_monthly_P50_profiles is None:
                    print("pwr_monthly_P50_profiles is None. Check the function for errors.")
                elif natgas_monthly_P50_profiles is None:
                    print("natgas_monthly_P50_profiles is None. Check the function for errors.")
                else:
                    print("Monthly P50 profiles calculated successfully.")
                    # Normalize the monthly P50 profiles
                    # Power
                    pwr_normalized_monthly_profiles = normalize_monthly_profiles(pwr_monthly_P50_profiles, pwr_annual_P50)
                    # Nat Gas
                    natgas_normalized_monthly_profiles = normalize_monthly_profiles(natgas_monthly_P50_profiles, natgas_annual_P50)

                    # Convert normalized profiles to a DataFrame for visualization or further processing
                    # Power
                    pwr_normalized_profiles_df = pd.DataFrame(pwr_normalized_monthly_profiles)
                    # NatGas
                    natgas_normalized_profiles_df = pd.DataFrame(natgas_normalized_monthly_profiles)

                    #---------------------------------------------
                    # Display the results
                    print(f" pwr_normalized_profiles_df: {pwr_normalized_profiles_df}")
                    print("Power Annual P50 Values:", pwr_annual_P50)

                    print(f" natgas_normalized_profiles_df: {natgas_normalized_profiles_df}")
                    print("Natural Gas Annual P50 Values:", natgas_annual_P50)
                    
                    # Load percentile data sets into dictionary
                    pwr_percentile_dict = {
                        'P10': hrly_pwr_percentiles_df['P10'],
                        'P25': hrly_pwr_percentiles_df['P25'],
                        'P50': hrly_pwr_percentiles_df['P50'],
                        'P75': hrly_pwr_percentiles_df['P75'],
                        'P90': hrly_pwr_percentiles_df['P90']
                    }

                    natgas_percentile_dict = {
                        'P10': hrly_natgas_percentiles_df['P10'],
                        'P25': hrly_natgas_percentiles_df['P25'],
                        'P50': hrly_natgas_percentiles_df['P50'],
                        'P75': hrly_natgas_percentiles_df['P75'],
                        'P90': hrly_natgas_percentiles_df['P90']
                    }
                    
                    # First Save files as CSV in output directory
                    # Power
                    for pwr_percentile_key, pwr_percentile_value in pwr_percentile_dict.items():
                        print("Power Percentiles extracted:")
                        print(f"{pwr_percentile_key}: {pwr_percentile_value.head()}")
                        #Name the file with P10/P25/P50/P75/P90 prefix
                        pwr_output_file_var = pwr_percentile_key + gbl.gbl_power_p_template_filename
                        print(f" output_file_var: {pwr_output_file_var}")
                        pwr_output_file = os.path.join(hrly_pwr_output_data_path, date_ext + pwr_output_file_var)
                        #Save as CSV file
                        pwr_percentile_value.to_csv(pwr_output_file, header=True, index=True)
                        dict_header = pwr_output_file_var.replace(".csv", "")

                        # Second Update Dictionary with P value files paths
                        output_file_attributes[dict_header] = pwr_output_file

                    # Natural Gas
                    for natgas_percentile_key, natgas_percentile_value in natgas_percentile_dict.items():
                        print("Power Percentiles extracted:")
                        print(f"{natgas_percentile_key}: {natgas_percentile_value.head()}")
                        #Name the file with P10/P25/P50/P75/P90 prefix
                        natgas_output_file_var = natgas_percentile_key + gbl.gbl_natgas_p_template_filename
                        print(f" output_file_var: {natgas_output_file_var}")
                        natgas_output_file = os.path.join(hrly_natgas_output_data_path, date_ext + natgas_output_file_var)
                        #Save as CSV file
                        natgas_percentile_value.to_csv(natgas_output_file, header=True, index=True)
                        dict_header = natgas_output_file_var.replace(".csv", "")

                        # Second Update Dictionary with P value files paths
                        output_file_attributes[dict_header] = natgas_output_file

        
        gbl.gbl_tracked_loaded_dict_json_file_data.save_to_json(gbl.gbl_json_file_path_loaded)

        # Pretty-print the JSON data
        print(json.dumps(gbl.gbl_tracked_loaded_dict_json_file_data, indent=4))

        return  hrly_pwr_percentiles_df, pwr_percentile_dict['P10'], pwr_percentile_dict['P25'], pwr_percentile_dict['P50'], pwr_percentile_dict['P75'], pwr_percentile_dict['P90'], \
                    hrly_natgas_percentiles_df, natgas_percentile_dict['P10'], natgas_percentile_dict['P25'], natgas_percentile_dict['P50'], natgas_percentile_dict['P75'], natgas_percentile_dict['P90']
#-------------------------------------------------
def create_time_series_chart(
                    P10, 
                    P25, 
                    P50, 
                    P75, 
                    P90, 
                    percentiles_df, 
                    chart_title_txt,
                    file_ext_txt,
                     ):
#-------------------------------------------------
    print("create_time_series_chart called")
    # Plotting the data
    plt.figure(figsize=(15, 10))
    
    # Extracting percentiles
    hours = range(len(percentiles_df))

    # Plotting the floating bars
    plt.fill_between(hours, P10, P90, color='lightgrey', label='P10-P90')
    plt.fill_between(hours, P25, P75, color='darkgrey', label='P25-P75')

    # Plotting the P50 line
    plt.plot(hours, P50, color='red', label='P50', linewidth=1)

    # Adding labels and title
    plt.xlabel('Hour')
    plt.ylabel('Price')
    plt.title(chart_title_txt)
    plt.legend()

    # Save Image 
    for key, value in gbl.gbl_tracked_loaded_dict_json_file_data["Input_Data"]["Price_Forecast"].items():
        input_file_attributes = value['Input_File_Attributes']

        image_file_name_adder = key
        start_year = input_file_attributes['start_year']
        end_year = input_file_attributes['end_year']
        date_ext = f'Date-{start_year}-{end_year}_'

        for key, value in gbl.gbl_tracked_loaded_dict_json_file_data["Output_Data"]["Processed_Price_Forecast"].items():
            
            output_file_attributes =value['Output_File_Attributes']

            frcst_output_csv_file_path = output_file_attributes['frcst_output_csv_file_path']
            output_data_path = frcst_output_csv_file_path
            output_file_var = image_file_name_adder + file_ext_txt
            print(gbl.gbl_output_general_data)
            #image_output_file_path = gbl.gbl_output_general_data['image_data_path']
            #image_output_file_path = gbl.gbl_output_general_data['image_data_path']
            image_output_file_path = gbl.gbl_output_general_data['image_data_path']
            title = os.path.join(image_output_file_path, date_ext + output_file_var)
            save_plot(plt, output_file_var, image_output_file_path)

            #output_file_var = 'p50_hourly_spot_electricity.csv'
            output_file = os.path.join(output_data_path, date_ext + output_file_var)
            P50.to_csv(output_file, header=True, index=True)

    # Show the plot
    show_visualizations_func() 
    #plt.show()
    return

#-------------------------------------------------
def create_heat_map_chart(
            percentiles_df
            ):
#-------------------------------------------------
    print("create_heat_map_chart called")
    #Loop through file dictionary to retrieve file meta data
    for key, value in gbl.gbl_tracked_loaded_dict_json_file_data["Input_Data"]["Price_Forecast"].items():

        input_file_attributes =value['Input_File_Attributes']
        P50_data_input_path = input_file_attributes['pwr_file_name_p50']
        start_year = input_file_attributes['start_year']
        end_year = input_file_attributes['end_year']


        for key, value in gbl.gbl_tracked_loaded_dict_json_file_data["Output_Data"]["Processed_Price_Forecast"].items():
            output_file_attributes =value['Output_File_Attributes']

            frcst_output_csv_file_path = output_file_attributes['frcst_output_csv_file_path']
            output_folder_path = frcst_output_csv_file_path
            image_data_path = gbl.gbl_output_general_data['image_data_path']
            # Apply the Time-of-Use function to the dataset
            # moved above
            P50_data_file_name = output_file_attributes['pwr_file_name_p50']
            P50_data_input_path = os.path.join(frcst_output_csv_file_path, P50_data_file_name)
            print(f"P50_data_input_path: {P50_data_input_path}")
            print()
            # /home/rob_kaz/python/projects/Hourly_Backcast_Forecast/outputs/csv_data/edc/EDC Q2 2025 Forecast Base Case Data/Date-2025-2039_p50_hourly_spot_electricity.csv
            # /home/rob_kaz/python/projects/Hourly_Backcast_Forecast/outputs/csv_data/edc/EDC Q2 2025 Forecast Base Case Data/Date-2025-2039_P50_hourly_spot_electricity.csv
            p50_data = pd.read_csv(P50_data_input_path)
            
            #Ensure DateTime is in datetime format
            p50_data['DateTime'] = pd.to_datetime(p50_data['DateTime'])
            p50_values = label_peak_hours(p50_data)

            # Initialize DataFrames to store frequency counts for each type of heatmap
            all_hours_df = pd.DataFrame()
            off_peak_df = pd.DataFrame()
            on_peak_df = pd.DataFrame()

            image_file_name_adder = "P50"
            date_ext = f'Date-{start_year}-{end_year}_'

            processed_price_forecast_items = gbl.gbl_processed_price_forecast

            # Loop through each year
            for year in sorted(p50_values['DateTime'].dt.year.unique()):
                # Identify the indices of the rows for the year
                year_indices = p50_values['DateTime'].dt.year == year

                # Apply the categorization function using loc
                p50_values.loc[year_indices, 'price_category'] = p50_values.loc[year_indices, 'P50'].apply(categorize_price)

                # Frequency analysis for All Hours
                all_hours_counts = p50_values.loc[year_indices, 'price_category'].value_counts().reindex([
                    "=$0", ">0<=10", ">10<=25", ">25<=50", ">50<=100", ">100<=250", ">250<=500", ">500<=999"
                ], fill_value=0)
                all_hours_df[year] = all_hours_counts
                print(f" all_hours_df: {len(all_hours_df)}")

                # Frequency analysis for Off-Peak Hours
                off_peak_indices = (p50_values['peak_status'] == 'Off-Peak') & year_indices
                off_peak_counts = p50_values.loc[off_peak_indices, 'price_category'].value_counts().reindex([
                    "=$0", ">0<=10", ">10<=25", ">25<=50", ">50<=100", ">100<=250", ">250<=500", ">500<=999"
                ], fill_value=0)
                off_peak_df[year] = off_peak_counts
                print(f" off_peak_df: {len(off_peak_df)}")

                # Frequency analysis for On-Peak Hours
                on_peak_indices = (p50_values['peak_status'] == 'On-Peak') & year_indices
                on_peak_counts = p50_values.loc[on_peak_indices, 'price_category'].value_counts().reindex([
                    "=$0", ">0<=10", ">10<=25", ">25<=50", ">50<=100", ">100<=250", ">250<=500", ">500<=999"
                ], fill_value=0)
                on_peak_df[year] = on_peak_counts
                print(f" on_peak_df: {len(on_peak_df)}")

                #---------------------------------------------
                # Generate heatmaps
                generate_heatmap(all_hours_df,' Frequency of P50 Price Buckets - All Hours',image_data_path, image_file_name_adder,date_ext)
                generate_heatmap(off_peak_df, ' Frequency of P50 Price Buckets - Off-Peak Hours',image_data_path, image_file_name_adder,date_ext)
                generate_heatmap(on_peak_df, ' Frequency of P50 Price Buckets - On-Peak Hours',image_data_path, image_file_name_adder,date_ext)

                # Save the data to CSV
                output_file_var = gbl.gbl_output_template['annual_allhour_electricity_heatmap_filename_str']
                output_file = os.path.join(output_folder_path, date_ext + output_file_var)
                all_hours_df.to_csv(output_file, header=True, index=True)
                # Update Dictionary
                output_file_attributes['annual_allhour_electricity_heatmap'] = output_file

                # Save the data to CSV
                output_file_var = gbl.gbl_output_template['annual_offpeak_electricity_heatmap_filename_str']
                output_file = os.path.join(output_folder_path,date_ext + output_file_var)
                off_peak_df.to_csv(output_file, header=True, index=True)
                # Update Dictionary
                output_file_attributes['annual_offpeak_electricity_heatmap'] = output_file

                # Save the data to CSV
                output_file_var = gbl.gbl_output_template['annual_onpeak_electricity_heatmap_filename_str']
                output_file = os.path.join(output_folder_path,date_ext + output_file_var)
                on_peak_df.to_csv(output_file, header=True, index=True)
                # Update Dictionary
                output_file_attributes['annual_onpeak_electricity_heatmap'] = output_file

                #-----------------------------------------------
                #Calculate STD/AVG for Power Prices, Natura Gas Prices, and Market Heat Rate
                # Calculate the STD and AVG for each seed for each year

                # Load from csv folder and ensure the DateTime is in datetime format
                file_path = output_file_attributes['hourly_electricity']
                df_electricity = pd.read_csv(file_path)
                df_electricity['DateTime'] = pd.to_datetime(df_electricity['DateTime'])
                df_electricity.set_index('DateTime', inplace=True)

                # Load from csv folder and ensure the DateTime is in datetime format
                file_path = output_file_attributes['hourly_natural_gas']
                df_natural_gas = pd.read_csv(file_path)
                df_natural_gas['DateTime'] = pd.to_datetime(df_natural_gas['DateTime'])
                df_natural_gas.set_index('DateTime', inplace=True)
                
                # Load from csv folder and ensure the DateTime is in datetime format
                file_path = output_file_attributes['hourly_market_heat_rate']
                df_hourly_market_heat_rate = pd.read_csv(file_path)
                df_hourly_market_heat_rate['DateTime'] = pd.to_datetime(df_hourly_market_heat_rate['DateTime'])
                df_hourly_market_heat_rate.set_index('DateTime', inplace=True)

                avg_hourly_electricity_volatility_by_year = df_electricity.resample('Y').apply(lambda x: x.std() / x.mean())
                avg_hourly_natural_gas_volatility_by_year = df_natural_gas.resample('Y').apply(lambda x: x.std() / x.mean())
                avg_hourly_market_heatrate_volatility_by_year = df_hourly_market_heat_rate.resample('Y').apply(lambda x: x.std() / x.mean())

                #-----------------------------------------------
                #Build Heat Map for Market Heat Rates 
                #-----------------------------------------------

                heatmap_data_market_electricity = avg_hourly_electricity_volatility_by_year  
                heatmap_data_market_naturalgas = avg_hourly_natural_gas_volatility_by_year  
                heatmap_data_market_heatrate = avg_hourly_market_heatrate_volatility_by_year  # No need to transpose as seeds are already columns and years are rows

                # Save the data to CSV 
                output_file_var = 'annual_heatmap_data_market_electricity.csv'
                output_file = os.path.join(output_folder_path,date_ext + output_file_var)
                heatmap_data_market_electricity.to_csv(output_file, header=True, index=True)
                # Update Dictionary
                output_file_attributes['annual_heatmap_data_market_electricity'] = output_file

                # Save the data to CSV 
                output_file_var = 'annual_heatmap_data_market_naturalgas.csv'
                output_file = os.path.join(output_folder_path,date_ext + output_file_var)
                heatmap_data_market_naturalgas.to_csv(output_file, header=True, index=True)
                # Update Dictionary
                output_file_attributes['annual_heatmap_data_market_naturalgas'] = output_file

                # Save the data to CSV 
                output_file_var = 'annual_market_heat_rate_std_avg_heatmap_data.csv'
                output_file = os.path.join(output_folder_path,date_ext + output_file_var)
                heatmap_data_market_heatrate.to_csv(output_file, header=True, index=True)
                # Update Dictionary
                output_file_attributes['annual_market_heat_rate_std_avg_heatmap_data'] = output_file

                # Adjust the column and row labels
                heatmap_data_market_electricity.columns = [f'Seed {i+1}' for i in range(len(heatmap_data_market_electricity.columns))]
                heatmap_data_market_electricity.index = heatmap_data_market_electricity.index.year  # Format the index to show just the year

                heatmap_data_market_naturalgas.columns = [f'Seed {i+1}' for i in range(len(heatmap_data_market_naturalgas.columns))]
                heatmap_data_market_naturalgas.index = heatmap_data_market_naturalgas.index.year  # Format the index to show just the year

                heatmap_data_market_heatrate.columns = [f'Seed {i+1}' for i in range(len(heatmap_data_market_heatrate.columns))]
                heatmap_data_market_heatrate.index = heatmap_data_market_heatrate.index.year  # Format the index to show just the year

                # Plot the volatility heatmaps on the same image using subpots with seeds as columns and years as rows
                fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(20, 6))
                #---------------------------------------------
                #Electricity Volatility
                # Plot the first heatmap on the first axis
                sns.heatmap(heatmap_data_market_electricity, annot=False, cmap="coolwarm", linewidths=.5, ax=axes[0])
                axes[0].set_title('Spot Power Price Volatility (STD/AVG) by Year and Seed')
                axes[0].set_xlabel('Seed')
                axes[0].set_ylabel('Year')
                axes[0].tick_params(axis='y', labelrotation=0)

                # Plot the second heatmap on the second axis
                sns.heatmap(heatmap_data_market_naturalgas, annot=False, cmap="coolwarm", linewidths=.5, ax=axes[1])
                axes[1].set_title('Spot Natural Gas Volatility (STD/AVG) by Year and Seed')
                axes[1].set_xlabel('Seed')
                axes[1].set_ylabel('Year')
                axes[1].tick_params(axis='y', labelrotation=0)

                # Plot the third heatmap on the third axis
                sns.heatmap(heatmap_data_market_heatrate, annot=False, cmap="coolwarm", linewidths=.5, ax=axes[2])
                axes[2].set_title('Market Heat Rate Volatility (STD/AVG) by Year and Seed')
                axes[2].set_xlabel('Seed')
                axes[2].set_ylabel('Year')
                axes[2].tick_params(axis='y', labelrotation=0)

                # Save updated json file
                gbl.gbl_tracked_loaded_dict_json_file_data.save_to_json(gbl.gbl_json_file_path_loaded)
                print(json.dumps(gbl.gbl_tracked_loaded_dict_json_file_data, indent=4))

                #Save image
                output_file = gbl.gbl_output_general_data['image_data_path']
                image_file_name = image_file_name_adder + ' Market Heat Rate Map'
                save_plot(plt, image_file_name, output_file)
        

                show_visualizations_func() 
                #plt.show()
    
    return
#-------------------------------------------------
def build_correlation_matrix(df_electricity, df_natural_gas, hourly_market_heat_rate, image_file_name_adder):
#-------------------------------------------------

    #-----------------------------------------------
    #Build Correlaton Matrix with Natural Gas and Power
    #-----------------------------------------------
    # Calculate the correlation matrix between df_electricity and df_natural_gas
    corr_matrix = df_electricity.corrwith(df_natural_gas)

    # Create a heatmap of the correlation matrix
    sns.heatmap(corr_matrix.to_frame(), cmap="coolwarm", annot=True, fmt=".2f")

    # Display the heatmap
    output_file = gbl.gbl_output_general_data['image_data_path']
    image_file_name = image_file_name_adder + ' Power and Natuarl Gas Correlation Matrix'
    save_plot(plt, image_file_name, output_file)

    #-----------------------------------------------
    # Plot the violin plot
    #-----------------------------------------------
    # Calculate the STD/AVG for each seed for each year
    std_avg_ratios = hourly_market_heat_rate.resample('Y').apply(lambda x: x.std() / x.mean())

    # Convert the DateTime index to string years
    std_avg_ratios.index = std_avg_ratios.index.year.astype(str)

    # Melt the DataFrame for better handling in seaborn
    melted_data = std_avg_ratios.reset_index().melt(id_vars='DateTime', var_name='Seed', value_name='STD/AVG Ratio')

    # Plot the violin plot
    plt.figure(figsize=(14, 7))
    sns.violinplot(x='DateTime', y='STD/AVG Ratio', data=melted_data, inner='quartile', palette="muted")
    plt.title('Hourly Spot Power Price STD/AVG Ratio Distribution by Year')
    plt.xlabel('Year')
    plt.ylabel('STD/AVG Ratio')
    plt.xticks(rotation=45)  # Rotate the x-axis labels if needed

    # Remove the legend
    plt.legend([], [], frameon=False)

    #save image
    output_file = gbl.gbl_output_general_data['image_data_path']
    image_file_name = image_file_name_adder + ' Market Heat rate volatility Violin Chart'
    save_plot(plt, image_file_name, output_file)
    show_visualizations_func() 
    #plt.show()
    
    return
# #-------------------------------------------------

##################################
def Calculate_LCOE(
        capacity_factor_range
        ):
    print("Calculate_LCOE called")

    # Check to see if a range was provided for capcity factors. If so, loop throught that range in the capacity_factor_range list
    # If not set cf to target capacity factor each generator and hold them all in the capacity_factor_range list

    if len(capacity_factor_range) == len(gbl.gbl_tracked_powergen_dict.keys()):
        print(f" len(capacity_factor_range): {len(capacity_factor_range)}")
        print(f" len(gbl.gbl_tracked_powergen_dict.keys()):: {len(gbl.gbl_tracked_powergen_dict.keys()):}")
        capacity_factor_range = [gbl.gbl_tracked_powergen_dict['generation_sources'][key]['target_capacity_factor'] for key in gbl.gbl_tracked_powergen_dict['generation_sources'].keys()]
        print(f"capacity_factor_range:{capacity_factor_range}")
    else:
        pass
        print(f"capacity_factor_range:{capacity_factor_range}")

    # Create Instance of TrackedDict object to track updates to the generator
    # attributes
    #gbl_tracked_powergen_dict = TrackedDict(gbl_power_generation_dict)

    if len(capacity_factor_range) == len(gbl.gbl_tracked_powergen_dict.keys()):
        print(f" len(capacity_factor_range): {len(capacity_factor_range)}")
        capacity_factor_range = [gbl.gbl_tracked_powergen_dict['generation_sources'][key]['target_capacity_factor'] for key in gbl.gbl_tracked_powergen_dict['generation_sources'].keys()]
        print(f"capacity_factor_range:{capacity_factor_range}")
    else:
        pass
        print(f"capacity_factor_range:{capacity_factor_range}")
        
    # print(type(gbl.gbl_tracked_powergen_dict['generation_sources']))

    lcoe_data_by_generator = {}

    # Only used if capacity_factor_range does not hold a range of values
    # If so, this variable is used to identify the position of the target_capacity_factor 
    # for the generator (key) in the gbl_tracked_powergen_dict
    target_capacity_factor_counter = 0

    #Loop through generators and extract the necessary data for LCOE calculations
    for key, value in gbl.gbl_tracked_powergen_dict['generation_sources'].items():
        lcoe_categories_list = []
        
        # Create inner loop for the capacity factor for 2x separate scenarios:
        # 1. If a range of capacity factors is provided
        # 2. If a single capacity factor is provided

        # Define capacity_factor_range as a list of the target_capacity_factor for each generator (key)
        # Check if the length of the capacity_factor_range is equal to the number of generators in the gbl_tracked_powergen_dict
        if len(capacity_factor_range) == len(gbl.gbl_tracked_powergen_dict.keys()):
            print(f" len(capacity_factor_range): {len(capacity_factor_range)}")
            print(f" len(gbl.gbl_tracked_powergen_dict.keys()):: {len(gbl.gbl_tracked_powergen_dict.keys()):}")
            #cf_values = capacity_factor_range  # Use the single value
            cf_values = [capacity_factor_range[target_capacity_factor_counter]]  # Use the dedicated value
        # Otherwise, define it as a fixed rang for all generators (keys)
        else:
            #cf_values = [capacity_factor_range[target_capacity_factor_counter]]  # Use the dedicated value
            cf_values = capacity_factor_range  # Use the single value

            for cf in cf_values:
                try:
                    #### 2. Create a Boolean test for each hour
                    # Define the heat rate and plant capacity
                    heat_rate = value['heat_rate']  # GJ/MWh
                    plant_capacity_mw_gross = value['plant_capacity_mw_gross']  # MW
                    plant_capacity_mw_net = value['plant_capacity_mw_net']   # MW
                    #target_capacity_factor = value['target_capacity_factor']  #% # Expected CF%
                    actual_capacity_factor = cf  #% Used for simulation purposes
                    target_annual_production_mwh = plant_capacity_mw_net * 8760 * actual_capacity_factor 
                    # Update tracked dictionary
                    value['target_annual_production_mwh'] = target_annual_production_mwh
                    
                    #------------------
                    #Capital Costs
                    capital_cost_per_kw = value['capital_cost_per_kw']  # $/kW
                    capital_cost_mm_dollars = capital_cost_per_kw * plant_capacity_mw_gross / 1000       
                    # Update tracked dictionary
                    value['capital_cost_mm_dollars'] = capital_cost_mm_dollars

                    #####################
                    #Operating Costs
                    #####################
                    #------------------
                    # Fuel Costs
                    target_nat_gas_price = value['target_nat_gas_price']  #$/GJ
                    fuel_efficiency = 3.6/ heat_rate # %
                    fuel_commodity_cost_mwh  = target_nat_gas_price * heat_rate #$/MWh
                    fuel_transport_cost_mwh  = 0 #$/MWh   
                    total_fuel_cost_mwh = fuel_commodity_cost_mwh + fuel_transport_cost_mwh #$/MWh
                    # Update tracked dictionary
                    value['fuel_efficiency'] = fuel_efficiency
                    # Not needed as these change each hour
                    # value['fuel_commodity_cost_mwh'] = fuel_commodity_cost_mwh
                    # value['fuel_transport_cost_mwh'] = fuel_transport_cost_mwh
                    # value['total_fuel_cost_mwh'] = total_fuel_cost_mwh

                    #------------------
                    # Variable O&M
                    vom_mwh = value['vom_mwh']  #$/MWh
                    #Don't need to update tracked dictionary as this is alread in $/MWh

                    #------------------
                    # Fixed Maintenance
                    fixed_operating_costs_fixed = value['fixed_operating_costs_fixed']  #$/kw-year
                    fixed_operating_costs_mwh = fixed_operating_costs_fixed * plant_capacity_mw_gross * 1000/target_annual_production_mwh  #$/MWh
                    
                    # Land Costs
                    land_cost_per_acre = value['land_cost_per_acre']  #$/acre
                    number_acres = value['number_acres']
                    land_costs = land_cost_per_acre * number_acres  # $ 
                    land_costs_mwh = land_costs/target_annual_production_mwh #/MWh
                    
                    # Insurance Costs
                    ins_prop_tax = value['ins_prop_tax']  # $/kW-year
                    ins_prop_tax_mwh =  ins_prop_tax * plant_capacity_mw_gross * 1000/target_annual_production_mwh  #$/MWh       
                    # Update tracked dictionary
                    value['fixed_operating_costs_mwh'] = fixed_operating_costs_mwh
                    value['land_costs_mwh'] = land_costs_mwh
                    value['ins_prop_tax_mwh'] = ins_prop_tax_mwh

                    #------------------

                    #Emission Costs
                    carbon_costs_per_tCO2e = value['carbon_costs_per_tCO2e']  #$/tCO2e
                    emissions_intensity = value['emissions_intensity']  #tCO2e/MWh
                    co2_reduction_target = value['co2_reduction_target'] 
                    total_co2_emissions = emissions_intensity * target_annual_production_mwh
                    taxable_co2_emissions = total_co2_emissions - co2_reduction_target
                    env_costs_per_mwh = carbon_costs_per_tCO2e*(emissions_intensity - co2_reduction_target) #$/MWh 
                    # Update tracked dictionary
                    value['total_co2_emissions'] = total_co2_emissions
                    value['taxable_co2_emissions'] = taxable_co2_emissions
                    value['env_costs_per_mwh'] = env_costs_per_mwh

                    #------------------
                    sts_percentage = value['sts_percentage']  #%
                    sts_mwh = 0
                     # Update tracked dictionary
                    value['sts_mwh'] = sts_mwh
                    #------------------

                    #Total Non-Fuel Variable Costs
                    non_fuel_vom_mwh = vom_mwh + fixed_operating_costs_mwh + sts_mwh #$/MWh
                    non_fuel_variable_bid_costs_mwh = non_fuel_vom_mwh + fixed_operating_costs_mwh #$/MWh
                    #Total Fuel Variable Costs
                    fuel_varible_costs_mwh = total_fuel_cost_mwh
                    # Total Fixed Opearting Costs
                    total_fixed_costs_mwh = fixed_operating_costs_mwh + land_costs_mwh + ins_prop_tax_mwh #$/MWh  
                    # Update tracked dictionary
                    value['non_fuel_vom_mwh'] = non_fuel_vom_mwh
                    value['non_fuel_variable_bid_costs_mwh'] = non_fuel_variable_bid_costs_mwh
                    value['fuel_varible_costs_mwh'] = fuel_varible_costs_mwh
                    value['total_fixed_costs_mwh'] = total_fixed_costs_mwh

                    ############################
                    #Capital Costs
                    #------------------
                    #Capital Recovery
                    term = value['term']  # years
                    Ke = value['Ke']  # %
                    Kd = value['Kd']  #%
                    tax_rate = value['tax_rate']  #% 
                    equity_percent = value['equity_percent']  # %
                    debt_percent = value['debt_percent']  # %
                    waccat = (equity_percent * Ke) + ((debt_percent * Kd) * (1-tax_rate)) 
                    print(f" term: {term}, Ke: {Ke}, Kd: {Kd}, tax_rate: {tax_rate}, equity_percent: {equity_percent}, debt_percent: {debt_percent},waccat: {waccat}")
                    

                    #..............................................           
                    # Update tracked dictionary
                    value['waccat'] = waccat

                    #------------------
                    #Levelized Capital Recovery
                    annual_index_rate = value['annual_index_rate']  # %
                    levelization_rate_LR = waccat # WACC at 
                    capital_recovery_factor_CF = levelization_rate_LR/(1-(1+levelization_rate_LR)**-term)  
                    print(f" capital_recovery_factor_CF: {capital_recovery_factor_CF}")
                    lcoe_index = True


                    if lcoe_index == True:         
                        levelization_factor = ((1 + levelization_rate_LR)**term - 1) / (levelization_rate_LR * (1 + levelization_rate_LR)**term)\
                                                / ((1 - (1 + annual_index_rate)**term * (1 + levelization_rate_LR)**-term) / (levelization_rate_LR - annual_index_rate))                  
                    else:
                        levelization_factor = 1 

                    indexed_capital_recovery_factor = levelization_factor * capital_recovery_factor_CF 
                    print(f" indexed_capital_recovery_factor: {indexed_capital_recovery_factor}")
                    finance_factor_FF_with_tax_credits = 1 
                    finance_factor_FF_without_credits = 1 
                    construction_finance_factor_CFF = 1 # IDC Calc 

                    #..............................................           
                    # Update tracked dictionary
                    value['levelization_rate_LR'] = levelization_rate_LR
                    value['capital_recovery_factor_CF'] = capital_recovery_factor_CF
                    value['lcoe_index'] = lcoe_index

                    value['levelization_factor'] = levelization_factor
                    value['indexed_capital_recovery_factor'] = indexed_capital_recovery_factor
                    value['finance_factor_FF_with_tax_credits'] = finance_factor_FF_with_tax_credits
                    value['finance_factor_FF_without_credits'] = finance_factor_FF_without_credits
                    value['construction_finance_factor_CFF'] = construction_finance_factor_CFF

                    #------------------
                    #Power Plant Capital Recovery $/MW
                    capital_recovery_without_idc_without_tax_credits = (capital_cost_mm_dollars * 1000000 * indexed_capital_recovery_factor * \
                                                                            finance_factor_FF_without_credits)/target_annual_production_mwh

                    print(f" capital_cost_mm_dollars: {capital_cost_mm_dollars}, indexed_capital_recovery_factor: {indexed_capital_recovery_factor}, finance_factor_FF_without_credits: {finance_factor_FF_without_credits}, target_annual_production_mwh: {target_annual_production_mwh}")

                    capital_recovery_with_idc_without_tax_credits = (capital_cost_mm_dollars * 1000000 * indexed_capital_recovery_factor * \
                                                                            finance_factor_FF_without_credits * construction_finance_factor_CFF)/target_annual_production_mwh

                    capital_recovery_with_idc_and_with_tax_credits =(capital_cost_mm_dollars  * 1000000 * indexed_capital_recovery_factor * \
                                                                            finance_factor_FF_with_tax_credits * construction_finance_factor_CFF)/target_annual_production_mwh

                    tax_credit_value_per_mwh = capital_recovery_with_idc_without_tax_credits - capital_recovery_with_idc_and_with_tax_credits       
                    # Update tracked dictionary
                    value['capital_recovery_without_idc_without_tax_credits'] = capital_recovery_without_idc_without_tax_credits
                    value['capital_recovery_with_idc_without_tax_credits'] = capital_recovery_with_idc_without_tax_credits
                    value['capital_recovery_with_idc_and_with_tax_credits'] = capital_recovery_with_idc_and_with_tax_credits
                    value['tax_credit_value_per_mwh'] = tax_credit_value_per_mwh
                    
                    #------------------
                    #Investment Tax Credit Calculations
                    eligibility_for_us_can_itc =  value['eligibility_for_us_can_itc']
                    itc_tax_credit_percent =  value['itc_tax_credit_percent'] # %
                    itc_tax_credit_percent_dollar_amount = capital_cost_mm_dollars * itc_tax_credit_percent #$MM
                    itc_tax_credit_percent_dollar_Amount_per_mwh = (itc_tax_credit_percent_dollar_amount * 1000000 * indexed_capital_recovery_factor)\
                                                                                /(1-tax_rate)/target_annual_production_mwh      
                    # Update tracked dictionary
                    value['itc_tax_credit_percent_dollar_amount'] = itc_tax_credit_percent_dollar_amount
                    value['itc_tax_credit_percent_dollar_Amount_per_mwh'] = itc_tax_credit_percent_dollar_Amount_per_mwh

                    #------------------
                    #Production Tax Credit Calculations
                    eligibility_for_ptc =  value['eligibility_for_ptc']
                    pc_term_yrs =  value['pc_term_yrs'] # years
                    ptc_capital_recovery_factor = levelization_rate_LR/(1-(1+levelization_rate_LR)**-pc_term_yrs)
                    rate = levelization_rate_LR
                    index =  value['annual_index_rate'] # %
                    ptc_levelization_factor = levelization_factor
                    indexed_capital_recovery_factor = ptc_capital_recovery_factor * ptc_levelization_factor
                    tax_credit_per_MWh_firstyear =  value['tax_credit_per_MWh_firstyear'] #$/MWh
                    levelized_tax_credit_over_project_life = (tax_credit_per_MWh_firstyear/(1-tax_rate)*capital_recovery_factor_CF/ptc_capital_recovery_factor)          
                    # Update tracked dictionary
                    value['ptc_capital_recovery_factor'] = ptc_capital_recovery_factor
                    value['rate'] = rate
                    value['ptc_levelization_factor'] = ptc_levelization_factor
                    value['indexed_capital_recovery_factor'] = indexed_capital_recovery_factor
                    value['levelized_tax_credit_over_project_life'] = levelized_tax_credit_over_project_life

                    #------------------
                    # LCOE Calculation 
                    lcoe_power_plant_capital = capital_recovery_with_idc_without_tax_credits
                    lcoe_carbon_capture_capital = value['lcoe_carbon_capture_capital']
                    lcoe_power_ga_ins_prop_tax = ins_prop_tax_mwh
                    lcoe_power_land_costs = land_costs_mwh
                    lcoe_power_fom = fixed_operating_costs_mwh
                    lcoe_power_vom = vom_mwh 

                    lcoe_feedstock_fuel = fuel_varible_costs_mwh
                    lcoe_recl_liability = 0 
                    lcoe_emission_costs = fixed_operating_costs_mwh 
                    total_lcoe = lcoe_power_plant_capital + lcoe_carbon_capture_capital + lcoe_power_ga_ins_prop_tax + lcoe_power_land_costs + lcoe_power_fom + \
                        lcoe_power_vom + lcoe_feedstock_fuel + lcoe_recl_liability + lcoe_emission_costs            
                    # Update tracked dictionary
                    value['lcoe_power_plant_capital'] = lcoe_power_plant_capital
                    value['lcoe_carbon_capture_capital'] = lcoe_carbon_capture_capital
                    value['lcoe_power_ga_ins_prop_tax'] = lcoe_power_ga_ins_prop_tax
                    value['lcoe_power_land_costs'] = lcoe_power_land_costs
                    value['lcoe_power_fom'] = lcoe_power_fom
                    value['lcoe_power_vom'] = lcoe_power_vom
                    value['lcoe_feedstock_fuel'] = lcoe_feedstock_fuel
                    value['lcoe_recl_liability'] = lcoe_recl_liability
                    value['lcoe_emission_costs'] = lcoe_emission_costs
                    value['total_lcoe'] = total_lcoe


                    #Print LCOE Cost Summary
                    print(f" {key} LCOE Cost Summary")
                    print(f" lcoe_power_plant_capital: {lcoe_power_plant_capital}")
                    print(f" lcoe_carbon_capture_capital : {lcoe_carbon_capture_capital}")
                    print(f" lcoe_power_ga_ins_prop_tax: {lcoe_power_ga_ins_prop_tax}")
                    print(f" lcoe_power_fom: {lcoe_power_fom}")
                    print(f" lcoe_power_vom: {lcoe_power_vom}")
                    print(f" lcoe_feedstock_fuel: {lcoe_feedstock_fuel}")
                    print(f" lcoe_recl_liability: {lcoe_recl_liability}")
                    print(f" lcoe_emission_costs: {lcoe_emission_costs}")
                    print("______")
                    #print(f" total_lcoe @ {actual_capacity_factor} capacity factor: {total_lcoe}")
                    print(f"total_lcoe @ {actual_capacity_factor:.1%} capacity factor: {total_lcoe}")
                    print("______")

                except KeyError as e:
                    print(f"Missing key in data for '{key}': {e}")

                except TypeError as e:
                    print(f"Invalid data type in data for '{key}': {e}")

                # Get all changes for the current iteration
                changes = gbl.gbl_tracked_powergen_dict.get_changes()

                # Save the updated dictionary to a JSON file
                gbl.gbl_tracked_powergen_dict.save_to_json(gbl.gbl_json_power_generation_path)


                # Optionally, clear the recorded changes
                #gbl_tracked_powergen_dict.clear_changes() 
                

                #---------------------------------------------------------
                #LCOE Target
                categories = {'Power Plant Capital':lcoe_power_plant_capital,
                            'Carbon Capture Capital': lcoe_carbon_capture_capital, 
                            'Power G&A+Ins+Prop Tax':lcoe_power_ga_ins_prop_tax,
                            'Power Land Costs':lcoe_power_land_costs,
                            'Power FOM':lcoe_power_fom,
                            'Power VOM': lcoe_power_vom,
                            'Feedstock/Fuel': lcoe_feedstock_fuel,
                            'Reclamation Liability': lcoe_recl_liability,
                            'Emission Costs': lcoe_emission_costs,
                            'Total LCOE': total_lcoe
                            #'LCOE (w/o Tax Credits)': lcoe_without_tax_credits,
                            #'LCOE (Tax Credits)':lcoe_tax_credits,
                            #'LCOE (w/ Tax Credits)': lcoe_with_tax_credits
                }

                # Add the current capacity factor's LCOE categories to the list
                lcoe_categories_list.append({
                        'capacity_factor': actual_capacity_factor,
                        'categories': categories
                    })
                
                # Store the list of LCOE categories for this generator type in the main dictionary
                lcoe_data_by_generator[key] = lcoe_categories_list

                # Increment the target capacity factor counter
                # This is only used when a range of capacity factors is not provided
                # and a target capacity factor for each generator is held in the capacity_factor_range
                # list. Otherwise the capacity_factor_range
                target_capacity_factor_counter = target_capacity_factor_counter + 1

    # Print tables for each dictionary key
    csv_filename = 'lcoe_by_generation_source.csv'
    print_lcoe_table(lcoe_data_by_generator, csv_filename)
    

    return lcoe_data_by_generator
#-------------------------------------------------
def Calculate_Merit_Test(
                generator_list,
                gstarting_index,
                gcurrent_annual_index, 
                gannual_index_rate, 
                gnox_emissons, 
                gcf_limit,  
                gstrategy,
                gSTRATEGY_CF_CAP,
                gSTRATEGY_PERFECT_FORESIGHT,
                gSTRATEGY_PREDICTIVE_BIDDING
                ):
#-------------------------------------------------
        print("Calculate_Merit_Test called")

        for key1, value1 in gbl.gbl_tracked_loaded_dict_json_file_data["Input_Data"]["Price_Forecast"].items():
        
            input_file_attributes =value1['Input_File_Attributes']
            
            start_year = input_file_attributes['start_year']
            end_year = input_file_attributes['end_year']
            stochastic_seeds = input_file_attributes['stochastic_seeds']
            stochastic_seeds_used = input_file_attributes['stochastic_seeds_used']

            for key2, value2 in gbl.gbl_tracked_loaded_dict_json_file_data["Output_Data"]["Processed_Price_Forecast"].items():

                output_file_attributes = value2['Output_File_Attributes']
                output_data_path = output_file_attributes['frcst_output_csv_file_path']
                output_sub_folder = output_file_attributes['output_sub_folder']
                file_name = output_file_attributes['consolidated_hourly']

                file_path = os.path.join(output_data_path, output_sub_folder, file_name)
                df = pd.read_csv(file_path)
            
                print(f"filename: {file_name}")
                print(f"file_path: {file_path}")
                print("conslidated data loaded")
                print(f"df: {df.head()}")

            gbl.gbl_frcst_output_csv_file_path = output_file_attributes['frcst_output_csv_file_path']

            #Ensure DateTime is in datetime format
            df['DateTime'] = pd.to_datetime(df['DateTime'])
            df.set_index('DateTime', inplace=True)

            # set up variables for hourly reporting

            ##############################
            #PART C: Do Merit Test and Calculate Capacity Factors and Capture Prices
            ##############################

            # New
            for current_generator in generator_list:
                print(f"Processing gbl.gbl_tracked_loaded_dict_json_file_data key: {key1} with generator: {current_generator}")
                #print(f" Conducting Back-Casting Analysis for {current_generator}")

                plant_capacity_mw_net = float(gbl.gbl_tracked_powergen_dict['generation_sources'][current_generator]['plant_capacity_mw_net'])
                heat_rate = float(gbl.gbl_tracked_powergen_dict['generation_sources'][current_generator]['heat_rate'])
                vom_costs = float(gbl.gbl_tracked_powergen_dict['generation_sources'][current_generator]['vom_mwh'])
                start_up_cost_per_start = 2000  #This is calculated in the hourly loop
                sts_cost = float(gbl.gbl_tracked_powergen_dict['generation_sources'][current_generator]['sts_mwh'])
                fom_cost = float(gbl.gbl_tracked_powergen_dict['generation_sources'][current_generator]['fixed_operating_costs_mwh'])
                run_hour_maintenance_target = float(gbl.gbl_tracked_powergen_dict['generation_sources'][current_generator]['run_hour_maintenance_target'])
                emissions_intensity = float(gbl.gbl_tracked_powergen_dict['generation_sources'][current_generator]['emissions_intensity'])
                base_line = float(gbl.gbl_tracked_powergen_dict['generation_sources'][current_generator]['co2_reduction_target'])
                min_down_time = float(gbl.gbl_tracked_powergen_dict['generation_sources'][current_generator]['min_down_time']) 
                min_up_time = float(gbl.gbl_tracked_powergen_dict['generation_sources'][current_generator]['min_up_time'])
                startcost_amort_hours = 10 

                #Load market variables
                #carbon_dict = gcarbon_dict
                cf_limit = gcf_limit
                starting_indext = gstarting_index
                annual_index_rate = gannual_index_rate
                nox_emissons = gnox_emissons #kg/GJ of energy output
                #carbon_dict = gcarbon_dict
                starting_index = gstarting_index
                current_annual_index = gcurrent_annual_index
                annual_index_rate = gannual_index_rate #2%
                #start_year = g_start_year
                #end_year = g_end_year
                date_ext = f'Date-{start_year}-{end_year}_'

                # Select strategy
                STRATEGY_CF_CAP = gSTRATEGY_CF_CAP
                STRATEGY_PERFECT_FORESIGHT = gSTRATEGY_PERFECT_FORESIGHT
                STRATEGY_PREDICTIVE_BIDDING = gSTRATEGY_PREDICTIVE_BIDDING
                strategy = gstrategy

                ##################################################################
                #---------------------------------------------------------
        
                # Initialize a dictionary to hold annual capacity factors and capture prices for each seed
                hourly_bids = {}
                capacity_factors = {}
                capture_prices = {}
                #new
                natgas_capture_prices = {}

                #Create lists to store monthly capacity factors and bids
                monthly_bids = {}
                monthly_capacity_factors = {}
                monthly_capture_prices = {}
                #new
                monthly_natgas_capture_prices = {}

    
                #NOx EMission limits as per CER regulations
                '''
                Application                                 Turbine power rating (MW)       NOx emission limits (g/GJ(energy output))
                Non-peaking combustion turbines             > 1 and < 4                     500     
                mechanical drive 

                Non-peaking combustion turbines –           > 1 and < 4                     290              
                electricity generation


                Peaking combustion turbines – all*          > 1 and < 4                     exempt

                Non-peaking combustion turbines             > 4 and ≤ 70                    140
                and peaking combustion turbines – all*


                Non-peaking combustion turbines – all*      > 70                            85
                Peaking combustion turbines – all*          > 70                            140
                '''

                # Loop over 50 stochastic seeds
                #for seed in tqdm(range(1, 51)):
                for seed in tqdm(range(1, stochastic_seeds_used)):
                    seed_generator_bids = []
                    seed_capacity_factors = []
                    seed_capture_prices = []
                    seed_natgas_capture_prices = []
                    
                    seed_monthly_bids = []
                    seed_monthly_capacity_factors = []
                    seed_monthly_capture_prices = []
                    seed_monthly_natgas_capture_prices = []
                    
                    year_counter = 0

                    # Loop over 15 years of hourly data
                    for year in tqdm(range(start_year, end_year + 1)):
                        year_counter += 1
                        current_annual_index = starting_index * (1 + annual_index_rate)**year_counter
                        year_str = str(year)

                        # Filter data for the specific year (Assuming df is pre-loaded)
                        year_data = df[df.index.year == year]
                        
                        # Calculate the monthly index rate based on the annual index rate
                        monthly_index_rate = (1 + annual_index_rate) ** (1/12) - 1

                        # Then loop over each month in the year
                        for month in range(1, 13):
                            month_counter = (year - start_year) * 12 + month
                            current_month_index = starting_index * (1 + monthly_index_rate) ** month_counter

                            month_data = year_data[year_data.index.month == month]

                            # Calculate running status and threshold price
                            adj_non_fuel_variable_bid_costs = vom_costs + sts_cost
                            carbon_cost = gbl.gbl_carbon_tax_annual_dict[year_str] * (emissions_intensity - base_line)
                            
                            #NEW Bidding Strategy Code
                            #################################
                 
                            # Pass the hourly data in the current month to the calculate_running_status function
                            # This returns a list of 1s and 0s indicating whether the generator is running in each hour
                            monthly_running_status, threshold_price_list, days_in_month = calculate_running_status(
                                                                            strategy, 
                                                                            STRATEGY_CF_CAP, 
                                                                            STRATEGY_PERFECT_FORESIGHT, 
                                                                            STRATEGY_PREDICTIVE_BIDDING, 
                                                                            df, 
                                                                            year_data, 
                                                                            seed, 
                                                                            month, 
                                                                            year, 
                                                                            plant_capacity_mw_net, 
                                                                            startcost_amort_hours, 
                                                                            cf_limit, 
                                                                            monthly_index_rate, 
                                                                            adj_non_fuel_variable_bid_costs, 
                                                                            start_up_cost_per_start, 
                                                                            #carbon_dict, 
                                                                            heat_rate, 
                                                                            emissions_intensity, 
                                                                            base_line, 
                                                                            start_year
                            )
                            
                       
                            # the returned data for threshold_price_list and monthly_running_status
                            # are arrays with hourly data for the given months

                            avg_generator_bid_monthly = np.mean(threshold_price_list)
                            total_capacity_run = np.sum(monthly_running_status) * plant_capacity_mw_net
                            #print(f"Number hours run: { np.sum(monthly_running_status) }")
                            
                            #Calculate monthly capcity factor
                            total_possible_capacity = plant_capacity_mw_net * days_in_month * 24
                            capacity_factor_monthly = total_capacity_run / total_possible_capacity

                            #Pass data to current seed list
                            seed_monthly_bids.append(avg_generator_bid_monthly)
                            seed_monthly_capacity_factors.append(capacity_factor_monthly)


                            # multiply strip of power capture prices against capacity and then sum it
                            # Divide strip of hourly revenue monthly by market revenue to create monthly 
                            # capture price metric for power plant 
                            capture_price_column, market_power_price = plant_capture_price(
                                                                            month_data[f'Seed {seed}_Power'], 
                                                                            monthly_running_status
                                                                            )
                            
                            hourly_revenue_monthly = capture_price_column * plant_capacity_mw_net
                            hourly_revenue_sum_monthly = np.nansum(hourly_revenue_monthly)
                            market_revenue_sum_monthly = np.nansum(market_power_price)
                            received_price_ratio_to_avg_monthly = hourly_revenue_sum_monthly / market_revenue_sum_monthly
                            
                            # multiply strip of nat gas capture prices against capacity adn then sum it
                            # Divide strip of hourly nat gas costs monthly by market nat gas costs to create monthly 
                            # capture cost metric for power plant 
                            natgas_capture_price_column, market_natgas_price = natgas_capture_price(
                                                                                    month_data[f'Seed {seed}_Gas'], 
                                                                                    monthly_running_status
                                                                                    )
                            
                            hourly_natgas_cost_monthly = natgas_capture_price_column * plant_capacity_mw_net * heat_rate
                            hourly_natgas_cost_sum_monthly = np.nansum(hourly_natgas_cost_monthly)
                            market_natgas_sum_monthly = np.nansum(market_natgas_price)
                            received_natgas_price_ratio_to_avg_monthly = hourly_natgas_cost_monthly / market_natgas_sum_monthly
                            
                            # Pass data to seed list
                            seed_monthly_capture_prices.append(capture_price_column)
                            seed_monthly_natgas_capture_prices.append(natgas_capture_price_column)

                            month_str = f"{year}-{month:02d}"
                            if month_str not in monthly_bids:
                                monthly_bids[month_str] = []
                                monthly_capacity_factors[month_str] = []
                                monthly_capture_prices[month_str] = []
                                monthly_natgas_capture_prices[month_str] = []
                            
                            monthly_bids[month_str].append(avg_generator_bid_monthly)
                            monthly_capacity_factors[month_str].append(capacity_factor_monthly)
                            monthly_capture_prices[month_str].append(np.nanmean(capture_price_column))
                            monthly_natgas_capture_prices[month_str].append(np.nanmean(natgas_capture_price_column))
                            
                    # Aggregate monthly data to get annual data 
                    seed_generator_bids = []
                    seed_capacity_factors = []
                    seed_capture_prices = []
                    #new
                    seed_natgas_capture_prices = []

                    # Loop through years and pass monthly data to annual data objects
                    for year in range(start_year, end_year + 1):
                        year_months = [f"{year}-{month:02d}" for month in range(1, 13)]

                        avg_generator_bid_annual = np.mean([monthly_bids[month_str][seed-1] for month_str in year_months])
                        avg_capacity_factor_annual = np.mean([monthly_capacity_factors[month_str][seed-1] for month_str in year_months])
                        avg_capture_price_annual = np.mean([monthly_capture_prices[month_str][seed-1] for month_str in year_months])
                        avg_natgas_capture_price_annual = np.mean([monthly_natgas_capture_prices[month_str][seed-1] for month_str in year_months])

                        seed_generator_bids.append(avg_generator_bid_annual)
                        seed_capacity_factors.append(avg_capacity_factor_annual)
                        seed_capture_prices.append(avg_capture_price_annual)
                        seed_natgas_capture_prices.append(avg_natgas_capture_price_annual)
                    
                    # End of Year Loop

                    hourly_bids[f'Seed{seed}'] = seed_generator_bids
                    #print(f"hourly_bids: {hourly_bids}")
                    capacity_factors[f'Seed{seed}'] = seed_capacity_factors
                    capture_prices[f'Seed{seed}'] = seed_capture_prices
                    natgas_capture_prices[f'Seed{seed}'] = seed_natgas_capture_prices
                    year_counter = 0
                
                # End of See Loop

                ##############################
                # Create summary annual DataFrames
                ##############################
                summary_generator_bid_df = pd.DataFrame(hourly_bids, index=range(start_year, end_year + 1)) 
                summary_generator_bid_df.index.name = 'Year'
                summary_cf_df = pd.DataFrame(capacity_factors, index=range(start_year, end_year + 1))
                summary_cf_df.index.name = 'Year'
                summary_capture_ratio_df = pd.DataFrame(capture_prices, index=range(start_year, end_year + 1))
                summary_capture_ratio_df.index.name = 'Year'
                summary_natgas_capture_ratio_df = pd.DataFrame(natgas_capture_prices, index=range(start_year, end_year + 1))
                summary_natgas_capture_ratio_df.index.name = 'Year'
                
                ##############################
                # Create summary monthly DataFrames
                ##############################
                monthly_index = pd.date_range(start=f'{start_year}-01', end=f'{end_year}-12', freq='M').strftime('%Y-%m')

                # Ensure the lengths match by checking before creating DataFrames
                print(f"Length of monthly_index: {len(monthly_index)}")
                print(f"Length of monthly_bids keys: {len(monthly_bids.keys())}")
                print(f"Length of monthly_capacity_factors keys: {len(monthly_capacity_factors.keys())}")
                #new
                print(f"Length of monthly_capture_prices keys: {len(monthly_capture_prices.keys())}")

                # Drop the extra month from dictionaries if needed
                if len(monthly_bids.keys()) > len(monthly_index):
                    extra_keys = sorted(monthly_bids.keys())[-(len(monthly_bids.keys()) - len(monthly_index)):]
                    for key in extra_keys:
                        del monthly_bids[key]
                        del monthly_capacity_factors[key]
                        del monthly_capture_prices[key]
                        del monthly_natgas_capture_prices[key]

                summary_monthly_generator_bid_df = pd.DataFrame(monthly_bids).T
                summary_monthly_generator_bid_df.index = monthly_index
                summary_monthly_generator_bid_df.index.name = 'Month'

                summary_monthly_cf_df = pd.DataFrame(monthly_capacity_factors).T
                summary_monthly_cf_df.index = monthly_index
                summary_monthly_cf_df.index.name = 'Month'

                summary_monthly_capture_ratio_df = pd.DataFrame(monthly_capture_prices).T
                summary_monthly_capture_ratio_df.index = monthly_index
                summary_monthly_capture_ratio_df.index.name = 'Month'

                #new
                summary_monthly_natgas_capture_ratio_df = pd.DataFrame(monthly_natgas_capture_prices).T
                summary_monthly_natgas_capture_ratio_df.index = monthly_index
                summary_monthly_natgas_capture_ratio_df.index.name = 'Month'

                # Save the combined DataFrame to a CSV file
                print("Creating Output File")

                #################################################
                # Save the data frames to a CSV file
                #################################################
                #-------------------------------------------------
                #Annual Data


                output_file_attributes['annual_generator_bid_output_file_var'] = 'annual_generator_bid_output.csv'
                output_file_var = output_file_attributes['annual_generator_bid_output_file_var'] 
                output_file = os.path.join(gbl.gbl_frcst_output_csv_file_path, date_ext + output_file_var)
                print(f" output_file: {output_file}")
                summary_generator_bid_df.to_csv(output_file, header=True, index=True)
                
                output_file_attributes['annual_cf_output_file_var'] = 'annual_cf_output.csv'
                output_file_var = output_file_attributes['annual_cf_output_file_var']
                output_file = os.path.join(gbl.gbl_frcst_output_csv_file_path, date_ext + output_file_var)
                print(f" output_file: {output_file}")
                summary_cf_df.to_csv(output_file, header=True, index=True)

                output_file_attributes['annual_power_recievedratio_output_file_var'] = 'annual_power_recievedratio_output.csv'
                output_file_var = output_file_attributes['annual_power_recievedratio_output_file_var']
                output_file = os.path.join(gbl.gbl_frcst_output_csv_file_path, date_ext + output_file_var)
                print(f" output_file: {output_file}")
                summary_capture_ratio_df.to_csv(output_file, header=True, index=True)

                output_file_attributes['annual_natgas_recievedratio_output_file_var'] = 'annual_natgas_recievedratio_output.csv'
                output_file_var = output_file_attributes['annual_natgas_recievedratio_output_file_var']
                output_file = os.path.join(gbl.gbl_frcst_output_csv_file_path, date_ext + output_file_var)
                print(f" output_file: {output_file}")
                summary_natgas_capture_ratio_df.to_csv(output_file, header=True, index=True)

                #-------------------------------------------------
                #Monthly Data
                output_file_attributes['monthly_generator_bid_output_file_var'] = 'monthly_generator_bid_output.csv'
                output_file_var = output_file_attributes['monthly_generator_bid_output_file_var']
                output_file = os.path.join(gbl.gbl_frcst_output_csv_file_path, date_ext + output_file_var)
                print(f" output_file: {output_file}")
                summary_monthly_generator_bid_df.to_csv(output_file, header=True, index=True)

                output_file_attributes['monthly_cf_output_file_var'] = 'monthly_cf_output.csv'
                output_file_var = output_file_attributes['monthly_cf_output_file_var']
                output_file = os.path.join(gbl.gbl_frcst_output_csv_file_path, date_ext + output_file_var)
                print(f" output_file: {output_file}")
                summary_monthly_cf_df.to_csv(output_file, header=True, index=True)

                output_file_attributes['monthly_power_recievedratio_output_file_var'] = 'monthly_power_recievedratio_output.csv'
                output_file_var = output_file_attributes['monthly_power_recievedratio_output_file_var']
                output_file = os.path.join(gbl.gbl_frcst_output_csv_file_path, date_ext + output_file_var)
                print(f" output_file: {output_file}")
                summary_monthly_capture_ratio_df.to_csv(output_file, header=True, index=True)

                #new
                output_file_attributes['monthly_natgas_recievedratio_output_file_var'] = 'monthly_natgas_recievedratio_output.csv'
                output_file_var = output_file_attributes['monthly_natgas_recievedratio_output_file_var']
                output_file = os.path.join(gbl.gbl_frcst_output_csv_file_path, date_ext + output_file_var)
                print(f" output_file: {output_file}")
                summary_monthly_natgas_capture_ratio_df.to_csv(output_file, header=True, index=True)

                #################################################
                # Save the data frames to a formatted Excel Workbook
                #################################################

                # Define metadata for the target file
                run_scenario = key
                run_case = current_generator
                excel_template_path = r'C:\Users\kaczanor\OneDrive - Enbridge Inc\Documents\Python\EDC Hourly Capacity Factor Q2 2024\template_excel_output_files\simluation_annual_monthly_output_file_template.xlsx'
                output_excel_folder = r' C:\Users\kaczanor\OneDrive - Enbridge Inc\Documents\Python\EDC Hourly Capacity Factor Q2 2024\outputs\excel_data'

                # Define the CSV file names and corresponding cell ranges
                # Note that the cell ranges are based on the template file
                # which assumes that their is 50x15 data for each CSV file.
                # However, if you chose to run smaller number of seeds, the 
                # ranges will need to be adjusted accordingly.

                csv_files = {
                    'Date-2024-2038_monthly_avg_electricity.csv': 'H22:BE200',
                    'Date-2024-2038_monthly_power_recievedratio_output.csv': 'H222:BE400',
                    'Date-2024-2038_monthly_natgas_recievedratio_output.csv': 'H422:BE600',
                    'Date-2024-2038_monthly_cf_output.csv': 'H622:BE800'
                }


                # create_excel_output_table(
                #     run_scenario,
                #     run_case,
                #     excel_template_path,
                #     output_excel_folder,
                #     csv_files,
                #     stochastic_seeds_used,
                # )


                print(f"Data pasted successfully and file saved as {output_file_var}!")

        # Continue with any additional processing or cleanup after the nested loops
        # For example, you might want to print a final completion message

        # Save updated json file
        gbl.gbl_tracked_loaded_dict_json_file_data.save_to_json(gbl.gbl_json_file_path_loaded)
        print(json.dumps(gbl.gbl_tracked_loaded_dict_json_file_data, indent=4))

        print("All scenarios and assets have been processed successfully!")

#-------------------------------------------------
# Define the CSV file names and the corresponding cell ranges in the Excel template
def Visualize_Merit_Test():
    
    print("Visualize_Merit_Test called")
    #-------------------------------------------------
    #################################################
    #### 3. Visualize the results
    #################################################
    #Using a ridgeline plot for Annual visualization:

    # Melt the DataFrame for visualization
    melted_cf_df = summary_cf_df.reset_index().melt(id_vars='Year', var_name='Seed', value_name='Capacity Factor')
    melted_capture_ratio_df = summary_capture_ratio_df.reset_index().melt(id_vars='Year', var_name='Seed', value_name='Capture Price')

    ####################
    #Joypy  Version
    ####################

    #annual capacity factor
    #Plot the ridgeline plot for capacity factors
    plt.figure(figsize=(12, 8))


    joyplot(
    data=melted_cf_df, 
    column='Capacity Factor', 
    by='Year', 
    bins=80,  # Specifying the number of bins
    overlap=1.0, 
    linewidth=1,
    kind='kde',
    bw_method=0.5,
    range_style='own',
    tails=0.0, 
    grid='y',
    fade=False,
    colormap=cm.viridis
    )

    # Add labels and title
    chart_title = f"Ridgeline Plot by Year for Capacity Factor"
    plt.suptitle(chart_title, y=1.05)

    # Format X axis with 0%
    formatter = FuncFormatter(lambda x, _: '{:.0%}'.format(x))
    plt.gca().xaxis.set_major_formatter(formatter)
    plt.xlabel('Capacity Factor')

    #plt.xlabel('Capacity Factor')
    plt.ylabel('Density')

    #Save Image
    output_file = gbl.gbl_output_general_data['image_data_path']
    image_file_name_adder = "Test1"
    image_file_name = image_file_name_adder + ' Annual Capacity Factor Ridgeline Plot'
    save_plot(plt, image_file_name, output_file)

    show_visualizations_func() 
    #plt.show()

    #----------------------------------------------
    # Plot the ridgeline plot for capture price
    plt.figure(figsize=(12, 8))


    joyplot(
    data=melted_capture_ratio_df, 
    column='Capture Price', 
    by='Year', 
    bins=80,  # Specifying the number of bins
    overlap=1.0, 
    linewidth=1,
    kind='kde',
    bw_method=0.5,
    range_style='own',
    tails=0.0, 
    grid='y',
    fade=False,
    colormap=cm.viridis
    )

    # Add labels and title
    chart_title = f"Ridgeline Plot by Year for Capture Price"
    plt.suptitle(chart_title, y=1.05)

    # Format X axis with 0%
    formatter = FuncFormatter(lambda x, _: '{:.2f}'.format(x)) #was {:.0%}'
    plt.gca().xaxis.set_major_formatter(formatter)
    plt.xlabel('Peaker Captured Spot Price')

    #plt.xlabel('Capture Price Ratio to Avg Price')
    # plt.ylabel('Density')

    #Save Image
    output_file = gbl.gbl_output_general_data['image_data_path']
    image_file_name_adder = "Test2"
    image_file_name = image_file_name_adder + ' Annual Capture Price Ridgeline Plot'
    save_plot(plt, image_file_name, output_file)

    show_visualizations_func() 
    
    return
    #plt.show()
