import sys
import pandas as pd
import gep_hypertension_v05
import os

base_dir = '/users/3/kula0049/Files/base_data'
country_label = sys.argv[1]
smod_ids = sys.argv[2].split(",")

countries_df = pd.read_excel(os.path.join(base_dir, 'Price_Prevalence/ht costs.xlsx'), sheet_name='costs')
prev_data = pd.read_csv(os.path.join(base_dir, 'Price_Prevalence/ht prevalence who 2021.csv'))
age_data = pd.read_excel(os.path.join(base_dir, 'Age/IDB_11-06-2025.xlsx'), sheet_name='results')

dcpp = countries_df.loc[countries_df['iso3_r250_label'].str.lower()==country_label,'Total cost per person in 2019 USD'].values[0]
country_prev =prev_data[(prev_data['SpatialDimValueCode'].str.lower()==country_label)&(prev_data['Period']==2019)&(prev_data['Dim1']=='Both sexes')&(prev_data['Indicator']=='Prevalence of hypertension among adults aged 30-79 years, age-standardized')]['FactValueNumeric'].values[0]
perc_adults = age_data.loc[age_data['iso3_r250_label'].str.lower()==country_label,'perc_adults'].iloc[0]

for smod_id in smod_ids:
    print("running", country_label, smod_id)
    try:
        gep_hypertension_v05.get_hypertension_gep(smod_id, dcpp, country_label, perc_adults, country_prev)
    except Exception as e:
        print("FAILED", country_label, smod_id, e)
