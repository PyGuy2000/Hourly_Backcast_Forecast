import sys
import os

import pandas as pd
from pprint import pprint

from library.enb_load_calcluations import review_enb_load
from library.class_objects.other_classes.classes import TrackedDict, ForecastFile

#def calculate_substation_fraction(contract_capacity_dts, estimate_for_rate_sts, contract_capacity_other, EstimateType, OtherParticipant, participant_type):
def calculate_substation_fraction(DTS, STS, OtherMarketParticipant, EstimateType, OtherParticipant,participant_type):
    
    def calculate_value(contract_capacity_dts, estimate_for_rate_sts, contract_capacity_other, EstimateType, OtherParticipant, participant_type):
        # Calculate the total sum based on the conditions
        total_sum = contract_capacity_dts + (estimate_for_rate_sts if EstimateType in ["STS Only", "DTS and STS"] else 0) + \
            (contract_capacity_other if OtherParticipant == "Yes" else 0)
        
        if participant_type == "DTS":
            if EstimateType == "STS Only" or total_sum == 0:
                return "NA"
            try:
                result = contract_capacity_dts / total_sum
            except ZeroDivisionError:
                result = 1
            return result

        elif participant_type == "STS":
            if EstimateType == "DTS Only" or total_sum == 0:
                return "NA"
            try:
                result = estimate_for_rate_sts / total_sum
            except ZeroDivisionError:
                result = 1
            return result

        elif participant_type == "Other Market Participant":
            if OtherParticipant == "No" or total_sum == 0:
                return "NA"
            try:
                result = contract_capacity_other / total_sum
            except ZeroDivisionError:
                result = 1
            return result

    DTS_value = calculate_value(DTS, STS, OtherMarketParticipant, EstimateType, OtherParticipant, "DTS")
    STS_value = calculate_value(DTS, STS, OtherMarketParticipant, EstimateType, OtherParticipant, "STS")
    OtherMarketParticipant_value = calculate_value(DTS, STS, OtherMarketParticipant, EstimateType, OtherParticipant, "Other Market Participant")

    #return calculate_value(contract_capacity_dts, estimate_for_rate_sts, contract_capacity_other, EstimateType, OtherParticipant, participant_type)
    return DTS_value, STS_value, OtherMarketParticipant_value

def clean_and_convert(value):
    if pd.isna(value):
        return value  # Return NaN as is
    # Remove dollar signs, commas, and whitespace
    value = str(value).replace('$', '').replace(',', '').replace(' ', '')
    # Handle negative values represented with parentheses
    if '(' in value and ')' in value:
        value = '-' + value.replace('(', '').replace(')', '')
    # Remove percentage signs and convert to float
    if '%' in value:
        value = value.replace('%', '')
        return float(value) / 100.0
    return float(value)

def lookup_value(csv_file, aeso_tariff, row_header, sub_header):
    """
    Look up a value in a CSV file based on the specified column and row headers.
    
    Parameters:
    - csv_file (str): Path to the CSV file.
    - aeso_tariff (str): The column header to look up.
    - row_header (str): The primary row header to filter.
    - sub_header (str): The secondary row header to filter.
    
    Returns:
    - value: The value found at the intersection of the specified column and row headers.
    """
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file)
    
    # Clean and convert the 'AESO 2024' column
    df[aeso_tariff] = df[aeso_tariff].apply(clean_and_convert)

    # Filter the DataFrame to get the specific row
    filtered_row = df[(df['Tariff'] == row_header) & (df['None'] == sub_header)]
    
    # Check if the filtered row is empty
    if filtered_row.empty:
        raise ValueError("No matching row found for the specified headers.")
    
    # Extract the value from the specific column
    value = filtered_row[aeso_tariff].values[0]
    
    return value


def safe_sum(*args):
    """
    Sums the provided arguments, ignoring any that are None.
    
    Parameters:
    - *args: A variable number of numerical arguments.
    
    Returns:
    - The sum of the provided arguments, excluding None values.
    """
    return sum(arg for arg in args if arg is not None)



