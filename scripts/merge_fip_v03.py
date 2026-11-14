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

county_boundaries = county_boundaries.to_crs('EPSG:4326')

metro_boundaries = gpd.read_file(
    os.path.join(base_dir, 'cartographic', 'tl_2019_us_cbsa', 'metros_boundaries.gpkg'))

metro_boundaries = metro_boundaries.to_crs('EPSG:4326')

# Option 1: Counties whose centroid falls within metro boundaries (fast, clean)
metro_counties = county_boundaries[
    county_boundaries.centroid.within(metro_boundaries.union_all())
]

# # Option 2: Counties that are "almost fully" contained (area overlap threshold)
# metro_union = metro_boundaries.union_all()
# county_boundaries["overlap_ratio"] = (
#     county_boundaries.intersection(metro_union).area / county_boundaries.area
# )
# metro_counties = county_boundaries[county_boundaries["overlap_ratio"] > 0.95]  # 95% threshold

# # Option 3: Spatial join — keeps counties that intersect (then filter by predicate)
# metro_counties = gpd.sjoin(
#     county_boundaries,
#     metro_boundaries,
#     how="inner",
#     predicate="within"       # or "intersects" for partial overlap
# ).drop(columns="index_right")

metro_counties_path = os.path.join(base_dir, 'cartographic', 'cb_2018_us_county_500k', 'metropolitan_counties.gpkg')
metro_counties.to_file(metro_counties_path, driver='GPKG')
