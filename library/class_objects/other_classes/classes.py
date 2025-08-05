from library import globals as gbl

#Create the TrackedDict Class
import json
import os

class TrackedDict(dict):
    '''
    TrackedDict Class: This class inherits from dict and overrides the __setitem__ method. 
    Whenever an item is set, it records the change in the changes dictionary. 
    The get_changes method returns the recorded changes.
    '''
    def __init__(self, *args, **kwargs):
        #super().__init__(*args, **kwargs)
        super(TrackedDict, self).__init__(*args, **kwargs) #replaced for logging purposes
        self.changes = {}

    # def __setitem__(self, key, value):
    #     if key not in self:
    #         #self[key] = {}
    #         super().__setitem__(key,{})
    #     if key not in self.changes:
    #         self.changes[key] = {}
    #     print(f"Updating changes[{key}] = {value}")  # Debug print
    #     self.changes[key][value[0]] = value[1]
    #     super().__getitem__(key)[value[0]] = value[1]
    
    # Had to revise as the function as written as part of the code attempts
    # to pass single integer values to the dictionay.  Integers in Python 
    # are not subscriptable, which means you cannot access their elements 
    # using square brackets like value[0].  In this updated method, we check 
    # if the value is a list or tuple of length 2 before attempting to subscript it. 
    # If it is, we proceed with the original logic. Otherwise, we treat it as a 
    # simple value and store it directly.
    def __setitem__(self, key, value):
        if key not in self:
            super().__setitem__(key, {})
        if key not in self.changes:
            self.changes[key] = {}
        #print(f"Updating changes[{key}] = {value}")  # Debug print
        
        if isinstance(value, (list, tuple)) and len(value) == 2:
            self.changes[key][value[0]] = value[1]
            super().__getitem__(key)[value[0]] = value[1]
        else:
            self.changes[key] = value
            super().__setitem__(key, value)

    def get_changes(self):
        return self.changes

    def save_to_json(self, file_path):
        with open(file_path, 'w') as json_file:
            print(f"Saving to JSON file: {file_path}")
            #json.dump(self, json_file, indent=4)
            json.dump(dict(self), json_file, indent=4) #Convert TrackedDict to a regular dict before saving.
            print(f"Dictionary saved to {file_path}")


    ###############################
    # This is not active yet.
    ###############################
    ############################################################
    # New Method: 
    # Create Folder with Error Handling
    def create_folder(self, folder_path, metadata_key=None, metadata_value=None):
        try:
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                if metadata_key and metadata_value:
                    self[metadata_key] = metadata_value
                print(f"Folder created: {folder_path}")
            else:
                print(f"Folder already exists: {folder_path}")
        except Exception as e:
            print(f"Error creating folder '{folder_path}': {e}")

    # Delete Folder with Error Handling
    def delete_folder(self, folder_path, metadata_key=None):
        try:
            if os.path.exists(folder_path):
                os.rmdir(folder_path)  # Note: This only works if the folder is empty
                if metadata_key and metadata_key in self:
                    del self[metadata_key]
                print(f"Folder deleted: {folder_path}")
            else:
                print(f"Folder does not exist: {folder_path}")
        except Exception as e:
            print(f"Error deleting folder '{folder_path}': {e}")

    # # Example Usage
    # # Create a folder and update metadata
    # gbl.gbl_tracked_dict_json_file_data.create_folder('path/to/new_folder', metadata_key='new_folder', metadata_value='folder_metadata')

    # # Delete a folder and remove it from metadata
    # gbl.gbl_tracked_dict_json_file_data.delete_folder('path/to/new_folder', metadata_key='new_folder')

    ############################################################
    # New Method:
    # Create File with Error Handling
    def create_file(self, file_path, content='', metadata_key=None):
        try:
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    f.write(content)
                if metadata_key:
                    self[metadata_key] = file_path
                print(f"File created: {file_path}")
            else:
                print(f"File already exists: {file_path}")
        except Exception as e:
            print(f"Error creating file '{file_path}': {e}")

    # Delete File with Error Handling
    def delete_file(self, file_path, metadata_key=None):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                if metadata_key and metadata_key in self:
                    del self[metadata_key]
                print(f"File deleted: {file_path}")
            else:
                print(f"File does not exist: {file_path}")
        except Exception as e:
            print(f"Error deleting file '{file_path}': {e}")


    ############################################################
    # Method to Load Dictionary from JSON File
    @classmethod
    def load_from_json(cls, file_path):
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
        return cls(data)

    # Load dictionary from JSON file
    #gbl.gbl_tracked_dict_json_file_data = TrackedDict.load_from_json(gbl.gbl_json_file_path_full)
    ############################################################
    # Combined Method to Handle Folder/File Creation and Metadata Update
    def add_entry(self, entry_type, path, metadata_key=None, metadata_value=None, content=''):
        if entry_type == 'folder':
            self.create_folder(path, metadata_key, metadata_value)
        elif entry_type == 'file':
            self.create_file(path, content, metadata_key)
        self.save_to_json('updated_metadata.json')  # Adjust this to your target JSON file path

    # Combined Method to Handle Folder/File Deletion and Metadata Removal
    def delete_entry(self, entry_type, path, metadata_key=None):
        if entry_type == 'folder':
            self.delete_folder(path, metadata_key)
        elif entry_type == 'file':
            self.delete_file(path, metadata_key)
        self.save_to_json('updated_metadata.json')  # Adjust this to your target JSON file path

    # Create a folder and update metadata in one go
    # gbl.gbl_tracked_dict_json_file_data.add_entry('folder', 'path/to/folder', metadata_key='new_folder', metadata_value='meta_data_about_folder')

    # Create a file and update metadata in one go
    # gbl.gbl_tracked_dict_json_file_data.add_entry('file', 'path/to/file.txt', metadata_key='new_file', content='This is file content')

    ############################################################
    def create_shortcuts(self):
        shortcuts = {}
        def _traverse_dict(d, path=''):
            for k, v in d.items():
                new_path = f"{path}['{k}']" if path else f"['{k}']"
                if isinstance(v, dict):
                    _traverse_dict(v, new_path)
                else:
                    shortcuts[k] = new_path
        _traverse_dict(self)
        return shortcuts
    ############################################################
    # Method to get a nested value using a list of keys
    def get_nested(self, keys):
        try:
            value = self
            for key in keys:
                value = value[key]
            return value
        except KeyError:
            print(f"Key path {' -> '.join(keys)} not found in the dictionary.")
            return None
        except TypeError:
            print(f"Type error occurred while accessing {' -> '.join(keys)}.")
            return None

    # Method to set a nested value using a list of keys
    def set_nested(self, keys, value):
        try:
            d = self
            for key in keys[:-1]:
                if key not in d:
                    d[key] = {}
                d = d[key]
            d[keys[-1]] = value
        except Exception as e:
            print(f"Error setting value for key path {' -> '.join(keys)}: {e}")

    # Method to delete a nested key using a list of keys
    def delete_nested(self, keys):
        try:
            d = self
            for key in keys[:-1]:
                d = d[key]
            del d[keys[-1]]
        except KeyError:
            print(f"Key path {' -> '.join(keys)} not found in the dictionary.")
        except Exception as e:
            print(f"Error deleting key for key path {' -> '.join(keys)}: {e}")

    # Get a nested value
    # keys = ["Output_Data", "Processed_Price_Forecast", "file_name_p50"]
    # gbl.gbl_tracked_dict_json_file_data.set_nested(keys, "new_p50_file_name.csv")
    ############################################################
    def search_by_key(self, key_name, current_dict=None, path = ""):
        current_dict = current_dict or self
        found_items = []

        for key, value in current_dict.items():
            new_path = f"{path}['{key}']"
            if key == key_name:
                found_items.append((new_path, value))

            if isinstance(value, dict):
                found_items.extend(self.search_by_key(key_name, value, new_path))
            
        return found_items

    # Example Usage: Search all entries with specific key
    # key_name = "forecast_post_processed_folder_path"
    # found_items = gbl.gbl_tracked_dict_json_file_data.search_by_key(key_name)
    # for path, value in found_items:
    #     print(f"Path: {path}, Value: {value}")

    # Dynamic method to search for values by a specific attribute (can be customized)
    def search_by_attribute(self, attribute_key, attribute_value, current_dict=None, path=""):
        current_dict = current_dict or self
        found_items = []

        for key, value in current_dict.items():
            new_path = f"{path}['{key}']"

            if isinstance(value, dict):
                if attribute_key in value and value[attribute_key] == attribute_value:
                    found_items.append((new_path, value))
                # Recursively check nested dictionaries
                found_items.extend(self.search_by_attribute(attribute_key, attribute_value, value, new_path))

        return found_items

    # Example Usage: Search all entries with a specific attribute (i.e. where forecaster is 'EDC')
    # attribute_key = "forecaster_name"
    # attribute_value = "EDC"
    # found_items = gbl.gbl_tracked_dict_json_file_data.search_by_attribute(attribute_key, attribute_value)
    # for path, value in found_items:
    #     print(f"Path: {path}, Value: {value}")
    ############################################################
    # Custom Filter Method
    def filter_dict(self, filter_func, current_dict=None, path=""):
        """
        Recursively filters the dictionary based on a provided filter function.

        Args:
        - filter_func (callable): A function that takes a key and value and returns True if the item should be included.
        - current_dict (dict): The current dictionary level being processed.
        - path (str): The current path to track where in the dictionary the search is occurring.

        Returns:
        - list of tuples containing path and value of the items that matched the filter.
        """
        current_dict = current_dict or self
        found_items = []

        for key, value in current_dict.items():
            new_path = f"{path}['{key}']"
            if filter_func(key, value):
                found_items.append((new_path, value))

            if isinstance(value, dict):
                found_items.extend(self.filter_dict(filter_func, value, new_path))

        return found_items

    # Example Usage
    # This approach allows you to customize the filtering condition according to your needs
    # and makes it reusable without having to remimplement the loop every time.
    # Define a filter function to find dictionaries that have a certain key
    # def my_filter_function(key, value):
    #     return isinstance(value, dict) and "forecaster_name" in value

    # # Example Usage# Use the custom filter function to find all matching items
    # found_items = gbl.gbl_tracked_dict_json_file_data.filter_dict(my_filter_function)
    #     for path, value in found_items:
    #         print(f" Path: {path}, Value: {value}")
    ############################################################
    def batch_update(self, update_func):
        """
        Applies an update function to each key-value pair in the dictionary.

        Args:
        - update_func (callable): A function that takes a key and value, performs an update, and returns a new value.
        """
        for key in self.keys():
            self[key] = update_func(key, self[key])

    def batch_delete(self, delete_condition_func):
        """
        Deletes key-value pairs based on a provided delete condition function.

        Args:
        - delete_condition_func (callable): A function that takes a key and value and returns True if the item should be deleted.
        """
        keys_to_delete = [key for key, value in self.items() if delete_condition_func(key, value)]
        for key in keys_to_delete:
            del self[key]
     # Example Usage

    ############################################################
    # def update_forecaster_name(key, value):
    #     if isinstance(value, dict) and "forecaster_name" in value and value["forecaster_name"] == "EDC":
    #         value["forecaster_name"] = "EDC_updated"
    #     return value

    # Example Usage
    # Update all entries with the forecaster_name as "EDC" by appending _udpated to the forecaster_name
    # gbl.gbl_tracked_dict_json_file_data.batch_update(update_forecaster_name)

    # def delete_inactive(key, value):
    #     return isinstance(value, dict) and value.get("Data_Active", True) is False

    # Delete all entries where Data_Active is set to False
    # gbl.gbl_tracked_dict_json_file_data.batch_delete(delete_inactive)
    ############################################################

    ############################################################
    # def Calculate_LCOE(input_data_path, output_data_path, loaded_dict, loaded_power_generation_dict, output_file_var, gas_fired_peaker, df):
    # # Convert loaded_power_generation_dict to TrackedDict
    # tracked_dict = TrackedDict(loaded_power_generation_dict)

    # for key, value in loaded_power_generation_dict.items():
    #     # Define the heat rate and plant capacity
    #     heat_rate = value['heat_rate']  # GJ/MWh
    #     plant_capacity_mw_gross = value['plant_capacity_mw_gross']  # MW
    #     plant_capacity_mw_net = value['plant_capacity_mw_net']   # MW
    #     target_capacity_factor = value['target_capacity_factor']  # %
    #     target_annual_production_mwh = plant_capacity_mw_net * 8760 * target_capacity_factor  # !!!!!!!!!!!!!!!!!!!!!!!!!!!
        
    #     # Update tracked dictionary
    #     tracked_dict[key] = ('target_annual_production_mwh', target_annual_production_mwh)

    #     # Capital Costs
    #     capital_cost_per_kw = value['capital_cost_per_kw']  # $/kW
    #     capital_cost_mm_dollars = capital_cost_per_kw * plant_capacity_mw_gross / 1000  # !!!!!!!!!!!!!!!!!!!!!!!!!!!
        
    #     # Update tracked dictionary
    #     tracked_dict[key] = ('capital_cost_mm_dollars', capital_cost_mm_dollars)
    
    # # Get changes
    # changes = tracked_dict.get_changes()
    # return changes

