import os
import glob
import pandas as pd
import geopandas as gpd

user_dir = '/users/3/kula0049'
output_dir = os.path.join(user_dir, 'gep_health', 'output') 

all_files = glob.glob(os.path.join(output_dir, "linear_county_prev_5_26_26", "*_hypertension_results_*.csv"))

dfs = []
for f in all_files:
    df = pd.read_csv(f)
    dfs.append(df)

big = pd.concat(dfs, ignore_index=True)
big.to_csv(os.path.join(output_dir, 'hypertension_linear_us_counties.csv'), index=False)


# I should also get these in the urban areas .gpkg and then I can start looking at differences by state/whatever
county_boundaries = gpd.read_file(
    os.path.join(user_dir, 'Files', 'base_data', 'cartographic', 'cb_2018_us_county_500k', 'metropolitan_counties.gpkg'))

county_boundaries['GEOID'] = county_boundaries['GEOID'].astype(int)

final_gdf = gpd.GeoDataFrame(pd.merge(big, county_boundaries, how = 'right', on = 'GEOID')
)

final_gdf.to_file(os.path.join(output_dir, 'hypertension_linear_us_counties.gpkg'), driver='GPKG')

