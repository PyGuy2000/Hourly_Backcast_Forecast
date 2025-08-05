# forcast_scenario_loader.py
import yaml
from library.class_objects.output_files.output_file import OutputFile
"""
This loads all the forecast scenarios from the forcast_scenarios.yaml file

"""
def load_output_files(yaml_path: str) -> list[OutputFile]:
    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)
    return [OutputFile(**entry) for entry in data]