#########################
def create_transmission_cost(
            csv_file, 
            aeso_tariff,
            EstimateType,
            OtherParticipant,
            PrimaryServiceCredit,
            is_this_regulated_generating_unit,
            RiderC,
            RiderE,
            RiderF,
            RiderJ,
            contract_capacity_dts,
            estimate_for_rate_sts,
            contract_capacity_other

):

    # Inputs
    #csv_file = r'C:\Users\kaczanor\OneDrive - Enbridge Inc\Documents\Python\AB Electricity Sector Stats\input_data\aeso_transmission_tariff_data\aeso_tariff_appendix_one_bill_estimator.csv'
    #csv_file = r'C:\Users\kaczanor\OneDrive - Enbridge Inc\Documents\Python\EDC Hourly Capacity Factor Q2 2024\inputs\AESO_Tariff_Data\aeso_tariff_appendix_one_bill_estimator.csv'
    #aeso_tariff = 'AESO 2024'

    # # ESTIMATES
    # EstimateType = 'DTS Only'  # 'DTS Only, STS Only, DTS and STS' (a) Is estimate for Rate DTS, Rate STS or both?
    # OtherParticipant = False # (b) Any other market participant at substation?
    # PrimaryServiceCredit = False  # (c) Does Primary Service Credit apply to service?
    # is_this_regulated_generating_unit = False  # (d) Is this a regulated generating unit within its base life?
    # RiderC = False  # (e) Include Deferral Account Adjustment Rider C?
    # RiderE = False  # (f) Include Losses Calibration Factor Rider E?
    # RiderF = False  # (g) Include Balancing Pool Consumer Allocation Rider F?
    # RiderJ = False  # (h) Include Wind Forecasting Service Cost Recovery Rider J?
    # contract_capacity_dts = 20.0
    # estimate_for_rate_sts = 0.0
    # contract_capacity_other = 0.0 

    # Calculate substation fraction for DTS
    DTS_substation_fraction = calculate_substation_fraction(contract_capacity_dts, estimate_for_rate_sts, contract_capacity_other, EstimateType, OtherParticipant, "DTS")
    print("DTS Substation Fraction:", DTS_substation_fraction)

    # Calculate substation fraction for STS
    STS_substation_fraction = calculate_substation_fraction(contract_capacity_dts, estimate_for_rate_sts, contract_capacity_other, EstimateType, OtherParticipant, "STS")
    print("STS Substation Fraction:", STS_substation_fraction)

    # Calculate substation fraction for Other Market Participant
    OtherMarketParticipant_substation_fraction = calculate_substation_fraction(contract_capacity_dts, estimate_for_rate_sts, contract_capacity_other, EstimateType, OtherParticipant, "Other Market Participant")
    print("Other Market Participant Substation Fraction:", OtherMarketParticipant_substation_fraction)

    # BILLING DETERMINANTS RATE DTS
    contract_capacity_dts_copy = contract_capacity_dts  # (i) MW Contract capacity:
    substation_fraction_dts = DTS_substation_fraction  # (j) Substation fraction (SF):
    highest_metered_demand_in_settlement_period_dts = 20.0  # (k) MW Highest metered demand in settlement period:
    coincidence_factor_with_15_minute_system_peak_dts = 0.75  # (l)%  Coincidence factor with 15-minute system peak:
    coincident_metered_demand_dts = 15.0  # (m) MW Coincident metered demand:
    highest_metered_demand_in_previous_24_months_dts = 20.0  # (n) MW Highest metered demand in previous 24 months:
    billing_capacity_dts = max(0.90 * contract_capacity_dts_copy, highest_metered_demand_in_settlement_period_dts, 0.90 * highest_metered_demand_in_previous_24_months_dts)  # (o) MW Billing cap’y (highest of 90%×(i), (k) or 90%×(n)):
    load_or_capacity_factor_dts = 0.65  # (p) % Load or capacity factor:
    hours_in_month_dts = 730  # (q) hrs Hours in month:
    metered_energy_dts = highest_metered_demand_in_settlement_period_dts * load_or_capacity_factor_dts *  hours_in_month_dts # (r) MWh Metered energy:
    pool_price_dts = 83.42  # (s) $/MWh Pool price:
    or_charge_estimate_percentage_of_pool_price_dts = lookup_value(csv_file, aeso_tariff, 'Operating Reserve Charge', 'Multiplier')   # (t) % of pool price for OR charge estimate:
    apparent_power_difference_when_pf_less_than_90_percent_dts = 0.0  # (u) Apparent power difference (when PF < 90%):
    loss_factor_dts = None  # (v) L% oss factor:
    regulated_generating_unit_mw_dts = None  # (w) Regulated generating unit MW:
    quarterly_rider_c_charge_credit_dts = None  # (x) Quarterly Rider C charge (credit):
    quarterly_rider_e_calibration_factor_charge_credit_dts = None  # (y) Quarterly Rider E calibrat’n factor charge (credit):
    balancing_pool_rider_f_charge_credit_dts = lookup_value(csv_file, aeso_tariff,'Rider F', 'Rider F')  # (z) $/MWh Balancing Pool Rider F charge (credit):
    wind_forecasting_cost_recovery_rider_j_charge_dts = None  # (aa) $/Mh Wind Forecasting Cost Recovery Rider J charge:

    # BILLING DETERMINANTS RATE STS
    estimate_for_rate_sts = False
    contract_capacity_sts_copy = estimate_for_rate_sts  # (i) Contract capacity:
    substation_fraction_sts = STS_substation_fraction  # (j) Substation fraction (SF):
    highest_metered_demand_in_settlement_period_sts = 0.0  # (k) Highest metered demand in settlement period:
    coincidence_factor_with_15_minute_system_peak_sts = None  # (l) Coincidence factor with 15-minute system peak:
    coincident_metered_demand_sts = None  # (m) Coincident metered demand:
    highest_metered_demand_in_previous_24_months_sts = None  # (n) Highest metered demand in previous 24 months:
    billing_capacity_sts = None  # (o) Billing cap’y (highest of 90%×(i), (k) or 90%×(n)):
    load_or_capacity_factor_sts = 0.50  # (p) Load or capacity factor:
    hours_in_month_sts = 730  # (q) Hours in month:
    metered_energy_sts = highest_metered_demand_in_settlement_period_sts * load_or_capacity_factor_sts *  hours_in_month_sts  # (r) Metered energy:
    pool_price_sts = 83.42  # (s) Pool price:
    or_charge_estimate_percentage_of_pool_price_sts = None  # (t) % of pool price for OR charge estimate:
    apparent_power_difference_when_pf_less_than_90_percent_sts = None  # (u) Apparent power difference (when PF < 90%):
    loss_factor_sts = 0.0361  # (v) Loss factor:
    regulated_generating_unit_mw_sts = 0.0  # (w) Regulated generating unit MW:
    quarterly_rider_c_charge_credit_sts = None  # (x) Quarterly Rider C charge (credit):
    quarterly_rider_e_calibration_factor_charge_credit_sts = -0.05  # (y) Quarterly Rider E calibrat’n factor charge (credit):
    balancing_pool_rider_f_charge_credit_sts = None  # (z) $/MWh Balancing Pool Rider F charge (credit):
    wind_forecasting_cost_recovery_rider_j_charge_sts = 0.01  # (aa) $/MWh Wind Forecasting Cost Recovery Rider J charge:
    ###################################################
    # BILLING DETERMINANTS Other Particicpants
    estimate_for_rate_other = False
    contract_capacity_other_copy = contract_capacity_other  # (i) Contract capacity:
    substation_fraction_other = OtherMarketParticipant_substation_fraction  # (j) Substation fraction (SF):
    highest_metered_demand_in_settlement_period_other = None  # (k) Highest metered demand in settlement period:
    coincidence_factor_with_15_minute_system_peak_other = None  # (l) Coincidence factor with 15-minute system peak:
    coincident_metered_demand_other = None  # (m) Coincident metered demand:
    highest_metered_demand_in_previous_24_months_other = None  # (n) Highest metered demand in previous 24 months:
    billing_capacity_other = None  # (o) Billing cap’y (highest of 90%×(i), (k) or 90%×(n)):
    load_or_capacity_factor_other = None  # (p) Load or capacity factor:
    hours_in_month_other = None  # (q) Hours in month:
    metered_energy_other = None  # (r) Metered energy:
    pool_price_other = None  # (s) Pool price:
    or_charge_estimate_percentage_of_pool_price_other = None  # (t) % of pool price for OR charge estimate:
    apparent_power_difference_when_pf_less_than_90_percent_other = None  # (u) Apparent power difference (when PF < 90%):
    loss_factor_other = None  # (v) Loss factor:
    regulated_generating_unit_mw_other = None  # (w) Regulated generating unit MW:
    quarterly_rider_c_charge_credit_other = None  # (x) Quarterly Rider C charge (credit):
    quarterly_rider_e_calibration_factor_charge_credit_other = None  # (y) Quarterly Rider E calibrat’n factor charge (credit):
    balancing_pool_rider_f_charge_credit_other = None  # (z) Balancing Pool Rider F charge (credit):
    wind_forecasting_cost_recovery_rider_j_charge_other = None  # (aa) Wind Forecasting Cost Recovery Rider J charge:

    ###############################
    # Load file
    # csv_file = r'C:\Users\kaczanor\OneDrive - Enbridge Inc\Documents\Python\AB Electricity Sector Stats\input_data\aeso_transmission_tariff_data\aeso_tariff_appendix_one_bill_estimator.csv'
    # csv_file = r'C:\Users\kaczanor\OneDrive - Enbridge Inc\Documents\Python\EDC Hourly Capacity Factor Q2 2024\inputs\AESO_Tariff_Data\aeso_tariff_appendix_one_bill_estimator.csv'
    # aeso_tariff = 'AESO 2024'

    # Convert all values to numbers


    #Billing Quantity				
    subs_fract_dts = None if EstimateType == "STS Only" else substation_fraction_dts #(j)	Substation fraction (SF)	
    high_met_demand_dts = None if EstimateType == "STS Only" else highest_metered_demand_in_settlement_period_dts #(k)	Highest metered demand	
    coin__met_demand_dts = None if EstimateType == "STS Only" else coincident_metered_demand_dts #(m)	Coincident metered demand	
    bil_cap_dts = None if EstimateType == "STS Only" else billing_capacity_dts #(o)	Billing capacity	
    met_energy_dts = None if EstimateType == "STS Only" else metered_energy_dts #(r)	Metered energy	
    poolprice_dts = pool_price_dts#(s)	Pool price	
    or_charge_dts = or_charge_estimate_percentage_of_pool_price_dts #(t)	% of pool price for operating reserve charge	
    app_power_diff_dts = None if EstimateType == "STS Only" else apparent_power_difference_when_pf_less_than_90_percent_dts #(u)	Apparent power difference	

    #Volume
    subs_fract_dts = None if EstimateType == "STS Only" else substation_fraction_dts   # 3(1)(e) Substation fraction
    first_seven_mw_volume = None if EstimateType == "STS Only" else min(billing_capacity_dts, 7.5 * substation_fraction_dts)   # 3(1)(f) First (7.5 × SF) MW of billing capacity
    next_nine_five_mw_volume = None if EstimateType == "STS Only" else max(min(billing_capacity_dts, 17.0 * substation_fraction_dts) - (7.5 * substation_fraction_dts), 0)   # 3(1)(g) Next (9.5 × SF) MW of billing capacity
    next_twenty_three_mw_volume = None if EstimateType == "STS Only" else max(min(billing_capacity_dts, 40.0 * substation_fraction_dts) - (17.0 * substation_fraction_dts), 0)   # 3(1)(h) Next (23 × SF) MW of billing capacity
    all_remaining_mw_volume = None if EstimateType == "STS Only" else max(min(billing_capacity_dts, - (40.0 * substation_fraction_dts)), 0)   # 3(1)(i) All remaining MW of billing capacity

    #########################################
    # Rate DTS: Demand Transmission Service
    #########################################
    # Connection Charge
    #----------------------------
    # Bulk System Charge
    #----------------------------
    # Quick test to see if the lookup_value function works
    # result = lookup_value(csv_file, aeso_tariff, 'Bulk System Charge', 'Coincident metered demand')
    # print(isinstance(result, str))

    coincident_metered_demand_amt = lookup_value(csv_file, aeso_tariff, 'Bulk System Charge', 'Coincident metered demand') * coincident_metered_demand_dts     # 3(1)(a) Coincident metered demand
    metered_energy_bulk_amt = None if EstimateType == "STS Only" else lookup_value(csv_file, aeso_tariff, 'Bulk System Charge', 'metered energy') *  metered_energy_dts     # 3(1)(b) Metered energy
    #----------------------------
    # Regional System Charge
    #----------------------------
    billing_capacity_amt = None if EstimateType == "STS Only" else lookup_value(csv_file, aeso_tariff, 'Regional System Charge', 'Billing capacity') * billing_capacity_dts   # 3(1)(c) Billing capacity
    metered_energy_region_amt = None if EstimateType == "STS Only" else lookup_value(csv_file, aeso_tariff, 'Regional System Charge', 'Metered Energy') *  metered_energy_dts  # 3(1)(d) Metered energy
    #----------------------------
    # Point of Delivery Charge
    #----------------------------
    substation_fraction_amt = None if EstimateType == "STS Only" else lookup_value(csv_file, aeso_tariff, 'Rate DTS Charge', '(e) Substation fraction (SF)') * subs_fract_dts   # 3(1)(e) Substation fraction
    first_seven_five_mw_billing_capacity_amt = None if EstimateType == "STS Only" else lookup_value(csv_file, aeso_tariff, 'Rate DTS Charge', '(f) First (7.5 × SF) MW of billing capacity') *  first_seven_mw_volume     # 3(1)(f) First (7.5 × SF) MW of billing capacity
    next_nine_five_mw_billing_capacity_amt =None if EstimateType == "STS Only" else lookup_value(csv_file, aeso_tariff, 'Rate DTS Charge', '(g) Next (9.5 × SF) MW of billing capacity') * next_nine_five_mw_volume     # 3(1)(g) Next (9.5 × SF) MW of billing capacity
    next_twenty_three_mw_billing_capacity_amt = None if EstimateType == "STS Only" else lookup_value(csv_file, aeso_tariff, 'Rate DTS Charge', '(h) Next (23 × SF) MW of billing capacity') * next_twenty_three_mw_volume        # 3(1)(h) Next (23 × SF) MW of billing capacity all_remaining_mw_billing_capacity_amt = None if EstimateType == "STS Only" else lookup_value(csv_file, aeso_tariff, 'Rate DTS Charge', '(i) All remaining MW of billing capacity') * all_remaining_mw_volume        # 3(1)(i) All remaining MW of billing capacity
    all_remaining_mw_volume_amt = None if EstimateType == "STS Only" else lookup_value(csv_file, aeso_tariff, 'Rate DTS Charge', '(i) All remaining MW of billing capacity') * all_remaining_mw_volume # 3(1)(i) All remaining MW of billing capacity


    subtotal_connection_charge_amt = safe_sum(coincident_metered_demand_amt, metered_energy_bulk_amt, billing_capacity_amt, metered_energy_region_amt, \
        substation_fraction_amt, first_seven_five_mw_billing_capacity_amt, next_nine_five_mw_billing_capacity_amt, next_twenty_three_mw_billing_capacity_amt, \
            all_remaining_mw_volume_amt)

    # subtotal_connection_charge_amt = coincident_metered_demand_amt + metered_energy_bulk_amt + billing_capacity_amt + metered_energy_region_amt + \
    #     substation_fraction_amt + first_seven_five_mw_billing_capacity_amt + next_nine_five_mw_billing_capacity_amt + \
    #         next_twenty_three_mw_billing_capacity_amt + all_remaining_mw_volume_amt  # New Item
    #----------------------------
    # # Operating Reserve Charge Estimate
    #----------------------------
    operating_reserve_charge_amt   =  poolprice_dts * or_charge_estimate_percentage_of_pool_price_dts * met_energy_dts      # 4
    #----------------------------
    # Transmission Constraint Rebalancing Charge Estimate
    #----------------------------
    trans_constr_rebalance_charge_amt  =   lookup_value(csv_file, aeso_tariff, 'Transmission Constraint Rebalancing Charge', 'Metered energy') * met_energy_dts  #5
    #----------------------------
    # Voltage Control Charge
    #----------------------------
    voltage_control_charge_amt   =   lookup_value(csv_file, aeso_tariff, 'Voltage Control Charge', 'Metered energy') * met_energy_dts      #6
    #----------------------------
    # Other System Support Services Charge
    #----------------------------      
    high_met_demand_amt =  lookup_value(csv_file, aeso_tariff, 'Other System Support Services Charge', 'Highest metered demand') * high_met_demand_dts       # 7(a)
    app_power_differnce__amt =  lookup_value(csv_file, aeso_tariff, 'Other System Support Services Charge', 'Apparent Power Difference') * app_power_diff_dts        # 7(b)

    subtotal_other_system_support_services_charge_amt = safe_sum(high_met_demand_amt, app_power_differnce__amt)

    #subtotal_other_system_support_services_charge_amt = high_met_demand_amt + app_power_differnce__amt  # New Item

    total_dts_amt = safe_sum(subtotal_connection_charge_amt, operating_reserve_charge_amt, trans_constr_rebalance_charge_amt, voltage_control_charge_amt, \
            subtotal_other_system_support_services_charge_amt)

    print("Total DTS Amount:", total_dts_amt)
    print(f" coincident_metered_demand_amt: {coincident_metered_demand_amt}, metered_energy_bulk_amt: {metered_energy_bulk_amt}, metered_energy_region_amt: {metered_energy_region_amt},\
        substation_fraction_amt: {substation_fraction_amt}, first_seven_five_mw_billing_capacity_amt: {first_seven_five_mw_billing_capacity_amt}, \
            next_nine_five_mw_billing_capacity_amt: {next_nine_five_mw_billing_capacity_amt}, next_twenty_three_mw_billing_capacity_amt: {next_twenty_three_mw_billing_capacity_amt}, \
                all_remaining_mw_volume_amt: {all_remaining_mw_volume_amt}, operating_reserve_charge_amt: {operating_reserve_charge_amt}, \
            trans_constr_rebalance_charge_amt: {trans_constr_rebalance_charge_amt}, voltage_control_charge_amt: {voltage_control_charge_amt}, \
            subtotal_other_system_support_services_charge_amt: {subtotal_other_system_support_services_charge_amt}")

    # total_dts_amt = coincident_metered_demand_amt + metered_energy_bulk_amt + billing_capacity_amt + metered_energy_region_amt + \
    #     subtotal_connection_charge_amt + operating_reserve_charge_amt + trans_constr_rebalance_charge_amt + voltage_control_charge_amt + \
    #         subtotal_other_system_support_services_charge_amt  

    #----------------------------
    #Rider C: Deferral Account Adjustment Rider									
    #----------------------------
    #These are % values
    con_charge_riderc_percent = 0.0 #2(4)(a)	Connection charge	
    operating_reserve_charge__riderc_percent = 0.0 #2(4)(b)	Operating reserve charge	
    trans_constr_rebalance_charg_riderc_percent = 0.0 #2(4)(c)	Transmission constraint rebalancing	
    voltage_control_charge_riderc_percent = 0.0 #2(4)(d)	Voltage control charge	
    other_charges_riderc_percent = 0.0 #2(4)(e)	Other system support services	

    #These are $ values
    con_charge_riderc_dollars = None if EstimateType == "STS Only" else subtotal_connection_charge_amt #2(4)(a)	Connection charge	
    operating_reserve_charge__riderc_dollars = None if EstimateType == "STS Only" else operating_reserve_charge_amt #2(4)(b)	Operating reserve charge	
    trans_constr_rebalance_charg_riderc_dollars = None if EstimateType == "STS Only" else  trans_constr_rebalance_charge_amt #2(4)(c)	Transmission constraint rebalancing	
    voltage_control_charge__riderc_dollars = None if EstimateType == "STS Only" else  voltage_control_charge_amt #0.0 2(4)(d)	Voltage control charge	
    other_charges_riderc_dollars = None if EstimateType == "STS Only" else  subtotal_other_system_support_services_charge_amt #2(4)(e)	Other system support services

    # These are scaled dollar values based on the % * $ values
    con_charge_riderc_amt = None if EstimateType == "STS Only" else  con_charge_riderc_percent * con_charge_riderc_dollars #2(4)(a)	Connection charge	
    operating_reserve_charge_riderc_amt = None if EstimateType == "STS Only" else  operating_reserve_charge__riderc_percent * operating_reserve_charge__riderc_dollars#2(4)(b)	Operating reserve charge	
    trans_constr_rebalance_charg_riderc_amt = None if EstimateType == "STS Only" else  trans_constr_rebalance_charg_riderc_percent * trans_constr_rebalance_charg_riderc_dollars #2(4)(c)	Transmission constraint rebalancing	
    voltage_control_charge_riderc_amt = None if EstimateType == "STS Only" else voltage_control_charge_riderc_percent * voltage_control_charge__riderc_dollars #2(4)(d)	Voltage control charge	
    other_charges_riderc_amt = None if EstimateType == "STS Only" else  other_charges_riderc_percent * other_charges_riderc_dollars #2(4)(e)	Other system support services

    total_riderc_charge_or_credit = safe_sum(con_charge_riderc_amt, operating_reserve_charge_riderc_amt, trans_constr_rebalance_charg_riderc_amt,\
        voltage_control_charge_riderc_amt, other_charges_riderc_amt) 

    # total_riderc_charge_or_credit = con_charge_riderc_amt + operating_reserve_charge_riderc_amt + trans_constr_rebalance_charg_riderc_amt + \
    #     voltage_control_charge_riderc_amt + other_charges_riderc_amt

    #Total estimated charge in settlement period under Rate DTS:
    total_riderc_amt = safe_sum(total_dts_amt, total_riderc_charge_or_credit)
    #total_riderc_amt = total_dts_amt + total_riderc_charge_or_credit 

    #----------------------------
    #Rider F: Balancing Pool Consumer Allocation Rider								
    #----------------------------
    #Charge
    riderF_charge = balancing_pool_rider_f_charge_credit_dts
    #Volume
    riderF_volmue = None if EstimateType == "STS Only" or RiderF != True else met_energy_dts

    #Amount
    riderF_amt = None if EstimateType == "STS Only" or RiderF != True else riderF_charge * riderF_volmue

    #########################################
    # Rate PSC: Primary Service Credit
    #########################################
    subs_fract_pcs = None if EstimateType == "STS Only" else substation_fraction_dts 
    bil_cap_pcs = None if EstimateType == "STS Only" else billing_capacity_dts 

    # Credit
    subs_fract_tariff_psc = None if EstimateType == "STS Only" else lookup_value(csv_file, aeso_tariff, 'Rate PSC Credit', '(e) Substation fraction (SF)') 
    first_seven_mw_tariff_psc = None if EstimateType == "STS Only" else lookup_value(csv_file, aeso_tariff, 'Rate PSC Credit', '(f) First (7.5 × SF) MW of billing capacity')  
    next_nine_five_mw_tariff_psc = None if EstimateType == "STS Only" else lookup_value(csv_file, aeso_tariff, 'Rate PSC Credit', '(g) Next (9.5 × SF) MW of billing capacity') 
    next_twenty_three_mw_tariff_psc = None if EstimateType == "STS Only" else lookup_value(csv_file, aeso_tariff, 'Rate PSC Credit', '(h) Next (23 × SF) MW of billing capacity')   
    all_remaining_mw_tariff_psc = None if EstimateType == "STS Only" else lookup_value(csv_file, aeso_tariff, 'Rate PSC Credit', '(i) All remaining MW of billing capacity') 

    # Volume
    subs_fract_psc = None if (EstimateType == "STS Only" or PrimaryServiceCredit != True) or PrimaryServiceCredit != True else substation_fraction_dts    #2(2)(a) Substation fraction
    first_seven_mw_volume_psc = None if (EstimateType == "STS Only" or PrimaryServiceCredit != True) or PrimaryServiceCredit != True else min(bil_cap_pcs, 7.5 * subs_fract_pcs) #2(2)(b) First (7.5 × SF) MW of billing capacity
    next_nine_five_mw_volume_psc = None if (EstimateType == "STS Only" or PrimaryServiceCredit != True) or PrimaryServiceCredit != True else max(min(bil_cap_pcs, 17.0 * subs_fract_pcs) - 7.5 * subs_fract_pcs, 0) #2(2)(c) Next (9.5 × SF) MW of billing capacity
    next_twenty_three_mw_volume_psc = None if (EstimateType == "STS Only" or PrimaryServiceCredit != True) or PrimaryServiceCredit != True else max(min(bil_cap_pcs, 40.0 * subs_fract_pcs) - 17.0 * subs_fract_pcs, 0)  #2(2)(d) Next (23 × SF) MW of billing capacity 
    all_remaining_mw_volume_psc = None if (EstimateType == "STS Only" or PrimaryServiceCredit != True) or PrimaryServiceCredit != True else max(min(bil_cap_pcs, - (40.0 * subs_fract_pcs), 0))  #2(2)(e) All remaining MW of billing capacity

    #Amount
    subs_fract_amt_psc = None if (EstimateType == "STS Only" or PrimaryServiceCredit != True) or PrimaryServiceCredit != True else subs_fract_tariff_psc * subs_fract_psc
    first_seven_mw_amt_psc = None if (EstimateType == "STS Only" or PrimaryServiceCredit != True) or PrimaryServiceCredit != True else first_seven_mw_tariff_psc * first_seven_mw_volume_psc
    next_nine_five_mw_amt_psc = None if (EstimateType == "STS Only" or PrimaryServiceCredit != True) or PrimaryServiceCredit != True else next_nine_five_mw_tariff_psc * next_nine_five_mw_volume_psc
    next_twenty_three_mw_amt_psc = None if (EstimateType == "STS Only" or PrimaryServiceCredit != True) or PrimaryServiceCredit != True else next_twenty_three_mw_tariff_psc * next_twenty_three_mw_volume_psc
    all_remaining_mw_amt_psc = None if (EstimateType == "STS Only" or PrimaryServiceCredit != True) or PrimaryServiceCredit != True else all_remaining_mw_tariff_psc * all_remaining_mw_volume_psc  

    # Error handle the sum with custom function to ignore None values
    # Use the function to calculate the total
    total_rate_psc_credit = safe_sum(subs_fract_amt_psc, first_seven_mw_amt_psc, next_nine_five_mw_amt_psc, next_twenty_three_mw_amt_psc, all_remaining_mw_amt_psc)
    #total_rate_psc_credit = subs_fract_amt_psc + first_seven_mw_amt_psc + next_nine_five_mw_amt_psc + next_twenty_three_mw_amt_psc + all_remaining_mw_amt_psc

    #Rider C: Deferral Account Adjustment Rider									
    #Credit
    psc_percent = con_charge_riderc_percent
    #Volume
    psc_volume = None if (EstimateType == "STS Only" or PrimaryServiceCredit != True) or PrimaryServiceCredit != True else total_rate_psc_credit
    #Amount
    psc_amt = None if (EstimateType == "STS Only" or PrimaryServiceCredit != True) or PrimaryServiceCredit != True else psc_percent * psc_volume
    total_riderc_charge_or_credit = None if (EstimateType == "STS Only" or PrimaryServiceCredit != True) or PrimaryServiceCredit != True else psc_amt

    total_estimated_credit_in_settlement_period_psc = safe_sum(total_rate_psc_credit, total_riderc_charge_or_credit)


    #########################################
    # Rate STS: Supply Transmission Service
    #########################################
    met_energy_sts  = None if EstimateType == 'DTS Only' else  metered_energy_sts
    pool_price_sts  = None if EstimateType == 'DTS Only' else  pool_price_sts
    loss_factor_sts  = None if EstimateType == 'DTS Only' else  loss_factor_sts
    regulated_generating_unit_mw_sts  = None if EstimateType == 'DTS Only' else  regulated_generating_unit_mw_sts

    #None if EstimateType == 'DTS Only' else  metered_energy_sts

    #-------------------
    # Losses Charge
    #-------------------
    # Charge
    met_energy_tariff_sts = None if EstimateType == 'DTS Only' else  pool_price_sts * loss_factor_sts
    # Volume
    met_energy_volume_sts = None if EstimateType == 'DTS Only' else  met_energy_sts        # 2(1)	Metered energy
    # Amount
    met_energy_amt_sts = None if EstimateType == 'DTS Only' else met_energy_tariff_sts * met_energy_volume_sts
    #-------------------
    # Regulated Generating Unit Connection Cost
    #-------------------
    # Charge
    reg_unit_tariff_sts = None if EstimateType == 'DTS Only' else  lookup_value(csv_file, aeso_tariff, 'Other System Support Services Charge', 'Regulated Generating Unit Connection Cost') 
                                                                
    # Volume
    reg_unit_volume_sts = None if EstimateType == 'DTS Only' or is_this_regulated_generating_unit != True else  met_energy_sts  # 2(1)	Metered energy

    # Amount
    reg_unit_amt_sts = None if EstimateType == 'DTS Only' or is_this_regulated_generating_unit != True else reg_unit_tariff_sts * reg_unit_volume_sts

    total_rate_sts_charge = safe_sum(met_energy_amt_sts, reg_unit_amt_sts)
    #total_rate_sts_charge = met_energy_amt_sts + reg_unit_amt_sts
    #-------------------
    # Rider E: Losses Calibration Factor Rider
    #-------------------
    # Charge
    loss_calib_factor_tariff = None if EstimateType == 'DTS Only' or RiderE != True else  pool_price_sts * quarterly_rider_e_calibration_factor_charge_credit_sts
    # Volume
    loss_calib_factor_volume = None if EstimateType == 'DTS Only' or RiderE != True else  met_energy_sts
    # Amount
    loss_calib_factor_amt = None if EstimateType == 'DTS Only' or RiderE != True else  loss_calib_factor_tariff * loss_calib_factor_volume
    #-------------------
    # Rider J: Wind Forecasting Service Cost Recovery Rider
    #-------------------
    # Charge
    riderj_charge = None if RiderJ != True else  wind_forecasting_cost_recovery_rider_j_charge_sts
    # Volume
    riderj_volume = None if EstimateType == 'DTS Only' or RiderJ != True else met_energy_sts
    # Amount
    riderj_amt = None if EstimateType == 'DTS Only' or RiderJ != True else riderj_charge * riderj_volume

    total_estimated_charge_in_settlement_period_sts = safe_sum(total_rate_sts_charge, loss_calib_factor_amt, riderj_amt)


    #############################################
    # MONTHLY SUMMARY
    #############################################
    # BILL ESTIMATES: MONTHLY DTS
    monthly_transmission_service_charge_credit_dts = None if EstimateType == "STS Only" else total_dts_amt # (1) Transmission service charge (credit):
    monthly_deferral_account_adjustment_rider_c_dts = None if EstimateType == "STS Only" or RiderC != True else total_riderc_amt     # (2) Deferral Account Adjustment Rider C:
    monthly_losses_calibration_factor_rider_e_dts = None  # (3) Losses Calibration Factor Rider E:
    monthly_balancing_pool_consumer_allocation_rider_f_dts = None if EstimateType == "STS Only" or RiderF != True else riderF_amt    # (4) Balancing Pool Consumer Allocation Rider F:
    monthly_wind_forecasting_service_cost_recovery_rider_j_dts = None  # (5) Wind Forecasting Service Cost Recovery Rider J:

    total_monthly_charges_dts = safe_sum(monthly_transmission_service_charge_credit_dts, monthly_deferral_account_adjustment_rider_c_dts, \
        monthly_losses_calibration_factor_rider_e_dts, monthly_balancing_pool_consumer_allocation_rider_f_dts, \
            monthly_wind_forecasting_service_cost_recovery_rider_j_dts)


    # BILL ESTIMATES: MONTHLY PSC
    monthly_transmission_service_charge_credit_psc = None if EstimateType == "STS Only" or PrimaryServiceCredit != True else total_rate_psc_credit  # (1) Transmission service charge (credit):
    monthly_deferral_account_adjustment_rider_c_psc = None if EstimateType == "STS Only" or PrimaryServiceCredit != True or RiderC != True else total_riderc_charge_or_credit   # (2) Deferral Account Adjustment Rider C:
    monthly_losses_calibration_factor_rider_e_psc = None  # (3) Losses Calibration Factor Rider E:
    monthly_balancing_pool_consumer_allocation_rider_f_psc = None  # (4) Balancing Pool Consumer Allocation Rider F:
    monthly_wind_forecasting_service_cost_recovery_rider_j_psc = None  # (5) Wind Forecasting Service Cost Recovery Rider J:

    total_monthly_charges_psc =  safe_sum(monthly_transmission_service_charge_credit_psc, monthly_deferral_account_adjustment_rider_c_psc, \
        monthly_losses_calibration_factor_rider_e_psc, monthly_balancing_pool_consumer_allocation_rider_f_psc, \
            monthly_wind_forecasting_service_cost_recovery_rider_j_psc)

            
    # BILL ESTIMATES: MONTHLY STS
    monthly_transmission_service_charge_credit_sts = None if EstimateType == "DTS Only" else total_rate_sts_charge  # (1) Transmission service charge (credit):
    monthly_deferral_account_adjustment_rider_c_sts = None  # (2) Deferral Account Adjustment Rider C:
    monthly_losses_calibration_factor_rider_e_sts = None if EstimateType == "STS Only" or RiderE != True else loss_calib_factor_amt   # (3) Losses Calibration Factor Rider E:
    monthly_balancing_pool_consumer_allocation_rider_f_sts = None  # (4) Balancing Pool Consumer Allocation Rider F:
    monthly_wind_forecasting_service_cost_recovery_rider_j_sts = None if EstimateType == "STS Only" or RiderJ != True else riderj_amt   # (5) Wind Forecasting Service Cost Recovery Rider J:

    total_monthly_charges_sts = safe_sum(monthly_transmission_service_charge_credit_sts, monthly_deferral_account_adjustment_rider_c_sts, \
        monthly_losses_calibration_factor_rider_e_sts, monthly_balancing_pool_consumer_allocation_rider_f_sts, \
            monthly_wind_forecasting_service_cost_recovery_rider_j_sts)


    # BILL ESTIMATES: MONTHLY Total

    monthly_transmission_service_charge_credit_tot = safe_sum(monthly_transmission_service_charge_credit_dts, monthly_transmission_service_charge_credit_psc, \
        monthly_transmission_service_charge_credit_sts)

    monthly_deferral_account_adjustment_rider_c_tot = safe_sum(monthly_deferral_account_adjustment_rider_c_dts, monthly_deferral_account_adjustment_rider_c_psc, \
        monthly_deferral_account_adjustment_rider_c_sts)

    monthly_losses_calibration_factor_rider_e_tot = safe_sum(monthly_losses_calibration_factor_rider_e_dts, monthly_losses_calibration_factor_rider_e_psc, \
        monthly_losses_calibration_factor_rider_e_sts)

    monthly_balancing_pool_consumer_allocation_rider_f_tot = safe_sum(monthly_balancing_pool_consumer_allocation_rider_f_dts, \
        monthly_balancing_pool_consumer_allocation_rider_f_psc, \
        monthly_balancing_pool_consumer_allocation_rider_f_sts)

    monthly_wind_forecasting_service_cost_recovery_rider_j_tot = safe_sum(monthly_wind_forecasting_service_cost_recovery_rider_j_dts, \
        monthly_wind_forecasting_service_cost_recovery_rider_j_psc, monthly_wind_forecasting_service_cost_recovery_rider_j_sts)

    total_monthly_charges_tot = safe_sum(total_monthly_charges_dts, total_monthly_charges_psc, total_monthly_charges_sts)


    ##########################################
    # BILL ESTIMATES: ANNUAL DTS  (Monthly × 12)
    annual_transmission_service_charge_credit_dts = None if monthly_transmission_service_charge_credit_dts is None else monthly_transmission_service_charge_credit_dts * 12  # (7) Transmission service charge (credit):
    annual_deferral_account_adjustment_rider_c_dts = None if monthly_deferral_account_adjustment_rider_c_dts is None else monthly_deferral_account_adjustment_rider_c_dts * 12   # (8) Deferral Account Adjustment Rider C:
    annual_losses_calibration_factor_rider_e_dts = None  # (9) Losses Calibration Factor Rider E:
    annual_balancing_pool_consumer_allocation_rider_f_dts = None if monthly_balancing_pool_consumer_allocation_rider_f_dts is None else monthly_balancing_pool_consumer_allocation_rider_f_dts * 12   # (10) Balancing Pool Consumer Allocation Rider F:
    annual_wind_forecasting_service_cost_recovery_rider_j_dts = None

    total_annual_charges_dts = safe_sum(annual_transmission_service_charge_credit_dts, annual_deferral_account_adjustment_rider_c_dts, \
        annual_losses_calibration_factor_rider_e_dts, annual_balancing_pool_consumer_allocation_rider_f_dts, \
            annual_wind_forecasting_service_cost_recovery_rider_j_dts)


    # BILL ESTIMATES: ANNUAL PSC  (Monthly × 12)
    annual_transmission_service_charge_credit_psc = None if monthly_transmission_service_charge_credit_psc is None else monthly_transmission_service_charge_credit_psc * 12  # (7) Transmission service charge (credit):
    annual_deferral_account_adjustment_rider_c_psc = None if monthly_deferral_account_adjustment_rider_c_psc is None else monthly_deferral_account_adjustment_rider_c_psc * 12  # (8) Deferral Account Adjustment Rider C: 
    annual_losses_calibration_factor_rider_e_psc = None  # (9) Losses Calibration Factor Rider E: 
    annual_balancing_pool_consumer_allocation_rider_f_psc = None 
    annual_wind_forecasting_service_cost_recovery_rider_j_psc = None

    total_annual_charges_psc = safe_sum(annual_transmission_service_charge_credit_psc, annual_deferral_account_adjustment_rider_c_psc, \
        annual_losses_calibration_factor_rider_e_psc, annual_balancing_pool_consumer_allocation_rider_f_psc, \
            annual_wind_forecasting_service_cost_recovery_rider_j_psc)

    # BILL ESTIMATES: ANNUAL STS  (Monthly × 12)
    annual_transmission_service_charge_credit_sts = None if monthly_transmission_service_charge_credit_sts is None else monthly_transmission_service_charge_credit_sts * 12  # (7) Transmission service charge (credit):
    annual_deferral_account_adjustment_rider_c_sts = None # (8) Deferral Account Adjustment Rider C:
    annual_losses_calibration_factor_rider_e_sts = None if monthly_losses_calibration_factor_rider_e_sts is None else monthly_losses_calibration_factor_rider_e_sts * 12  # (9) Losses Calibration Factor Rider E:
    annual_balancing_pool_consumer_allocation_rider_f_sts = None  # (10) Balancing Pool Consumer Allocation Rider F:
    annual_wind_forecasting_service_cost_recovery_rider_j_sts = None if monthly_wind_forecasting_service_cost_recovery_rider_j_sts is None else monthly_wind_forecasting_service_cost_recovery_rider_j_sts * 12  # (11) Wind Forecasting Service Cost Recovery Rider J:

    total_annual_charges_sts = safe_sum(annual_transmission_service_charge_credit_sts, annual_deferral_account_adjustment_rider_c_sts, \
        annual_losses_calibration_factor_rider_e_sts, annual_balancing_pool_consumer_allocation_rider_f_sts, \
            annual_wind_forecasting_service_cost_recovery_rider_j_sts)

    # BILL ESTIMATES: ANNUAL TOTAL  (Monthly × 12)
    annual_transmission_service_charge_credit_total = safe_sum(annual_transmission_service_charge_credit_dts, annual_transmission_service_charge_credit_psc, \
        annual_transmission_service_charge_credit_sts, annual_transmission_service_charge_credit_sts)

    annual_deferral_account_adjustment_rider_c_total = safe_sum(annual_deferral_account_adjustment_rider_c_dts, annual_deferral_account_adjustment_rider_c_psc, \
        annual_deferral_account_adjustment_rider_c_sts, annual_deferral_account_adjustment_rider_c_sts)

    annual_losses_calibration_factor_rider_e_total = safe_sum(annual_losses_calibration_factor_rider_e_dts, annual_losses_calibration_factor_rider_e_psc, \
        annual_losses_calibration_factor_rider_e_sts, annual_losses_calibration_factor_rider_e_sts)

    annual_balancing_pool_consumer_allocation_rider_f_total = safe_sum(annual_balancing_pool_consumer_allocation_rider_f_dts, \
        annual_balancing_pool_consumer_allocation_rider_f_psc, annual_balancing_pool_consumer_allocation_rider_f_sts, \
            annual_balancing_pool_consumer_allocation_rider_f_sts)

    annual_wind_forecasting_service_cost_recovery_rider_j_total = safe_sum(annual_wind_forecasting_service_cost_recovery_rider_j_dts, \
        annual_wind_forecasting_service_cost_recovery_rider_j_psc, annual_wind_forecasting_service_cost_recovery_rider_j_sts, \
            annual_wind_forecasting_service_cost_recovery_rider_j_sts)

    total_annual_charges_total = safe_sum(annual_transmission_service_charge_credit_total, annual_deferral_account_adjustment_rider_c_total, \
        annual_losses_calibration_factor_rider_e_total, annual_balancing_pool_consumer_allocation_rider_f_total, \
            annual_wind_forecasting_service_cost_recovery_rider_j_total)


    ######################################
    # CREATE TABLE
    ######################################

    # Define the data for the table using the variables
    data_monthly = {
        "Description": [
            "Transmission service charge (credit):",
            "Deferral Account Adjustment Rider C:",
            "Losses Calibration Factor Rider E:",
            "Balancing Pool Consumer Allocation Rider F:",
            "Wind Forecasting Service Cost Recovery Rider J:",
            "Total monthly charges:"
        ],
        "Rate DTS": [
            monthly_transmission_service_charge_credit_dts,
            monthly_deferral_account_adjustment_rider_c_dts,
            monthly_losses_calibration_factor_rider_e_dts,
            monthly_balancing_pool_consumer_allocation_rider_f_dts,
            monthly_wind_forecasting_service_cost_recovery_rider_j_dts,
            total_monthly_charges_dts
        ],
        "Rate PSC": [
            monthly_transmission_service_charge_credit_psc,
            monthly_deferral_account_adjustment_rider_c_psc,
            monthly_losses_calibration_factor_rider_e_psc,
            monthly_balancing_pool_consumer_allocation_rider_f_psc,
            monthly_wind_forecasting_service_cost_recovery_rider_j_psc,
            total_monthly_charges_psc
        ],
        "Rate STS": [
            monthly_transmission_service_charge_credit_sts,
            monthly_deferral_account_adjustment_rider_c_sts,
            monthly_losses_calibration_factor_rider_e_sts,
            monthly_balancing_pool_consumer_allocation_rider_f_sts,
            monthly_wind_forecasting_service_cost_recovery_rider_j_sts,
            total_monthly_charges_sts
        ],
        "Total": [
            monthly_transmission_service_charge_credit_tot,
            monthly_deferral_account_adjustment_rider_c_tot,
            monthly_losses_calibration_factor_rider_e_tot,
            monthly_balancing_pool_consumer_allocation_rider_f_tot,
            monthly_wind_forecasting_service_cost_recovery_rider_j_tot,
            total_monthly_charges_tot
        ]
    }

    data_annual = {
        "Description": [
            "Transmission service charge (credit):",
            "Deferral Account Adjustment Rider C:",
            "Losses Calibration Factor Rider E:",
            "Balancing Pool Consumer Allocation Rider F:",
            "Wind Forecasting Service Cost Recovery Rider J:",
            "Total annual charges:"
        ],
        "Rate DTS": [
            annual_transmission_service_charge_credit_dts,
            annual_deferral_account_adjustment_rider_c_dts,
            annual_losses_calibration_factor_rider_e_dts,
            annual_balancing_pool_consumer_allocation_rider_f_dts,
            annual_wind_forecasting_service_cost_recovery_rider_j_dts,
            total_annual_charges_dts
        ],
        "Rate PSC": [
            annual_transmission_service_charge_credit_psc,
            annual_deferral_account_adjustment_rider_c_psc,
            annual_losses_calibration_factor_rider_e_psc,
            annual_balancing_pool_consumer_allocation_rider_f_psc,
            annual_wind_forecasting_service_cost_recovery_rider_j_psc,
            total_annual_charges_psc
        ],
        "Rate STS": [
            annual_transmission_service_charge_credit_sts,
            annual_deferral_account_adjustment_rider_c_sts,
            annual_losses_calibration_factor_rider_e_sts,
            annual_balancing_pool_consumer_allocation_rider_f_sts,
            annual_wind_forecasting_service_cost_recovery_rider_j_sts,
            total_annual_charges_sts
        ],
        "Total": [
            annual_transmission_service_charge_credit_total,
            annual_deferral_account_adjustment_rider_c_total,
            annual_losses_calibration_factor_rider_e_total,
            annual_balancing_pool_consumer_allocation_rider_f_total,
            annual_wind_forecasting_service_cost_recovery_rider_j_total,
            total_annual_charges_total
        ]
    }

    # Create DataFrames
    df_monthly = pd.DataFrame(data_monthly)
    df_annual = pd.DataFrame(data_annual)

    # Set the index to Description for better readability
    df_monthly.set_index("Description", inplace=True)
    df_annual.set_index("Description", inplace=True)

    # Function to format numbers
    def format_currency(x):
        if pd.notnull(x):
            return f"${x:,.0f}"
        return x

    # Apply the formatting to all elements
    df_monthly = df_monthly.applymap(format_currency)
    df_annual = df_annual.applymap(format_currency)

    # Display DataFrames
    print("BILL ESTIMATES: MONTHLY")
    print(df_monthly)
    print("\nBILL ESTIMATES: ANNUAL")
    print(df_annual)

    # # Display DataFrames using pprint
    # print("BILL ESTIMATES: MONTHLY")
    # pprint(df_monthly.to_dict())

    # print("\nBILL ESTIMATES: ANNUAL")
    # pprint(df_annual.to_dict())

    return

