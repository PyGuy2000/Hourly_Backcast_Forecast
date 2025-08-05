# Standard Library Imports
#import contextily as ctx
import library.initializer as init 
import library.globals as gbl
from library.class_objects.other_classes.classes import TrackedDict, ForecastFile

import csv
import datetime as dt
from datetime import datetime, time, timedelta
import calendar
import locale
import math
import os
import re
import traceback
import warnings
from collections import Counter
from collections import defaultdict #Monthly Loop
from pathlib import Path
from textwrap import wrap
from time import sleep

# Third-Party Imports
import geopandas as gpd
import matplotlib
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.ticker import AutoMinorLocator, FormatStrFormatter, FuncFormatter, PercentFormatter
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.lines import Line2D
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
import numpy as np
import pandas as pd
from pandas.tseries.holiday import AbstractHolidayCalendar, Holiday, USFederalHolidayCalendar
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
from scipy import signal
from scipy.interpolate import griddata, interp1d
from shapely.geometry import Point
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
from statsmodels.tsa.seasonal import seasonal_decompose
from tqdm import tqdm
from bs4 import BeautifulSoup
from IPython.display import display
import pywt
from joypy import joyplot



from library.functions import *

from library.config import (
     #Graphing
     set_custom_rcparams,
     code_begin,
     code_end,
     reset_rcparams_to_default,
     apply_custom_style_to_plotly,
     tech_type_desired_order,
     tech_type_list_plus_BTF,
     original_tech_type_desired_order,
     #Color Palette Config
     custom_color_palette,
     tech_type_colors,
     original_color_map,
     #TECH_TYPE REDUCED Config
     tech_type_font_colors,
     tech_type_custom_line_thickness,
     tech_type_markers,
     tech_type_custom_line_styles,
     tech_type_desired_order_reduced,
     #TECH_TYPE REDUCED Config
     tech_type_reduced_colors,
     tech_type_custom_line_thickness_reduced,
     tech_type_reduced_custom_line_styles,
     #FUEL_TYPE Config
     fuel_type_desired_order,
     fuel_type_colors,
     original_fuel_type_color_map,
     fuel_type_font_colors,
     fuel_type_custom_line_thickness,
     fuel_type_markers,
     fuel_type_custom_line_styles,
 )


# import input_data_prep as idp

########################################################################
# Calculate_LCOE
########################################################################
def calculate_lcoe(
        gbl_generation_sources,
        years,
        capacity_factor_range,

    ):

    # Check to see if a range was provided for capcity factors. If so, loop throught that range in the capacity_factor_range list
    # If not set cf to target capacity factor each generator and hold them all in the capacity_factor_range list

    if len(capacity_factor_range) == len(gbl.gbl_tracked_powergen_dict.keys()):
        print(f" len(capacity_factor_range): {len(capacity_factor_range)}")
        print(f" len(gbl.gbl_tracked_powergen_dict.keys()):: {len(gbl.gbl_tracked_powergen_dict.keys()):}")
        capacity_factor_range = [gbl.gbl_tracked_powergen_dict['generation_sources'][key]['target_capacity_factor'] for key in gbl.gbl_tracked_powergen_dict['generation_sources'].keys()]
        print(f"capacity_factor_range:{capacity_factor_range}")
    else:
        #pass
        print(f"capacity_factor_range:{capacity_factor_range}")
        



    gbl.gbl_hist_processed_price_data = load_csv_with_datetime_index(r'C:\Users\kaczanor\OneDrive - Enbridge Inc\Documents\Python\EDC Hourly Capacity Factor Q2 2024\inputs\AB_Historical_Prices\merged_pool_price_data_2000_to_2024.csv')
    processed_price_data_copy = gbl.gbl_hist_processed_price_data.copy()
    print(f"processed_price_data_copy.head():{processed_price_data_copy.head()}")
    print(f"processed_price_data_copy.index():{processed_price_data_copy.index}")
    print(f"processed_price_data_copy.columns:{processed_price_data_copy.columns}")

    gbl.gbl_hist_processed_nat_gas_price = load_csv_with_datetime_index(r'C:\Users\kaczanor\OneDrive - Enbridge Inc\Documents\Python\EDC Hourly Capacity Factor Q2 2024\inputs\AB_Historical_Prices\merged_nat_gas_price_data_2000_to_2024.csv')
    processed_nat_gas_price_copy = gbl.gbl_hist_processed_nat_gas_price.copy()
    print(f"processed_nat_gas_price_copy.head():{processed_nat_gas_price_copy.head()}")
    print(f"processed_nat_gas_price_copy.index:{processed_nat_gas_price_copy.index}")
    print(f"processed_nat_gas_price_copy.columns:{processed_nat_gas_price_copy.columns}")

    # Call the function again before creating another plot
    set_custom_rcparams()

    #Create title variable for graphing later
    if len(years) > 1:
        year_title = f"Analysis from {min(years)} to {max(years)}"
    else:
        year_title = f"Analysis from {years[0]}"

    #######################################################
    # Filter gbl_processed_nat_gas_price for the specified years
    processed_price_data_copy = processed_price_data_copy[processed_price_data_copy.index.year.isin(years)].copy()
    print(f" processed_price_data_copy:{processed_price_data_copy}")

    # For processed_nat_gas_price, first reset the index and then filter

    processed_nat_gas_price_copy['year'] = processed_nat_gas_price_copy.index.year
    #print(f" processed_nat_gas_price_copy:{processed_nat_gas_price_copy}")

    # Filter for the specified years
    processed_nat_gas_price_copy = processed_nat_gas_price_copy[processed_nat_gas_price_copy['year'].isin(years)]
    print(f" processed_nat_gas_price_copy:{processed_nat_gas_price_copy}")

    # Convert the 'NAT_GAS_PRICE' column to numeric, handling non-numeric entries
    processed_nat_gas_price_copy[gbl.gbl_natgas_primary_data_col] = pd.to_numeric(processed_nat_gas_price_copy[gbl.gbl_natgas_primary_data_col], errors='coerce')

    print(type(gbl.gbl_tracked_powergen_dict['generation_sources']))

    # Only used if capacity_factor_range does not hold a range of values
    # If so, this variable is used to identify the position of the target_capacity_factor 
    # for the generator (key) in the tracked_dict
    target_capacity_factor_counter = 0

    #Loop through generators and extract the necessary data for LCOE calculations
    for key, value in gbl.gbl_tracked_powergen_dict['generation_sources'].items():
        lcoe_categories_list = []
        
        # Create inner loop for the capacity factor for 2x separate scenarios:
        # 1. If a range of capacity factors is provided
        # 2. If a single capacity factor is provided

        # Define capacity_factor_range as a list of the target_capacity_factor for each generator (key)
        # Check if the length of th ecapacity_factor_range is equal to the number of generators ub the tracked_dict
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

                # Save the updated dictionary to a JSON filE
                gbl.gbl_tracked_powergen_dict.save_to_json(gbl.gbl_json_power_generation_path) #Took Out

                # Optionally, clear the recorded changes
                #tracked_dict.clear_changes() 
                

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
                gbl.gbl_lcoe_data_by_generator[key] = lcoe_categories_list

                # Increment the target capacity factor counter
                # This is only used when a range of capacity factors is not provided
                # and a target capacity factor for each generator is held in the capacity_factor_range
                # list. Otherwise the capacity_factor_range
                target_capacity_factor_counter = target_capacity_factor_counter + 1

        # Transfer generator results to csv file and update dictionary and json file
        data_dict_filename_str = f"{key}_lcoe.csv"
        gen_type = data_dict_filename_str.replace("_lcoe.csv", "")
        output_path = r'C:\Users\kaczanor\OneDrive - Enbridge Inc\Documents\Python\EDC Hourly Capacity Factor Q2 2024\outputs\csv_data\Generator_Ouput_Data'
        gen_data = gbl.gbl_lcoe_data_by_generator[key]
        json_dict = gbl.gbl_tracked_loaded_dict_json_file_data
        json_dict_path = gbl.gbl_json_file_path_loaded
        save_data_as_csv_print_data_table_and_update_dictdate_dict(
            output_path, 
            gen_type, 
            data_dict_filename_str,
            json_dict, 
            json_dict_path, 
            gen_data
            )

    # Create LCOE Time Graph by capcity factor range 10-100%
    graph_lcoe(gbl.gbl_lcoe_data_by_generator)
    
    # Create LCOE Waterfall Chart
    plot_waterfall_chart(gbl.gbl_lcoe_data_by_generator)

    #Create stacked lcoe chart for ALL generators in the dictionary
    #This graph needs to use the default target capacity factor for each generator.
    stacked_lcoe_chart_all_generators(gbl.gbl_lcoe_data_by_generator)
    

    return year_title
########################################################################
# Helper Functions for Back-Casting Analysis
########################################################################
def calculate_start_cost(current_generator, capacity, start_up_cost_amortization_hours, nat_gas_price, current_start_status):
 # Apply the start costs estimate if the plant is starting
    #if current_hour_start:
    if current_start_status == 'cold_start':
        start_up_cost = float(gbl.gbl_tracked_powergen_dict['generation_sources'][current_generator]['start_up_cost']['cold_start']['nonfuel_cost_dollar_start']/capacity/start_up_cost_amortization_hours)\
            + (float(gbl.gbl_tracked_powergen_dict['generation_sources'][current_generator]['start_up_cost']['cold_start']['fixed_cost_recovery_dollar_start'])/capacity/start_up_cost_amortization_hours) \
                + (float(gbl.gbl_tracked_powergen_dict['generation_sources'][current_generator]['start_up_cost']['cold_start']['fuel_consumed_gj_mw']) * nat_gas_price)
                
        # print(float(gbl.gbl_tracked_powergen_dict['generation_sources'][current_generator]['start_up_cost']['cold_start']['nonfuel_cost_dollar_start']))
        # print((float(gbl.gbl_tracked_powergen_dict['generation_sources'][current_generator]['start_up_cost']['cold_start']['fixed_cost_recovery_dollar_start'])/start_up_cost_amortization_hours))
        # print(f" {gbl.gbl_tracked_powergen_dict['generation_sources'][current_generator]['start_up_cost']['cold_start']['fuel_consumed_gj_mw']} * {nat_gas_price})")
        # print(f"Total start-up cost: {start_up_cost}")
    
    elif current_start_status == 'warm_start':
        start_up_cost = float(gbl.gbl_tracked_powergen_dict['generation_sources'][current_generator]['start_up_cost']['warm_start']['nonfuel_cost_dollar_start']/capacity/start_up_cost_amortization_hours)\
            + (float(gbl.gbl_tracked_powergen_dict['generation_sources'][current_generator]['start_up_cost']['warm_start']['fixed_cost_recovery_dollar_start'])/capacity/start_up_cost_amortization_hours) \
                + (float(gbl.gbl_tracked_powergen_dict['generation_sources'][current_generator]['start_up_cost']['warm_start']['fuel_consumed_gj_mw']) * nat_gas_price)
        
        # print(float(gbl.gbl_tracked_powergen_dict['generation_sources'][current_generator]['start_up_cost']['warm_start']['nonfuel_cost_dollar_start']))
        # print((float(gbl.gbl_tracked_powergen_dict['generation_sources'][current_generator]['start_up_cost']['warm_start']['fixed_cost_recovery_dollar_start'])/start_up_cost_amortization_hours))
        # print((float(gbl.gbl_tracked_powergen_dict['generation_sources'][current_generator]['start_up_cost']['warm_start']['fuel_consumed_gj_mw']) * nat_gas_price))
        # print(f"Total start-up cost: {start_up_cost}")
    
    elif current_start_status == 'hot_start':
        start_up_cost = float(gbl.gbl_tracked_powergen_dict['generation_sources'][current_generator]['start_up_cost']['hot_start']['nonfuel_cost_dollar_start']/capacity/start_up_cost_amortization_hours)\
            + (float(gbl.gbl_tracked_powergen_dict['generation_sources'][current_generator]['start_up_cost']['hot_start']['fixed_cost_recovery_dollar_start'])/capacity/start_up_cost_amortization_hours) \
                + (float(gbl.gbl_tracked_powergen_dict['generation_sources'][current_generator]['start_up_cost']['hot_start']['fuel_consumed_gj_mw']) * nat_gas_price)
        
        # print(float(gbl.gbl_tracked_powergen_dict['generation_sources'][current_generator]['start_up_cost']['hot_start']['nonfuel_cost_dollar_start']))
        # print((float(gbl.gbl_tracked_powergen_dict['generation_sources'][current_generator]['start_up_cost']['hot_start']['fixed_cost_recovery_dollar_start'])/start_up_cost_amortization_hours))
        # print((float(gbl.gbl_tracked_powergen_dict['generation_sources'][current_generator]['start_up_cost']['hot_start']['fuel_consumed_gj_mw']) * nat_gas_price))
        # print(f"Total start-up cost: {start_up_cost}")

    else:
        # current_start_status is None:
        start_up_cost = 0
        
    #else:
    #    start_up_cost = 0
    #print(f"Start cost applied at {hour}. Total cost: {total_cost}")    

    return start_up_cost

