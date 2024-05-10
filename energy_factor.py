import pandas as pd

# Read the energy data with correct decimal and thousands separators
energy_data = pd.read_csv('data/energy_smard.csv', delimiter=',', decimal='.', thousands=None)
energy_data.columns = [
    'Datum von', 'Datum bis', 'Biomasse [MWh]', 'Wasserkraft [MWh]', 
    'Wind Offshore [MWh]', 'Wind Onshore [MWh]', 'Photovoltaik [MWh]', 
    'Sonstige Erneuerbare [MWh]', 'Kernenergie [MWh]', 'Braunkohle [MWh]', 
    'Steinkohle [MWh]', 'Erdgas [MWh]', 'Pumpspeicher [MWh]', 
    'Sonstige Konventionelle [MWh]'
]

# Display first few rows to inspect data loading
print("Energy Data (first few rows):")
print(energy_data.head())

# Convert all energy values to numeric, coercing errors to NaN
energy_columns = [
    'Biomasse [MWh]', 'Wasserkraft [MWh]', 'Wind Offshore [MWh]', 
    'Wind Onshore [MWh]', 'Photovoltaik [MWh]', 'Sonstige Erneuerbare [MWh]', 
    'Kernenergie [MWh]', 'Braunkohle [MWh]', 'Steinkohle [MWh]', 
    'Erdgas [MWh]', 'Pumpspeicher [MWh]', 'Sonstige Konventionelle [MWh]'
]
energy_data[energy_columns] = energy_data[energy_columns].apply(pd.to_numeric, errors='coerce')

# Verify conversion results
print("\nConverted Energy Data (first few rows):")
print(energy_data[energy_columns].head())

# Read the energy sources data
energy_sources = pd.read_csv('data/energy_sources.csv')

# Create dictionaries for renewable status and emission factors
renewable_status = dict(zip(energy_sources['sourcename'], energy_sources['renewable']))
emission_factors = dict(zip(energy_sources['sourcename'], energy_sources['emissionfactor']))

# Mapping column names to the corresponding source names in the dictionary
column_to_source = {
    'Biomasse [MWh]': 'Biomass',
    'Wasserkraft [MWh]': 'Hydropower',
    'Wind Offshore [MWh]': 'Offshore Wind',
    'Wind Onshore [MWh]': 'Onshore Wind',
    'Photovoltaik [MWh]': 'Photovoltaic (Solar Power)',
    'Sonstige Erneuerbare [MWh]': 'Other Renewables',
    'Kernenergie [MWh]': 'Nuclear Energy',
    'Braunkohle [MWh]': 'Lignite (Brown Coal)',
    'Steinkohle [MWh]': 'Hard Coal',
    'Erdgas [MWh]': 'Natural Gas',
    'Pumpspeicher [MWh]': 'Pumped Storage',
    'Sonstige Konventionelle [MWh]': 'Other Conventional'
}

# Calculate the percentage for each source and total emission factor
def calculate_percentages_and_emission_factor(row):
    total_energy = row[energy_columns].sum()
    
    if total_energy == 0:
        return pd.Series([0, 0, 0], index=['renewablespercentage', 'conventionalpercentage', 'Total Emission Factor'])
    
    total_renewable = 0
    total_non_renewable = 0
    total_emissions = 0
    
    for column, source in column_to_source.items():
        energy = row[column]
        if pd.notnull(energy):
            if renewable_status[source]:
                total_renewable += energy
            else:
                total_non_renewable += energy
            
            total_emissions += energy * emission_factors[source]
    
    percent_renewable = (total_renewable / total_energy) * 100
    percent_conventional = (total_non_renewable / total_energy) * 100
    total_emission_factor = total_emissions / total_energy  # in gCO2e/kWh

    return pd.Series([percent_renewable, percent_conventional, total_emission_factor], 
                     index=['renewablespercentage', 'conventionalpercentage', 'Total Emission Factor'])

# Apply the function to calculate percentages and emission factor
energy_data[['renewablespercentage', 'conventionalpercentage', 'Total Emission Factor']] = energy_data.apply(calculate_percentages_and_emission_factor, axis=1)

# Prepare the final DataFrame
final_df = energy_data[['Datum von', 'renewablespercentage', 'conventionalpercentage', 'Total Emission Factor']]
final_df.rename(columns={'Datum von': 'startdate'}, inplace=True)
final_df['factorunit'] = 'gCO2e/kWh'

# Print the results for debugging
print("\nFinal DataFrame (first few rows):")
print(final_df.head(20))

# Optionally, save the results to a new CSV
final_df.to_csv('data/energy.csv', index=False)
