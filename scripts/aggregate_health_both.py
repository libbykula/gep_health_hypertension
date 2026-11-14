import os
import glob
import pandas as pd

folders = ['linear_2_17_2026', 'indiv_2_17_2026']


for folder in folders:
    base_dir = os.path.join('/users/3/kula0049/gep_health/output/', folder)
    all_files = glob.glob(os.path.join(base_dir, "*_hypertension_results_*.csv"))

    dfs = []
    for f in all_files:
        df = pd.read_csv(f)
        dfs.append(df)

    big = pd.concat(dfs, ignore_index=True)
    big.to_csv('/users/3/kula0049/gep_health/output/health_gep_' + folder + '_urban_areas.csv', index=False)

    # group by country and sum
    agg = big.groupby("country", as_index=False)["total_value_usd"].sum()

    agg.to_csv('/users/3/kula0049/gep_health/output/health_gep_' + folder + '.csv', index=False)

    print(folder, "csv written!")
