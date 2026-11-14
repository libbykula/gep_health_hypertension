import sys
import os
import pandas as pd
from multiprocessing import Pool
import gep_hypertension_v05

base_dir = '/users/3/kula0049/'
smod_ids_dir = os.path.join(base_dir, 'urban-cooling/Data/urbanspatial-guppd-v1-gpkg')
countries_df = pd.read_excel(os.path.join(base_dir, 'base_data/Price_Prevalence/ht costs.xlsx', sheet_name='costs'))

# country_labels = countries_df['iso3_r250_label'].str.lower().tolist()
# # country_labels = [c for c in country_labels if c != 'can']
# # country_labels = ['mex', 'chn', 'pol', 'khm', 'grc', 'jam']
# # country_labels = ['usa']
# # country_labels = ['usa', 'mex', 'pol', 'vnm', 'zwe']
country_labels = ['usa']
# Prevalence
prev_data = pd.read_csv(os.path.join(base_dir, 'base_data/Price_Prevalence/ht prevalence who 2021.csv'))
prev_data = prev_data[prev_data['Dim1'] == 'Both sexes']

# Age data for percent adults
age_data = pd.read_excel(os.path.join(base_dir, 'base_data/Age/IDB_11-06-2025.xlsx', sheet_name='results'))

# country_label = 'usa'
for country_label in country_labels:
    country_smodids_path = os.path.join(smod_ids_dir, f'{country_label}_smod_id.csv')
    country_smodids = pd.read_csv(country_smodids_path)['SMOD_ID'].astype(str).tolist()
    
    country_prev_data = prev_data[
        (prev_data['SpatialDimValueCode'].str.lower() == country_label) & 
        (prev_data['Period'] == 2019)
    ]
    country_prev = country_prev_data['FactValueNumeric'].values[0]
    
    # Percent of population in the adults 30-79 age group 
    perc_adults = age_data.loc[age_data['iso3_r250_label'].str.lower() == country_label, 'perc_adults'].iloc[0]

    def run():
        # Prepare argument list for multiprocessing
        args_list = [
            (smod_id, countries_df.loc[countries_df['iso3_r250_label'].str.lower() == country_label, 'Total cost per person in 2019 USD'].values[0], country_label, perc_adults, country_prev)
            for smod_id in country_smodids
        ]
        n_procs = 12
        with Pool(processes=n_procs) as pool:
            pool.map(process_combo, args_list)

    def process_combo(args):
        smod_id, dcpp, country_label, perc_adults, country_prev = args
        print(f'Processing SMOD_ID: {smod_id} in country: {country_label}')
        try:
            gep_hypertension_v05.get_hypertension_gep(smod_id, dcpp, country_label, perc_adults, country_prev)
        except Exception as e:
            print(f'Error processing {smod_id} in {country_label}: {e}')

    if __name__ == '__main__':
        run()