#####################################

#####################################
def adjust_for_dst(enb_demand_data):
    # Define DST changes
    dst_changes = [
        {"year": 2021, "spring_forward": "2021-03-14 02:00:00", "fall_back": "2021-11-07 01:00:00"},
        {"year": 2022, "spring_forward": "2022-03-13 02:00:00", "fall_back": "2022-11-06 01:00:00"},
        {"year": 2023, "spring_forward": "2023-03-12 02:00:00", "fall_back": "2023-11-05 01:00:00"},
        {"year": 2024, "spring_forward": "2024-03-10 02:00:00", "fall_back": "2024-11-03 01:00:00"},
    ]

    for change in dst_changes:
        year = change["year"]
        spring_forward = pd.Timestamp(change["spring_forward"])
        fall_back = pd.Timestamp(change["fall_back"])

        # Insert missing hour in spring
        if spring_forward not in enb_demand_data.index and (spring_forward - pd.Timedelta(hours=1)) in enb_demand_data.index:
            enb_demand_data.loc[spring_forward] = enb_demand_data.loc[spring_forward - pd.Timedelta(hours=1)]
            enb_demand_data.sort_index(inplace=True)

         # Remove duplicate hour in fall
        if fall_back in enb_demand_data.index:
            duplicate_fall_back = enb_demand_data.loc[fall_back]
            if len(duplicate_fall_back) > 1:
                enb_demand_data = enb_demand_data.drop(fall_back)

    return enb_demand_data