##################################################
#def calc_start_status(year_integer, month_integer, day_integer, hour_integer, gbl_tracked_powergen_dict, current_generator, current_down_time_count, current_up_time_count, current_hour_start): 
def calc_start_status(
            #gbl_tracked_powergen_dict, 
            current_generator,
            current_down_time_count
            ): 

    try: 
        cold_start_threshold = float(gbl.gbl_tracked_powergen_dict['generation_sources'][current_generator]['start_up_cost']['cold_start']['cold_start_determination_hrs']) 
        warm_start_threshold = float(gbl.gbl_tracked_powergen_dict['generation_sources'][current_generator]['start_up_cost']['warm_start']['warm_start_determination_hrs']) 
        hot_start_threshold = float(gbl.gbl_tracked_powergen_dict['generation_sources'][current_generator]['start_up_cost']['hot_start']['hot_start_determination_hrs']) 

        # Determine the current start status based on the down time count
        # This is determined BEFORE the bid costs are known to avoid circular logic
        # This is determined what the start state is IF the plan decides to start
        # The thresholds look like this:
        # ------------8----------------16----------------24
        #   Hot Start     Warm Start         Cold Start
        #   0-8 hrs       8-16 hrs           16-24 hrs


        if current_down_time_count >= cold_start_threshold:
            return 'cold_start'
        elif current_down_time_count >= warm_start_threshold and current_down_time_count < cold_start_threshold:
            return 'warm_start'
        elif current_down_time_count > 0 and current_down_time_count < warm_start_threshold:
                return 'hot_start'
        else:
            return 'none_start'
        
        # At this point in the code these are the only possible outcomes
        # prior to testing for price and all other contraints.  The start_status
        # has to be updated later in the code after all the constraints are tested 

    except Exception as e: 
        # Error handling 
        print(f"Error in calc_start_status: {e}")
        #print(f" year:{year_integer}, month: {month_integer},  day: {day_integer}, hour: {hour_integer}, current generator: {current_generator}, current_down_time_count: {current_down_time_count}")

#############################################
# Hourly Loop
#############################################

