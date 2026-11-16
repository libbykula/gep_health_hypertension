import os
import glob
import pandas as pd

base_dir = '/users/3/kula0049/gep_health/output/linear_p0_upd_11_16_2026'  

all_files = glob.glob(os.path.join(base_dir, "*_hypertension_results_*.csv"))

dfs = []
for f in all_files:
    df = pd.read_csv(f)
    dfs.append(df)

big = pd.concat(dfs, ignore_index=True)
big.to_csv('/users/3/kula0049/gep_health/output/health_gep_linear_p0_upd_11_16_2026_urban_areas.csv', index=False)

# group by country and sum
agg = big.groupby("country", as_index=False)["total_value_usd"].sum()

agg.to_csv("/users/3/kula0049/gep_health/output/health_gep_linear_11_16_2026.csv", index=False)

print("health_gep_linear_11_16_2026.csv written!")
