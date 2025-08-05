import pandas as pd
import numpy as np

# Option #1
#Multiple Year csv files for hisoricals
def create_hourly_gas(annual_gas_price, historical_year):
    # Load the historical hourly data for the selected year
    historical_file_path = f'historical_data/{historical_year}.csv'
    historical_data = pd.read_csv(historical_file_path, parse_dates=['datetime'], index_col='datetime')
    
    # Calculate the hourly index
    hourly_average = historical_data['price'].mean()
    hourly_index = historical_data['price'] / hourly_average
    
    # Apply the hourly index to the annual forecast price
    hourly_forecast = hourly_index * annual_gas_price
    
    # Create a DataFrame for the hourly forecast
    hourly_forecast_df = pd.DataFrame({'datetime': historical_data.index, 'price': hourly_forecast.values})
    
    return hourly_forecast_df

# Example usage
# annual_gas_price = 50  # Example annual forecast price in $/MWh
# historical_year = 2020  # Example year to use for the historical shape
# hourly_natgas = create_hourly_gas(annual_gas_price, historical_year)

# # Display the first few rows of the result
# print(hourly_natgas.head())
#####################################################

# Option #2
# Single csv file for Historical data
def create_hourly_gas(annual_gas_price, historical_year):
    # Load the historical hourly data from the single CSV file
    historical_data = pd.read_csv('historical_data/combined_data.csv', parse_dates=['DateTime'])
    
    # Filter the data by the selected year
    historical_data['year'] = historical_data['DateTime'].dt.year
    historical_data_year = historical_data[historical_data['year'] == historical_year]
    
    # Calculate the hourly index
    hourly_average = historical_data_year['NAT_GAS_PRICE'].mean()
    hourly_index = historical_data_year['NAT_GAS_PRICE'] / hourly_average
    
    # Apply the hourly index to the annual forecast price
    hourly_forecast = hourly_index * annual_gas_price
    
    # Create a DataFrame for the hourly forecast
    hourly_forecast_df = pd.DataFrame({'DateTime': historical_data_year['DateTime'], 'price': hourly_forecast.values})
    
    return hourly_forecast_df

# Example usage
# annual_gas_price = 50  # Example annual forecast price in $/MWh
# historical_year = 2000  # Example year to use for the historical shape
# hourly_natgas = create_hourly_gas(annual_gas_price, historical_year)

# # Display the first few rows of the result
# print(hourly_natgas.head())

##################################################

#Option #3
#Monthly forecast Data
def create_hourly_gas_monthly_forecast(monthly_forecast_file, historical_data_file, historical_year):
    # Load the historical hourly data from the single CSV file
    historical_data = pd.read_csv(historical_data_file, parse_dates=['DateTime'])
    
    # Filter the data by the selected year
    historical_data['year'] = historical_data['DateTime'].dt.year
    historical_data_year = historical_data[historical_data['year'] == historical_year]
    
    # Calculate the hourly index
    hourly_average = historical_data_year['NAT_GAS_PRICE'].mean()
    hourly_index = historical_data_year['NAT_GAS_PRICE'] / hourly_average
    
    # Load the monthly forecast data
    monthly_forecast = pd.read_csv(monthly_forecast_file, parse_dates=['Date'])
    monthly_forecast.set_index('Date', inplace=True)
    
    # Create an empty DataFrame to store the hourly forecast
    hourly_forecast_df = pd.DataFrame()
    
    # Iterate through each month in the forecast
    for month_start in monthly_forecast.index:
        month_end = (month_start + pd.DateOffset(months=1)) - pd.DateOffset(days=1)
        monthly_price = monthly_forecast.loc[month_start, 'Gas Price$/GJ']
        
        # Filter the historical data for the corresponding month
        historical_data_month = historical_data_year[(historical_data_year['DateTime'] >= month_start) & (historical_data_year['DateTime'] <= month_end)]
        
        # Apply the hourly index to the monthly forecast price
        hourly_forecast = hourly_index.loc[historical_data_month.index] * monthly_price
        
        # Append the hourly forecast to the DataFrame
        hourly_forecast_df = hourly_forecast_df.append(pd.DataFrame({'DateTime': historical_data_month['DateTime'], 'price': hourly_forecast.values}))
    
    return hourly_forecast_df

# Example usage
monthly_forecast_file = 'monthly_forecast.csv'  # Path to the monthly forecast data file
historical_data_file = 'historical_data/combined_data.csv'  # Path to the historical data file
historical_year = 2020  # Example year to use for the historical shape
hourly_natgas = create_hourly_gas_monthly_forecast(monthly_forecast_file, historical_data_file, historical_year)

# Display the first few rows