def hourly_loop(hour):
    # print("*" *90)
    # print(f" Simulation Hour: {hour}")
    # print("*" *90)
    # print(f" gbl_tracked_dict_run_variables: {gbl_tracked_dict_run_variables}")
    # print(f" gbl_tracked_dict_run_variables: {gbl_tracked_dict_run_variables_ideal}")

    # Step 1: Create access the DataFrames and Dictionaries directly from the variable dictionaries
    processed_nat_gas_price_copy = gbl.gbl_tracked_dict_general_data['processed_nat_gas_price_copy']
    processed_price_data_copy = gbl.gbl_tracked_dict_general_data['processed_price_data_copy']
    gbl.gbl_carbon_tax_annual_dict = gbl.gbl_tracked_dict_general_data['gbl_carbon_tax_annual_dict']
    gbl.gbl_tracked_powergen_dict = gbl.gbl_tracked_dict_general_data['gbl_tracked_powergen_dict']
    
    ##############################
    # Step 2:
    # Extract current hour data from the loaded time-series data
    # in the gbl_tracked_dict_general_data{} dictionary
    ##############################
    nat_gas_price = processed_nat_gas_price_copy.loc[hour, gbl.gbl_tracked_dict_general_data['gbl_natgas_primary_data_col']]# Taken from hourly data matching the pool price hour
    pool_price = processed_price_data_copy.loc[hour, gbl.gbl_tracked_dict_general_data['gbl_pool_price_primary_data_col']]  # Taken from hourly data matching the pool price hour
    year_str = str(gbl.gbl_tracked_dict_time_variables['year_integer'])
    carbon_cost_per_tonne = gbl.gbl_carbon_tax_annual_dict[year_str]# Taken from the annual carbon tax dictionary basd on year

    # Step 3: Pass values from generator specific variable dictionary to local variables 
    current_generator = gbl.gbl_tracked_dict_generator_specific['current_generator']
    capacity = gbl.gbl_tracked_dict_generator_specific['capacity']
    min_down_time = gbl.gbl_tracked_dict_generator_specific['min_down_time']
    min_up_time = gbl.gbl_tracked_dict_generator_specific['min_up_time']
    start_up_cost = gbl.gbl_tracked_dict_generator_specific['start_up_cost']
    run_hour_maintenance_target = gbl.gbl_tracked_dict_generator_specific['run_hour_maintenance_target']
    start_up_cost_amortization_hours = gbl.gbl_tracked_dict_generator_specific["start_up_cost_amortization_hours"]
    nat_gas_cost = nat_gas_price *  gbl.gbl_tracked_dict_generator_specific['heat_rate']     # $/MWh based on plant efficiency and nat gas price
    var_cost = gbl.gbl_tracked_dict_generator_specific['vom_costs']  # $/MWh 
    sts_cost = gbl.gbl_tracked_dict_generator_specific['sts_cost']   # $/MWh based on plant location as per AESO rates
    fixed_cost = gbl.gbl_tracked_dict_generator_specific['fom_cost']   # $/MWh converted from $/kW-year
    carbon_cost = carbon_cost_per_tonne * (gbl.gbl_tracked_dict_generator_specific['co2_emissions_intensity'] - gbl.gbl_tracked_dict_generator_specific['co2_reduction_target']) # $/MWh based on plant emissions and carbon tax
    
    # Step 4: Pass values from run variable dictionary to local variables
    is_running = gbl.gbl_tracked_dict_run_variables['is_running']
    is_running_counter = gbl.gbl_tracked_dict_run_variables['is_running_counter']
    current_down_time_count = gbl.gbl_tracked_dict_run_variables['current_down_time_count']
    current_up_time_count = gbl.gbl_tracked_dict_run_variables['current_up_time_count']
    previous_down_time_count = gbl.gbl_tracked_dict_run_variables['previous_down_time_count']
    previous_up_time_count = gbl.gbl_tracked_dict_run_variables['previous_up_time_count']
    number_of_starts = gbl.gbl_tracked_dict_run_variables['number_of_starts']
    number_of_stops = gbl.gbl_tracked_dict_run_variables['number_of_stops']
    previous_hour_start = gbl.gbl_tracked_dict_run_variables['previous_hour_start']
    previous_hour_stop = gbl.gbl_tracked_dict_run_variables['previous_hour_stop']
    current_hour_start = gbl.gbl_tracked_dict_run_variables['current_hour_start']
    current_hour_stop = gbl.gbl_tracked_dict_run_variables['current_hour_stop']
    cum_hour_integer = gbl.gbl_tracked_dict_run_variables['cum_hour_integer']
    constrained_ramp_up = gbl.gbl_tracked_dict_run_variables['constrained_ramp_up']
    constrained_ramp_down = gbl.gbl_tracked_dict_run_variables['constrained_ramp_down']
    current_hour_cold_start_count = gbl.gbl_tracked_dict_run_variables['current_hour_cold_start_count']
    current_hour_warm_start_count = gbl.gbl_tracked_dict_run_variables['current_hour_warm_start_count']
    current_hour_hot_start_count = gbl.gbl_tracked_dict_run_variables['current_hour_hot_start_count']
    current_hour_none_start_count = gbl.gbl_tracked_dict_run_variables['current_hour_none_start_count']

    # Step 5: Pass values from ideal run variable dictionary to local variables
    is_running_ideal = gbl.gbl_tracked_dict_run_variables_ideal['is_running_ideal']
    is_running_counter_ideal = gbl.gbl_tracked_dict_run_variables_ideal['is_running_counter_ideal']
    current_down_time_count_ideal = gbl.gbl_tracked_dict_run_variables_ideal['current_down_time_count_ideal']
    current_up_time_count_ideal = gbl.gbl_tracked_dict_run_variables_ideal['current_up_time_count_ideal']
    previous_down_time_count_ideal = gbl.gbl_tracked_dict_run_variables_ideal['previous_down_time_count_ideal']
    previous_up_time_count_ideal = gbl.gbl_tracked_dict_run_variables_ideal['previous_up_time_count_ideal']
    number_of_starts_ideal = gbl.gbl_tracked_dict_run_variables_ideal['number_of_starts_ideal']
    number_of_stops_ideal = gbl.gbl_tracked_dict_run_variables_ideal['number_of_stops_ideal']
    previous_hour_start_ideal = gbl.gbl_tracked_dict_run_variables_ideal['previous_hour_start_ideal']
    previous_hour_stop_ideal = gbl.gbl_tracked_dict_run_variables_ideal['previous_hour_stop_ideal']
    current_hour_start_ideal = gbl.gbl_tracked_dict_run_variables_ideal['current_hour_start_ideal']
    current_hour_stop_ideal = gbl.gbl_tracked_dict_run_variables_ideal['current_hour_stop_ideal']
    cum_hour_integer_ideal = gbl.gbl_tracked_dict_run_variables_ideal['cum_hour_integer_ideal']
    constrained_ramp_up_ideal = gbl.gbl_tracked_dict_run_variables_ideal['constrained_ramp_up_ideal']
    constrained_ramp_down_ideal = gbl.gbl_tracked_dict_run_variables_ideal['constrained_ramp_down_ideal']
    current_hour_cold_start_count_ideal = gbl.gbl_tracked_dict_run_variables_ideal['current_hour_cold_start_count_ideal']
    current_hour_warm_start_count_ideal = gbl.gbl_tracked_dict_run_variables_ideal['current_hour_warm_start_count_ideal']
    current_hour_hot_start_count_ideal = gbl.gbl_tracked_dict_run_variables_ideal['current_hour_hot_start_count_ideal']
    current_hour_none_start_count_ideal = gbl.gbl_tracked_dict_run_variables_ideal['current_hour_none_start_count_ideal']

    ###################################
    #Step 6:
    # Determine whether if the plant were to start - what kind of start would it be (cold, warm, hot)
    # This will be used to determine the start costs for bidding purposes.  If the plant does not actually 
    # start the current_start_status will be set to None
    ##################################
    current_start_status = calc_start_status(
            #gbl_tracked_powergen_dict,
            current_generator, 
            current_down_time_count

            )

    #print(f"1) current_start_status: {current_start_status}")

    current_start_status_ideal = calc_start_status(
            #gbl_tracked_powergen_dict,
            current_generator,
            current_down_time_count_ideal
            ) 
    #print(f"current_start_status_ideal: {current_start_status_ideal}")

    ###################################
    # Step 3:
    # Calculate start costs for the hour
    ##################################
    # Call calculate_start_cost() function to determine the start cost using current_start_status
    # The function passes back the start costs in $ prior to knowing if they will be used
    start_up_cost = calculate_start_cost(current_generator, capacity, start_up_cost_amortization_hours, nat_gas_price, current_start_status)
    #print(f"2) current_start_status: {current_start_status}")
    start_up_cost_ideal = calculate_start_cost(current_generator, capacity, start_up_cost_amortization_hours, nat_gas_price, current_start_status_ideal)


    ##################################
    # Step 4:
    # Calculate total costs per MWH
    ##################################
    # Calculated total cost with the inclusion of the start costs
    # Note total cost will have start costs removed fo the ideal case later in the code
    # Total cost $/MWh assuming the plant runs inclues all the costs of running and the start costs
    total_cost = nat_gas_cost + var_cost + start_up_cost + sts_cost + fixed_cost + carbon_cost
    total_cost_ideal = nat_gas_cost + var_cost + sts_cost + fixed_cost + carbon_cost
        
    # #Debugging prints
    # print(f"Year: {year}, Month: {hour.month}, Day: {hour.day}, Hour: {hour.hour}")
    # print(f"Hour: {hour}, is_running: {is_running}, constrained_ramp_up: {constrained_ramp_up}, constrained_ramp_down: {constrained_ramp_down}")
    # print(f"pool_price: {pool_price}, type: {type(pool_price)}")
    # print(f"total_cost: {total_cost}, type: {type(total_cost)}")

    # Ensure pool_price and total_cost are scalar values
    if not isinstance(hour, pd.Timestamp):
        hour = pd.Timestamp(hour)

    ##############################
    # Step 5:
    # Ensure all components are scalar values
    ##############################
    if isinstance(pool_price, pd.Series):
        pool_price = pool_price.iloc[0]
    
    if isinstance(nat_gas_cost, pd.Series):
        nat_gas_cost = nat_gas_cost.iloc[0]
        
    if isinstance(var_cost, pd.Series):
        var_cost = var_cost.iloc[0]
        
    if isinstance(start_up_cost, pd.Series):
        start_up_cost = start_up_cost.iloc[0]

    if isinstance(sts_cost, pd.Series):
        sts_cost = sts_cost.iloc[0]
        
    if isinstance(fixed_cost, pd.Series):
        fixed_cost = fixed_cost.iloc[0]
        
    if isinstance(carbon_cost, pd.Series):
        carbon_cost = carbon_cost.iloc[0]

    if isinstance(total_cost, pd.Series):
        total_cost = total_cost.iloc[0]

    ###################
    # Step 6:
    # Update constraints before the decision
    ###################
    #------------------------------
    # Actual Running Constraints
    #------------------------------
    constrained_ramp_up = not is_running and current_down_time_count < min_down_time
    constrained_ramp_down = is_running and current_up_time_count < min_up_time

    #------------------------------
    #Ideal Running Constraints
    #------------------------------
    constrained_ramp_up_ideal = not is_running_ideal and current_down_time_count_ideal < min_down_time
    constrained_ramp_down_ideal = is_running_ideal and current_up_time_count_ideal < min_up_time
    ####################

    ####################
    # Step 7:
    # Determine plant start-up and shut-down decisions and track the number of starts and stops
    ###################

    # Determine if the plant should start based on whether its variable costs are less than the pool price
    # The fist pass calculates the actual plant production and operating hours taking into account
    # the minimum up and down time constraints and includes start up costs in the hourly bid
    #####################################
    # 1st Pass: With the start up costs
    #####################################
    # Step 7a: Check if the generator is in the money in the current hour to determine if it should run
    # Special Note: Need to consider additional logic to incorporate the plants expections of the day-ahead
    # market prices and the plants expectations of the future pool prices to allow for strategies to maximize
    # profits
    # print(f"3) current_start_status: {current_start_status}")


    #print(f" preliminary current_start_status: {current_start_status}")
    if pool_price > total_cost:
        
        # Step 7b: if the plant should start determine if it can actually start based on the minimum down time constraint
        # generator is idle and in the money and can turn on.
        # Special Note: the constrined_ramp_up is a boolean to define if the plant can start at full capacity or not.
        # Need to consider future logic to account for delayed ramp-up times for plants that need to ramp up to full capacity
        
        #old
        #if not is_running and not constrained_ramp_up:
        #new
        if not is_running and not constrained_ramp_up and is_running_counter < run_hour_maintenance_target:
            # if the plant is not running and can start
            #register a start
            current_hour_start = True
            current_hour_stop = False #new
            #increment the number of starts
            number_of_starts += 1 #Note this is cumulative
            is_running = True
            is_running_counter += 1 #increment cumulative counter
            #print(f" year:{year_integer}, month: {month_integer},  day: {day_integer}, hour: {hour_integer}, current generator: {current_generator}, pool_price: {pool_price}, total_cost: {total_cost}")
            #reset the down time count
            current_down_time_count = 0  # Reset as the plant starts
            #start counting up time
            current_up_time_count = 1
            #print(f"Plant started at {hour}. Number of starts: {number_of_starts}")

            # Not these are cumulative not incremental
            if current_start_status == 'cold_start':
                current_hour_cold_start_count +=1
            elif current_start_status == 'warm_start':
                current_hour_warm_start_count +=1
            elif current_start_status == 'hot_start':
                current_hour_hot_start_count +=1
            elif current_start_status == 'none_start':
                current_hour_none_start_count +=1
            
        # Step 7c: generator is already running and continues to be in the money and should run 
        else:
            # Plant is running and should stay running if it can
            current_hour_start = False
            current_hour_stop = False #new
            #old
            #if is_running:
            #new
            if is_running and is_running_counter < run_hour_maintenance_target:
                current_up_time_count = previous_up_time_count + 1 #staus running
                is_running_counter += 1 #increment cumulative counter
                #reset start status as it was set assuming the plant would start (cold, warm, hot, none)
                current_start_status = 'none_start'
                #print(f"Plant is running. Uptime count: {current_up_time_count}")
            #new
            elif is_running_counter >= run_hour_maintenance_target:
                # if running time has exceeded the limit, stop the plant
                current_hour_start = False
                current_hour_stop = True
                # Increment the number of stops
                number_of_stops += 1
                is_running = False
                 #reset start status as it was set assuming the plant would start (cold, warm, hot, none)
                current_start_status = 'none_start'
                # Reset as the plant stops
                current_up_time_count = 0
                # Start counting down time
                current_down_time_count = 1
                #print(f" Plant stopped due to runtime limit at {hour}. Number of stops: {number_of_stops}")

    # generator is not in the money and should not run
    else:
        # Step 7d: if the plant is running, and it needs to stop, we need to determine if it can actually
        # stop based on the minimum up time constraint
        # Special Note: need to incorproate future logic to account for plants that have minimum stable capacity
        # levels that also need to be considered (e.g. 50% of capacity)
        if is_running and not constrained_ramp_down and current_up_time_count >= min_up_time:
            #is_running = True #Changed from False
            # Register a start/stop
            current_hour_start = False #new
            current_hour_stop = True
            # Increment the number of stops
            number_of_stops += 1
            is_running = False 
            #reset start status as it was set assuming the plant would start (cold, warm, hot, none)
            current_start_status = 'none_start'
            # Reset as the plant stops
            current_up_time_count = 0
            # Start counting down time  
            current_down_time_count = 1  
            #print(f"Plant stopped at {hour}. Number of stops: {number_of_stops}")
        
        # Step 7e: generator is down and is not in the money and should not start    
        else:
            # Plant is not running and should stay off if it can
            # Register a non-stop
            current_hour_start = False #new
            current_hour_stop = False
            if not is_running:
                # Increment down time
                current_down_time_count = max(current_down_time_count + 1, min_down_time)  # Increment down time
                #reset start status as it was set assuming the plant would start (cold, warm, hot, none)
                current_start_status = 'none_start'
                #print(f"Plant is not running. Downtime count: {current_down_time_count}")
    

    # print(f" reset current_start_status: {current_start_status}")
    # print(f" currrent_hour_cold_start_count: {current_hour_cold_start_count}")
    # print(f" current_hour_warm_start_count: {current_hour_warm_start_count}")
    # print(f" current_hour_hot_start_count: {current_hour_hot_start_count}")
    # print(f" current_hour_none_start_count: {current_hour_none_start_count}")

    #print(f"4) current_start_status: {current_start_status}")
    #####################################
    # 2nd Pass: With the start up costs excluded from the hourly bidding
    #####################################
    # generator is in the money and should run
    # Take out the start costs for this case

    
    #print(f" preliminary current_start_status_ideal: {current_start_status_ideal}")

    if pool_price > total_cost_ideal:
        # if the plant should start determine if it can actually start based on the minimum down time constraint
        # generator is idle and in the money and can turn on
        
        #old
        #if not is_running_ideal and not constrained_ramp_up_ideal:
        #new
        if not is_running_ideal and not constrained_ramp_up_ideal and is_running_counter_ideal < run_hour_maintenance_target:
            # if the plant is not running and can start
            # Register a start/stops
            current_hour_start_ideal = True
            current_hour_stop_ideal = False #new
            # Increment the number of starts
            number_of_starts_ideal += 1 #Note this is cumulative and does not reset
            is_running_ideal = True
            is_running_counter_ideal += 1 #increment cumulative counter
            # Reset the down time count
            current_down_time_count_ideal = 0  
            # Start counting up time
            current_up_time_count_ideal = 1
            #print(f"Plant started at {hour}. Number of starts: {number_of_starts}")

            # Not these are cumulative not incremental
            if current_start_status_ideal == 'cold_start':
                current_hour_cold_start_count_ideal +=1
            elif current_start_status_ideal == 'warm_start':
                current_hour_warm_start_count_ideal +=1
            elif current_start_status_ideal == 'hot_start':
                current_hour_hot_start_count_ideal +=1
            elif current_start_status_ideal == 'none_start':
                current_hour_none_start_count_ideal +=1

        # generator is already running and continues to be in the money and should run
        else:
            # Plant is running and should stay running if it can
            current_hour_start_ideal = False
            current_hour_stop_ideal = False #new
            # Increment up time
            #old
            #if is_running_ideal:
            #new
            if is_running_ideal and is_running_counter_ideal < run_hour_maintenance_target:
                current_up_time_count_ideal += 1 
                is_running_counter_ideal += 1 #increment cumulative counter
                #reset start status as it was set assuming the plant would start (cold, warm, hot, none)
                current_start_status_ideal = 'none_start'
                #print(f"Plant is running. Uptime count: {current_up_time_count}")
            #new
            elif is_running_counter_ideal >= run_hour_maintenance_target:
                # if running time has exceeded the lmit, stop the plant
                current_hour_start_ideal = False
                current_hour_stop_ideal = True
                # Increment the number of stops
                number_of_stops_ideal += 1
                is_running_ideal = False
                #reset start status as it was set assuming the plant would start (cold, warm, hot, none)
                current_start_status_ideal = 'none_start'
                # Reset as the plant stops
                current_up_time_count_ideal = 0
                # Start counting down time
                current_down_time_count_ideal = 1
                #print(f" Plant stopped due to runtime limit at {hour}. Number of stops: {number_of_stops}")

    # generator is not in the money and should not run
    else:
        # if the plant is running determine and it needs to stop determine if it can actually
        if is_running_ideal and not constrained_ramp_down_ideal and current_up_time_count_ideal >= min_up_time:
            # Plant is running and should stay running if it can
            #is_running_ideal = True #Changed from False
            # Register a stop
            current_hour_start_ideal = False #new
            current_hour_stop_ideal = True
            # Increment the number of stops
            number_of_stops_ideal += 1
            is_running_ideal = False 
            #reset start status as it was set assuming the plant would start (cold, warm, hot, none)
            current_start_status_ideal = 'none_start'
            # Reset as the plant stops
            current_up_time_count_ideal = 0  
            # Start counting down time
            current_down_time_count_ideal = 1  
            #print(f"Plant stopped at {hour}. Number of stops: {number_of_stops}")
        # generator is down and is not in the money and should not start
        else:
            # Plant is not running and should stay off if it can
            current_hour_stop_ideal = False
            current_hour_stop_ideal = False #new
            if not is_running_ideal:
                # Increment down time
                current_down_time_count_ideal = max(current_down_time_count_ideal + 1, min_down_time)  # Increment down time
                #reset start status as it was set assuming the plant would start (cold, warm, hot, none)
                current_start_status_ideal = 'none_start'
                #print(f"Plant is not running. Downtime count: {current_down_time_count}")


    # print(f" reset current_start_status_ideal: {current_start_status_ideal}")
    # print(f" currrent_hour_cold_start_count_ideal: {current_hour_cold_start_count_ideal}")
    # print(f" current_hour_warm_start_count_ideal: {current_hour_warm_start_count_ideal}")
    # print(f" current_hour_hot_start_count_ideal: {current_hour_hot_start_count_ideal}")
    # print(f" current_hour_none_start_count_ideal: {current_hour_none_start_count_ideal}")

    #print(f"5) current_start_status: {current_start_status}")

    ####################################
    # Update dictionary values and pass dictionary back to routine that called this function
    ####################################
    # gbl_tracked_dict_time_variables,
    # No updated need here as these variables are updated outside of the loop

    # gbl_tracked_dict_general_data,
    # No updated need here as these are all inputs that are not changed in the function
    
    # gbl_tracked_dict_generator_specific,
    # No updated need here as these are all inputs that are not changed in the function
    
    #gbl_tracked_dict_run_variables,
    gbl.gbl_tracked_dict_run_variables['current_start_status'] = current_start_status
    gbl.gbl_tracked_dict_run_variables['is_running'] = is_running
    gbl.gbl_tracked_dict_run_variables['is_running_counter'] = is_running_counter
    gbl.gbl_tracked_dict_run_variables['current_down_time_count'] = current_down_time_count
    gbl.gbl_tracked_dict_run_variables['current_up_time_count'] = current_up_time_count
    gbl.gbl_tracked_dict_run_variables['previous_down_time_count'] = previous_down_time_count
    gbl.gbl_tracked_dict_run_variables['previous_up_time_count'] = previous_up_time_count
    gbl.gbl_tracked_dict_run_variables['number_of_starts'] = number_of_starts
    gbl.gbl_tracked_dict_run_variables['number_of_stops'] = number_of_stops
    gbl.gbl_tracked_dict_run_variables['previous_hour_start'] = previous_hour_start
    gbl.gbl_tracked_dict_run_variables['previous_hour_stop'] = previous_hour_stop
    gbl.gbl_tracked_dict_run_variables['current_hour_start'] = current_hour_start
    gbl.gbl_tracked_dict_run_variables['current_hour_stop'] = current_hour_stop
    gbl.gbl_tracked_dict_run_variables['cum_hour_integer'] = cum_hour_integer
    gbl.gbl_tracked_dict_run_variables['constrained_ramp_up'] = constrained_ramp_up
    gbl.gbl_tracked_dict_run_variables['constrained_ramp_down'] = constrained_ramp_down
    gbl.gbl_tracked_dict_run_variables['current_hour_cold_start_count'] = current_hour_cold_start_count
    gbl.gbl_tracked_dict_run_variables['current_hour_warm_start_count'] = current_hour_warm_start_count
    gbl.gbl_tracked_dict_run_variables['current_hour_hot_start_count'] = current_hour_hot_start_count
    gbl.gbl_tracked_dict_run_variables['current_hour_none_start_count'] = current_hour_none_start_count
    gbl.gbl_tracked_dict_run_variables['total_cost'] = total_cost
    
    #gbl_tracked_dict_run_variables_ideal
    gbl.gbl_tracked_dict_run_variables_ideal['current_start_status_ideal'] = current_start_status_ideal
    gbl.gbl_tracked_dict_run_variables_ideal ['is_running_ideal'] = is_running_ideal
    gbl.gbl_tracked_dict_run_variables_ideal ['is_running_counter_ideal'] = is_running_counter_ideal
    gbl.gbl_tracked_dict_run_variables_ideal ['current_down_time_count_ideal'] = current_down_time_count_ideal
    gbl.gbl_tracked_dict_run_variables_ideal ['current_up_time_count_ideal'] = current_up_time_count_ideal
    gbl.gbl_tracked_dict_run_variables_ideal ['previous_down_time_count_ideal'] = previous_down_time_count_ideal
    gbl.gbl_tracked_dict_run_variables_ideal ['previous_up_time_count_ideal'] = previous_up_time_count_ideal
    gbl.gbl_tracked_dict_run_variables_ideal ['number_of_starts_ideal'] = number_of_starts_ideal
    gbl.gbl_tracked_dict_run_variables_ideal ['number_of_stops_ideal'] = number_of_stops_ideal
    gbl.gbl_tracked_dict_run_variables_ideal ['previous_hour_start_ideal'] = previous_hour_start_ideal
    gbl.gbl_tracked_dict_run_variables_ideal ['previous_hour_stop_ideal'] = previous_hour_stop_ideal
    gbl.gbl_tracked_dict_run_variables_ideal ['current_hour_start_ideal'] = current_hour_start_ideal
    gbl.gbl_tracked_dict_run_variables_ideal ['current_hour_stop_ideal'] = current_hour_stop_ideal
    gbl.gbl_tracked_dict_run_variables_ideal ['cum_hour_integer_ideal'] = cum_hour_integer_ideal
    gbl.gbl_tracked_dict_run_variables_ideal ['constrained_ramp_up_ideal'] = constrained_ramp_up_ideal
    gbl.gbl_tracked_dict_run_variables_ideal ['constrained_ramp_down_ideal'] = constrained_ramp_down_ideal
    gbl.gbl_tracked_dict_run_variables_ideal ['current_hour_cold_start_count_ideal'] = current_hour_cold_start_count_ideal
    gbl.gbl_tracked_dict_run_variables_ideal ['current_hour_warm_start_count_ideal'] = current_hour_warm_start_count_ideal
    gbl.gbl_tracked_dict_run_variables_ideal ['current_hour_hot_start_count_ideal'] = current_hour_hot_start_count_ideal
    gbl.gbl_tracked_dict_run_variables_ideal ['current_hour_none_start_count_ideal'] = current_hour_none_start_count_ideal
    gbl.gbl_tracked_dict_run_variables['total_cost_ideal'] = total_cost_ideal

    # pass some of the current hour market variables back as well
    current_hour_market_stats = {
        'pool_price' : pool_price, 
        'nat_gas_price' : nat_gas_price, 
        'nat_gas_cost' : nat_gas_cost,  
        'total_cost' : total_cost, 
        'carbon_cost_per_tonne' : carbon_cost_per_tonne,
        'carbon_cost' : carbon_cost,
        'var_cost' : var_cost,
        'start_up_cost' : start_up_cost,
        'sts_cost' : sts_cost, 
        'fixed_cost' : fixed_cost, 
        'total_cost' : total_cost,
        'total_cost_ideal' : total_cost_ideal
    }

    return current_hour_market_stats 

