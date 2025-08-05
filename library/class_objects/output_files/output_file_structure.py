from library.class_objects.output_files.output_file import OutputFile

def build_output_file_structure(output_files: list[OutputFile]) -> dict:
    # This routine passes the invidual class instances for the XXXX to a dictionary.
    # It returns a list of these dictionaries 
    consolidated_hourly = {}
    hourly_electricity = {}
    hourly_natural_gas = {}
    hourly_market_heat_rate = {}
    monthly_avg_electricity = {}
    monthly_avg_natural_gas = {}
    monthly_market_heat_rate = {}
    annual_avg_electricity = {}
    annual_avg_natural_gas = {}
    annual_market_heat_rate = {}
    annual_allhour_electricity_heatmap = {}
    annual_offpeak_electricity_heatmap = {}
    annual_onpeak_electricity_heatmap = {}
    annual_heatmap_data_market_electricity = {}
    annual_heatmap_data_market_naturalgas = {}
    annual_market_heat_rate_std_avg_heatmap_data = {}
    annual_generator_bid_output_file_var = {}
    annual_cf_output_file_var = {}
    annual_power_recievedratio_output_file_var = {}
    annual_natgas_recievedratio_output_file_var = {}
    monthly_generator_bid_output_file_var = {}
    monthly_cf_output_file_var = {}
    monthly_power_recievedratio_output_file_var = {}
    monthly_natgas_recievedratio_output_file_var = {}
    P10_hourly_spot_electricity = {}
    P25_hourly_spot_electricity = {}
    P50_hourly_spot_electricity = {}
    P75_hourly_spot_electricity = {}
    P90_hourly_spot_electricity = {}
    top_hour_percentage_summary = {}
    P10_hourly_spot_natural_gas = {}
    P25_hourly_spot_natural_gas = {}
    P50_hourly_spot_natural_gas = {}
    P75_hourly_spot_natural_gas = {}
    P90_hourly_spot_natural_gas = {}
    combined_forecast_ = {}
    combined_forecast_with_Top_Percent_Price = {}

    for file in output_files:
        consolidated_hourly[file.consolidated_hourly]  = file.consolidated_hourly
        hourly_electricity[file.hourly_electricity]  = file.hourly_electricity
        hourly_natural_gas[file.hourly_natural_gas]  = file.hourly_natural_gas
        hourly_market_heat_rate[file.hourly_market_heat_rate]  = file.hourly_market_heat_rate
        monthly_avg_electricity[file.monthly_avg_electricity]  = file.monthly_avg_electricity
        monthly_avg_natural_gas[file.monthly_avg_natural_gas]  = file.monthly_avg_natural_gas
        monthly_market_heat_rate[file.monthly_market_heat_rate]  = file.monthly_market_heat_rate
        annual_avg_electricity[file.annual_avg_electricity]  = file.annual_avg_electricity
        annual_avg_natural_gas[file.annual_avg_natural_gas]  = file.annual_avg_natural_gas
        annual_market_heat_rate[file.annual_market_heat_rate]  = file.annual_market_heat_rate
        annual_allhour_electricity_heatmap[file.annual_allhour_electricity_heatmap]  = file.annual_allhour_electricity_heatmap
        annual_offpeak_electricity_heatmap[file.annual_offpeak_electricity_heatmap]  = file.annual_offpeak_electricity_heatmap
        annual_onpeak_electricity_heatmap[file.annual_onpeak_electricity_heatmap]  = file.annual_onpeak_electricity_heatmap
        annual_heatmap_data_market_electricity[file.annual_heatmap_data_market_electricity]  = file.annual_heatmap_data_market_electricity
        annual_heatmap_data_market_naturalgas[file.annual_heatmap_data_market_naturalgas]  = file.annual_heatmap_data_market_naturalgas
        annual_market_heat_rate_std_avg_heatmap_data[file.annual_market_heat_rate_std_avg_heatmap_data]  = file.annual_market_heat_rate_std_avg_heatmap_data
        annual_generator_bid_output_file_var[file.annual_generator_bid_output_file_var]  = file.annual_generator_bid_output_file_var
        annual_cf_output_file_var[file.annual_cf_output_file_var]  = file.annual_cf_output_file_var
        annual_power_recievedratio_output_file_var[file.annual_power_recievedratio_output_file_var]  = file.annual_power_recievedratio_output_file_var
        annual_natgas_recievedratio_output_file_var[file.annual_natgas_recievedratio_output_file_var]  = file.annual_natgas_recievedratio_output_file_var
        monthly_generator_bid_output_file_var[file.monthly_generator_bid_output_file_var]  = file.monthly_generator_bid_output_file_var
        monthly_cf_output_file_var[file.monthly_cf_output_file_var]  = file.monthly_cf_output_file_var
        monthly_power_recievedratio_output_file_var[file.monthly_power_recievedratio_output_file_var]  = file.monthly_power_recievedratio_output_file_var
        monthly_natgas_recievedratio_output_file_var[file.monthly_natgas_recievedratio_output_file_var]  = file.monthly_natgas_recievedratio_output_file_var
        P10_hourly_spot_electricity[file.P10_hourly_spot_electricity]  = file.P10_hourly_spot_electricity
        P25_hourly_spot_electricity[file.P25_hourly_spot_electricity ] = file.P25_hourly_spot_electricity
        P75_hourly_spot_electricity[file.P75_hourly_spot_electricity]  = file.P75_hourly_spot_electricity
        P90_hourly_spot_electricity[file.P90_hourly_spot_electricity]  = file.P90_hourly_spot_electricity
        top_hour_percentage_summary[file.top_hour_percentage_summary]  = file.top_hour_percentage_summary
        P10_hourly_spot_natural_gas[file.P10_hourly_spot_natural_gas]  = file.P10_hourly_spot_natural_gas
        P25_hourly_spot_natural_gas[file.P25_hourly_spot_natural_gas]  = file.P25_hourly_spot_natural_gas
        P50_hourly_spot_natural_gas[file.P50_hourly_spot_natural_gas]  = file.P50_hourly_spot_natural_gas
        P75_hourly_spot_natural_gas[file.P75_hourly_spot_natural_gas]  = file.P75_hourly_spot_natural_gas
        P90_hourly_spot_natural_gas[file.P90_hourly_spot_natural_gas]  = file.P90_hourly_spot_natural_gas
        combined_forecast_[file.combined_forecast_]  = file.combined_forecast_
        combined_forecast_with_Top_Percent_Price[file.combined_forecast_with_Top_Percent_Price] = file.combined_forecast_with_Top_Percent_Price


    return {
        'consolidated_hourly': consolidated_hourly,
        'hourly_electricity': hourly_electricity,
        'hourly_natural_gas': hourly_natural_gas,
        'hourly_market_heat_rate': hourly_market_heat_rate,
        'monthly_avg_electricity': monthly_avg_electricity,
        'monthly_avg_natural_gas': monthly_avg_natural_gas,
        'monthly_market_heat_rate': monthly_market_heat_rate,
        'annual_avg_electricity': annual_avg_electricity,
        'annual_avg_natural_gas': annual_avg_natural_gas,
        'annual_market_heat_rate': annual_market_heat_rate,
        'annual_allhour_electricity_heatmap': annual_allhour_electricity_heatmap,
        'annual_offpeak_electricity_heatmap': annual_offpeak_electricity_heatmap,
        'annual_onpeak_electricity_heatmap': annual_onpeak_electricity_heatmap,
        'annual_heatmap_data_market_electricity': annual_heatmap_data_market_electricity,
        'annual_heatmap_data_market_naturalgas': annual_heatmap_data_market_naturalgas,
        'annual_market_heat_rate_std_avg_heatmap_data': annual_market_heat_rate_std_avg_heatmap_data,
        'annual_generator_bid_output_file_var': annual_generator_bid_output_file_var,
        'annual_cf_output_file_var': annual_cf_output_file_var,
        'annual_power_recievedratio_output_file_var': annual_power_recievedratio_output_file_var,
        'annual_natgas_recievedratio_output_file_var': annual_natgas_recievedratio_output_file_var,
        'monthly_generator_bid_output_file_var': monthly_generator_bid_output_file_var,
        'monthly_cf_output_file_var': monthly_cf_output_file_var,
        'monthly_power_recievedratio_output_file_var': monthly_power_recievedratio_output_file_var,
        'monthly_natgas_recievedratio_output_file_var': monthly_natgas_recievedratio_output_file_var,
        'P10_hourly_spot_electricity': P10_hourly_spot_electricity,
        'P25_hourly_spot_electricity': P25_hourly_spot_electricity,
        'P50_hourly_spot_electricity': P50_hourly_spot_electricity,
        'P75_hourly_spot_electricity': P75_hourly_spot_electricity,
        'P90_hourly_spot_electricity': P90_hourly_spot_electricity,
        'top_hour_percentage_summary': top_hour_percentage_summary,
        'P10_hourly_spot_natural_gas': P10_hourly_spot_natural_gas,
        'P25_hourly_spot_natural_gas': P25_hourly_spot_natural_gas,
        'P50_hourly_spot_natural_gas': P50_hourly_spot_natural_gas,
        'P75_hourly_spot_natural_gas': P75_hourly_spot_natural_gas,
        'P90_hourly_spot_natural_gas': P90_hourly_spot_natural_gas,
        'combined_forecast_': combined_forecast_,
        'combined_forecast_with_Top_Percent_Price': combined_forecast_with_Top_Percent_Price,
    }