###############################
# This is not active yet.
###############################
class ForecastFile:
    def __init__(self, gbl_input_path, gbl_csv_output_path, forecaster_name, input_sub_folder, folder_name, key, filename, file_data_structure, dst_type,\
                        gbl_frcst_input_excel_file_path, start_year, end_year, gbl_frcst_output_excel_file_path, gbl_frcst_output_csv_file_path, \
                            datetime_column, price_column, output_sub_folder, stochastic_seeds, stochastic_seeds_used, input_raw_data_path, \
                                raw_data_file_path, pwr_file_name_p50, natgas_file_name_p50, data_active, quarter_part, case_part
                                ):
        
        self.input_path = gbl_input_path
        self.csv_output_path = gbl_csv_output_path
        self.forecaster_name = forecaster_name
        self.input_sub_folder = input_sub_folder
        self.key = key
        self.filename = filename
        self.file_data_structure = file_data_structure
        self.dst_type = dst_type
        self.frcst_input_excel_file_path = gbl_frcst_input_excel_file_path
        self.frcst_output_excel_file_path = gbl_frcst_output_excel_file_path
        self.frcst_output_csv_file_path =  gbl_frcst_output_csv_file_path
        self.datetime_column = datetime_column
        self.price_column = price_column
        self.start_year = start_year
        self.end_year = end_year
        self.stochastic_seeds = stochastic_seeds
        self.stochastic_seeds_used = stochastic_seeds_used
        self.input_raw_data_path = input_raw_data_path
        self.raw_data_file_path = raw_data_file_path
        self.pwr_file_name_p50 = pwr_file_name_p50,
        self.natgas_file_name_p50 = natgas_file_name_p50,
        self.data_active = data_active,
        self.quarter_part = quarter_part,
        self.case_part = case_part

        # Setting dynamic attributes
        self.quarter_part = key.split('_')[0][1:]  # Extract the quarter part
        self.year_part = key.split('_')[1]

        # Creating paths
        self.input_sub_folder = folder_name
        self.output_sub_folder = folder_name
        self.input_raw_data_path = os.path.join(gbl_input_path, folder_name, filename)
        self.frcst_input_excel_file_path = os.path.join(gbl_input_path, forecaster_name, folder_name, filename)
        self.frcst_output_csv_file_path = os.path.join(gbl_csv_output_path, forecaster_name, folder_name)

    def get_metadata(self, gbl_input_path, gbl_csv_output_path, forecaster_name, input_sub_folder, folder_name, key, filename, file_data_structure, dst_type,\
                        gbl_frcst_input_excel_file_path, start_year, end_year, gbl_frcst_output_excel_file_path, gbl_frcst_output_csv_file_path, \
                            datetime_column, price_column, output_sub_folder, stochastic_seeds, stochastic_seeds_used, input_raw_data_path, \
                                raw_data_file_path, pwr_file_name_p50, natgas_file_name_p50, data_active, quarter_part, case_part):
        
        return {
            "Input_File_Attributes": {
                'forecaster_name' : forecaster_name,
                'input_sub_folder' : input_sub_folder,
                'filename': filename,
                'file_structure' : file_data_structure,
                'dst_type' : dst_type,
                'frcst_input_excel_file_path' : gbl_frcst_input_excel_file_path,
                'frcst_output_excel_file_path' : gbl_frcst_output_excel_file_path,
                'frcst_output_csv_file_path' : gbl_frcst_output_csv_file_path,
                'datetime_column': datetime_column,
                'price_column': price_column,
                'start_year': start_year,
                'end_year': end_year,
                'stochastic_seeds': stochastic_seeds,
                'stochastic_seeds_used': stochastic_seeds_used,
                'input_raw_data_path' : input_raw_data_path,
                'base_path_processed_data': raw_data_file_path,
                'pwr_file_name_p50': f"Date-{start_year}-{end_year}_p50_hourly_spot_electricity.csv",
                'natgas_file_name_p50': f"Date-{start_year}-{end_year}_p50_hourly_spot_natural_gas.csv",
                'Data_Active': data_active
            },
            "Output_File_Attributes": {
                'forecaster_name' : forecaster_name,
                'output_sub_folder': output_sub_folder,
                'filename' : None,
                'frcst_output_excel_file_path' : gbl_frcst_output_excel_file_path, 
                'frcst_output_csv_file_path' : gbl_frcst_output_csv_file_path,
                'start_year': start_year,
                'end_year': end_year,
                'stochastic_seeds': stochastic_seeds,
                'stochastic_seeds_used': stochastic_seeds_used,
                'pwr_file_name_p50': f"Date-{start_year}-{end_year}_p50_hourly_spot_electricity.csv",
                'natgas_file_name_p50': f"Date-{start_year}-{end_year}_p50_hourly_spot_natural_gas.csv",
                'Data_Active': data_active
            }
    }