####################################################

#Format Data in Table
def format_revenue_cost_margin(value):
    return "${:,.1f} MM".format(value / 1_000_000) if not pd.isnull(value) else "$0.0 MM"

def format_received_pool_price(value):
    return "${:,.2f}".format(value) if not pd.isnull(value) else "$0.00"

def format_capacity_factor(value):
    return "{:.1%}".format(value) if not pd.isnull(value) else "0.0%"

def format_thousands(value):
    return "{:,.0f}".format(value) if not pd.isnull(value) else "0"

def truncate_to_two_decimals(value):
    if pd.isnull(value):
        return "0.00"
    return "{:.2f}".format(math.trunc(value * 100) / 100)
# *****************************************

# Apply formatting for printing
def apply_formatting(df):
    formatted_df = df.copy()
    formatted_df['YEAR'] = formatted_df['YEAR'].apply(str)  # Ensure year is treated as a string for printing
    formatted_df['STARTS'] = formatted_df['STARTS'].apply(format_thousands)
    formatted_df['STOPS'] = formatted_df['STOPS'].apply(format_thousands)
    formatted_df['COLD_STARTS'] = formatted_df['COLD_STARTS'].apply(format_thousands)
    formatted_df['WARM_STARTS'] = formatted_df['WARM_STARTS'].apply(format_thousands)
    formatted_df['HOT_STARTS'] = formatted_df['HOT_STARTS'].apply(format_thousands)
    formatted_df['START_COST'] = formatted_df['START_COST'].apply(format_thousands)
    formatted_df['MW_PRODUCTION'] = formatted_df['MW_PRODUCTION'].apply(format_thousands)
    formatted_df['CAPACITY_FACTOR'] = formatted_df['CAPACITY_FACTOR'].apply(format_capacity_factor)
    formatted_df['RUN_HOURS'] = formatted_df['RUN_HOURS'].apply(format_thousands)
    formatted_df['RUN_HOURS_CUM'] = formatted_df['RUN_HOURS_CUM'].apply(format_thousands)
    formatted_df['IN_MERIT'] = formatted_df['IN_MERIT'].apply(format_thousands)
    formatted_df['RUN_RATE'] = formatted_df['RUN_RATE'].apply(format_capacity_factor)
    formatted_df['NAT_GAS_PRICE_GJ'] = formatted_df['NAT_GAS_PRICE_GJ'].apply(format_received_pool_price)
    formatted_df['NAT_GAS_COST_MWH'] = formatted_df['NAT_GAS_COST_MWH'].apply(format_received_pool_price)
    formatted_df['ACTUAL_EMISSIONS'] = formatted_df['ACTUAL_EMISSIONS'].apply(format_thousands)
    formatted_df['EMISSIONS_INTENSITY'] = formatted_df['EMISSIONS_INTENSITY'].apply(format_received_pool_price)
    formatted_df['TAXABLE_EMISSIONS'] = formatted_df['TAXABLE_EMISSIONS'].apply(format_thousands)
    formatted_df['CARBON_TAX_DOLLARS'] = formatted_df['CARBON_TAX_DOLLARS'].apply(format_revenue_cost_margin)
    formatted_df['CARBON_TAX_DOLLARS_TONNE'] = formatted_df['CARBON_TAX_DOLLARS_TONNE'].apply(format_thousands)
    formatted_df['CARBON_TAX_DOLLARS_MWH'] = formatted_df['CARBON_TAX_DOLLARS_MWH'].apply(format_thousands)
    formatted_df['RECEIVED_POOL_PRICE'] = formatted_df['RECEIVED_POOL_PRICE'].apply(format_received_pool_price)
    formatted_df['AVG_POOL_PRICE'] = formatted_df['AVG_POOL_PRICE'].apply(format_received_pool_price)
    formatted_df['RECEIVED_POOL_PRICE_RATIO_TO_AVG_SPOT'] = formatted_df['RECEIVED_POOL_PRICE_RATIO_TO_AVG_SPOT'].apply(truncate_to_two_decimals)
    formatted_df['NAT_GAS_COST_DOLLARS'] = formatted_df['NAT_GAS_COST_DOLLARS'].apply(format_revenue_cost_margin)
    formatted_df['TOTAL_COST_DOLLARS'] = formatted_df['TOTAL_COST_DOLLARS'].apply(format_revenue_cost_margin)
    formatted_df['REVENUE'] = formatted_df['REVENUE'].apply(format_revenue_cost_margin)
    formatted_df['OPERATING_MARGIN'] = formatted_df['OPERATING_MARGIN'].apply(format_revenue_cost_margin)
    return formatted_df

####################################################
def create_update_end_of_hour_row_data(
                        # gbl_tracked_dict_general_data,
                        # gbl_tracked_dict_generator_specific,
                        #temp_data_dict, >>moved below
                        is_ideal = False):

    temp_data_dict = {}
    if is_ideal: 
        temp_data_dict = gbl.gbl_tracked_dict_run_variables
    else:
        temp_data_dict = gbl.gbl_tracked_dict_run_variables_ideal

    suffix = '_ideal' if is_ideal else ""

   # Update dictionary previous period values with current period values
    temp_data_dict[f'constrained_ramp_down{suffix}']: temp_data_dict[f'is_running{suffix}'] < gbl.gbl_tracked_dict_generator_specific['min_up_time']
    temp_data_dict[f'previous_hour_start{suffix}']: temp_data_dict[f'current_hour_start{suffix}']
    temp_data_dict[f'previous_hour_warm_start_count{suffix}']: temp_data_dict[f'current_hour_warm_start_count{suffix}']
    temp_data_dict[f'previous_hour_hot_start_count{suffix}']: temp_data_dict[f'current_hour_hot_start_count{suffix}']
    temp_data_dict[f'previous_hour_none_start_count{suffix}']: temp_data_dict[f'current_hour_none_start_count{suffix}']
    temp_data_dict[f'previous_hour_stop{suffix}']: temp_data_dict[f'current_hour_stop{suffix}']
    temp_data_dict[f'cum_hour_integer{suffix}']: temp_data_dict[f'cum_hour_integer{suffix}'] + 1  # Increment the value


    return temp_data_dict, temp_data_dict

