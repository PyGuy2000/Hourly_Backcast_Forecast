import pandas as pd 
import numpy as np 
from scipy.signal import find_peaks 
from statsmodels.tsa.statespace.sarimax import SARIMAX 
import matplotlib.pyplot as plt 
import seaborn as sns 

from library.class_objects.other_classes.classes import TrackedDict, ForecastFile

# # Load data 
# data = pd.read_csv('power_demand.csv', parse_dates=['Date'], dayfirst=True) 
# # # Ensure the Date column is datetime type and set it as the index 
# data['Date'] = pd.to_datetime(data['Date'], format='%d-%b-%y %H:%M:%S') 
# data.set_index('Date', inplace=True)

def find_monthly_peaks(data): 
    # Find the maximum value for each month and graph the results
    monthly_peaks = data.resample('M').max()
    print(monthly_peaks)

    plt.figure(figsize=(10, 6))

    # plt.plot(monthly_peaks, label='Hourly Load')
    # plt.scatter(monthly_peaks.index, monthly_peaks, color='red', label='Monthly Peaks')
    
    if isinstance(monthly_peaks, pd.Series):
        plt.plot(monthly_peaks.index, monthly_peaks, label='Load')
        plt.scatter(monthly_peaks.index, monthly_peaks, color='red', label='Monthly Peaks')
    else:

        for column in monthly_peaks.columns:
            plt.plot(monthly_peaks.index, monthly_peaks[column], label=f'{column} Load')
            plt.scatter(monthly_peaks.index, monthly_peaks[column], color='red', label=f'{column} Monthly Peaks')
    
    
    plt.legend()
    plt.title('Monthly Peaks in Load Data')
    plt.show()

    return monthly_peaks


###################
def calculate_peak_stats(data):
    # Calculate peak statistics for each load point and store results in a dictionary for each load point 
    
    peak_stats = {} 
    
    for column in data.columns: 
        # Clean the data: remove commas and convert to numeric
        clean_data = data[column].replace({',': ''}, regex=True).astype(float)

        # Find all peaks 
        #peaks, _ = find_peaks(clean_data[column])
        peaks, _ = find_peaks(clean_data) 
        peak_data = data.iloc[peaks]
        
        # Determine monthly frequency and average duration of peaks 
        monthly_peak_count = peak_data.resample('M').count() 
        average_duration = peak_data.resample('M').apply(lambda x: (x.index[-1] - x.index[0]).total_seconds() / 3600 if len(x) > 1 else 0)
        # Store results 
        peak_stats[column] = {
            'monthly_peak_count': monthly_peak_count,
            'average_duration': average_duration
        }

    # Create visualization for peak stats
    plt.figure(figsize=(10, 6))
    for column in peak_stats:
        plt.plot(peak_stats[column]['monthly_peak_count'], label=f'{column} Peak Count')
    plt.legend()
    plt.title('Monthly Peak Count for Load Points')
    plt.show()

    return peak_stats



####################
def calculate_correlations(data):

    # Clean the data: remove commas and convert to numeric
    clean_data = data.replace({',': ''}, regex=True).astype(float)

    enb_load_correlations = clean_data.corr() 
    #print(enb_load_correlations) 

    # Plot the correlations     
    plt.figure(figsize=(10, 8)) 
    sns.heatmap(enb_load_correlations, annot=True, cmap='coolwarm') 
    plt.title('Correlation between different load points') 
    plt.show()

    return enb_load_correlations

###############################

def create_demand_forecast(data, steps=24*30):
    forecasts = {}
    
    for column in data.columns:
        # Fit a SARIMAX model for each load point
        model = SARIMAX(data[column], order=(1, 1, 1), seasonal_order=(1, 1, 1, 24))
        results = model.fit()
        
        # Forecast future peaks
        forecast = results.get_forecast(steps=steps)
        
        # Forecast for the next time period
        forecast_mean = forecast.predicted_mean
        
        # Store the results
        forecasts[column] = forecast_mean
        
        # Plot forecast
        plt.figure(figsize=(15, 6))
        data[column].plot(label='Historical Data')
        forecast_mean.plot(label='Forecasted Peaks', color='red')
        plt.title(f'Forecast for {column}')
        plt.legend()
        plt.show()
    
    return forecasts

###############################
def enb_load_stats(filtered_data, timeseries_format):
    # Load data is using the same format as the AESO data and requires DST adjustments 

    #Convert all columns to numeric, coerce errors to NaN to handle any non-numeric values
    filtered_data_clean = filtered_data.apply(pd.to_numeric, errors='coerce')
    #print(f"filtered_data: {filtered_data_clean.head()}")

    #Replace NaN values with 0
    filtered_data_clean.fillna(0, inplace=True)

    # Filtering load data by year and performing annual summary analysis 
    annual_summary = filtered_data_clean.resample('Y').agg(['sum', 'mean', 'max'])

    # Create Load Factor % column as AVG/MAX and format as percentage
    load_factor = (annual_summary.xs('mean', level=1, axis=1) / annual_summary.xs('max', level=1, axis=1)) * 100
    load_factor.columns = [f' {col} Load Factor %' for col in load_factor.columns]
    annual_summary = pd.concat([annual_summary, load_factor], axis=1)

    #Format numbers to '0,000' and Load Factor % to '0.0%
    formatted_summary = annual_summary.copy()
    formatted_summary.iloc[:, :-load_factor.shape[1]] = formatted_summary.iloc[:, :-load_factor.shape[1]].applymap(lambda x: f'{x:,.0f}' if pd.notna(x) else x).map(lambda df: df)
    formatted_summary.iloc[:,-load_factor.shape[1]:] = load_factor.applymap(lambda x: f'{x:0.1f}%' if pd.notna(x) else x).map(lambda df: df)

    #print("Annual Summary (Sum, Mean, Max, Load Factor %):\n", annual_summary)

    #output_path = r'C:\Users\kaczanor\OneDrive - Enbridge Inc\Documents\Python\AB Electricity Sector Stats\output_data\CSV_Folder\enb_load_stats.csv'
    output_path = r'C:\Users\kaczanor\OneDrive - Enbridge Inc\Documents\Python\EDC Hourly Capacity Factor Q2 2024\outputs\csv_data\ENB_Load_Analysis_Data'
    formatted_summary.to_csv(output_path)

    return formatted_summary 

