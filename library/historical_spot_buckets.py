from library import globals as gbl
from library import config as cfg

from library.class_objects.other_classes.classes import TrackedDict, ForecastFile

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from library.functions import (
    consolidate_annual_files, 
    show_visualizations_func, 
    save_plot, 
    remove_folder_contents,
    create_folder)


import pandas as pd
from prettytable import PrettyTable
from colorama import Fore, Back, Style, init
from tabulate import tabulate
from tqdm import tqdm
import re
from rich.console import Console
from rich.table import Table

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

########################################
# Helper Functions
########################################
# Define a function to remove ANSI escape codes
# This is needed because when you save the file to csv, the ANSI escape codes are saved as well
# This needs to be called prior to saving the file to csv
# Define a function to remove ANSI escape codes
def remove_ansi_escape_codes(text):
    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', text) if isinstance(text, str) else text
#---------------------------------------------------
# Define a function to clean column headers
def clean_and_reformat_header(text):
    # Remove ANSI escape codes
    text = remove_ansi_escape_codes(text)
    # Replace newline characters with spaces
    text = text.replace('\n', ' ')
    return text
#---------------------------------------------------
# Function to print DataFrame using tabulate with carriage returns in column headers
def print_tabulate_table(df, new_columns):
    df.columns = new_columns
    print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))

# def print_pretty_table(df,new_columns):
#     x = PrettyTable()
#     #x.field_names = df.columns.tolist()
#     x.field_names = new_columns
    
#     for row in df.itertuples(index=False, name=None):
#         x.add_row(row)
#     print(x)

#---------------------------------------------------
# Function to compute top % summary
#---------------------------------------------------
def compute_top_summary(df, column_name, percentage):
    #print(f" df.columns: {df.columns}")
    top_hours = int(len(df) * percentage)
    if top_hours == 0:
        return float('nan'), float('nan')  # Return NaN if there are no top hours to consider
    top_df = df.nlargest(top_hours, column_name)
    avg_price = top_df[column_name].mean()
    percent_value = top_df[column_name].sum() / df[column_name].sum()
    return avg_price, percent_value
#---------------------------------------------------
# Function to compute 'Percent of Value in Received Hours'
#---------------------------------------------------
def compute_received_value_percent(df, column_name, variable_cost,percentage):
    # Filter the DataFrame for hours where the price is greater than the variable cost
    # print(f" df.shape.head(): {df.head()}")
    # print(f" df.describe(){df.describe()}")
    received_df = df[df[column_name] > variable_cost]
    if received_df.empty:
        return float('nan')
    
    top_hours = int(len(received_df) * percentage)
    if top_hours == 0:
        return float('nan')
    
    top_received_df = received_df.nlargest(top_hours, column_name)
    #print(f" top_received_df.describe(): {top_received_df.describe()}")
    percent_value = top_received_df[column_name].sum() / received_df[column_name].sum()
    return percent_value

################################################### 
#---------------------------------------------------
# Function to sort forecast data high to low
#---------------------------------------------------
def sort_forecast_data(df, column_name='P50'):
    return df.sort_values(by=column_name, ascending=False)

#---------------------------------------------------
# Function to sort forecast data low to high
#---------------------------------------------------
def sort_forecast_data_low_high(df, column_name='DateTime'):
    return df.sort_values(by=column_name, ascending=True)

#---------------------------------------------------
# Function to calculate the average top % price across all historical years
#---------------------------------------------------
def calculate_average_top_pct(historical_top_percent_summary_df, top_pct_band):
    print(historical_top_percent_summary_df)
    try:
        mean_value = historical_top_percent_summary_df[top_pct_band].mean()
        print(f"Calculated mean for {top_pct_band}: {mean_value}")
        return mean_value
    except KeyError as e:
        print(f"KeyError: Column {top_pct_band} not found in DataFrame.")
        return None
    except Exception as e:
        print(f"Error calculating average for {top_pct_band}: {e}")
        return None