####################################################  
#New Function to create row data
def create_row_data(
        hour,
        current_hour_market_stats,
        is_ideal = False):
    """
    Function to create row data dictionary for both actual and ideal scenarios.
    The temp_data_dict represents the two diciontaries that exist for the 
    gbl_tracked_dict_run_variables and gbl_tracked_dict_run_variables_ideal.
    These function is called twice and whatever of these two dictionaries
    is passed to it is refered to as the 'temp_data_dict' and a 'suffix'
    variable is used to differentiate between them as they hold variables 
    with different names like: is_running_counter vs. is_running_counter_ideal

    Other dictionaries have common variables that do not make that distinction like 
    gbl_tracked_dict_time_variables, gbl_tracked_dict_general_data, gbl_tracked_dict_generator_specific

    The current_hour_market_stats holds a handful of market varaibes from the current hour.
    And these are mulitpled by the is_running{suffix} variable to capture what prices
    the generator garnered in that hour.

    """
    temp_data_dict = {}
    if is_ideal: 
        temp_data_dict = gbl.gbl_tracked_dict_run_variables_ideal
        
    else:
        temp_data_dict = gbl.gbl_tracked_dict_run_variables



    suffix = '_ideal' if is_ideal else ""
 
    row_data = {
        'DateTime': hour,
        'hour': hour.hour,
        'year': hour.year,
        'month': hour.month,
        'Capacity' : gbl.gbl_tracked_dict_generator_specific['capacity'],
        'STARTS': temp_data_dict[f'number_of_starts{suffix}'],
        'COLD_STARTS': temp_data_dict[f'current_hour_cold_start_count{suffix}'],
        'WARM_STARTS': temp_data_dict[f'current_hour_warm_start_count{suffix}'],
        'HOT_STARTS': temp_data_dict[f'current_hour_hot_start_count{suffix}'],
        'NONE_STARTS': temp_data_dict[f'current_hour_none_start_count{suffix}'],
        'STOPS': temp_data_dict[f'number_of_stops{suffix}'],
        'START_STATUS': temp_data_dict[f'current_start_status{suffix}'],
        'RUN_HOURS': temp_data_dict[f'is_running{suffix}'],
        'RUN_HOURS_CUM': temp_data_dict[f'is_running_counter{suffix}'],
        'CURRENT_HOUR_START': temp_data_dict[f'current_hour_start{suffix}'],
        'CURRENT_HOUR_STOP': temp_data_dict[f'current_hour_stop{suffix}'],
        'PREVIOUS_HOUR_START': temp_data_dict[f'previous_hour_start{suffix}'],
        'PREVIOUS_HOUR_STOP': temp_data_dict[f'previous_hour_stop{suffix}'],
        'UPTIME_COUNT': temp_data_dict[f'current_up_time_count{suffix}'],
        'DOWNTIME_COUNT': temp_data_dict[f'current_down_time_count{suffix}'],
        'CONSTRAINED_RAMP_UP': temp_data_dict[f'constrained_ramp_up{suffix}'],
        'CONSTRAINED_RAMP_DOWN': temp_data_dict[f'constrained_ramp_down{suffix}'],
        'MW_PRODUCTION': gbl.gbl_tracked_dict_generator_specific['capacity'] * temp_data_dict[f'is_running{suffix}'],
        'ACTUAL_EMISSIONS': gbl.gbl_tracked_dict_generator_specific['capacity'] * temp_data_dict[f'is_running{suffix}'] * gbl.gbl_tracked_dict_generator_specific['co2_emissions_intensity'],
        'TAXABLE_EMISSIONS': gbl.gbl_tracked_dict_generator_specific['capacity'] * temp_data_dict[f'is_running{suffix}'] * (gbl.gbl_tracked_dict_generator_specific['co2_emissions_intensity']- gbl.gbl_tracked_dict_generator_specific['co2_reduction_target']),
        'POOL_PRICE': current_hour_market_stats['pool_price'],
        'RECEIVED_POOL_PRICE': current_hour_market_stats['pool_price'] * temp_data_dict[f'is_running{suffix}'],
        'NAT_GAS_PRICE': current_hour_market_stats['nat_gas_price'] * temp_data_dict[f'is_running{suffix}'],
        'NAT_GAS_COST_MWH': current_hour_market_stats['nat_gas_cost'],
        'NAT_GAS_COST_DOLLARS': current_hour_market_stats['nat_gas_cost'] * gbl.gbl_tracked_dict_generator_specific['capacity'] * temp_data_dict[f'is_running{suffix}'],
        'CARBON_TAX_DOLLARS_TONNE': current_hour_market_stats['carbon_cost_per_tonne'],
        'CARBON_TAX_DOLLARS_MWH': current_hour_market_stats['carbon_cost'],
        'CARBON_TAX_DOLLARS': current_hour_market_stats['carbon_cost'] * gbl.gbl_tracked_dict_generator_specific['capacity'] * temp_data_dict[f'is_running{suffix}'],
        'VAR_COST': current_hour_market_stats['var_cost'],
        'START_COST': current_hour_market_stats['start_up_cost'],
        'STS_COST': current_hour_market_stats['sts_cost'],
        'FOM_COST': current_hour_market_stats['fixed_cost'],
        'TOTAL_COST_DOLLARS': current_hour_market_stats[f'total_cost{suffix}'] * gbl.gbl_tracked_dict_generator_specific['capacity'] * temp_data_dict[f'is_running{suffix}'],
        'TOTAL_COST_MWH': current_hour_market_stats[f'total_cost{suffix}'] / gbl.gbl_tracked_dict_generator_specific['capacity'] * temp_data_dict[f'is_running{suffix}'],
        'IN_MERIT': current_hour_market_stats['pool_price'] > current_hour_market_stats[f'total_cost{suffix}'] * temp_data_dict[f'is_running{suffix}'],
        'OPERATING_MARGIN': ( current_hour_market_stats['pool_price'] * temp_data_dict[f'is_running{suffix}']) - (current_hour_market_stats[f'total_cost{suffix}']  * gbl.gbl_tracked_dict_generator_specific['capacity'] * temp_data_dict[f'is_running{suffix}'])
    }
    return row_data

####################################################
# New Function to create operating data

def create_operating_data(seed):
    """
    Function to create operating data for actual and ideal scenarios.
    """
    

    operating_data_rows = []
    operating_data_ideal_rows = []
    end_of_hour_update_data = []
    end_of_hour_update_data_ideal = []
    current_hour_market_stats = {}
    processed_price_data_copy = gbl.gbl_tracked_dict_general_data['processed_price_data_copy']

    #Run hourly dispatch loop for given year
    for hour in tqdm(processed_price_data_copy.index, desc='hourly loop'):
        # year_integer = hour.year
        # month_integer = hour.month
        # day_integer = hour.day
        # hour_integer = hour.hour

        gbl.gbl_tracked_dict_time_variables['hour_counter'] =  0
        gbl.gbl_tracked_dict_time_variables['year_integer'] = hour.year
        gbl.gbl_tracked_dict_time_variables['month_integer'] =  hour.month
        gbl.gbl_tracked_dict_time_variables['day_integer'] = hour.day
        gbl.gbl_tracked_dict_time_variables['hour_integer'] = hour.hour

        #Increment cum hour counter
        gbl.gbl_tracked_dict_run_variables["cum_hour_integer"] += 1
        gbl.gbl_tracked_dict_run_variables_ideal["cum_hour_integer_ideal"] += 1
 

        #Check Dictionary Data
        # print_dict_as_table(gbl.gbl_tracked_dict_run_variables)
        # print("*" *90)
        # print_dict_as_table(gbl.gbl_tracked_dict_run_variables_ideal)


        # Pull Data from the current hour
        # Return updated values in gbl_tracked_dict_run_variables,gbl_tracked_dict_run_variables_ideal 
        # As well as current hour spot electricity price, nat gas price and carbon price
        current_hour_market_stats =  hourly_loop(
                hour)

        # Pass returned variables from hourly loop to functions
        row_data = create_row_data(
            hour,
            current_hour_market_stats,
            is_ideal = False)

        row_data_ideal = create_row_data(
            hour,
            current_hour_market_stats,
            is_ideal = True)
        
        # Append the row data to the respective lists
        operating_data_rows.append(row_data)
        #print(f" operating_data_rows: {operating_data_rows}")
        operating_data_ideal_rows.append(row_data_ideal)   
        #print(f" operating_data_ideal_rows: {operating_data_ideal_rows}")                  
        
        # At the ned of the hour all 'current' values have to passed their 'previous' value counter-parts
        # for the beginning of the next hour.
        create_update_end_of_hour_row_data(
                                is_ideal = False)

        
        create_update_end_of_hour_row_data(
                                is_ideal = True)

    # End of Hour Loop

    # Convert the lists of dictionaries to DataFrames
    operating_cost_data = pd.DataFrame(operating_data_rows)
    print(f" operating_cost_data: {operating_cost_data.head()}")
    operating_cost_data_ideal = pd.DataFrame(operating_data_ideal_rows)
    print(f" operating_cost_data: {operating_cost_data.head()}")

    return operating_cost_data, operating_cost_data_ideal, current_hour_market_stats


####################################################
# New Function to create annual data
def create_annual_data(operating_data, year, capacity, summary_period='annual'):
    """
    Function to create annual statistics based on the operating data.
    The summary_period parameter can be used to create weekly, monthly, quarterly, or annual summaries.
    """
    # Filter the data for the current year
    year_data = operating_data[operating_data['year'] == year]
    print(f"year_data: {year_data.columns}")

    # Initialize the annual_stats DataFrame
    annual_stats = pd.DataFrame({'YEAR': [year]})

    # Calculate and aggregate statistics
    annual_stats['STARTS'] = year_data['STARTS'].max()
    annual_stats['RECEIVED_POOL_PRICE'] = year_data['RECEIVED_POOL_PRICE'].mean()
    annual_stats['AVG_POOL_PRICE'] = year_data['POOL_PRICE'].mean()
    annual_stats['RECEIVED_POOL_PRICE_RATIO_TO_AVG_SPOT'] = annual_stats['RECEIVED_POOL_PRICE'] / annual_stats['AVG_POOL_PRICE']
    annual_stats['MW_PRODUCTION'] = year_data['MW_PRODUCTION'].sum()
    annual_stats['CAPACITY_FACTOR'] = annual_stats['MW_PRODUCTION'] / (capacity * 8760)
    annual_stats['STARTS'] = year_data['STARTS'] # remember this is cumulative variable
    annual_stats['COLD_STARTS'] = year_data['COLD_STARTS'].max()
    annual_stats['WARM_STARTS'] = year_data['WARM_STARTS'].max()
    annual_stats['HOT_STARTS'] = year_data['HOT_STARTS'].max()
    annual_stats['NONE_STARTS'] = year_data['NONE_STARTS'].max()
    annual_stats['STOPS'] = year_data['STOPS'].max()
    annual_stats['START_COST'] = year_data['START_COST'].sum()
    annual_stats['RUN_HOURS'] = year_data[year_data['RUN_HOURS'] == True]['RUN_HOURS'].count()
    annual_stats['RUN_RATE'] = annual_stats['RUN_HOURS'] / 8760
    annual_stats['REVENUE'] = (year_data['MW_PRODUCTION'] * year_data['RECEIVED_POOL_PRICE']).sum()
    annual_stats['TOTAL_COST_DOLLARS'] = year_data['TOTAL_COST_DOLLARS'].sum()
    annual_stats['OPERATING_MARGIN'] = annual_stats['REVENUE'] - annual_stats['TOTAL_COST_DOLLARS']

    return annual_stats
#############################################
def dictionary_datatype_for_df(operating_cost_data, is_ideal=False): 
    """ Function to ensure the correct data types for both actual and ideal operating cost data. """ 
    
    suffix = '_ideal' if is_ideal else '' 
    # Ensure the correct data types 
    operating_cost_data[f'DateTime'] = pd.to_datetime(operating_cost_data[f'DateTime']) 
    operating_cost_data[f'hour'] = operating_cost_data[f'hour'].astype(int) 
    operating_cost_data[f'year'] = operating_cost_data[f'year'].astype(int) 
    operating_cost_data[f'month'] = operating_cost_data[f'month'].astype(int) 
    operating_cost_data[f'STARTS'] = operating_cost_data[f'STARTS'].astype(int) 
    operating_cost_data[f'COLD_STARTS'] = operating_cost_data[f'COLD_STARTS'].astype(int) 
    operating_cost_data[f'WARM_STARTS'] = operating_cost_data[f'WARM_STARTS'].astype(int) 
    operating_cost_data[f'HOT_STARTS'] = operating_cost_data[f'HOT_STARTS'].astype(int) 
    operating_cost_data[f'NONE_STARTS'] = operating_cost_data[f'NONE_STARTS'].astype(int) 
    operating_cost_data[f'STOPS'] = operating_cost_data[f'STOPS'].astype(int) 
    operating_cost_data[f'START_STATUS'] = operating_cost_data[f'START_STATUS'].astype(str) 
    operating_cost_data[f'RUN_HOURS'] = operating_cost_data[f'RUN_HOURS'].astype(bool) 
    operating_cost_data[f'RUN_HOURS_CUM'] = operating_cost_data[f'RUN_HOURS_CUM'].astype(int) 
    operating_cost_data[f'CURRENT_HOUR_START'] = operating_cost_data[f'CURRENT_HOUR_START'].astype(bool) 
    operating_cost_data[f'CURRENT_HOUR_STOP'] = operating_cost_data[f'CURRENT_HOUR_STOP'].astype(bool) 
    operating_cost_data[f'PREVIOUS_HOUR_START'] = operating_cost_data[f'PREVIOUS_HOUR_START'].astype(bool) 
    operating_cost_data[f'PREVIOUS_HOUR_STOP'] = operating_cost_data[f'PREVIOUS_HOUR_STOP'].astype(bool) 
    operating_cost_data[f'UPTIME_COUNT'] = operating_cost_data[f'UPTIME_COUNT'].astype(int) 
    operating_cost_data[f'DOWNTIME_COUNT'] = operating_cost_data[f'DOWNTIME_COUNT'].astype(int) 
    operating_cost_data[f'CONSTRAINED_RAMP_UP'] = operating_cost_data[f'CONSTRAINED_RAMP_UP'].astype(bool) 
    operating_cost_data[f'CONSTRAINED_RAMP_DOWN'] = operating_cost_data[f'CONSTRAINED_RAMP_DOWN'].astype(bool) 
    operating_cost_data[f'MW_PRODUCTION'] = operating_cost_data[f'MW_PRODUCTION'].astype(int) 
    operating_cost_data[f'ACTUAL_EMISSIONS'] = operating_cost_data[f'ACTUAL_EMISSIONS'].astype(int) 
    operating_cost_data[f'TAXABLE_EMISSIONS'] = operating_cost_data[f'TAXABLE_EMISSIONS'].astype(int) 
    operating_cost_data[f'POOL_PRICE'] = operating_cost_data[f'POOL_PRICE'].astype(float) 
    operating_cost_data[f'NAT_GAS_PRICE'] = operating_cost_data[f'NAT_GAS_PRICE'].astype(float) 
    operating_cost_data[f'NAT_GAS_COST_MWH'] = operating_cost_data[f'NAT_GAS_COST_MWH'].astype(float) 
    operating_cost_data[f'NAT_GAS_COST_DOLLARS'] = operating_cost_data[f'NAT_GAS_COST_DOLLARS'].astype(float) 
    operating_cost_data[f'CARBON_TAX_DOLLARS_TONNE'] = operating_cost_data[f'CARBON_TAX_DOLLARS_TONNE'].astype(float) 
    operating_cost_data[f'CARBON_TAX_DOLLARS_MWH'] = operating_cost_data[f'CARBON_TAX_DOLLARS_MWH'].astype(float) 
    operating_cost_data[f'CARBON_TAX_DOLLARS'] = operating_cost_data[f'CARBON_TAX_DOLLARS'].astype(float) 
    operating_cost_data[f'VAR_COST'] = operating_cost_data[f'VAR_COST'].astype(float) 
    operating_cost_data[f'START_COST'] = operating_cost_data[f'START_COST'].astype(float) 
    operating_cost_data[f'STS_COST'] = operating_cost_data[f'STS_COST'].astype(float) 
    operating_cost_data[f'FOM_COST'] = operating_cost_data[f'FOM_COST'].astype(float) 
    operating_cost_data[f'TOTAL_COST_DOLLARS'] = operating_cost_data[f'TOTAL_COST_DOLLARS'].astype(float) 
    operating_cost_data[f'TOTAL_COST_MWH'] = operating_cost_data[f'TOTAL_COST_MWH'].astype(float) 
    operating_cost_data[f'IN_MERIT'] = operating_cost_data[f'IN_MERIT'].astype(bool) 
    operating_cost_data[f'RECEIVED_POOL_PRICE'] = operating_cost_data[f'RECEIVED_POOL_PRICE'].astype(float) 
    operating_cost_data[f'OPERATING_MARGIN'] = operating_cost_data[f'OPERATING_MARGIN'].astype(float) 
    
    return operating_cost_data
