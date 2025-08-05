import pandas as pd

def remove_duplicate_columns(df):
    print(f" df.columns: {df.columns}")
    print(f" df.columns.duplicated(): {df.columns.duplicated()}")
    df = df.loc[:, ~df.columns.duplicated()]
    print(df.columns)
    return df

input_path = r'C:\Users\kaczanor\OneDrive - Enbridge Inc\Desktop\Metered Volume Data\Consolidated Data\Consolidated Generation Metered Volumes_2000_to_2024.csv'
output_path = r'C:\Users\kaczanor\OneDrive - Enbridge Inc\Desktop\Metered Volume Data\Consolidated Data'
df = pd.read_csv(input_path)

df_clean = remove_duplicate_columns(df)

df.drop_duplicates()
df.to_csv(output_path + 'Consolidated Generation Metered Volumes_2000_to_2024.csv', index=False)