#---------------------------------------------------
# Apply the tope % band from historical data or dollar cap
#---------------------------------------------------
def apply_top_band(
    sorted_forecast_df, 
    top_pct_value, 
    top_pct_band, year):

    # Extract the numeric part of the top_pct_band string (e.g., 'Top 10%' -> 10)
    percentage = int(top_pct_band.split()[1].replace('%', ''))

    # Calculate the number of top hours to pick
    count_top_hours = int(len(sorted_forecast_df) * (percentage / 100))

    # Get the top hours from forecast data
    top_forecast_df = sorted_forecast_df.head(count_top_hours).copy()
    print(f" Processing year: {year}")

    print(f" Min after applying top band: {top_forecast_df['P50'].min()}")
    print(f" Max after applying top band: {top_forecast_df['P50'].max()}")

    # Create a boolean mask where P50 values are greater than top_pct_value
    mask = top_forecast_df['P50'] > top_pct_value

    # Replace the P50 values with the top_pct_value and update 'Old Price' and 'Replaced' columns
    top_forecast_df['Old Price'] = None  # Initialize the 'Old Price' column with None
    top_forecast_df['Replaced'] = False  # Initialize the 'Replaced' column with False

    if mask.any():
        top_forecast_df.loc[mask, 'Old Price'] = top_forecast_df.loc[mask, 'P50']
        top_forecast_df.loc[mask, 'P50'] = top_pct_value
        top_forecast_df.loc[mask, 'Replaced'] = True
        print(f"Top {count_top_hours} rows for {top_pct_band} replaced with value: {top_pct_value}")
    else:
        print(f"No rows replaced for {top_pct_band}")

    return top_forecast_df
#---------------------------------------------------

#---------------------------------------------------

def apply_historical_to_forecast(
            forecast_folder,
            output_data_path, 
            historical_top_percent_summary_df, 
            temp_forecast_data_dict, 
            start_year, 
            top_pct_band, 
            historical_year=None, 
            dollar_cap=None,
            ):

    global gbl_output_template
    
    try:
        top_pct_value = None
        if dollar_cap is not None:
            top_pct_value = dollar_cap
        else:
            if historical_year is None:
                # Calculate the average top % price across all historical years
                top_pct_value = calculate_average_top_pct(historical_top_percent_summary_df, top_pct_band)
            else:
                if historical_year not in historical_top_percent_summary_df.index:
                    Console.print(f"No historical data for year {historical_year}", style="bold red")
                    return None
                top_pct_value = historical_top_percent_summary_df.loc[historical_top_percent_summary_df['Year'] == historical_year, top_pct_band].values[0]

        print(f"Top % value: {top_pct_value}")
        print(f"Applying historical data to forecast data starting from {start_year}")
        if top_pct_value is None:
            Console.print(f"Invalid top % band: {top_pct_band}", style="bold red")
            return None
        
        for file_name, forecast_df in temp_forecast_data_dict.items():

            # Extract the year from the DateTime column
            forecast_df['Year'] = forecast_df['DateTime'].dt.year
            print(f" forecast_df: {forecast_df}")
            
            # Process each year within the DataFrame
            for year in forecast_df['Year'].unique():
                if year < start_year:
                    # If TRUE, skip to the next year but before you to so
                    # you need to unsort the file and save it to a csv in the same
                    # folder as all the files that end up being processed because
                    # at the end of the routine we merge all the individual files into
                    # a larger file

                    # Sort the combined data by DateTime in ascending order
                    combined_df = forecast_df[forecast_df['Year'] == year].copy() #>>> NEW
                    combined_df.loc['Old Price'] = None #Plug Header that is not used if file not being processed
                    combined_df.loc['Replaced'] = None #Plug Header that is not used if file not being processed

                    # Save the combined sorted DataFrame to a CSV file
                    #output_file_var = f'combined_forecast_{year}_with_{top_pct_band.replace(" ", "_")}.csv'
                    # Pull fle template from dictionary
                    file_name_str = gbl.gbl_output_template['combined_forecast_filename_str']
                    output_file_var = file_name_str.format(year, top_pct_band.replace(" ", "_"))
                    print(f"output_file_var: {output_file_var}")
                    output_file = os.path.join(output_data_path, output_file_var)
                    print(f"output_file: {output_file}")
                    combined_df.to_csv(output_file, index=True)
                    
                    #continue
                else:
                    yearly_forecast_df = forecast_df[forecast_df['Year'] == year] #>>> NEW
                    
                    # Sort the forecast data high to low
                    sorted_forecast_df = sort_forecast_data(yearly_forecast_df)

                    print(f" Processing year: {year}")
                    print(f" Min before applying top band: {sorted_forecast_df['P50'].min()}")
                    print(f" Max before applying top band: {sorted_forecast_df['P50'].max()}")

                    # Apply the top % band from historical data or dollar cap
                    top_forecast_df = apply_top_band(sorted_forecast_df, top_pct_value, top_pct_band, year)

                    # Check if top_forecast_df is None
                    if top_forecast_df is None:
                        continue
            
                    # Combine the top forecast data with the remaining forecast data
                    combined_df = pd.concat([top_forecast_df, sorted_forecast_df]).drop_duplicates(keep='last')
                    
                    # Sort the combined data by DateTime in ascending order
                    combined_sorted_df = sort_forecast_data_low_high(combined_df)
                    
                    # Save the combined sorted DataFrame to a CSV file
                    file_name_str = gbl.gbl_output_template['combined_forecast_with_Top_Percent_Price_filename_str']
                    #output_file_var = f'combined_forecast_{year}_with_{top_pct_band.replace(" ", "_")}.csv'
                    output_file_var = file_name_str.format(year, top_pct_band.replace(" ", "_"))
                    output_file = os.path.join(output_data_path, output_file_var)
                    combined_sorted_df.to_csv(output_file, index=True)
                        
                    print("Adjusted Forecast Completed!")
    except Exception as e:
        print(f"Error in apply_historical_to_forecast: {e}")

