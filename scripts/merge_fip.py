# Libby Kula
#  Global GEP Hypertension
# 5/26/2026
# Update: merging in FIP state code to match up counties 

import os
import numpy as np
import geopandas as gpd
import pandas as pd
import re

dir = '/users/3/kula0049/'
base_dir = os.path.join(dir, 'Files/base_data')

county_boundaries = gpd.read_file(
    os.path.join(base_dir, 'cartographic', 'cb_2018_us_county_500k', 'cb_2018_us_county_500k.shp'))

# county_boundaries = gpd.read_file(
#     os.path.join(base_dir, 'cartographic', 'cb_2018_us_county_500k', 'metropolitan_counties.gpkg'))

county_boundaries['st'] = county_boundaries['STATEFP'].astype(int)

fips_df = pd.read_csv(os.path.join(base_dir, 'cartographic', 'us-state-ansi-fips.csv'))
fips_df['st'] = fips_df[' st'].astype(int)

merged = pd.merge(county_boundaries, fips_df, on='st')
merged = merged.to_crs('EPSG:4326')

merged.to_file(os.path.join(base_dir, 
                            'cartographic', 
                            'cb_2018_us_county_500k', 
                            'counties_w_state.gpkg'), driver='GPKG')