###############################    
def filter_data_by_asset_group(df, asset_group): 
    # Filter data by specified asset group (e.g. selecting specific columns for specific stations) 
    filtered_data = df[asset_group]
    filtered_data.index = df.index  # Ensure the index is retained
    return filtered_data

###############################
def review_enb_load(
            processed_demand_data,
            enb_demand_data,
            timeseries_format2,
            asset_group,
            peak_demand_methodology,
            gbl_tracked_loaded_dict_json_file_data
):

    # Ensure the Date columns for the System and ENB Load is datetime type and set it as the index 
    #SYSTEM LOAD
    #processed_demand_data_copy.rename(columns={'DateTime': 'Date'}, inplace=True)
    #processed_demand_data_copy['Date'] = pd.to_datetime(processed_demand_data_copy['Date'], format=timeseries_format) 
    # processed_demand_data_copy.set_index('Date', inplace=True)
    # print(f"processed_demand_data_copy: {processed_demand_data_copy.head()}")

    #ENB LOAD
    enb_demand_data['Date'] = pd.to_datetime(enb_demand_data['Date'], format=timeseries_format2) 
    enb_demand_data.set_index('Date', inplace=True)
    print(f"enb_demand_data: {enb_demand_data.head()}")

    #Filter site data by asset group
    filtered_data = filter_data_by_asset_group(enb_demand_data, asset_group) 
    print("Filtered Data for Asset Group:\n", filtered_data.head())

    # Run the load review function 
    enb_annual_load_stats = enb_load_stats(filtered_data, timeseries_format2) 
    print("Annual Load Stats:\n", enb_annual_load_stats)

    #Find monthly peaks
    enb_monthly_peaks = find_monthly_peaks(filtered_data)
    print("Monthly Peaks:\n", enb_monthly_peaks)

    # Calculate peak statistics for each load point
    enb_peak_stats = calculate_peak_stats(filtered_data)
    print("Peak Stats:\n", enb_peak_stats)

    # Calculate correlations between load points
    enb_load_correlations = calculate_correlations(filtered_data)
    print("Load Correlations:\n", enb_load_correlations)

    # Create a demand forecast for one of the load points
    forecast, forecast_mean = create_demand_forecast(filtered_data, 'Load_Point_1')
    print("Forecast:\n", forecast)

    # save the annual summary to a csv file
    #path = r'C:\Users\kaczanor\OneDrive - Enbridge Inc\Documents\Python\AB Electricity Sector Stats\output_data\CSV_Folder\enb_annual_load_stats.csv'
    path = r'C:\Users\kaczanor\OneDrive - Enbridge Inc\Documents\Python\EDC Hourly Capacity Factor Q2 2024\outputs\csv_data\ENB_Load_Analysis_Data\enb_annual_load_stats.csv'
    enb_annual_load_stats.to_csv(path)

    # save the monthly peaks to a csv file
    #path = r'C:\Users\kaczanor\OneDrive - Enbridge Inc\Documents\Python\AB Electricity Sector Stats\output_data\CSV_Folder\enb_monthly_peaks.csv'
    path = r'C:\Users\kaczanor\OneDrive - Enbridge Inc\Documents\Python\EDC Hourly Capacity Factor Q2 2024\outputs\csv_data\ENB_Load_Analysis_Data\enb_monthly_peaks.csv'
    enb_monthly_peaks.to_csv(path)

    # save the peak stats to a csv file
    #path = r'C:\Users\kaczanor\OneDrive - Enbridge Inc\Documents\Python\AB Electricity Sector Stats\output_data\CSV_Folder\enb_peak_stats.csv'
    #enb_peak_stats.to_csv(path)

    # save the correlations to a csv file
    #path = r'C:\Users\kaczanor\OneDrive - Enbridge Inc\Documents\Python\AB Electricity Sector Stats\output_data\CSV_Folder\enb_load_correlations.csv'
    path = r'C:\Users\kaczanor\OneDrive - Enbridge Inc\Documents\Python\EDC Hourly Capacity Factor Q2 2024\outputs\csv_data\ENB_Load_Analysis_Data\enb_load_correlations.csv'
    enb_load_correlations.to_csv(path)

    #save the forecast to a csv file
    path = r'C:\Users\kaczanor\OneDrive - Enbridge Inc\Documents\Python\AB Electricity Sector Stats\output_data\CSV_Folder\enb_demand_forecast.csv'
    path =  r'C:\Users\kaczanor\OneDrive - Enbridge Inc\Documents\Python\EDC Hourly Capacity Factor Q2 2024\outputs\csv_data\ENB_Load_Analysis_Data\enb_demand_forecast.csv'
    forecast.to_csv(path)

    
    return filtered_data

