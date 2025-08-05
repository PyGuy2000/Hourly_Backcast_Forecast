{
    "Input_Data": {
        "General_Data": {
            "json_data": "C:/Users/kaczanor/OneDrive - Enbridge Inc/Documents/Python/EDC Hourly Capacity Factor Q2 2024/outputs/json_data/file_data.json"
        },
        "Price_Forecast": {
            "EDC Q2 2023": 
                "Source_Attributes" : {
                            "data": "Q2-2023 Hourly Data.xlsx",
                            "sub_folder": "EDC Q2 2023 Forecast Data/",
                            "datetime_column": "begin_datetime_mpt",
                            "price_column": "price",
                            "start_year": 2023,
                            "end_year": 2037,
                            "stochastic_seeds": 50,
                            "stochastic_seeds_used": 3,
                            "base_path_processed_data": "edcq2_2023_base_path_processed_data",
                            "consolidated_hourly_file": "Date-2023-2037_consolidated_hourly_file.csv",
                            "file_name_p50": "Date-2023-2037_p50_hourly_spot_electricity.csv",
                            "image_file_name_adder": "EDC 2023",
                            "Data_Active": false
                            },
                "Target_Attributes" : {
                        "hourly_electricity": "",
                            "hourly_natural_gas": "",
                            "hourly_market_heat_rate": "",
                            "monthly_avg_electricity": "",
                            "monthly_avg_natural_gas": "",
                            "monthly_market_heat_rate": "",
                            "annual_avg_electricity": "",
                            "annual_avg_natural_gas": "",
                            "annual_market_heat_rate": "",
                            "annual_allhour_electricity_heatmap": "",
                            "annual_offpeak_electricity_heatmap": "",
                            "annual_onpeak_electricity_heatmap": "",
                            "annual_heatmap_data_market_electricity": "",
                            "annual_heatmap_data_market_naturalgas": "",
                            "annual_market_heat_rate_std_avg_heatmap_data": "",
                            "annual_generator_bid_output_file_var": "",
                            "annual_cf_output_file_var": "",
                            "annual_power_recievedratio_output_file_var": "",
                            "annual_natgas_recievedratio_output_file_var": "",
                            "monthly_generator_bid_output_file_var": "",
                            "monthly_cf_output_file_var": "",
                            "monthly_power_recievedratio_output_file_var": "",
                            "monthly_natgas_recievedratio_output_file_var": ""
                    }
		        }
    },
    "Output_Template_Data": {
        "hourly_electricity_filename_str": "hourly_electricity.csv",
        "hourly_natural_gas_filename_str": "hourly_natural_gas.csv",
        "hourly_market_heat_rate_filename_str": "hourly_market_heat_rate.csv",
        "monthly_avg_electricity_filename_str": "monthly_avg_electricity.csv",
        "monthly_avg_natural_gas_filename_str": "monthly_avg_natural_gas.csv",
        "monthly_market_heat_rate_filename_str": "monthly_market_heat_rate.csv",
        "annual_avg_electricity_filename_str": "annual_avg_electricity.csv",
        "annual_avg_natural_gas_filename_str": "annual_avg_natural_gas.csv",
        "annual_market_heat_rate_filename_str": "annual_market_heat_rate.csv",
        "annual_allhour_electricity_heatmap_filename_str": "annual_allhour_electricity_heatmap.csv",
        "annual_offpeak_electricity_heatmap_filename_str": "annual_offpeak_electricity_heatmap.csv",
        "annual_onpeak_electricity_heatmap_filename_str": "annual_onpeak_electricity_heatmap.csv",
        "annual_heatmap_data_market_electricity_filename_str": "annual_heatmap_data_market_electricity.csv",
        "annual_heatmap_data_market_naturalgas_filename_str": "annual_heatmap_data_market_naturalgas.csv",
        "annual_market_heat_rate_std_avg_heatmap_data_filename_str": "annual_market_heat_rate_std_avg_heatmap_data.csv",
        "annual_generator_bid_output_file_var": "annual_generator_bid_output.csv",
        "annual_cf_output_file_var": "annual_cf_output.csv",
        "annual_power_recievedratio_output_file_var": "annual_power_recievedratio_output.csv",
        "annual_natgas_recievedratio_output_file_var": "annual_natgas_recievedratio_output.csv",
        "monthly_generator_bid_output_file_var": "monthly_generator_bid_output.csv",
        "monthly_cf_output_file_var": "monthly_cf_output.csv",
        "monthly_power_recievedratio_output_file_var": "monthly_power_recievedratio_output.csv",
        "monthly_natgas_recievedratio_output_file_var": "monthly_natgas_recievedratio_output.csv"
    }
}