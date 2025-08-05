
from library import globals as gbl
from library import config as cfg
from library import functions  # Import the functions.py module

from library.functions import (
    delete_folder, 
    create_folder,
    process_excel_data
    )

from library.class_objects.other_classes.classes import TrackedDict, ForecastFile

import os
from openpyxl import load_workbook
import pandas as pd
import json

import threading
from queue import Queue # needed to return wb object from load_workbook_thread() function
import time
from tqdm import tqdm 
import logging
import calendar

#------------------------------------------------
# Helper function to create DateTime index
#------------------------------------------------
def combine_date_and_hour(df):
    #print(f"Combining date and hour columns")
    try:
        df['DateTime'] = pd.to_datetime(df['Date']) + pd.to_timedelta(df['HE'], unit='h')
        return df
    except Exception as e:
        print(f"Error combining date and hour columns: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on error

# Helper function to identify DST start and end dates
def get_dst_dates(year):
    # Second Sunday in March
    march_dates = pd.date_range(start=f'{year}-03-01', end=f'{year}-03-14')
    #dst_start_date = march_dates[march_dates.weekday == 6][1]
    #dst_start_date = march_dates[march_dates.dayofweek == 6][1] #Pylint does not like this
    dst_start_date = march_dates[march_dates.to_series().dt.dayofweek == 6][1]
    
    # First Sunday in November
    november_dates = pd.date_range(start=f'{year}-11-01', end=f'{year}-11-07')
    #dst_end_date = november_dates[november_dates.weekday == 6][0]
    #dst_end_date = november_dates[november_dates.dayofweek == 6][0] #Pylint does not like this
    dst_end_date = november_dates[november_dates.to_series().dt.dayofweek == 6][0]
    
    return dst_start_date, dst_end_date
#####################################
# Helper function to process each excel source file with hourly forecast data

def process_sheet(wb, ws, g_start_year, g_end_year, year_str, input_file_attributes):
    try:
        logging.info(f"Processing sheet: {year_str}")
        print(f"Processing sheet: {year_str}")
        ws = wb[year_str]
        data = list(ws.values)
        cols = data[0]
        #Exclude the first row which contains the column names
        df = pd.DataFrame(data[1:], columns=cols)

        print(f"Initial data loaded for sheet {ws}, first few rows:\n{df.head()}")
        print(f"Initial Data First set of Unique values in HE column before -1 adjustment for sheet {ws}: {df['HE'].unique()}")
        
        # Print dat for January 1, first year
        if input_file_attributes['file_structure'] == 'multiple_worksheets_YYYY':
            first_day_date = pd.to_datetime(f"{g_start_year}-01-01")    
        else:
            first_day_date = pd.to_datetime(f"{year_str}-01-01")
        
        ##########################
        # 1) figure out how many hours we actually need
        year_int = int(year_str)
        hours = 24 * (366 if calendar.isleap(year_int) else 365)

        # 2) slice the data list down to just those rows
        #    data[0] is the header, so data[1 : hours+1] are the next `hours` rows
        header = data[0]
        body   = data[1 : hours+1]

        # 3) build your DataFrame from that slice
        df = pd.DataFrame(body, columns=header)
        print(df.head(5))  # Print first 5 rows for debugging
        
        
        # 4) parse the full timestamp
        df['Date'] = pd.to_datetime(
            df['Date'],
            #format='%Y-%m-%d %H:%M:%S',   # matches "YYYY-MM-DD HH:MM:SS"
            format='%Y-%m-%d',
            errors='raise'
        )

        # sanity check
        if len(df) != hours:
            logging.warning(f"Sheet {year_int}: expected {hours} rows, got {len(df)}")
        ##########################
        
        # Convert 'Date' column to datetime
        df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
        print(df.head(5))  # Print first 5 rows for debugging
        
        # Ensure 'HE' column exists and print unique values
        if 'HE' not in df.columns:
            print(f"'HE' column not found in data for sheet {ws}. Columns are: {df.columns}")
            return pd.DataFrame()  # Return empty DataFrame on error

        print(f"First set of Unique values in HE column before -1 adjustment for sheet {ws}: {df['HE'].unique()}")
        print(f"Data before -1 adjustment January 1, {g_start_year}:\n{df.loc[df['Date'] == first_day_date]}")
        ################################
        # Handle possible NaN values in 'HE' column
        logging.info("Working through HE Adustments")
        df['HE'] = pd.to_numeric(df['HE'], errors='coerce')
        print(df.head(5))  # Print first 5 rows for debugging
        
        # Identify rows with NaN values in 'HE' column
        nan_rows = df[df['HE'].isna()]
        if not nan_rows.empty:
            print(f"Rows with NaN values in HE column:\n{nan_rows}")

        # Fill NaN values with 0 (or choose another value or drop them)
        df['HE'].fillna(0, inplace=True)
        print(df.head(5))  # Print first 5 rows for debugging

        # Identify rows with floating-point values in 'HE' column
        floating_point_rows = df[df['HE'] % 1 != 0]
        if not floating_point_rows.empty:
            print(f"Rows with floating-point values in HE column:\n{floating_point_rows}")
        
        ##################################
        # Adjust HE column to 0-23 hour range as they are currently in 1-24
        try:
            df['HE'] = df['HE'].astype(int) - 1
            print(f"Second set of Unique values in HE column after adjustment for sheet {ws}: {df['HE'].unique()}")
            # Print data for January 1, first year
            print(f"Data AFTER -1 adjustment and BEFORE DST March adjustments on January 1, {g_start_year}:\n{df.loc[df['Date'] == first_day_date]}")
        except Exception as e:
            print(f"Error adjusting HE column for sheet {ws}: {e}")
            return pd.DataFrame()  # Return empty DataFrame on error

        # Check if there's any missing row for January 1, first year
        missing_hours = set(range(24)) - set(df.loc[df['Date'] == first_day_date, 'HE'])
        if missing_hours:
            print(f"Missing hours in HE for January 1, {g_start_year}:: {missing_hours}")
        
        # Handle DST changes
        try:
            logging.info(f"Working through DST changes for sheet {year_str}")
            dst_start_date, dst_end_date = get_dst_dates(int(year_str))
            print(f"DST start date: {dst_start_date}, DST end date: {dst_end_date}")

            # Handle DST start (March - Missing hour)
            if dst_start_date in df['Date'].values:
                print(f"Handling DST start for date: {dst_start_date}")

                # Print the initial data for the DST start date
                print(f"Initial data on DST start date:\n{df.loc[df['Date'] == dst_start_date]}")

                # Ensure we are checking the correct condition for missing hour
                if (df.loc[df['Date'] == dst_start_date, 'HE'] == 1).sum() == 0:
                    print(f"No hour 1 found for DST start date {dst_start_date}, duplicating hour 0 data")
                    # Duplicate the previous hour's data to create a mock hour 1
                    mock_hour = df.loc[(df['Date'] == dst_start_date) & (df['HE'] == 0)].copy()
                    print(f"Mock hour data before adjustment:\n{mock_hour}")

                    # Change the HE from 0 to 1 to reflect it as a missing hour
                    mock_hour['HE'] = 1
                    df = pd.concat([df, mock_hour])
                    print(f"Data after adding mock hour before combining:\n{df.loc[df['Date'] == dst_start_date]}")

                else:
                    print(f"Hour 1 exists for DST start date {dst_start_date}, no need to duplicate hour 0 data")

                # Print DataFrame after handling DST start
                print(f"After handling DST start, data:\n{df.loc[df['Date'] == dst_start_date]}")

            # Print HE values after DST start handling
            print(f"Third set of Unique values in HE column after missing hour DST adjustment {ws}: {df['HE'].unique()}")

        except Exception as e:
            print(f"Error handling DST changes for sheet {ws}: {e}")
            return pd.DataFrame()  # Return empty DataFrame on error

        # Print data for January 1, 2024
        print(f"Data AFTER March Adjustments but BEFORE Nov Adjustment on January 1, {g_start_year}::\n{df.loc[df['Date'] == first_day_date]}")
        
        
        try:   
            # Handle DST end (November - Extra hour)
            if dst_end_date in df['Date'].values:
                print(f"Handling DST end for date: {dst_end_date}")

                # Remove the duplicate hour 1
                extra_hour_mask = (df['Date'] == dst_end_date) & (df['HE'] == 1)
                df = df[~extra_hour_mask]
                print(f"Data after removing duplicate hour 1:\n{df.loc[df['Date'] == dst_end_date]}")

                # Adjust the remaining hours
                condition_mask = (df['Date'] == dst_end_date) & (df['HE'] > 0)
                print(f"Condition mask for hours > 0:\n{df.loc[condition_mask]}")

                df.loc[condition_mask, 'HE'] -= 1
                print(f"Data after adjusting hours:\n{df.loc[df['Date'] == dst_end_date]}")

            # Print HE values after DST end handling
            print(f"Fourth set of Unique values in HE column after DST extra hour adjustment {ws}: {df['HE'].unique()}")

        
        except Exception as e:
            print(f"Error handling DST changes for sheet {ws}: {e}")
            return pd.DataFrame()  # Return empty DataFrame on error

        # Print data for January 1, first year
        print(f"Data AFTER all DST adjustmenta on January 1, {g_start_year}::\n{df.loc[df['Date'] == first_day_date]}")
    
        # Combine date and hour into a single DateTime column and sort at the end
        df = combine_date_and_hour(df)
        df = df.sort_values(by=['DateTime'])
        print(f"Data after combining date and hour and sorting:\n{df.head()}")
        
        return df


    except Exception as e:
        print(f"Error processing Excel worksheet for year {ws}: {e}")
        return pd.DataFrame() # Return empty DataFrames on error
    
##############################   

def process_data():
    '''
    This function processes the raw data files and saves the consolidated data to a CSV file.
    '''
    print("process_data called")
    # Set up the logger
    #logging.basicConfig(level=logging.INFO)
    print(json.dumps(gbl.gbl_tracked_dict_json_file_data, indent=4))

    #########################################
    # Set-up Directories and Input Files
    #########################################
    #print("Loading Excel File")

    #########################################
    # Step A: Load the electricity price forecasts in the Excel workbook(s) and process each year and append the results
    # into a consolidated data frame
    #########################################

    # Loop through output file structure
    for key, value in tqdm(gbl.gbl_tracked_loaded_dict_json_file_data["Input_Data"]['Price_Forecast'].items()):
        print(f" key {key}" )
        
        input_file_attributes = value["Input_File_Attributes"]

        start_year = input_file_attributes['start_year']
        end_year = input_file_attributes['end_year']
        frcst_input_excel_file_path = input_file_attributes['frcst_input_excel_file_path']
        print("Excel workbook meta data retrieved.")

    # Loop through output file attributes
    for key, value in tqdm(gbl.gbl_tracked_loaded_dict_json_file_data["Output_Data"]['Processed_Price_Forecast'].items()):
        print(f"Processing data for {key}")

        output_file_attributes = value["Output_File_Attributes"]
        ###########################
        # Step A1:
        # Prepare output folders. 
        ###########################

        # Remove existing forecaster output folder if it exists
        # This removes ALL the forecaster folders in the csv folder
        csv_output_path = gbl.gbl_output_general_data['csv_output_path']

        print(f" csv_output_path: {csv_output_path}")
        existing_output_folder = output_file_attributes['forecaster_name']
        existing_folder_path = os.path.join(csv_output_path, existing_output_folder)
        delete_folder(existing_folder_path)
        print(f" Existing forecaster ({existing_output_folder}) data folder deleted.")

        # Recreate the forecaster folders
        forecaster_folder = output_file_attributes['forecaster_name']
        scenario_folder = output_file_attributes['output_sub_folder']
        # Combine the base path with the forecater folder and report folder (e.g. EDC\EDC Q4 2024 Forecast Data)
        new_forecaster_folder_path = os.path.join(csv_output_path, forecaster_folder, scenario_folder)
        create_folder(new_forecaster_folder_path)
        #print(f" New forecaster ({existing_output_folder})data folder created.")

        print("Creating Output File")
        output_file_var = gbl.gbl_output_template['consolidated_hourly_filename_str']
        
        date_ext = f'Date-{start_year}-{end_year}_'
        output_file = os.path.join(new_forecaster_folder_path, date_ext + output_file_var)
        print(f"output_file created: {output_file}")

        ###########################
        # Step A2:
        # Pull source Excel file meta data prior to search file
        ###########################
        # Loop through intput file structure
        for key, value in tqdm(gbl.gbl_tracked_loaded_dict_json_file_data["Input_Data"]['Price_Forecast'].items()):
            input_file_attributes = value["Input_File_Attributes"]
            # frcst_input_excel_file_path = input_file_attributes['frcst_input_excel_file_path']
            # filename = input_file_attributes['filename']
            # print(f" Excel workbook ({filename}) meta data retrieved.")
    
            ###########################
            # Step A3:
            # Load and Process Excel file

            date_ext = f'Date-{start_year}-{end_year}_'

            # Load the Excel workbook once
            # Create an event to signal when the workbook has been loaded
            # Create a queue to receive the workbook object
            
            # Define workbook path, filename, and worksheet name
            frcst_input_excel_file_path = input_file_attributes['frcst_input_excel_file_path']
            filename = input_file_attributes['filename']
            ws = None
            
            print(f" Excel workbook ({filename}).")
            wb, ws = process_excel_data(frcst_input_excel_file_path, ws)
            
            print("Workbook loaded successfully!")

            #List of years to process
            years = list(range(start_year, end_year + 1))

            # Initialize an empty DataFrame to hold the results for all years in the forecast
            df_all = pd.DataFrame()

            # This needs to accomodate all forecast files
            #Loop through each worksheet in the Excel file with releveant data
            
            if input_file_attributes['file_structure'] == 'multiple_worksheets_YYYY':
                # Assumes sheets are named as 4 digit years e.g. 2010, 2011, 2012

                # Loop through sheet name that are in YYYY
                for year in tqdm(years, desc=f" Processing {years}"):
                    try:
                        # Define sheet name to process
                        year_str = str(year)
                        # This needs to accomodate all file formats
                        df_year = process_sheet(wb, ws, start_year, end_year, year_str, input_file_attributes) # took out 'wb'
                        print(f" df_year: {df_year}")

                        if df_year.empty:
                            print(f"Empty DataFrame for year {year_str}, skipping.")
                        else:
                            print(f"empty df check: {not df_year.empty}")
                            # Concatenate each year into the df_all data frame
                            df_all = pd.concat([df_all, df_year], ignore_index=True)
                            #int(f"Current df_all shape: {df_all.shape}")
                            print(f"Current df_all shape: {df_all.shape}")
                            print(f"Current df_all head:\n{df_all.head(36)}")
                    except Exception as e:
                        print(f"Error processing Excel worksheet for year {year_str}: {e}")
            else:
                # Process the single worksheet named 'Hourly'
                try:
                    ws = 'Hourly'
                    #########################################
                    #new code
                    #Load Excel data into hourly data frame
                    df_hourly = pd.read_excel(frcst_input_excel_file_path, sheet_name=ws)
                    for year in tqdm(years, desc=f" Processing {years}"):
                        print(f"Processing {year}")
                        # Filter the data for the specific year
                        df_year = df_hourly[pd.to_datetime(df_hourly['date']).dt.year == year]

                        if df_year.empty:
                            print(f"Empty DataFrame for year {year}, skipping.")
                        else:
                            print(f"empty df check: {not df_year.empty}")
                            # Process the filtered data
                            df_year_processed = process_sheet(df_year, start_year, end_year, year, input_file_attributes)
                            print(f" df_year_processed: year {year}, data {df_year_processed}")
                            
                            # Concatenate into the df_all data frame
                            df_all = pd.concat([df_all, df_year_processed], ignore_index=True)
                            print(f"Current df_all shape: {df_all.shape}")
                            print(f"Current df_all head:\n{df_all.head(36)}")
                except Exception as e:
                    print(f"Error processing Excel worksheet 'Hourly': {e}")
                                     
                    #########################################
                    #Note their is only 1x worksheet an it is called 'Hourly'
                    #so the 'year' variable does not act like it does when the other
                    #data sets with worksheets named in YYYY.  Here we are simply passing
                    #it a value to complete the function call.
                    # year = start_year
                    # df_hourly = process_sheet(ws, start_year, end_year, year, input_file_attributes) # took out 'wb'
                    
                    # if df_hourly.empty:
                    #     print("Empty DataFrame for 'Hourly' sheet, skipping.")
                    # else:
                    #     print(f"empty df check: {not df_hourly.empty}")
                    #     # Concatenate into the df_all data frame
                    #     df_all = pd.concat([df_all, df_hourly], ignore_index=True)
                    #     print(f"Current df_all shape: {df_all.shape}")
                    #     print(f"Current df_all head:\n{df_all.head(36)}")
                # except Exception as e:
                #     print(f"Error processing Excel worksheet 'Hourly': {e}")
                
            print(f"Final df_all.head(): {df_all.head()}")
            #########################################
            # Step B: Save the combined DataFrame to a CSV file, update dictionary, and save updated dictionary to .json
            #########################################
            # Save data to csv
            # if not df_all.empty:
            #     try:
            #         # After processing all years, remove rows with -1 in the HE column
            #         df_all = df_all[df_all['HE'] != -1]
            #         # Save data frame to csv
            #         df_all.to_csv(output_file, index=False)
            #         print("Data consolidated and saved to output file.")
            #         # Update dictionary with new meta data
            #         output_file_attributes['consolidated_hourly'] = output_file
            #         # Save udpated dictionary to existing .json file
            #         gbl.gbl_tracked_loaded_dict_json_file_data.save_to_json(gbl.gbl_json_file_path_loaded)
            #     except PermissionError:
            #         print(f"Permission denied: Unable to write to the file {output_file}. Please close any application that might be using the file or check your write permissions.")
            #     except Exception as e:
            #         print(f"An error occurred while saving the file: {e}")
            # else:
            #     print("No data to save.")
            if not df_all.empty:
                try:
                    # After processing all years, remove rows with -1 in the HE column
                    df_all = df_all[df_all['HE'] != -1]
                    # Save data frame to csv
                    df_all.to_csv(output_file, index=False)
                    print("Data consolidated and saved to output file.")
                    # Update dictionary with new meta data
                    output_file_attributes['consolidated_hourly'] = output_file
                    # Save updated dictionary to existing .json file
                    gbl.gbl_tracked_loaded_dict_json_file_data.save_to_json(gbl.gbl_json_file_path_loaded)
                except PermissionError:
                    print(f"Permission denied: Unable to write to the file {output_file}. Please close any application that might be using the file or check your write permissions.")
                except Exception as e:
                    print(f"An error occurred while saving the file: {e}")
            else:
                print("No data to save.")

        # Pretty-print the JSON data
        print(json.dumps(gbl.gbl_tracked_loaded_dict_json_file_data, indent=4))

    return 