#########################################
# Functions to support interactive user input
#########################################
def get_validated_input(prompt, validation_func=None, error_message="Invalid input. Please try again."):
        while True:
            user_input = input(prompt)
            if user_input.lower() == 'exit':
                return 'exit'
            if validation_func:
                try:
                    if validation_func(user_input):
                        return user_input
                except Exception as e:
                    print(f"{error_message} Error: {e}")
            else:
                return user_input
            print(error_message)
#---------------------------------------------------
def is_valid_year(year_str):
    year = int(year_str)
    if year < 1000 or year > 9999:
        raise ValueError("Year must be a four-digit number.")
    return True
#---------------------------------------------------
def is_valid_top_pct_band(band_str):
    parts = band_str.split()
    if len(parts) != 3:
        return False
    if parts[0].lower() != 'top':
        return False
    if not parts[1].endswith('%') or not parts[1][:-1].isdigit():
        return False
    if parts[2].lower() != 'price':
        return False
    return True
#---------------------------------------------------
def is_valid_dollar_cap(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

#######################################################
# Visualizations
###############################################
def create_visualization(
    filename, 
    year, 
    image_file_name_adder, 
    output_path,
    ):


    #Step 1: Show comparative duration curves for a given year(s)

    #Step 2: Show comparative time series graphs for a given year(s) using red markers for the top X hours that were replaced

    graph_year = year

    #path = 'C:/Users/kaczanor/OneDrive - Enbridge Inc/Documents/Python/EDC Hourly Capacity Factor Q2 2024/outputs/csv_data/'
    path = output_path
    input_file_var = filename
    input_file = os.path.join(path, input_file_var)
    df = pd.read_csv(input_file, parse_dates=['DateTime'])

    # Then filter data for the year
    df = df[df['DateTime'].dt.year == graph_year]

    print(df)

    df.set_index('DateTime', inplace=True)

    # Set the style
    sns.set_style('darkgrid')

    # Create a new figure and set the figsize
    plt.figure(figsize=(16, 8))

    # Plot the time series graph without confidence interval
    sns.lineplot(data=df, x='DateTime', y='P50', label='Forecast Data', errorbar=None)

    # Plot the original uncapped prices as red markers
    sns.scatterplot(data=df[df['Replaced'] == True], x='DateTime', y='Old Price', color='red', label='Original Top 10% Hours')

    # Set the title and labels
    chart_title = f'Hourly Spot Electricity Prices for {year}'
    plt.title(chart_title)
    plt.xlabel('Date')
    plt.ylabel('Price ($/MWh)')
    plt.legend()

    # Display the plot
    cfg.config.show_visualizatons = True
    show_visualizations_func()
    #plt.show()

    #Save the plot
    image_file_name = image_file_name_adder + chart_title
    save_plot(plt, chart_title, image_file_name)

########################################
# Processing of Hourly Data Dictionary
########################################
def process_hourly_data_dict(
    temp_hourly_data_dict, 
    variable_cost, 
    color_settings
     ):

    #--------------------------------------------
        # Process each hisotorical hourly power price dataset in the dictionary
        for key, value in temp_hourly_data_dict.items():
            df = value['data']
            print(f" df.columns: {df.columns}")
            frcst_output_csv_file_path = value['frcst_output_csv_file_path']
            datetime_column = value['datetime_column'] 
            price_column = value['price_column']

            print(f"Processing dataset: {key}")
            print(f"Column names for {key}: {df.columns.tolist()}")
        
            
            summary = {}
            #Loop through each year in the dataset
            for year, group in df.groupby(df.index.year):
                print(year)
                print(group)
                # Print stats for the data set
                print(group.describe())

                if group.empty:
                    print(f"No data for year {year} in dataset {key}")
                    continue
                
                print(f"Processing year: {year}, number of rows: {len(group)}")
                
                summary[year] = {}
                # Loop through each percentage band 
                for pct in [0.10, 0.15, 0.20, 0.25, 0.50, .75, 1.0]:
                    color = color_settings[int(pct * 100)]
                    
                    # Compute the average price and percent value for the top % hours
                    avg_price, percent_value = compute_top_summary(group, price_column, pct)
                    # Compute the percent value in received hours
                    percent_value_received = compute_received_value_percent(group, price_column, variable_cost, pct)
                    # Format the values
                    formatted_avg_price = f"${avg_price:,.2f}"
                    formatted_percent_value = f"{percent_value:.1%}"
                    formatted_percent_value_received = f"{percent_value_received:.1%}"

                    # Store the values in the summary dictionary
                    summary[year][f'Top {int(pct*100)}%'] = f"{color}{formatted_avg_price}{Style.RESET_ALL}"
                    summary[year][f'% of Value {int(pct*100)}%'] = f"{color}{formatted_percent_value}{Style.RESET_ALL}"
                    summary[year][f'% of Value in Received Hours {int(pct*100)}%'] = f"{color}{formatted_percent_value_received}{Style.RESET_ALL}"

            if not summary:
                print(f"No summaries created for dataset {key}")
                continue
            
            #--------------------------------------------
            # Transpose and convert summary dictionary to DataFrame
            summary_df = pd.DataFrame(summary).T

            #--------------------------------------------
            # Unique code for Tabulate library
            # Apply color to the 'Year' column
            summary_df.index = [f"{Fore.WHITE}{year}{Style.RESET_ALL}" for year in summary_df.index]
            
            # For PrettyTable/Tabulate
            # This converts the DataFrame index (index) to a column and renames it to 'Year'.
            summary_df.reset_index(inplace=True)
            summary_df.rename(columns={'index': 'Year'}, inplace=True)

            new_columns = [
                Fore.WHITE + 'Year',
                Fore.RED + 'Top 10%' + Style.RESET_ALL + '\n' + Fore.RED + 'Price',
                Fore.RED + '% Value' + Style.RESET_ALL + '\n' + Fore.RED + '10%',
                Fore.RED + '% Value' + Style.RESET_ALL + '\n' + Fore.RED + 'in Rec' + Style.RESET_ALL + '\n' + Fore.RED + 'Hrs 10%',
                Fore.BLUE + 'Top 15%' + Style.RESET_ALL + '\n' + Fore.BLUE + 'Price',
                Fore.BLUE + '% Value' + Style.RESET_ALL + '\n' + Fore.BLUE + '15%',
                Fore.BLUE + '% Value' + Style.RESET_ALL + '\n' + Fore.BLUE + 'in Rec' + Style.RESET_ALL + '\n' + Fore.BLUE + 'Hrs 15%',
                Fore.GREEN + 'Top 20%' + Style.RESET_ALL + '\n' + Fore.GREEN + 'Price',
                Fore.GREEN + '% Value' + Style.RESET_ALL + '\n' + Fore.GREEN + '20%',
                Fore.GREEN + '% Value' + Style.RESET_ALL + '\n' + Fore.GREEN + 'in Rec' + Style.RESET_ALL + '\n' + Fore.GREEN + 'Hrs 20%',
                Fore.CYAN + 'Top 25%' + Style.RESET_ALL + '\n' + Fore.CYAN + 'Price',
                Fore.CYAN + '% Value' + Style.RESET_ALL + '\n' + Fore.CYAN + '25%',
                Fore.CYAN + '% Value' + Style.RESET_ALL + '\n' + Fore.CYAN + 'in Rec' + Style.RESET_ALL + '\n' + Fore.CYAN + 'Hrs 25%',
                Fore.YELLOW + 'Top 50%' + Style.RESET_ALL + '\n' + Fore.YELLOW + 'Price',
                Fore.YELLOW + '% Value' + Style.RESET_ALL + '\n' + Fore.YELLOW + '50%',
                Fore.YELLOW + '% Value' + Style.RESET_ALL + '\n' + Fore.YELLOW + 'in Rec' + Style.RESET_ALL + '\n' + Fore.YELLOW,
                Fore.MAGENTA + 'Top 75%' + Style.RESET_ALL + '\n' + Fore.MAGENTA + 'Price',
                Fore.MAGENTA + '% Value' + Style.RESET_ALL + '\n' + Fore.MAGENTA  + '75%',
                Fore.MAGENTA + '% Value' + Style.RESET_ALL + '\n' + Fore.MAGENTA + 'in Rec' + '\n' + Fore.MAGENTA + 'Hrs 75%',
                Fore.LIGHTGREEN_EX + 'Top 100%' + Style.RESET_ALL + '\n' + Fore.LIGHTGREEN_EX + 'Price',
                Fore.LIGHTGREEN_EX + '% Value' + Style.RESET_ALL + '\n' + Fore.LIGHTGREEN_EX  + '100%',
                Fore.LIGHTGREEN_EX + '% Value' + Style.RESET_ALL + '\n' + Fore.LIGHTGREEN_EX + 'in Rec' + '\n' + Fore.LIGHTGREEN_EX + 'Hrs 100%'

            ]

            #--------------------------------------------
            # Print the DataFrame using PrettyTable
            print("*" *50)
            print(f"Summary for dataset: {key}")
            print("*" *50)
            print_tabulate_table(summary_df, new_columns)

            #--------------------------------------------
            # Clean-up data frame as it contains ANSI escape codes
            # Remove ANSI escape codes from the DataFrame prior to saving as CSV
            clean_df = summary_df.applymap(remove_ansi_escape_codes)

            # Remove ANSI escape codes from the column headers
            # Clean and reformat the column headers
            clean_df.columns = [clean_and_reformat_header(col) for col in clean_df.columns]

            #--------------------------------------------
            # Save the summary data frame to a CSV file
            
            #folder
            output_path = gbl.gbl_tracked_loaded_dict_json_file_data["Output_Data"]['Processed_Price_Forecast'][key]['Output_File_Attributes']['forecast_post_processed_folder_path']
            #filename
            output_file_var = gbl.gbl_output_template['top_hour_percentage_summary_filename_str']
            output_file = os.path.join(output_path, output_file_var)
            clean_df.to_csv(output_file, index=False)
            
            # Pass and save the data to JSON file
            # The output folder in the temp dictionary is the 'frcst_output_csv_file_path' key in the 
            # the greater file dictionary. Use that key to pass the file name of the new file back to the
            # to the greater file dictionary
            gbl.gbl_tracked_loaded_dict_json_file_data["Output_Data"]["Processed_Price_Forecast"][key]['Output_File_Attributes']['top_hour_percentage_summary'] = output_file
            gbl.gbl_tracked_loaded_dict_json_file_data.save_to_json(gbl.gbl_json_file_path_loaded)

        print("Summary tables have been created and saved to CSV files.")
        print("*" *50)
        print("*" *50)

#########################################
# Make Final Changes to Data
########################################
def change_forecast(
        gvariable_cost, 
        input_filename_template, 
        output_filename_template, 
        datetime_column
        ):
    '''
    This allows the user to pull historical data and super impose the pricing in the top X hours from historical data onto the forecast data.

    The user must decide which years in the forecast to pull the average price from and which bucket to use.

    '''
    print("Step 5: Super-impose onto forecast data")
    output_path = gbl.gbl_tracked_loaded_dict_json_file_data['Output_Data']['General_Data']['temp_data_path']

    # Initialize console for pretty printing
    console = Console()
    remove_folder_contents(output_path)

    #-------------------------------------------------------------------
    # Load Historical Summary Data of Top % Hours
    #-------------------------------------------------------------------
    for key1, value1 in gbl.gbl_tracked_loaded_dict_json_file_data["Input_Data"]["Price_Forecast"].items():

        # Pull path for loading historical data
        input_file_attributes =value1['Input_File_Attributes']
        # Pass file path to file path variable
        file_path = gbl.gbl_tracked_loaded_dict_json_file_data['Input_Data']['General_Data']['historic_data_path']
        
        # Load annual historical data with percentage bands
        for key2, value2 in gbl.gbl_tracked_loaded_dict_json_file_data["Output_Data"]["Processed_Price_Forecast"].items():
            output_file_attributes = value2['Output_File_Attributes']

            file_path = gbl.gbl_tracked_loaded_dict_json_file_data['Output_Data']['Processed_Price_Forecast'][key2]['Output_File_Attributes']['top_hour_percentage_summary']

            # Load historical hourly data
            historical_top_percent_summary_df = pd.read_csv(file_path)

            # Prepare to pull Foreasted P50 file name from dictionary
            file_path_P50 = gbl.gbl_tracked_loaded_dict_json_file_data['Output_Data']['Processed_Price_Forecast'][key2]['Output_File_Attributes']['P50_hourly_spot_electricity']
            image_data_path = gbl.gbl_tracked_loaded_dict_json_file_data['Output_Data']['General_Data']['image_data_path']
            print(f" file_path_P50: {file_path_P50}")

        # Clean the data
        print(f"historical_top_percent_summary_df.columns: {historical_top_percent_summary_df.columns}")
        for col in historical_top_percent_summary_df.columns:
            if historical_top_percent_summary_df[col].dtype == 'object':
                print(f"Cleaning column: {col}")
                # Remove dollar signs and percentage signs, then convert to float
                historical_top_percent_summary_df[col] = historical_top_percent_summary_df[col].str.replace('$', '', regex=False).str.replace('%', '', regex=False)
                historical_top_percent_summary_df[col] = pd.to_numeric(historical_top_percent_summary_df[col], errors='coerce')

        # Convert the Year column to integer
        historical_top_percent_summary_df['Year'] = historical_top_percent_summary_df['Year'].astype(int)
        #print(f"historical_top_percent_summary_df: {historical_top_percent_summary_df}")']


        # Use dictionary comprehension
        temp_forecast_data_dict = {
            os.path.basename(file_path_P50): pd.read_csv(file_path_P50, parse_dates=['DateTime'], index_col='DateTime').reset_index()
        }

        # Print the keys to verify
        print(f" temp_forecast_data_dict.keys(): {temp_forecast_data_dict.keys()}")

        # print(f" Min at time of loading file {file_path_edcq2_2024['P50'].min()}")
        # print(f" Max at time of loading file: {file_path_edcq2_2024['P50'].max()}")


        while True:
            # try:
            # Get user input for top percentage band
            top_pct_band = get_validated_input(
                "Enter the top percentage band (e.g., 'Top 10% Price', 'Top 15% Price', 'Top 20% Price', 'Top 25% Price') or 'exit' to quit: ",
                is_valid_top_pct_band,
                "Invalid format. Please enter in the format 'Top X% Price'."
            )
            if top_pct_band == 'exit':
                break

            # Get user input for price adjustment type
            adjustment_type = get_validated_input(
                "What type of price adjustment do you want to make to the forecast (e.g., '$' or 'year') or 'exit' to quit: ",
                lambda x: x in ['$', 'year'],
                "Invalid input. Please enter '$' or 'year'."
            )
            if adjustment_type == 'exit':
                break

            dollar_cap = None
            historical_year = None
            if adjustment_type == 'year':
                historical_option = get_validated_input(
                    "Enter 'average' to use the average top % price across all historical years, or enter a specific historical year, or 'exit' to quit: "
                )
                if historical_option == 'exit':
                    break

                if historical_option.lower() == 'average':
                    historical_year = None
                else:
                    historical_year = int(get_validated_input(
                        "Enter a specific historical year (e.g., 2020) or 'exit' to quit: ",
                        is_valid_year,
                        "Invalid year. Please enter a valid four-digit year."
                    ))
                    if historical_year == 'exit':
                        break
            elif adjustment_type == '$':
                dollar_cap = float(get_validated_input(
                    "Enter the fixed $/MWh cap for the forecast (e.g., 302.04) or 'exit' to quit: ",
                    is_valid_dollar_cap,
                    "Invalid input. Please enter a valid number."
                ))
                if dollar_cap == 'exit':
                    break

            start_year = int(get_validated_input(
                "Enter the starting forecast year to apply the changes (e.g., 2023) or 'exit' to quit: ",
                is_valid_year,
                "Invalid year. Please enter a valid four-digit year."
            ))
            if start_year == 'exit':
                break
            
            for key3, value3 in gbl.gbl_tracked_loaded_dict_json_file_data["Input_Data"]["Price_Forecast"].items():
                
                forecast_folder = input_file_attributes['base_path_processed_data']
                output_folder = gbl.gbl_tracked_loaded_dict_json_file_data["Output_Data"]["General_Data"]['temp_data_path']

                # Apply historical data to forecast data
                print(f" historical_top_percent_summary_df: {historical_top_percent_summary_df}")
                apply_historical_to_forecast(
                    forecast_folder, 
                    output_folder, 
                    historical_top_percent_summary_df, 
                    temp_forecast_data_dict, 
                    start_year, 
                    top_pct_band, 
                    historical_year, 
                    dollar_cap)

                # merge all annual files and delete temp files
                # Create file path to load individual files
                input_data_path = output_path
                # Create file path for output file
                #output_data_path = input_file_attributes['output_path']
                output_data_path = output_file_attributes['frcst_output_csv_file_path']
                # Use template name to locate all the files create as they all have the 
                # the same prefix
                input_filename_template_search_term =  "combined_forecast_*.csv"
                output_filename_template = gbl.gbl_output_template['combined_forecast_with_Top_Percent_Price_filename_str']
                datetime_column = 'DateTime'
                
                filename = consolidate_annual_files(
                            forecast_folder, 
                            output_data_path,
                            input_data_path, 
                            input_filename_template_search_term, 
                            datetime_column, 
                            output_filename_template
                            )

                print("Consolidation of Annual Files Completed!")

                #Create Visualizations
                #image_file_name_adder = r'C:\Users\kaczanor\OneDrive - Enbridge Inc\Documents\Python\EDC Hourly Capacity Factor Q2 2024\outputs\image_data'
                image_file_name_adder = image_data_path
                year = 2036
                create_visualization (
                    filename, 
                    year, 
                    image_file_name_adder, 
                    output_data_path
                    )

            # Exit the loop after successful processing
            break


            # except Exception as e:
            #     print(f"An error occurred: {e}")

########################################
# Main Adjustment Function
########################################
def adjust_forecast_data(
            gvariable_cost, 
            input_filename_template, 
            output_filename_template, 
            datetime_column,
            p50_label
        ):

    # Initialize colorama
    init(autoreset=True)
    # Define color settings in a dictionary
    color_settings = {
        10: Fore.RED,
        15: Fore.BLUE,
        20: Fore.GREEN,
        25: Fore.CYAN,
        50: Fore.YELLOW,
        75: Fore.MAGENTA,
        100: Fore.LIGHTGREEN_EX
    }

    # Set display options in Pandas
    # pd.set_option('display.max_rows', None)
    # pd.set_option('display.max_columns', None)

    '''
    colorama Color Options
    Foreground (Text) Colors
    Fore.BLACK
    Fore.RED
    Fore.GREEN
    Fore.YELLOW
    Fore.BLUE
    Fore.MAGENTA
    Fore.CYAN
    Fore.WHITE
    Fore.RESET (to reset to default color)

    Background Colors
    Back.BLACK
    Back.RED
    Back.GREEN
    Back.YELLOW
    Back.BLUE
    Back.MAGENTA
    Back.CYAN
    Back.WHITE
    Back.RESET (to reset to default background)

    Styles
    Style.DIM
    Style.NORMAL
    Style.BRIGHT
    Style.RESET_ALL (to reset all styles)
    '''

    #########################################
    # Step 4: Calculate Top % Hour Pricing for both Historical and Forecast Data
    #########################################

    '''
    This code adjustes the forecast data by applying different options for adjustment

    Option 1:  Hard Price Caps in X hours 

    Option 2:  Impute Historical Data Buckets on Forecast

    Option 3:  Other

    Option 4:  Other

    Option 5:  Other
    '''
    print("*" *50)
    print("*" *50)
    print("Calculate Top % Hour Pricing for both Historical and Forecast Data")

    # Create dictionary to hold the historical data and the forecast data prior to loading them
    temp_hourly_data_dict = {}

    # Define the variable cost of the generator
    variable_cost = gvariable_cost 

    # Load the historical power price data
    file_path_hist = gbl.gbl_tracked_loaded_dict_json_file_data["Input_Data"]["General_Data"]["historic_data_path"]
    file_path_hist = os.path.normpath(file_path_hist)
    print(f" file_path_hist: {file_path_hist}")
    # Load the historical data to a data frame
    df_hist = pd.read_csv(file_path_hist, parse_dates=['begin_datetime_mpt'])  # Replace 'datetime_column_name' with the actual column name


    # Ensure datetime is the index
    df_hist.set_index('begin_datetime_mpt', inplace=True)
    #print(f" df_hist.head(): {df_hist.head()}")

    #Loop through price forecast dictionary
    for key1, value1 in gbl.gbl_tracked_loaded_dict_json_file_data["Output_Data"]["Processed_Price_Forecast"].items():
        
         # Debugging: Check the type of value1
        print(f"key1: {key1}, type of value1: {type(value1)}, value1: {value1}")

        if isinstance(value1, dict):
            output_file_attributes = value1.get('Output_File_Attributes', None)
            if output_file_attributes is not None:
                # Further processing with output_file_attributes
                print(f"output_file_attributes: {output_file_attributes}")
            else:
                print(f"Output_File_Attributes not found in value1 for key {key1}")
        else:
            print(f"Skipping key {key1} as value1 is not a dictionary.")

        # Check the complete structure of gbl.gbl_tracked_loaded_dict_json_file_data
        print(f"Complete structure of gbl_tracked_loaded_dict_json_file_data: {gbl.gbl_tracked_loaded_dict_json_file_data}")

        
        #Second set p variables so that you can add the forecast data to the hourly dictionary
        #--------------------------------------------
        #Create a new output folder for the prossessed data
        frcst_output_csv_file_path = output_file_attributes['frcst_output_csv_file_path']
        base_processed_folder = "Processed Forecast Data"
        forecast_post_processed_folder_path = os.path.join(frcst_output_csv_file_path, base_processed_folder)
        create_folder(forecast_post_processed_folder_path)
        # Update the Dictionary/JSON structure to include the new folder path
        output_file_attributes['forecast_post_processed_folder_path'] = forecast_post_processed_folder_path
        # Save to JSON file
        gbl.gbl_tracked_loaded_dict_json_file_data.save_to_json(gbl.gbl_json_file_path_loaded)

        # Create the path to pull the exising p50 file from
        P50_file_name = output_file_attributes['pwr_file_name_p50']
        p50_file_path = os.path.join(frcst_output_csv_file_path, P50_file_name)
        

        #--------------------------------------------
        # Load Forecast Data
        # Check this as its passing the same file path to 4x file path variables
        # If this was assessing mulitple price curves (e.g. EDC Q3 2024 versus EDC Q4 2024)
        # these paths would need to be passed to the variable that were held in some form of containter.

    for key2, value2 in gbl.gbl_tracked_loaded_dict_json_file_data["Input_Data"]["Price_Forecast"].items():
        input_file_attributes =value2['Input_File_Attributes']

        
        datetime_column = input_file_attributes['datetime_column']

        #Load the P50 file for the forecast data that you want to adjust
        df_forecast = pd.read_csv(p50_file_path, parse_dates=['DateTime'])
        print(f" df_forecast.head(): {df_forecast.head()}")

        #--------------------------------------------
        # Ensure datetime is the index
        df_forecast.set_index('DateTime', inplace=True)

        #--------------------------------------------
        # Resample historical hourtly data to yearly data
        # Unclear where this data goes!!!!!!!!!
        yearly_data_hist = df_hist.resample('Y').agg({'pool_price': ['sum', 'count']}) 
        yearly_data_hist.columns = ['total_value', 'total_hours']
        print(f"yearly_data_hist: {yearly_data_hist}")

        yearly_data_df = df_forecast.resample('Y').agg({'P50': ['sum', 'count']})
        yearly_data_df.columns = ['total_value', 'total_hours']
        print(f"yearly_data_df: {yearly_data_df}")


        #--------------------------------------------
        # Build a temporary data frame dictionary to hold each data frame and metadata
        # for each price forecast file

        # Create Temp dictionary to hold data frames and meta data
        temp_hourly_data_dict[key2] = {
            'data': df_forecast,
            #'data': yearly_data_df,
            'sub_folder': key2,
            'datetime_column' : datetime_column,
            'price_column': p50_label,
            'frcst_output_csv_file_path': forecast_post_processed_folder_path
        }
        
    # End of Loop

    # At the end of the this loop the hourly_data_dict should be populate as follows
    #     hourly_data_dict = {
    #     'Historical': {'data': df_hist, 'sub_folder': "Processed Historical Data", 'datetime_column' : 'DateTime', 'price_column' : 'pool_price'}, 
    #     'EDC Q2 2023': {'data': df_edcq2_2023, 'sub_folder': "EDC Q2 2023", 'datetime_column' : 'begin_datetime_mpt', 'price_column' : 'P50'}, 
    #     'EDC Q2 2024': {'data': df_edcq2_2024, 'sub_folder': "EDC Q2 2024", 'datetime_column' : 'begin_datetime_mpt', 'price_column' : 'P50'},
    #     'EDC Q3 2024': {'data': df_edcq3_2024, 'sub_folder': "EDC Q3 2024", 'datetime_column' : 'begin_datetime_mpt', 'price_column' : 'P50'}
    # }

    # Pass hourly_data_dict to the function to calculate the summary of hours
    # the reached a threshold of the top X% hours
    process_hourly_data_dict(
        temp_hourly_data_dict, 
        variable_cost, 
        color_settings, #loaded_dict
        )

    # Superimpose historical data on forecast data
    change_forecast(
            gvariable_cost, 
            input_filename_template, 
            output_filename_template, 
            datetime_column,
            )

     
