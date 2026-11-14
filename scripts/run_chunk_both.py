import sys
import pandas as pd
import geopandas as gpd
import gep_hypertension_v06
import gep_hypertension_v06_linear
import os

base_dir = '/users/3/kula0049/Files/base_data'
print(sys.argv)
country_label = sys.argv[1]
smod_ids = sys.argv[2].split(",")

countries_df = pd.read_csv(os.path.join(base_dir, 'Price_Prevalence/ht final costs.csv'))
prev_data = pd.read_csv(os.path.join(base_dir, 'Price_Prevalence/ht prevalence who 2021.csv'))
age_data = pd.read_csv(os.path.join(base_dir, 'Age/IDB_02-18-2026.csv'))

# age_data = pd.read_excel(os.path.join(base_dir, 'Age/IDB_11-06-2025.xlsx'), sheet_name='results')

dcpp = countries_df.loc[countries_df['iso3_r250_label'].str.lower()==country_label,'Total cost per person in 2019 USD'].values[0]
country_prev =prev_data[(prev_data['SpatialDimValueCode'].str.lower()==country_label)&(prev_data['Period']==2019)&(prev_data['Dim1']=='Both sexes')&(prev_data['Indicator']=='Prevalence of hypertension among adults aged 30-79 years, age-standardized')]['FactValueNumeric'].values[0]

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

baseline_risk = country_prev/0.76 # Prevalence/p0 = 0.76 (Average for China and Australia)

for smod_id in smod_ids:
    print("running", country_label, smod_id)
    try:
        gep_hypertension_v06.get_hypertension_gep(smod_id, dcpp, country_label, perc_adults, country_prev, baseline_risk)
    except Exception as e:
        print("FAILED", country_label, smod_id, e)

    try:
        gep_hypertension_v06_linear.get_hypertension_gep(smod_id, dcpp, country_label, perc_adults, country_prev, baseline_risk)
    except Exception as e:
        print("FAILED", country_label, smod_id, e)
