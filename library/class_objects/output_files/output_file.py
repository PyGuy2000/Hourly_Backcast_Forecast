
from dataclasses import dataclass
from typing import Tuple
import os
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

@dataclass
class OutputFile:
    consolidated_hourly: str
    hourly_electricity:str
    hourly_natural_gas: str
    hourly_market_heat_rate: str 
    monthly_avg_electricity: str
    monthly_avg_natural_gas: str
    monthly_market_heat_rate: str
    annual_avg_electricity: str
    annual_avg_natural_gas: str
    annual_market_heat_rate: str
    annual_allhour_electricity_heatmap: str
    annual_offpeak_electricity_heatmap:str
    annual_onpeak_electricity_heatmap: str
    annual_heatmap_data_market_electricity: str 
    annual_heatmap_data_market_naturalgas: str
    annual_market_heat_rate_std_avg_heatmap_data:str 
    annual_generator_bid_output_file_var: str
    annual_cf_output_file_var: str
    annual_power_recievedratio_output_file_var:str 
    annual_natgas_recievedratio_output_file_var: str
    monthly_generator_bid_output_file_var: str
    monthly_cf_output_file_var: str
    monthly_power_recievedratio_output_file_var:str 
    monthly_natgas_recievedratio_output_file_var:str 
    P10_hourly_spot_electricity:str
    P25_hourly_spot_electricity:str 
    P50_hourly_spot_electricity:str 
    P75_hourly_spot_electricity:str 
    P90_hourly_spot_electricity:str 
    top_hour_percentage_summary:str 
    P10_hourly_spot_natural_gas:str 
    P25_hourly_spot_natural_gas:str 
    P50_hourly_spot_natural_gas:str 
    P75_hourly_spot_natural_gas:str 
    P90_hourly_spot_natural_gas:str 
    combined_forecast_:str
    combined_forecast_with_Top_Percent_Price:str 

    # def raw_data_path(self, base_path: str) -> str:
    #     return os.path.join(base_path, self.forecaster, self.folder_name)

    def create_file(self, name: str) -> str:
        return create_file_from_string((f" {name} +_filename_str", 'csv'))