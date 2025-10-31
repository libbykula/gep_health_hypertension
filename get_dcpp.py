import pandas as pd
import re
import os

# --- Step 1: Read the dataset ---
os.chdir('D:/base_data/GEP/')

# Adjust path and sep depending on your file format
df = pd.read_excel("Data/Price_Prevalence/ht_costs_new.xlsx")

# --- Step 2: Extract the Direct Cost per person (DCpp) value ---
def extract_dcpp(text):
    """
    Extracts 'Int$ (DCpp)' value from a text string.
    Returns a float or NaN if not found.
    """
    if isinstance(text, str):
        # Match patterns like '123.45 Int$ (DCpp)' or '12,345.67 Int$ (DCpp – Hidalgo)'
        match = re.search(r'([\d,\.]+)\s*Int\$.*\(DCpp', text)
        if match:
            value = match.group(1).replace(",", "")
            try:
                return float(value)
            except ValueError:
                return None
    return None

# Combine columns that may contain DCpp values
df["combined_text"] = df.astype(str).apply(" ".join, axis=1)
df["DCpp"] = df["combined_text"].apply(extract_dcpp)

# --- Step 3: Clean and aggregate by country ---
# Standardize country names (remove region qualifiers like '(Hidalgo)')
df["Country_clean"] = (
    df["Country (region)"]
    .str.replace(r"\(.*?\)", "", regex=True)
    .str.strip()
)

# Average DCpp per country
dcpp_summary = (
    df.groupby("Country_clean", as_index=False)["DCpp"]
    .mean()
    .dropna()
    .sort_values("DCpp", ascending=False)
)

# --- Step 4: Export to a new dataset ---
dcpp_summary.to_csv("Data/Price_Prevalence/direct_costs_per_person_by_country.csv", index=False)