###################################################

def powergen_production_simulation(
            generator_list,
            years,
            run_type
                ):
        ################


        print("Calculate_Merit_Test called")
        
        #---------------------------------------------------------------
        # Step #1: Define variables to extract file and inpath locations
        #---------------------------------------------------------------
        for key1, value1 in gbl.gbl_tracked_loaded_dict_json_file_data["Input_Data"]["Price_Forecast"].items():
        
            input_file_attributes =value1['Input_File_Attributes']
            
            start_year = input_file_attributes['start_year']
            end_year = input_file_attributes['end_year']
            stochastic_seeds = input_file_attributes['stochastic_seeds']
            stochastic_seeds_used = input_file_attributes['stochastic_seeds_used']

            #---------------------------------------------------------------
            # Step #2: Define variables to extract file and outpath locations
            #---------------------------------------------------------------
            for key2, value2 in gbl.gbl_tracked_loaded_dict_json_file_data["Output_Data"]["Processed_Price_Forecast"].items():

                # Create path and file name for forecast seed data that was generated
                # which has the X Seeds of power nad the X seeds of hourly natural gas data
                output_file_attributes = value2['Output_File_Attributes']
                #Moved below
                # frcst_output_data_path = output_file_attributes['frcst_output_csv_file_path']
                # frcst_output_sub_folder = output_file_attributes['output_sub_folder']
                # frcst_file_name = output_file_attributes['consolidated_hourly']

                #Moved below
                # frcst_file_path = os.path.join(frcst_output_data_path, frcst_output_sub_folder, frcst_file_name)
                # power_natgas_consol_df = pd.read_csv(frcst_file_path)
            
                print(f"filename: {frcst_file_name}")
                print(f"file_path: {frcst_file_path}")
                print("conslidated data loaded")
                print(f"power_natgas_consol_df : {power_natgas_consol_df .head()}")

            # not used!!!!!
            gbl.gbl_frcst_output_csv_file_path = output_file_attributes['frcst_output_csv_file_path']

            #Ensure DateTime is in datetime format
            # power_natgas_consol_df ['DateTime'] = pd.to_datetime(power_natgas_consol_df ['DateTime'])
            # power_natgas_consol_df.set_index('DateTime', inplace=True)

            # set up variables for hourly reporting

            ##############################
            #PART C: Do Merit Test and Calculate Capacity Factors and Capture Prices
            ##############################

            #---------------------------------------------------------------
            # Step 3: Loop through generator list
            #---------------------------------------------------------------
            for current_generator in generator_list:
                print(f" Conducting Back-Casting Analysis for {current_generator}")

                capacity = float(gbl.gbl_tracked_powergen_dict['generation_sources'][current_generator]['plant_capacity_mw_net'])
                heat_rate = float(gbl.gbl_tracked_powergen_dict['generation_sources'][current_generator]['heat_rate'])
                vom_costs = float(gbl.gbl_tracked_powergen_dict['generation_sources'][current_generator]['vom_mwh'])
                start_up_cost = 0  #This is calculated in the hourly loop
                sts_cost = float(gbl.gbl_tracked_powergen_dict['generation_sources'][current_generator]['sts_mwh'])
                fom_cost = float(gbl.gbl_tracked_powergen_dict['generation_sources'][current_generator]['fixed_operating_costs_mwh'])
                run_hour_maintenance_target = float(gbl.gbl_tracked_powergen_dict['generation_sources'][current_generator]['run_hour_maintenance_target'])
                co2_emissions_intensity = float(gbl.gbl_tracked_powergen_dict['generation_sources'][current_generator]['emissions_intensity'])
                co2_reduction_target = float(gbl.gbl_tracked_powergen_dict['generation_sources'][current_generator]['co2_reduction_target'])
                min_down_time = float(gbl.gbl_tracked_powergen_dict['generation_sources'][current_generator]['min_down_time']) 
                min_up_time = float(gbl.gbl_tracked_powergen_dict['generation_sources'][current_generator]['min_up_time'])
                
                #---------------------------------------------------------------
                # Step 4:Determine what type of input data is being used for the
                # specific run type (Actuals, P-Value, Stochastic Seeds)
                 
                # Run Types define what type of data the capcity factors are being
                # simulated against.  
                #---------------------------------------------------------------
                # "Actuals" are single time series of power and natural gas
                if run_type == "Actuals":

                    # Over-ride seed variable values as Actuals are based on a single time-series
                    stochastic_seeds = 1
                    stochastic_seeds_used = 1
                    
                    # Create a copy of the historical hourly power and natural gas data
                    gbl.gbl_hist_processed_price_data = load_csv_with_datetime_index(r'C:\Users\kaczanor\OneDrive - Enbridge Inc\Documents\Python\EDC Hourly Capacity Factor Q2 2024\inputs\AB_Historical_Prices\merged_pool_price_data_2000_to_2024.csv')
                    print(f" gbl.gbl_hist_processed_nat_gas_price.head(): {gbl.gbl_hist_processed_nat_gas_price.head()}")
                    print(f" gbl.gbl_hist_processed_nat_gas_price.head(): {gbl.gbl_hist_processed_nat_gas_price.head()}")
                    #gbl.gbl_hist_processed_price_data['DateTime'] = pd.to_datetime(gbl.gbl_hist_processed_price_data['DateTime'])
                    #gbl.gbl_hist_processed_price_data['Year'] = gbl.gbl_hist_processed_price_data['DateTime'].dt.year
                    gbl.gbl_hist_processed_price_data.index = pd.to_datetime(gbl.gbl_hist_processed_price_data.index)
                    gbl.gbl_hist_processed_price_data['Year'] = gbl.gbl_hist_processed_price_data.index.year
                    print(f" gbl.gbl_processed_price_data.head(): {gbl.gbl_hist_processed_price_data.head()}")
                    #gbl.gbl_hist_processed_price_data.set_index('DateTime', inplace=True)
                    processed_price_data_copy = gbl.gbl_hist_processed_price_data[gbl.gbl_hist_processed_price_data['Year'].isin(years)].copy() 
                    print(f"processed_price_data_copy: {processed_price_data_copy.head()}")

                    # Create a copy of the historical processed_nat_gas_price
                    gbl.gbl_hist_processed_nat_gas_price = load_csv_with_datetime_index(r'C:\Users\kaczanor\OneDrive - Enbridge Inc\Documents\Python\EDC Hourly Capacity Factor Q2 2024\inputs\AB_Historical_Prices\merged_nat_gas_price_data_2000_to_2024.csv')
                    print(f" gbl.gbl_processed_price_data.head(): {gbl.gbl_hist_processed_price_data.head()}")
                    print(f" gbl.gbl_processed_nat_gas_price.head(): {gbl.gbl_hist_processed_nat_gas_price.head()}")
                    #gbl.gbl_hist_processed_nat_gas_price['DateTime'] = pd.to_datetime(gbl.gbl_hist_processed_nat_gas_price['DateTime'])
                    #gbl.gbl_hist_processed_nat_gas_price['Year'] = gbl.gbl_hist_processed_nat_gas_price['DateTime'].dt.year
                    gbl.gbl_hist_processed_nat_gas_price.index = pd.to_datetime(gbl.gbl_hist_processed_nat_gas_price.index)
                    gbl.gbl_hist_processed_nat_gas_price['Year'] = gbl.gbl_hist_processed_nat_gas_price.index.year
                    print(f" gbl.gbl_processed_nat_gas_price.head(): {gbl.gbl_hist_processed_nat_gas_price.head()}")
                    #gbl.gbl_hist_processed_nat_gas_price.set_index('DateTime', inplace=True)
                    processed_nat_gas_price_copy = gbl.gbl_hist_processed_nat_gas_price[gbl.gbl_hist_processed_nat_gas_price['Year'].isin(years)].copy()
                    print(f"processed_nat_gas_price_copy: {processed_nat_gas_price_copy.head()}")

                    #######################
                    # Determine the common date range
                    common_start_date = max(processed_price_data_copy.index.min(), processed_nat_gas_price_copy.index.min())
                    common_end_date = min(processed_price_data_copy.index.max(), processed_nat_gas_price_copy.index.max())
                    print(f"common_start_date: {common_start_date}")
                    print(f"common_end_date: {common_end_date}")
                    
                    

                    # Truncate both DataFrames to the common date range
                    processed_price_data_copy = processed_price_data_copy.loc[common_start_date:common_end_date]
                    processed_nat_gas_price_copy = processed_nat_gas_price_copy.loc[common_start_date:common_end_date]

                    print(f"Truncated processed_price_data_copy: {processed_price_data_copy.head()}")
                    print(f"Truncated processed_nat_gas_price_copy: {processed_nat_gas_price_copy.head()}")
                    #######################

                    # First check for duplicate indeces:duplicate_indices_price_data = processed_price_data_copy.index[processed_price_data_copy.index.duplicated()]
                    # Find duplicate indices in processed_price_data_copy
                    duplicate_indices_price_data = processed_price_data_copy.index[processed_price_data_copy.index.duplicated()]

                    if not duplicate_indices_price_data.empty:
                        print("Duplicate indices in processed_price_data_copy:")
                        print(duplicate_indices_price_data)
                    else:
                        print("No duplicate indices in processed_price_data_copy.")

                    # Find duplicate indices in processed_nat_gas_price_copy
                    duplicate_indices_nat_gas_data = processed_nat_gas_price_copy.index[processed_nat_gas_price_copy.index.duplicated()]

                    if not duplicate_indices_nat_gas_data.empty:
                        print("Duplicate indices in processed_nat_gas_price_copy:")
                        print(duplicate_indices_nat_gas_data)
                    else:
                        print("No duplicate indices in processed_nat_gas_price_copy.")

                    # Initialize dataframes to store operating costs and MW production
                    operating_cost_data = pd.DataFrame(index = gbl.gbl_hist_processed_price_data.index)
                    operating_cost_data_ideal = pd.DataFrame(index = gbl.gbl_hist_processed_price_data.index)
                
                # "P-Value" is also a single time series of power and natural gas but
                # its a forecast
                elif run_type == "P-Value":

                    # Over-ride seed variable values as Actuals are based on a single time-series
                    stochastic_seeds = 1
                    stochastic_seeds_used = 1
                    
                    # Load P_Value file
                    p50_power_data_path = output_file_attributes['P50_hourly_spot_electricity']
                    p50_natgas_data_path = output_file_attributes['P50_hourly_spot_natural_gas']
                    frcst_output_sub_folder = output_file_attributes['output_sub_folder']
                    #frcst_file_name = output_file_attributes['consolidated_hourly']
                    frcst_file_path = os.path.join(frcst_output_data_path, frcst_output_sub_folder, frcst_file_name)
                    power_natgas_consol_df = pd.read_csv(frcst_file_path)
                    
                    # Over-ride years as they are based on the range provided in the foreast
                    start_year = output_file_attributes['start_year']
                    end_year = output_file_attributes['end_year']
                    years = range(start_year, end_year + 1)

                    pass

                # "Stochastic Seeds" is forecaste data but is multiple time series data sets for power and natural gas
                # This allows for the simulatin to be done across an entire set of stochastic hourly data sets
                elif run_type == "Stochastic Seeds":
                    stochastic_seeds = input_file_attributes['stochastic_seeds']
                    stochastic_seeds_used = input_file_attributes['stochastic_seeds_used']

                    # Load consolidated forecast files with seeds
                    frcst_output_data_path = output_file_attributes['frcst_output_csv_file_path']
                    frcst_output_sub_folder = output_file_attributes['output_sub_folder']
                    frcst_file_name = output_file_attributes['consolidated_hourly']
                    frcst_file_path = os.path.join(frcst_output_data_path, frcst_output_sub_folder, frcst_file_name)
                    power_natgas_consol_df = pd.read_csv(frcst_file_path)

                    #Ensure DateTime is in datetime format
                    power_natgas_consol_df ['DateTime'] = pd.to_datetime(power_natgas_consol_df ['DateTime'])
                    power_natgas_consol_df .set_index('DateTime', inplace=True)
                    
                    # Over-ride years as they are based on the range provided in the foreast
                    start_year = min(power_natgas_consol_df.index.year)
                    end_year = max(power_natgas_consol_df.index.year)
                    years = range(start_year, end_year + 1)

                    pass

                # Initialize a list for collecting row data
                operating_cost_data_rows = []
                operating_cost_data_ideal_rows = []

                #OLD
                # cf_limit = gcf_limit
                # starting_index = gstarting_index
                # annual_index_rate = gannual_index_rate #2%

                #OLD
                # Select strategy
                # STRATEGY_CF_CAP = gSTRATEGY_CF_CAP
                # STRATEGY_PERFECT_FORESIGHT = gSTRATEGY_PERFECT_FORESIGHT
                # STRATEGY_PREDICTIVE_BIDDING = gSTRATEGY_PREDICTIVE_BIDDING
                # strategy = gstrategy

                ##################################################################
                #---------------------------------------------------------
        
                # Initialize a dictionary to hold annual capacity factors and capture prices for each seed
                # #OLD
                # hourly_bids = {}
                # capacity_factors = {}
                # capture_prices = {}
                # #new
                # natgas_capture_prices = {}

                # #Create lists to store monthly capacity factors and bids
                # monthly_bids = {}
                # monthly_capacity_factors = {}
                # monthly_capture_prices = {}
                # #new
                # monthly_natgas_capture_prices = {}

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

                #---------------------------------------------------------------
                # Step 5: Create ACTUAL hourly operating data variables for the current generator
                # Initialize running variables prior to entering the hourly loop
                # There are two sets of variables: 
                #   one set for the actual plant (with start-up costs) and 
                #   one set for the ideal plant (ignoring start-up costs)
                #---------------------------------------------------------------
                ##################################
                # Actual and Ideal plant run-time variables
                ##################################
                # Start in Down Time Mode with pending cold start-up
                # Do this by adding 1 hour to the cold start threshold

                previous_down_time_count = float(gbl.gbl_tracked_powergen_dict['generation_sources'][current_generator]['start_up_cost']['cold_start']['cold_start_determination_hrs'])
                current_down_time_count = 1 + previous_down_time_count
                previous_up_time_count = 0
                current_up_time_count = 0 

                previous_down_time_count_ideal = previous_down_time_count
                current_down_time_count_ideal = 1 + previous_down_time_count_ideal
                previous_up_time_count_ideal = 0
                current_up_time_count_ideal = 0 

                previous_hour_cold_start_count = 0 #new
                previous_hour_cold_start_count_ideal = 0 #new

                previous_hour_warm_start_count = 0 #new
                previous_hour_warm_start_count_ideal = 0 #new

                previous_hour_hot_start_count = 0 #new
                previous_hour_hot_start_count_ideal = 0 #new

                previous_hour_none_start_count = 0  #new
                previous_hour_none_start_count_ideal = 0 #new

                #-------------------------------
                #Previous Period (at start of simulation) 
                #-------------------------------
                try: 
                    cold_start_threshold = float(gbl.gbl_tracked_powergen_dict['generation_sources'][current_generator]['start_up_cost']['cold_start']['cold_start_determination_hrs']) 
                    warm_start_threshold = float(gbl.gbl_tracked_powergen_dict['generation_sources'][current_generator]['start_up_cost']['warm_start']['warm_start_determination_hrs']) 
                    hot_start_threshold = float(gbl.gbl_tracked_powergen_dict['generation_sources'][current_generator]['start_up_cost']['hot_start']['hot_start_determination_hrs']) 
                
                    if current_down_time_count >= cold_start_threshold:
                        previous_start_status = 'cold_start'
                        previous_hour_stop = True #forced stop
                        previous_hour_start = False #forced stop
                        #previous_hour_cold_start_count = 0 #new

                        previous_start_status_ideal = 'cold_start'
                        previous_hour_stop_ideal = True
                        previous_hour_start_ideal = False
                        #previous_hour_cold_start_count_ideal = 0 

                    elif current_down_time_count >= warm_start_threshold and current_down_time_count < cold_start_threshold:
                        previous_start_status ='warm_start' 
                        previous_hour_stop = True #forced stop
                        previous_hour_start = False #forced stop
                        #previous_hour_warm_start_count= 0 #new

                        previous_start_status_ideal ='warm_start' 
                        previous_hour_stop_ideal = True
                        previous_hour_start_ideal = False
                        #previous_hour_warm_start_count_ideal = 0 #new

                    elif current_down_time_count < warm_start_threshold:
                        previous_start_status = 'hot_start' 
                        previous_hour_stop = True #forced stop
                        previous_hour_start = False #forced stop
                        #previous_hour_hot_start_count = 0 #new

                        previous_start_status_ideal = 'hot_start' 
                        previous_hour_stop_ideal = True #forced stop
                        previous_hour_start_ideal = False #forced stop
                        #previous_hour_hot_start_count_ideal = 0 #new

                    print(f" start status: {previous_start_status}")
                except Exception as e: 
                    # Error handling 
                    print(f" start status error: {e}")

                #-------------------------------
                # Current Period - Actual 
                #-------------------------------
                # Not known yet as this is set within the hourly loop
                current_hour_start = None 
                current_hour_stop = None
                is_running = False #Changed from True
                is_running_counter = 0
                #Initialize counters
                current_up_time_count = 0
                number_of_stops = 0 #ignores previous period stop in counter
                number_of_starts = 0 #ignores previous period stop in counter
                cum_hour_integer = 1 # Start at 1
                current_hour_cold_start_count = 0 #new
                current_hour_warm_start_count = 0 #new
                current_hour_hot_start_count = 0 #new
                current_hour_none_start_count = 0 #new
                #Ramping Constraints
                constrained_ramp_up = None
                constrained_ramp_down = None

 
                # Create IDEAL operating data for the current generator
                #-------------------------------
                # Current Period - Ideal
                #-------------------------------
                # Not known yet as this is set within the hourly loop
                current_hour_start_ideal = current_hour_start
                current_hour_stop_ideal = current_hour_stop 
                is_running_ideal = is_running
                is_running_counter_ideal = 0
                #Initialize counters
                current_up_time_count_ideal = current_up_time_count
                number_of_stops_ideal = number_of_stops #ignores previous period stop in counter
                number_of_starts_ideal = number_of_starts #ignores previous period stop in counter
                cum_hour_integer_ideal = cum_hour_integer # Start at 1
                current_hour_cold_start_count_ideal = 0 #new
                current_hour_warm_start_count_ideal = 0 #new
                current_hour_hot_start_count_ideal = 0 #new
                current_hour_none_start_count_ideal = 0 #new
                #Ramping Constraints
                constrained_ramp_up_ideal = constrained_ramp_up
                constrained_ramp_down_ideal = constrained_ramp_down

                #################################
                # Common Variables
                #################################
                start_up_cost_amortization_hours = 10 # number of hours to amortize start-up costs
                cum_hour_integer = 0 # Start at 0
                cum_hour_integer_ideal = 0 # Start at 0
                hour_counter = 0
                year_integer = None 
                month_integer = None
                day_integer = None 
                hour_integer = None
                hour = None

                #---------------------------------------------------------------
                # Step 6:
                # pass all variables to a collection of dictionaries to pass back and forth to functions
                # Pass the variables to lists to make them easier to understand
                # later in the code
                #---------------------------------------------------------------
                # gbl_tracked_dict_time_variables
                # These are counters variables for time keeping
                gbl.gbl_tracked_dict_time_variables["hour_counter"] = hour_counter
                gbl.gbl_tracked_dict_time_variables["year_integer"] = year_integer
                gbl.gbl_tracked_dict_time_variables["month_integer"] = month_integer
                gbl.gbl_tracked_dict_time_variables["day_integer"] = day_integer
                gbl.gbl_tracked_dict_time_variables["hour_integer"] = hour_integer

                # gbl_tracked_dict_general_data
                # These are mix of data_frames, dictionaries, and column headers text
                print(f" processed_price_data_copy: {processed_price_data_copy}")
                gbl.gbl_tracked_dict_general_data["processed_price_data_copy"] = processed_price_data_copy
                gbl.gbl_tracked_dict_general_data["processed_nat_gas_price_copy"] = processed_nat_gas_price_copy
                gbl.gbl_tracked_dict_general_data["gbl_natgas_primary_data_col"] = gbl.gbl_natgas_primary_data_col
                gbl.gbl_tracked_dict_general_data["gbl_pool_price_primary_data_col"] = gbl.gbl_pool_price_primary_data_col
                gbl.gbl_tracked_dict_general_data["gbl_carbon_tax_annual_dict"] = gbl.gbl_carbon_tax_annual_dict
                gbl.gbl_tracked_dict_general_data["gbl_tracked_powergen_dict"] = gbl.gbl_tracked_powergen_dict
            
                # gbl_tracked_dict_generator_specific
                # These are generator operating variables
                gbl.gbl_tracked_dict_generator_specific["current_generator"] = current_generator
                gbl.gbl_tracked_dict_generator_specific["capacity"] = capacity
                gbl.gbl_tracked_dict_generator_specific["heat_rate"] = heat_rate
                gbl.gbl_tracked_dict_generator_specific["vom_costs"] = vom_costs
                gbl.gbl_tracked_dict_generator_specific["start_up_cost"] = start_up_cost
                gbl.gbl_tracked_dict_generator_specific["sts_cost"] = sts_cost
                gbl.gbl_tracked_dict_generator_specific["fom_cost"] = fom_cost
                gbl.gbl_tracked_dict_generator_specific["co2_emissions_intensity"] = co2_emissions_intensity
                gbl.gbl_tracked_dict_generator_specific["co2_reduction_target"] = co2_reduction_target
                gbl.gbl_tracked_dict_generator_specific["run_hour_maintenance_target"] = run_hour_maintenance_target
                gbl.gbl_tracked_dict_generator_specific["min_down_time"] = min_down_time
                gbl.gbl_tracked_dict_generator_specific["min_up_time"] = min_up_time
                gbl.gbl_tracked_dict_generator_specific["total_cost"] = None
                gbl.gbl_tracked_dict_generator_specific["start_up_cost_amortization_hours"] = start_up_cost_amortization_hours


                # For runs where start costs ARE NOT factored into hourly bid
                # These are run-time variables that track starts/stops/ramps etc
                # that drive the operatabilty of the generator subject to to the 
                # technical contraints of the technology
                gbl.gbl_tracked_dict_run_variables["is_running"] = is_running
                gbl.gbl_tracked_dict_run_variables["is_running_counter"] = is_running_counter
                gbl.gbl_tracked_dict_run_variables["current_down_time_count"] = current_down_time_count
                gbl.gbl_tracked_dict_run_variables["current_up_time_count"] = current_up_time_count
                gbl.gbl_tracked_dict_run_variables["previous_down_time_count"] = previous_down_time_count
                gbl.gbl_tracked_dict_run_variables["previous_up_time_count"] = previous_up_time_count
                gbl.gbl_tracked_dict_run_variables["number_of_starts"] = number_of_starts
                gbl.gbl_tracked_dict_run_variables["number_of_stops"] = number_of_stops
                gbl.gbl_tracked_dict_run_variables["previous_hour_start"] = previous_hour_start
                gbl.gbl_tracked_dict_run_variables["previous_hour_stop"] = previous_hour_stop
                gbl.gbl_tracked_dict_run_variables["current_hour_start"] = current_hour_start
                gbl.gbl_tracked_dict_run_variables["current_hour_stop"] = current_hour_stop
                gbl.gbl_tracked_dict_run_variables["cum_hour_integer"] = cum_hour_integer
                gbl.gbl_tracked_dict_run_variables["constrained_ramp_up"] = constrained_ramp_up
                gbl.gbl_tracked_dict_run_variables["constrained_ramp_down"] = constrained_ramp_down
                gbl.gbl_tracked_dict_run_variables["previous_hour_cold_start_count"] = previous_hour_cold_start_count
                gbl.gbl_tracked_dict_run_variables["previous_hour_warm_start_count"] = previous_hour_warm_start_count
                gbl.gbl_tracked_dict_run_variables["previous_hour_hot_start_count"] = previous_hour_hot_start_count
                gbl.gbl_tracked_dict_run_variables["previous_hour_none_start_count"] = previous_hour_none_start_count
                gbl.gbl_tracked_dict_run_variables["current_hour_cold_start_count"] = current_hour_cold_start_count
                gbl.gbl_tracked_dict_run_variables["current_hour_warm_start_count"] = current_hour_warm_start_count
                gbl.gbl_tracked_dict_run_variables["current_hour_hot_start_count"] = current_hour_hot_start_count
                gbl.gbl_tracked_dict_run_variables["current_hour_none_start_count"] = current_hour_none_start_count
                
                # For runs where start costs ARE factored into hourly bid
                # Poorer dispatch
                gbl.gbl_tracked_dict_run_variables_ideal["is_running_ideal"] = is_running_ideal
                gbl.gbl_tracked_dict_run_variables_ideal["is_running_counter_ideal"] = is_running_counter_ideal
                gbl.gbl_tracked_dict_run_variables_ideal["current_down_time_count_ideal"] = current_down_time_count_ideal
                gbl.gbl_tracked_dict_run_variables_ideal["current_up_time_count_ideal"] = current_up_time_count_ideal
                gbl.gbl_tracked_dict_run_variables_ideal["previous_down_time_count_ideal"] = previous_down_time_count_ideal
                gbl.gbl_tracked_dict_run_variables_ideal["previous_up_time_count_ideal"] = previous_up_time_count_ideal
                gbl.gbl_tracked_dict_run_variables_ideal["number_of_starts_ideal"] = number_of_starts_ideal
                gbl.gbl_tracked_dict_run_variables_ideal["number_of_stops_ideal"] = number_of_stops_ideal
                gbl.gbl_tracked_dict_run_variables_ideal["previous_hour_start_ideal"] = previous_hour_start_ideal
                gbl.gbl_tracked_dict_run_variables_ideal["previous_hour_stop_ideal"] = previous_hour_stop_ideal
                gbl.gbl_tracked_dict_run_variables_ideal["current_hour_start_ideal"] = current_hour_start_ideal
                gbl.gbl_tracked_dict_run_variables_ideal["current_hour_stop_ideal"] = current_hour_stop_ideal
                gbl.gbl_tracked_dict_run_variables_ideal["cum_hour_integer_ideal"] = cum_hour_integer_ideal
                gbl.gbl_tracked_dict_run_variables_ideal["constrained_ramp_up_ideal"] = constrained_ramp_up_ideal
                gbl.gbl_tracked_dict_run_variables_ideal["constrained_ramp_down_ideal"] = constrained_ramp_down_ideal
                gbl.gbl_tracked_dict_run_variables_ideal["previous_hour_cold_start_count_ideal"] = previous_hour_cold_start_count_ideal
                gbl.gbl_tracked_dict_run_variables_ideal["previous_hour_warm_start_count_ideal"] = previous_hour_warm_start_count_ideal
                gbl.gbl_tracked_dict_run_variables_ideal["previous_hour_hot_start_count_ideal"] = previous_hour_hot_start_count_ideal
                gbl.gbl_tracked_dict_run_variables_ideal["previous_hour_none_start_count_ideal"] = previous_hour_none_start_count_ideal
                gbl.gbl_tracked_dict_run_variables_ideal["current_hour_cold_start_count_ideal"] = current_hour_cold_start_count_ideal
                gbl.gbl_tracked_dict_run_variables_ideal["current_hour_warm_start_count_ideal"] = current_hour_warm_start_count_ideal
                gbl.gbl_tracked_dict_run_variables_ideal["current_hour_hot_start_count_ideal"] = current_hour_hot_start_count_ideal
                gbl.gbl_tracked_dict_run_variables_ideal["current_hour_none_start_count_ideal"] = current_hour_none_start_count_ideal

                print_dict_as_table(gbl.gbl_tracked_dict_time_variables)
                print("*" *90)
                print_dict_as_table(gbl.gbl_tracked_dict_general_data)
                print("*" *90)
                print_dict_as_table(gbl.gbl_tracked_dict_generator_specific)
                print("*" *90)
                print_dict_as_table(gbl.gbl_tracked_dict_run_variables)
                print("*" *90)
                print_dict_as_table(gbl.gbl_tracked_dict_run_variables_ideal)
                print("*" *90)

                #---------------------------------------------------------------
                # Step 7:  Run Seed Loop

                # This outer loop loops through the stochastic seeds for each year
                # If P50 values or Historical Data is being used then there is really
                # only 1 "seed" value and this outer loop becomes redundant.  But when
                # seed data is being used, all the stats from all the seeds are stored 
                # summarized to create P_values for those variables
                #---------------------------------------------------------------

                #Initialize objects to track/aggregate stats across all seeds
                all_seeds_hourly_stats = []
                all_seeds_annual_stats = []
                all_seeds_annual_stats_ideal = []

                for seed in tqdm(range(1, stochastic_seeds_used + 1)):
                    # Create list object for current seed data
                    seed_hourly_data = []
                    seed_hourly_data_ideal = []
                    seed_annual_data = []
                    seed_annual_data_ideal = []
                
                    #---------------------------------------------------------------
                    # Step 8: Annual/Hourly Loop
                    operating_cost_data, operating_cost_data_ideal, current_hour_market_stats = create_operating_data(seed)

                    print(f"operating_cost_data: {operating_cost_data}")
                    print(f"operating_cost_data.columns: {operating_cost_data.columns}")
                    print(f"operating_cost_data_ideal.columns: {operating_cost_data_ideal.columns}")

                    # Collect hourly data for teh current seed
                    seed_hourly_data.append(operating_cost_data)
                    seed_hourly_data_ideal.append(operating_cost_data_ideal)
                    #---------------------------------------------------------------
                    
                    # Create annual_data for both the Actual and Ideal Cases
                    # Initialize an empty DataFrame to accumulate annual statistics
                    annual_stats_all_years = pd.DataFrame()
                    annual_stats_all_years_ideal = pd.DataFrame()

                    # Loop through each year in the current seed to calculate annual statistics for that seed
                    print(f"years: {years}")
                    for year in years:
                        # Generate annual statistics for actual and ideal data
                        annual_stats = create_annual_data(operating_cost_data, year, capacity)
                        #print(f"annual_stats: {annual_stats}.head(10)")
                        
                        annual_stats_ideal = create_annual_data(operating_cost_data_ideal, year, capacity)
                        #print(f"annual_stats_ideal: {annual_stats_ideal.head(10)}")
                        

                        # Append stats to the annual seed data
                        seed_annual_data.append(annual_stats)
                        seed_annual_data_ideal.append(annual_stats_ideal)

                        # Append the annual statistics for the current year to the master DataFrame
                        annual_stats_all_years = pd.concat([annual_stats_all_years, annual_stats])
                        #print(f"annual_stats_all_years: {annual_stats_all_years}")

                        annual_stats_all_years_ideal = pd.concat([annual_stats_all_years_ideal, annual_stats_ideal])
                        #print(f"annual_stats_all_years_ideal: {annual_stats_all_years_ideal}")

                        # Add capacity factor efficiency column to annual_stats AFTER the annual stats are calculated
                        # for both annual_stats_all_years and annual_stats_all_years_ideal for the given year
                        annual_stats_all_years['CAPACITY_FACTOR_EFFICIENCY'] = annual_stats['CAPACITY_FACTOR'] /annual_stats_ideal['CAPACITY_FACTOR']

                    print(f"annual_stats_all_years.columns: {annual_stats_all_years.columns}")
                    print(f"annual_stats_all_years_ideal.columns: {annual_stats_all_years_ideal.columns}")

                    #Reorder annual_stata data frames and format column headers for Excel
                    annual_stats_all_years = annual_stats_all_years[
                        ['YEAR', 'RECEIVED_POOL_PRICE',	'AVG_POOL_PRICE', 'RECEIVED_POOL_PRICE_RATIO_TO_AVG_SPOT', \
                            'MW_PRODUCTION', 'CAPACITY_FACTOR', 'CAPACITY_FACTOR_EFFICIENCY', 'STARTS', 'COLD_STARTS', 'WARM_STARTS', 'HOT_STARTS', 'NONE_STARTS', 'STOPS', \
                                'START_COST', 'RUN_HOURS', 'RUN_RATE', 'REVENUE', 'TOTAL_COST_DOLLARS', 'OPERATING_MARGIN']]
                    annual_stats_all_years.columns = replace_underscores_with_spaces_in_list(annual_stats_all_years.columns)
                    print(f" annual_stats_all_years.columns{annual_stats_all_years.columns}")
                    print(f" annual_stats_all_years: {annual_stats_all_years}")

                    annual_stats_all_years_ideal = annual_stats_all_years_ideal[
                        ['YEAR', 'RECEIVED_POOL_PRICE',	'AVG_POOL_PRICE', 'RECEIVED_POOL_PRICE_RATIO_TO_AVG_SPOT', \
                            'MW_PRODUCTION', 'CAPACITY_FACTOR', 'STARTS', 'COLD_STARTS', 'WARM_STARTS', 'HOT_STARTS', 'NONE_STARTS', 'STOPS', \
                                'START_COST', 'RUN_HOURS', 'RUN_RATE', 'REVENUE', 'TOTAL_COST_DOLLARS', 'OPERATING_MARGIN']]
                    annual_stats_all_years_ideal.columns = replace_underscores_with_spaces_in_list(annual_stats_all_years_ideal.columns)
                    print(f" annual_stats_all_years_ideal.columns{annual_stats_all_years_ideal.columns}")
                    print(f" annual_stats_all_years_ideal: {annual_stats_all_years_ideal}")

                    # Append seed_specific stats to global aggregate stats
                    all_seeds_hourly_stats.append({'seed':seed, 'hourly_data': seed_hourly_data})
                    all_seeds_annual_stats.append({'seed':seed, 'hourly_data': annual_stats_all_years})
                    all_seeds_annual_stats_ideal.append({'seed':seed, 'hourly_data': annual_stats_all_years_ideal})

                    ################################
                    # Ensure the correct data types for operating_cost_data and operating_cost_data_ideal
                    operating_cost_data = dictionary_datatype_for_df(operating_cost_data, is_ideal = False)
                    operating_cost_data_ideal = dictionary_datatype_for_df(operating_cost_data_ideal, is_ideal = True)

                    # Debug print to check the data types and values
                    print(operating_cost_data.dtypes)
                    print(operating_cost_data.head())

                    print(operating_cost_data_ideal.dtypes)
                    print(operating_cost_data_ideal.head())

                    ########################
                    # Save the operating cost data for the current generator


                    # Save Operating Cost Data table as CSV File
                    filename = f'operating_cost_data_{current_generator}.csv'
                    save_dataframe_to_csv(operating_cost_data, filename)

                    filename = f'operating_cost_data_ideal_{current_generator}.csv'
                    save_dataframe_to_csv(operating_cost_data_ideal, filename)

                    ########################
                    # CSV Files
                    #Save annual_stats_all_years files as CSV File and to Excel formatted template
                    filename = f'annual_stats_all_years_{current_generator}.csv'
                    save_dataframe_to_csv(annual_stats_all_years, filename)

                    #Save annual_stats_all_years_ideal files as CSV File and to Excel formatted template
                    filename = f'annual_stats_all_years_ideal_{current_generator}.csv'
                    save_dataframe_to_csv(annual_stats_all_years_ideal, filename)

                    ############################
                    # Load the Excel templates
                    ############################
                    # Monthly/Annual P_data file
                    
                    template_path = r'C:\Users\kaczanor\OneDrive - Enbridge Inc\Documents\Python\EDC Hourly Capacity Factor Q2 2024\template_excel_output_files\annual_stats_all_years_capacity_factor.xlsx'
                    # moved to inside function
                    #workbook = load_workbook(template_path)

                    # Prep the output path
                    output_path = r'C:\Users\kaczanor\OneDrive - Enbridge Inc\Documents\Python\EDC Hourly Capacity Factor Q2 2024\outputs\excel_data'
                    output_filename = f"annual_stats_all_years_capacity_factor_{current_generator}.xlsx"
                    
                    # Save the 2x data frames for the ideal and base results into 2x worksheets in the same file
                    # Save DataFrame to Excel template and rename the worksheet
                    worksheet_name = 'Actual_Annual_Results'
                    new_worksheet_name = f"Actual_{current_generator}"
                    print(f" annual_stats_all_years: {annual_stats_all_years.head(25)}")
                    output_path = r'C:\Users\kaczanor\OneDrive - Enbridge Inc\Documents\Python\EDC Hourly Capacity Factor Q2 2024\outputs\excel_data'
                    save_dataframe_to_excel_template(annual_stats_all_years, output_path, template_path, output_filename, worksheet_name, new_worksheet_name)

                    # Save another DataFrame to the same Excel template and rename the worksheet
                    worksheet_name = 'Ideal_Annual_Results'
                    new_worksheet_name = f"Ideal_{current_generator}"
                    print(f" annual_stats_all_years_ideal: {annual_stats_all_years_ideal.head(25)}")
                    save_dataframe_to_excel_template(annual_stats_all_years_ideal, output_path, template_path, output_filename, worksheet_name, new_worksheet_name)

                    ##################################################################

                    # End of Seed Loop
                
                # After processing all seeds, aggregate data across seeds
                # Combine hourly data across seeds


                # Combine annual data across seeds


                # Save combined stats to files
            
        return 
