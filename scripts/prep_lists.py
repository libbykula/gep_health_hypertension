import pandas as pd
import math

chunk_size = 25

df = pd.read_csv("/users/3/kula0049/urban-cooling/Data/urbanspatial-guppd-v1-gpkg/idn_smod_id.csv")
smod_ids = df.SMOD_ID.astype(str).tolist()

chunks = [smod_ids[i:i+chunk_size] for i in range(0, len(smod_ids), chunk_size)]

with open("idn_chunks.txt","w") as f:
    for c in chunks:
        f.write(",".join(c) + "\n")

print(len(chunks), "chunks created")
