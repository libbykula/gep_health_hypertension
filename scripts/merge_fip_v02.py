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
    os.path.join(base_dir, 'cartographic', 'cb_2018_us_county_500k', 'counties_w_state.gpkg'))

metro_boundaries = gpd.read_file(
    os.path.join(base_dir, 'cartographic', 'tl_2019_us_cbsa', 'metros_boundaries.gpkg'))

metro_boundaries = metro_boundaries.to_crs('EPSG:4326')

metro_counties = gpd.clip(county_boundaries, metro_boundaries)
print(metro_counties.shape)

metro_counties_path = os.path.join(base_dir, 'cartographic', 'cb_2018_us_county_500k', 'metropolitan_counties.gpkg')
metro_counties.to_file(metro_counties_path, driver='GPKG')
