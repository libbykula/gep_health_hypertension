import pandas as pd
import geopandas as gpd
import os

# Base directories
base_dir = '/users/3/kula0049/'
cartographic_dir = os.path.join(base_dir, 'Files/base_data/cartographic')

# Load US county boundaries
county_boundaries = gpd.read_file(
    os.path.join(
        cartographic_dir,
        'cb_2018_us_county_500k',
        'metropolitan_counties.gpkg'
    )
)

# Get county GEOIDs
geoids = county_boundaries['GEOID'].astype(str).tolist()

# Chunk settings
chunk_size = 50
chunks = [geoids[i:i + chunk_size] for i in range(0, len(geoids), chunk_size)]

# Output file
outfile = os.path.join(base_dir, 'gep_health', 'scripts', 'usa_metro_county_chunks.txt')

with open(outfile, "w") as f:
    for chunk in chunks:
        f.write(",".join(chunk) + "\n")

print("USA counties →", outfile, "→", len(chunks), "chunks")
print("Total GEOIDs:", len(geoids))