def adjust_processed_demand_data_for_dst(processed_demand_data):
    # Define DST changes
    dst_changes = [
        {"year": 2021, "spring_forward": "2021-03-14 02:00:00", "fall_back": "2021-11-07 01:00:00"},
        {"year": 2022, "spring_forward": "2022-03-13 02:00:00", "fall_back": "2022-11-06 01:00:00"},
        {"year": 2023, "spring_forward": "2023-03-12 02:00:00", "fall_back": "2023-11-05 01:00:00"},
        {"year": 2024, "spring_forward": "2024-03-10 02:00:00", "fall_back": "2024-11-03 01:00:00"},
    ]

    for change in dst_changes:
        year = change["year"]
        spring_forward = pd.Timestamp(change["spring_forward"])
        fall_back = pd.Timestamp(change["fall_back"])

        # Add the missing hour in spring
        if spring_forward not in processed_demand_data.index and (spring_forward - pd.Timedelta(hours=1)) in processed_demand_data.index:
            # Create a new row with the same structure and data as the previous hour
            new_row = processed_demand_data.loc[spring_forward - pd.Timedelta(hours=1)].copy()
            new_row.name = spring_forward
            processed_demand_data = pd.concat([processed_demand_data, pd.DataFrame([new_row])])
            processed_demand_data.sort_index(inplace=True)

        # Remove the duplicate hour in fall
        if fall_back in processed_demand_data.index:
            duplicate_fall_back = processed_demand_data.loc[fall_back]
            if len(duplicate_fall_back) > 1:
                processed_demand_data = processed_demand_data.drop(fall_back)

    return processed_demand_data
