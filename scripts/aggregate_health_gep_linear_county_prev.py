import os
import glob
import pandas as pd
import geopandas as gpd

user_dir = '/users/3/kula0049'
base_dir = '/users/3/kula0049/gep_health/output/linear_county_prev_5_26_26'  

all_files = glob.glob(os.path.join(base_dir, "*_hypertension_results_*.csv"))

dfs = []
for f in all_files:
    df = pd.read_csv(f)
    dfs.append(df)

big = pd.concat(dfs, ignore_index=True)
# big.to_csv('/users/3/kula0049/gep_health/output/health_county_prev_linear_urban_areas.csv', index=False)


# I should also get these in the urban areas .gpkg and then I can start looking at differences by state/whatever
urban_boundaries = gpd.read_file(
    os.path.join(user_dir, 'urban-cooling/Data/urbanspatial-guppd-v1-gpkg/usa_guppd_w_county_geoid.gpkg'),
    layer='usa_guppd_w_county_geoid'
)

final_gdf = gpd.GeoDataFrame(pd.merge(big, urban_boundaries, how = 'right', on = 'SMOD_ID')
)

final_gdf.to_file(os.path.join(user_dir, 'urban-cooling/Data/urbanspatial-guppd-v1-gpkg/usa_guppd_w_county_geoid_w_val.gpkg'), driver='GPKG')

