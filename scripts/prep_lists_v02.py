import pandas as pd
import os
import math

base_dir = '/users/3/kula0049/'
smod_ids_dir = os.path.join(base_dir, 'urban-cooling/Data/urbanspatial-guppd-v1-gpkg')
countries_df = pd.read_csv(os.path.join(base_dir, 'Files/base_data/Price_Prevalence/ht final costs.csv'))

country_labels = countries_df['iso3_r250_label'].str.lower().tolist()
chunk_size = 50

for country_label in country_labels:
    path = os.path.join(smod_ids_dir, f'{country_label}_smod_id.csv')
    if not os.path.exists(path):
        print("no smod file for", country_label)
        continue

    df = pd.read_csv(path)
    smod_ids = df.SMOD_ID.astype(str).tolist()
    chunks = [smod_ids[i:i+chunk_size] for i in range(0, len(smod_ids), chunk_size)]

    outfile = f"{country_label}_chunks.txt"
    with open(outfile,"w") as f:
        for c in chunks:
            f.write(",".join(c) + "\n")

    print(country_label, "→", outfile, "→", len(chunks), "chunks")