#####################################
# # Initialize and set parameters
# # Step 1: Initialize and set parameters
# # Step 1.1 Load Alberta system load data

# peak_demand_methodology = 'twelve_cp_peak_demand' #twelve_cp_peak_demand, five_cp_peak_demand, highest_in_month_each_month
# timeseries_format1 =  '%Y-%m-%d %H:%M:%S' 
# timeseries_format2 =  '%m/%d/%Y %H:%M' 

# #initialize data frame
# processed_demand_data = pd.DataFrame()
# processed_demand_data = pd.read_csv(r"C:\Users\kaczanor\OneDrive - Enbridge Inc\Documents\Python\AB Electricity Sector Stats\output_data\CSV_Folder\processed_demand_data.csv")


# # Convert the "Date_Begin_Local" column to datetime if it's not already
# processed_demand_data['Date'] = pd.to_datetime(processed_demand_data['DateTime'], format=timeseries_format1)
# print(f" processed_demand_data_upload before format change: {processed_demand_data}")

# processed_demand_data.set_index('Date', inplace=True)
# print(f"processed_demand_data after setting index: {processed_demand_data.head()}")


# # Step 1.2 Load ENB load data
# #Load enb demand data
# # Adjust the `skiprows` parameter based on your actual data structure
# skiprows = 16  # Example: Skip the first 10 rows, adjust as needed
# enb_demand_data = pd.read_csv(r"C:\Users\kaczanor\OneDrive - Enbridge Inc\Documents\Python\AB Electricity Sector Stats\input_data\ENB_Load\Power Consumption Consolidated D1&2.csv", skiprows=skiprows)

