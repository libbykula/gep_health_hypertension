import sys
import pandas as pd
import gep_hypertension_v05

smod_id = sys.argv[1]

base_dir = '/users/3/kula0049/Files/base_data/'
countries_df = pd.read_excel(base_dir + 'Price_Prevalence/ht costs.xlsx', sheet_name='costs')
prev_data = pd.read_csv(base_dir + 'Price_Prevalence/ht prevalence who 2021.csv')
age_data = pd.read_excel(base_dir + 'Age/IDB_11-06-2025.xlsx', sheet_name='results')

country_label = 'idn'   # Indonesia

dcpp = countries_df.loc[countries_df['iso3_r250_label'].str.lower()==country_label,'Total cost per person in 2019 USD'].values[0]
country_prev = prev_data[(prev_data['SpatialDimValueCode'].str.lower()==country_label)&(prev_data['Period']==2019)]['FactValueNumeric'].values[0]
perc_adults = age_data.loc[age_data['iso3_r250_label'].str.lower()==country_label,'perc_adults'].iloc[0]

print("running",smod_id)
gep_hypertension_v05.get_hypertension_gep(smod_id, dcpp, country_label, perc_adults, country_prev)