# Updated create_forecast_metadata function
def create_forecast_metadata2(
            forecaster_name_dict,
            sto_seed_dict,
            dst_type_dict,
            forecaster_data_structure_dict,
            input_filename_dict, 
            forecast_years_dict, 
            forecast_folder_dict,
            forecast_data_flag_dict,
            output_file_dict,
            output_file_attributes_dict,
        ):

    input_data_dict = {}
    output_data_dict = {}

    for key, filename in input_filename_dict.items():
        forecaster_acronym = key.split('_')[2]  # This extracts 'EDC'
        forecaster_name = forecaster_name_dict.get(forecaster_acronym)

        if forecaster_name:
            start_year, end_year = forecast_years_dict[f"{key}_years"]
            folder_name = forecast_folder_dict[f"{key}_folder_name"]
            data_active = forecast_data_flag_dict[f"{key}_flag"]
            
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
            start_year, end_year = forecast_years_dict[f"{key}_years"]

            # Folder name
            folder_name = forecast_folder_dict[f"{key}_folder_name"]
            print(f" folder_name: {folder_name}")
            
            # Raw data file path
            quarter_part = key.split('_')[0][1:]  # Extract the quarter part
            
            case_part = key.split('_')[3][0:]  # Extract the 'basecase'
            
            raw_data_file_path = f"{forecaster_name.lower()}q{quarter_part}_{year_part}_base_path_processed_data"
            #print(f" raw_data_file_path: {raw_data_file_path}")
            
            file_data_structure = forecaster_data_structure_dict[f'{forecaster_name}_data_structure']
            
            dst_type = dst_type_dict[f'{forecaster_name}_dst_type']
            
            price_column = 'price' 
            
            datetime_column = 'begin_datetime_mpt',
            
            input_sub_folder = folder_name 
            output_sub_folder = folder_name
            filename = input_filename_dict[key]
            
            print(input_sub_folder)
            print(output_sub_folder)
            print(filename)
            
            input_raw_data_path = os.path.join(gbl.gbl_input_path, input_sub_folder, filename)
            pwr_file_name_p50 = f"Date-{start_year}-{end_year}_p50_hourly_spot_electricity.csv"
            natgas_file_name_p50 = f"Date-{start_year}-{end_year}_p50_hourly_spot_natural_gas.csv"
            
             # Create input folder that has existing data
            gbl.gbl_frcst_input_excel_file_path = os.path.join(gbl.gbl_input_path, forecaster_name, filename)
            # Create input folder that has existing data
            gbl.gbl_frcst_output_excel_file_path = os.path.join(gbl.gbl_input_path, forecaster_name, filename)
            # Create output folder that does not yet have any data
            gbl.gbl_frcst_output_csv_file_path = os.path.join(gbl.gbl_csv_output_path, forecaster_name, output_sub_folder)

            # Create ForecastFile object
            forecast_file = ForecastFile(
                gbl.gbl_input_path, gbl.gbl_csv_output_path, forecaster_name, input_sub_folder, folder_name, key, filename, file_data_structure, dst_type,\
                        gbl.gbl_frcst_input_excel_file_path, start_year, end_year, gbl.gbl_frcst_output_excel_file_path, gbl.gbl_frcst_output_csv_file_path, \
                            datetime_column, price_column, output_sub_folder, stochastic_seeds, stochastic_seeds_used, input_raw_data_path, \
                                raw_data_file_path, pwr_file_name_p50, natgas_file_name_p50, data_active, quarter_part, case_part
            )

            # Add metadata to the dictionaries
            metadata = forecast_file.get_metadata(
                gbl.gbl_input_path, gbl.gbl_csv_output_path, forecaster_name, input_sub_folder, folder_name, key, filename, file_data_structure, dst_type,\
                        gbl.gbl_frcst_input_excel_file_path, start_year, end_year, gbl.gbl_frcst_output_excel_file_path, gbl.gbl_frcst_output_csv_file_path, \
                            datetime_column, price_column, output_sub_folder, stochastic_seeds, stochastic_seeds_used, input_raw_data_path, \
                                raw_data_file_path, pwr_file_name_p50, natgas_file_name_p50, data_active, quarter_part, case_part
                )
            
            input_data_dict[f"{forecaster_name} Q{forecast_file.quarter_part} {forecast_file.year_part} {forecast_file.case_part}"] = metadata["Input_File_Attributes"]
            output_data_dict[f"{forecaster_name} Q{forecast_file.quarter_part} {forecast_file.year_part} {forecast_file.case_part}"] = metadata["Output_File_Attributes"]
            

    # Create the final dictionary structure
    final_dict = {
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


    output_data_dict[f"{forecaster_name} Q{quarter_part} {year_part} {case_part}"]["Output_File_Attributes"].update(output_file_attributes_dict)

    return final_dict, input_data_dict, output_data_dict

class PowergenProduction: 
    def __init__(self, name, plant_capacity_mw_net, heat_rate, vom_costs, start_up_cost, emissions_intensity, baseline, startcost_amort_hours): 
        self.name = name 
        self.plant_capacity_mw_net = plant_capacity_mw_net 
        self.heat_rate = heat_rate 
        self.vom_costs = vom_costs 
        self.start_up_cost = start_up_cost 
        self.emissions_intensity = emissions_intensity 
        self.baseline = baseline 
        self.startcost_amort_hours = startcost_amort_hours 
        
        def calculate_threshold_price(self, natural_gas_price, carbon_cost, monthly_index_rate, year, month, start_year): 
            adj_vom = self.vom_costs * (1 + monthly_index_rate) ** ((year - start_year) * 12 + month) 
            return self.heat_rate * natural_gas_price + carbon_cost + (self.start_up_cost / self.plant_capacity_mw_net / self.startcost_amort_hours) + adj_vom 
            
        def is_running(self, electricity_price, threshold_price, cf_limit_reached): 
            if cf_limit_reached: 
                return False 
                return electricity_price >= threshold_price 
                
class MarketPrice: 
    def __init__(self, df, carbon_dict): 
        self.df = df 
        self.carbon_dict = carbon_dict 
    
    def get_hourly_data(self, year, month, seed): 
        month_data = self.df[(self.df.index.year == year) & (self.df.index.month == month)] 
        power_prices = month_data[f'Seed {seed}_Power'] 
        gas_prices = month_data[f'Seed {seed}_Gas'] 
        return power_prices, gas_prices 
        
    def get_carbon_cost(self, year, emissions_intensity, baseline): 
        return self.carbon_dict[str(year)] * (emissions_intensity - baseline) 

'''
# Example Refactored Loop 
for current_generator in generator_list:
    print(f"Conducting Back-Casting Analysis for {current_generator}") 
    # Initialize PowergenProduction object 
    powergen = PowergenProduction( 
        name=current_generator, 
        plant_capacity_mw_net=float(tracked_dict['generation_sources'][current_generator]['plant_capacity_mw_net']), 
        heat_rate=float(tracked_dict['generation_sources'][current_generator]['heat_rate']), 
        vom_costs=float(tracked_dict['generation_sources'][current_generator]['vom_mwh']), 
        start_up_cost=2000, # This is calculated in the hourly loop 
        emissions_intensity=float(tracked_dict['generation_sources'][current_generator]['emissions_intensity']), 
        baseline=float(tracked_dict['generation_sources'][current_generator]['co2_reduction_target']), 
        startcost_amort_hours=10 
        ) 
    
    # Initialize MarketPrice object 
    market = MarketPrice(df=df, carbon_dict=gcarbon_dict) 
    # Loop through stochastic seeds 
    for seed in tqdm(range(1, stochastic_seeds_used)): 
        seed_monthly_bids = [] 
        seed_monthly_capacity_factors = [] 
        seed_monthly_capture_prices = [] 
        seed_monthly_natgas_capture_prices = [] 
        # Loop through years 
            for year in tqdm(range(start_year, end_year + 1)): 
                year_data = df[df.index.year == year] 
                days_in_month = 0 
                
                # Loop through each month in the year 
                for month in range(1, 13): 
                    days_in_month = calendar.monthrange(year, month)[1] 
                    power_prices, gas_prices = market.get_hourly_data(year, month, seed) 
                    carbon_cost = market.get_carbon_cost(year, powergen.emissions_intensity, powergen.baseline) 
                    total_possible_capacity = powergen.plant_capacity_mw_net * days_in_month * 24 
                    monthly_running_status = [] 
                    threshold_price_list = [] 
                    current_month_cum_energy = 0 
                    cf_limit_reached = False 
                    
                    # Loop through hours in the month 
                    for i in range(len(power_prices)): 
                        if current_month_cum_energy / total_possible_capacity > gcf_limit: 
                            cf_limit_reached = True 
                        threshold_price = powergen.calculate_threshold_price( gas_prices.iloc[i], 
                            carbon_cost, gannual_index_rate, year, month, start_year ) 
                        running_status = powergen.is_running(power_prices.iloc[i], \
                                threshold_price, cf_limit_reached) 
                        
                        monthly_running_status.append(running_status) 
                        threshold_price_list.append(threshold_price) 
                        
                        if running_status: 
                            current_month_cum_energy += powergen.plant_capacity_mw_net 
                        
                        # Store monthly metrics 
                        avg_generator_bid_monthly = np.mean(threshold_price_list) 
                        total_capacity_run = np.sum(monthly_running_status) * powergen.plant_capacity_mw_net 
                        capacity_factor_monthly = total_capacity_run / total_possible_capacity 
                        
                        seed_monthly_bids.append(avg_generator_bid_monthly) 
                        seed_monthly_capacity_factors.append(capacity_factor_monthly) 
                        
                        # Capture prices calculation can be added here... 
        
            # Aggregate and store annual data for each seed 
            # # Use dataframes to store the metrics per seed and year 
            summary_generator_bid_df = pd.DataFrame({ 
                f'Seed_{seed}': seed_monthly_bids 
            }, index=pd.date_range(start=f'{start_year}-01', end=f'{end_year}-12', freq='M').strftime('%Y-%m')) 
                summary_generator_bid_df.index.name = 'Month' 
                
            summary_cf_df = pd.DataFrame({
                 f'Seed_{seed}': seed_monthly_capacity_factors
                }, 
                 index=pd.date_range(start=f'{start_year}-01', end=f'{end_year}-12', freq='M').strftime('%Y-%m')) 
                 summary_cf_df.index.name = 'Month' 
                
                # Capture prices and other metrics can be aggregated similarly... 
                
                # Save annual summary data for each seed 
                output_path = os.path.join(output_data_path, f'{current_generator}_Seed_{seed}_Annual_Summary.csv') 
                summary_generator_bid_df.to_csv(output_path) 
                output_path = os.path.join(output_data_path, f'{current_generator}_Seed_{seed}_CF_Annual_Summary.csv') 
                summary_cf_df.to_csv(output_path) 
    print("All scenarios and assets have been processed successfully!")
'''
     