# enb_demand_data['Date'] = pd.to_datetime(enb_demand_data['Date'], format=timeseries_format2) 
# enb_demand_data.set_index('Date', inplace=True)
# print(f"enb_demand_data after setting index: {enb_demand_data.head()}")

# # Adjust the `skiprows` parameter based on your actual data structure
# # I only need the hourly data from the 16th row onwards
# # I dont need the summay statistics at the top of the file
# '''
# 2021,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
# AVG,,"24,443","22,044","18,685","29,355","31,262","13,404","25,335","24,089","21,842","1,465","23,339","25,525","24,265","10,381","2,609","12,390","1,341","21,906","26,048","19,136",,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
# MAX,,"75,399","80,915","69,298","68,616","99,263","94,288","38,789","99,173","95,335","9,981","83,232","67,851","85,658","63,686","9,901","32,905","9,647","87,183","77,798","73,586",,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
# Load Factor %,,32%,27%,27%,43%,31%,14%,65%,24%,23%,15%,28%,38%,28%,16%,26%,38%,14%,25%,33%,26%,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
# ,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
# 2022,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
# AVG,,"24,448","22,024","18,691","29,357","31,263","13,416","25,336","24,091","21,839","1,465","23,341","25,528","24,270","10,381","2,613","12,387","1,341","21,907","26,050","19,137",,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
# MAX,,"75,399","80,915","69,298","68,616","99,263","94,288","38,789","99,173","95,335","9,981","83,232","67,851","85,658","63,686","9,901","32,905","9,647","87,183","77,798","73,586",,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
# Load Factor %,,32%,27%,27%,43%,31%,14%,65%,24%,23%,15%,28%,38%,28%,16%,26%,38%,14%,25%,33%,26%,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
# ,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
# 2023,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
# AVG,,"24,447","21,997","18,687","29,359","31,263","13,418","25,338","24,094","21,837","1,465","23,344","25,533","24,276","10,380","2,618","12,388","1,340","21,909","26,053","19,139",,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
# MAX,,"75,399","80,915","69,298","68,616","99,263","94,288","38,789","99,173","95,335","9,981","83,232","67,851","85,658","63,686","9,901","32,905","9,647","87,183","77,798","73,586",,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
# Load Factor %,,32%,27%,27%,43%,31%,14%,65%,24%,23%,15%,28%,38%,28%,16%,26%,38%,14%,25%,33%,26%,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
# ,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
# ,,District 1,,,,,District 2,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
# ,Year,EP,KG,ST,YP,ME,CC,KB,HR,MI,IL-93,ZP,CK,BU,RT-67,RQ-93,QU,WC,OD,AP,LB,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
# 01-Jan-21 00:00:00,2021,9990.5,47842.0,6245.5,31534.9,30802.8,2755.4,23365.1,22789.1,22176.3,913.0717572,24808.0,20462.84257,20512.88242,10745.44476,1422.240462,14873.46192,161.7291616,21022.3941,25957.76316,17086.08622,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
# '''



