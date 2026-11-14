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

county_boundaries = county_boundaries.to_crs('EPSG:4326')

metro_boundaries = gpd.read_file(
    os.path.join(base_dir, 'cartographic', 'tl_2019_us_cbsa', 'metros_boundaries.gpkg'))

metro_boundaries = metro_boundaries.to_crs('EPSG:4326')

metro_counties = gpd.clip(county_boundaries, metro_boundaries, keep_geom_type = True)

metro_counties['st'] = metro_counties['STATEFP'].astype(int)

fips_df = pd.read_csv(os.path.join(base_dir, 'cartographic', 'us-state-ansi-fips.csv'))
fips_df['st'] = fips_df[' st'].astype(int)

fips_df = fips_df.drop_duplicates(subset='st')
merged = pd.merge(metro_counties, fips_df, on='st', validate='m:1')

metro_counties_path = os.path.join(base_dir, 'cartographic', 'cb_2018_us_county_500k', 'metropolitan_counties.gpkg')

merged.to_file(metro_counties_path, driver='GPKG')