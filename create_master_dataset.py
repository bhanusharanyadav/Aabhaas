import os
import pandas as pd

# ============================================================
# SETTINGS
# ============================================================

base_path = r"C:\Users\bhanu\OneDrive\Desktop\AI-Hybrid-Landslide Prediction"

processed_path = os.path.join(
    base_path,
    "DATA",
    "processed"
)

years = [
    2016, 2017, 2018, 2019, 2020,
    2021, 2022, 2023, 2024, 2025, 2026
]

# ============================================================
# LOAD AND COMBINE ALL YEARS
# ============================================================

print("=" * 70)
print("CREATING MASTER DATASET")
print("=" * 70)

all_data = []

for year in years:

    print(f"\nLoading {year}...")

    file_path = os.path.join(
        processed_path,
        f"shimla_{year}_rainfall.csv"
    )

    df = pd.read_csv(file_path)

    df["time"] = pd.to_datetime(df["time"])

    print("Rows:", len(df))
    print("Columns:", len(df.columns))

    all_data.append(df)

# ============================================================
# COMBINE
# ============================================================

master_df = pd.concat(
    all_data,
    ignore_index=True
)

# ============================================================
# SORT
# ============================================================

master_df = master_df.sort_values(
    ["time", "latitude", "longitude"]
).reset_index(drop=True)

# ============================================================
# ADD YEAR
# ============================================================

master_df["year"] = master_df["time"].dt.year

# ============================================================
# CHECKS
# ============================================================

print("\n" + "=" * 70)
print("MASTER DATASET CHECK")
print("=" * 70)

print("Total rows:", len(master_df))
print("Total columns:", len(master_df.columns))

print("\nYears:")
print(sorted(master_df["year"].unique()))

print("\nRows by year:")
print(master_df["year"].value_counts().sort_index())

print("\nMissing values:")
print(
    master_df.isna().sum()
    .sort_values(ascending=False)
    .head(15)
)

print("\nDuplicate rows:")
print(master_df.duplicated().sum())

print("\nDuplicate time + location:")
print(
    master_df.duplicated(
        subset=["time", "latitude", "longitude"]
    ).sum()
)

print("\nGrid:")
print("Latitude:", sorted(master_df["latitude"].unique()))
print("Longitude:", sorted(master_df["longitude"].unique()))

# ============================================================
# SAVE
# ============================================================

output_file = os.path.join(
    processed_path,
    "shimla_master_dataset.csv"
)

master_df.to_csv(
    output_file,
    index=False
)

print("\n" + "=" * 70)
print("MASTER DATASET CREATED")
print("=" * 70)

print("Output:")
print(output_file)

print("=" * 70)