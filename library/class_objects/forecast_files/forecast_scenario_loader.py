# forcast_scenario_loader.py
import yaml
from library.class_objects.forecast_files.forecast_scenario import ForecastScenario
"""
This loads all the forecast scenarios from the forcast_scenarios.yaml file

"""
def load_forecast_scenarios(yaml_path: str) -> list[ForecastScenario]:
    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)
    return [ForecastScenario(**entry) for entry in data]
