import sys
import os
import pandas as pd
import geopandas as gpd
from multiprocessing import Pool
import gep_hypertension_linear_county_prev_v01

user_dir = '/users/3/kula0049/'
base_dir = os.path.join(user_dir, 'Files/base_data')
smod_ids_dir = os.path.join(user_dir, 'urban-cooling/Data/urbanspatial-guppd-v1-gpkg')
countries_df = pd.read_excel(os.path.join(base_dir, 'Price_Prevalence/ht costs.xlsx'), sheet_name='costs')

# Age data for percent adults
age_data = pd.read_csv(os.path.join(base_dir, 'Age/IDB_02-18-2026.csv'))

country_label = 'usa'
country_smodids_path = os.path.join(smod_ids_dir, f'{country_label}_smod_id.csv')
country_smodids = pd.read_csv(country_smodids_path)['SMOD_ID'].astype(str).tolist()

# merge in ee_r264_correspondence for income group
ee_r264 = gpd.read_file(os.path.join(base_dir, 'cartographic/ee/ee_r264_correspondence.gpkg'))

baseline_risk_dict = {'1. High income: OECD': 0.4352,
                 '2. High income: nonOECD': 0.4352,
                 '3. Upper middle income': 0.3670,
                 '4. Lower middle income': 0.3670, 
                 '5. Low income': 0.3220
                 }

income_grp = ee_r264.loc[ee_r264['iso3_r250_label'].str.lower()==country_label, 'income_grp'].values[0]
baseline_risk = baseline_risk_dict[income_grp]

# Prepping age -- do I need to merge in iso3 labels?
age_data = age_data[age_data['GROUP'].notna()]

age_data = pd.merge(age_data, ee_r264,
                    how = 'left', left_on='Country/Area Name', 
                    right_on='iso3_r250_name')

# print(age_data['iso3_r250_name'].unique())
age_data = age_data[age_data['GROUP'] != '']
age_data = age_data[age_data['iso3_r250_label'].str.lower()==country_label]

age_data['GROUP_NUM'] = (
    age_data['GROUP']
    .replace({'100+': 100})
)
age_data['GROUP_NUM'] = pd.to_numeric(age_data['GROUP_NUM'], errors='coerce')
age_data['Population'] = pd.to_numeric(
    age_data['Population'].astype(str).str.replace(',', '', regex=False).str.strip(),
    errors='coerce'
)

total_pop = age_data['Population'].sum()

pop_30_79 = age_data.loc[age_data['GROUP_NUM'].between(30, 79),
    'Population'
].sum()

perc_adults = pop_30_79 / total_pop

print('dcpp: ', countries_df.loc[countries_df['iso3_r250_label'].str.lower() == country_label, 'Total cost per person in 2019 USD'].values[0], 
      'percent adults: ', perc_adults, 
      'baseline risk: ', baseline_risk)


def run():
    # Prepare argument list for multiprocessing
    args_list = [
        (smod_id, countries_df.loc[countries_df['iso3_r250_label'].str.lower() == country_label, 'Total cost per person in 2019 USD'].values[0], country_label, perc_adults, baseline_risk)
        for smod_id in country_smodids
    ]
    n_procs = 30
    with Pool(processes=n_procs) as pool:
        pool.map(process_combo, args_list)
    
def process_combo(args):
    smod_id, dcpp, country_label, perc_adults, baseline_risk = args
    print(f'Processing SMOD_ID: {smod_id} in country: {country_label}')
    try:
        gep_hypertension_linear_county_prev_v01.get_hypertension_gep(smod_id, dcpp, country_label, perc_adults, baseline_risk)
    except Exception as e:
        print(f'Error processing {smod_id} in {country_label}: {e}')

# process_combo(['22_16160', 11785.826143492188, 'usa', 0.5766864604609373, 0.4352])
if __name__ == '__main__':
    run() 