# # Adjust enfor DST changes
# enb_demand_data = adjust_for_dst(enb_demand_data)
# print(f"enb_demand_data after DST adjustment: {enb_demand_data.index}")

# # Adjust processed_demand_data for DST changes
# processed_demand_data = adjust_processed_demand_data_for_dst(processed_demand_data)
# print(f"processed_demand_data after DST adjustment: {processed_demand_data.index}")

# # Debugging: Print initial date ranges before filtering
# print(f"enb_demand_data min/max dates pre filter: {enb_demand_data.index.min()}, and {enb_demand_data.index.max()}")
# print(f"processed_demand_data min/max dates pre filter: {processed_demand_data.index.min()}, and {processed_demand_data.index.max()}")
# # Set date range in system data to match the ENB data
# start_date = enb_demand_data.index.min()
# end_date = enb_demand_data.index.max()
# processed_demand_data = processed_demand_data.loc[start_date:end_date]

# # Debugging: Print date ranges after filtering
# print(f"enb_demand_data min/max dates post filter: {enb_demand_data.index.min()}, and {enb_demand_data.index.max()}")
# print(f"processed_demand_data min/max dates post filter: {processed_demand_data.index.min()}, and {processed_demand_data.index.max()}")


# # Ensure that the indices are aligned
# if not processed_demand_data.index.equals(enb_demand_data.index):
#     print("Mismatched dates between the two datasets:")
#     mismatched_dates = processed_demand_data.index.difference(enb_demand_data.index)
#     if not mismatched_dates.empty:
#         print(f"Dates in processed_demand_data not in enb_demand_data: {mismatched_dates}")
#     mismatched_dates = enb_demand_data.index.difference(processed_demand_data.index)
#     if not mismatched_dates.empty:
#         print(f"Dates in enb_demand_data not in processed_demand_data: {mismatched_dates}")
#     raise ValueError("The date indices in the two datasets do not match")


# # Convert the datetime objects to the desired format (timeseries_format2)
# processed_demand_data.index = processed_demand_data.index.strftime(timeseries_format2)
# print(f"processed_demand_data after format change: {processed_demand_data.head()}")


# filtered_data = review_enb_load(
#             processed_demand_data,
#             enb_demand_data,
#             timeseries_format2,
#             asset_group,
#             peak_demand_methodology
#         )

#print(f" filtered_data: {filtered_data}")

