

from dataclasses import dataclass
from typing import Tuple
import os

def create_path(output_data_path_str, csv_folder_name_str, gbl_p50_output_file_var, data_years, folder_name):
    # Extracting the start and end year from the tuple
    start_year, end_year = data_years
    
    # Constructing the file name
    file_name = f"Date-{start_year}-{end_year}_{gbl_p50_output_file_var}"
    
    # Constructing the full file path
    full_path = os.path.join(output_data_path_str.replace("/", "//"), csv_folder_name_str, folder_name, file_name)
    
    return full_path

@dataclass
class ForecastScenario:
    name: str
    forecaster: str
    file_name: str
    folder_name: str
    year_range: Tuple[int, int]
    is_active: bool
    data_structure: str
    dst_type: str
    stochastic_seeds: int
    stochastic_seeds_used: int


    def raw_data_path(self, base_path: str) -> str:
        return os.path.join(base_path, self.forecaster, self.folder_name)

    def processed_p50_path(self, base_output_path: str, csv_folder: str, p50_file: str) -> str:
        return create_path(base_output_path, csv_folder, p50_file, self.year_range, self.folder_name)
