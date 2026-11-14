import os
import glob
import pandas as pd

base_dir = '/users/3/kula0049/gep_health/output/indiv_11_17_2025_v02'  

all_files = glob.glob(os.path.join(base_dir, "*_hypertension_results_*.csv"))

dfs = []
for f in all_files:
    df = pd.read_csv(f)
    dfs.append(df)

big = pd.concat(dfs, ignore_index=True)
big.to_csv('/users/3/kula0049/gep_health/output/health_gep_nonlinear_11_17_2025_urban_areas.csv', index=False)

# # group by country and sum
# agg = big.groupby("country", as_index=False)["total_value_usd"].sum()

# agg.to_csv("/users/3/kula0049/gep_health/output/health_gep_nonlinear_11_17_2025.csv", index=False)

# print("health_gep_nonlinear_11_17_2025.csv written!")
