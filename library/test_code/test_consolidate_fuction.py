import os
import glob
import re
import pandas as pd
from tqdm import tqdm

def consolidate_annual_files(input_folder_template, input_path, output_path, datetime_column, file_dict):

    def remove_duplicate_columns(df):
        df = df.loc[:, ~df.columns.duplicated()]
        return df

    # Create dictionaries to store lists of DataFrames for each file type
    data_frames_dict = {key: [] for key in file_dict.keys()}
    
    # List all matching folders
    folders = glob.glob(os.path.join(input_path, input_folder_template))
    print(f"Found folders: {folders}")

    years = []

    for folder in tqdm(folders):
        folder_name = os.path.basename(folder)
        year_matches = re.findall(r'(\d{4})', folder_name)
        
        if year_matches:
            if len(year_matches) == 1:
                years.append(int(year_matches[0]))
            else:
                years.extend([int(year) for year in year_matches])
            
            for key, filename in tqdm(file_dict.items()):
                file_path = os.path.join(folder, filename)
                if os.path.exists(file_path):
                    df = pd.read_csv(file_path)
                    df[datetime_column] = pd.to_datetime(df[datetime_column])
                    df = remove_duplicate_columns(df)  # Remove duplicates before appending
                    data_frames_dict[key].append(df)
                else:
                    print(f"File {file_path} does not exist.")
    
    # Ensure there are years extracted
    if not years:
        raise ValueError("No valid years were found in the folder names.")

    # Get the latest year for column alignment
    latest_year = max(years)
    latest_year_folder = f'Metered_Volume_{latest_year}'
    
    # Concatenate all DataFrames for each file type and align columns
    for key in tqdm(data_frames_dict.keys()):
        if data_frames_dict[key]:
            # Concatenate all dataframes
            merged_df = pd.concat(data_frames_dict[key], ignore_index=True)
            
            # Read the latest year's file to get the updated column order
            latest_file_path = os.path.join(input_path, latest_year_folder, file_dict[key])
            if os.path.exists(latest_file_path):
                latest_df = pd.read_csv(latest_file_path)
                merged_df = merged_df.reindex(columns=latest_df.columns)
            
            # Remove duplicate columns before setting the index
            merged_df = remove_duplicate_columns(merged_df)

            # Ensure the datetime column is unique
            if datetime_column in merged_df.columns:
                merged_df = remove_duplicate_columns(merged_df)
            
            # Set the datetime column as the index if it exists and is unique
            if datetime_column in merged_df.columns:
                merged_df.set_index(datetime_column, inplace=True, drop=False)
            
            start_year = min(years)
            end_year = max(years)

            output_filename = f"{key}_{start_year}_to_{end_year}.csv"
            output_file_path = os.path.join(output_path, output_filename)
            merged_df.to_csv(output_file_path)
            print(f"Consolidated data for {key} saved to {output_file_path}")
        else:
            print(f"No data found for {key} to consolidate.")


###################################################
# Example usage
input_path = r'C:\Users\kaczanor\OneDrive - Enbridge Inc\Desktop\Metered Volume Data'
output_path = r'C:\Users\kaczanor\OneDrive - Enbridge Inc\Desktop\Metered Volume Data\Consolidated Data'
datetime_column = 'begin_date_mpt'
input_folder_template = 'Metered_Volume_*'

file_dict = {
    'Consolidated Generation Metered Volumes': 'Consolidated Generation Metered Volumes.csv',
    'DISCO': 'DISCO.csv', 
    'EXPORTER': 'EXPORTER.csv', 
    'FWD BUY': 'FWD BUY.csv', 
    'FWD SELL': 'FWD SELL.csv', 
    'GENCO': 'GENCO.csv', 
    'GRIDCO': 'GRIDCO.csv', 
    'IMPORTER': 'IMPORTER.csv', 
    'IPP': 'IPP.csv', 
    'LOAD': 'LOAD.csv', 
    'RETAILER': 'RETAILER.csv',
    'SPP': 'SPP.csv'
}

consolidate_annual_files(input_folder_template, input_path, output_path, datetime_column, file_dict)
print("Consolidation complete.")
