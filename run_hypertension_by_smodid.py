import sys
import os
import pandas as pd
from multiprocessing import Pool
import gep_hypertension_v03

smod_ids_dir = 'D:/base_data/GEP/Data/Urban Boundaries/urbanspatial-guppd-v1-gpkg/country_smodids'
countries_df = pd.read_csv('D:/base_data/GEP/Data/Price_Prevalence/direct_costs_per_person_by_country.csv')

# country_labels = countries_df['iso3_r250_label'].str.lower().tolist()
# country_labels = [c for c in country_labels if c != 'can']
country_labels = ['usa']
country_label = 'usa'
# for country_label in country_labels:
country_smodids_path = os.path.join(smod_ids_dir, f'{country_label}_smod_id.csv')
country_smodids = pd.read_csv(country_smodids_path)['SMOD_ID'].astype(str).tolist()
    # for smod_id in country_smodids:
    #     args_list = [smod_id, countries_df.loc[countries_df['iso3_r250_label'].str.lower() == country_label, 'DCpp'].values[0]]
    #                                                     country_label=country_label

    # # for smod_id in country_smodids:

def run():
    # Prepare argument list for multiprocessing
    args_list = [
        (smod_id, countries_df.loc[countries_df['iso3_r250_label'].str.lower() == country_label, 'DCpp'].values[0], country_label)
        for smod_id in country_smodids
    ]

    n_procs = 12
    with Pool(processes=n_procs) as pool:
        pool.map(process_combo, args_list)

def process_combo(args):
    smod_id, dcpp, country_label = args
    print(f'Processing SMOD_ID: {smod_id} in country: {country_label}')
    try:
        gep_hypertension_v03.get_hypertension_gep(smod_id, dcpp, country_label)
    except Exception as e:
        print(f'Error processing {smod_id} in {country_label}: {e}')

if __name__ == '__main__':
    run()