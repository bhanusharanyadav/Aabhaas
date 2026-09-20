import pandas as pd
import os

INPUT = r"DATA\processed\shimla_master_dataset.csv"

OUTPUT = r"DATA\processed\shimla_baseline_dataset.csv"

print("=" * 70)
print("PREPARING SHIMLA BASELINE DATASET")
print("=" * 70)

df = pd.read_csv(INPUT)

df["time"] = pd.to_datetime(df["time"])

print("\nOriginal rows:", len(df))

rain_features = [
    "rain_3h",
    "rain_6h",
    "rain_12h",
    "rain_24h",
    "rain_72h"
]

# Remove rows where rainfall accumulation
# cannot be calculated completely.
df_clean = df.dropna(
    subset=rain_features
).copy()

# Sort
df_clean = df_clean.sort_values(
    ["time", "latitude", "longitude"]
).reset_index(drop=True)

# Save
df_clean.to_csv(OUTPUT, index=False)

print("Clean rows:", len(df_clean))
print("Removed rows:", len(df) - len(df_clean))

print("\nMissing rainfall features after cleaning:")

print(
    df_clean[rain_features]
    .isna()
    .sum()
    .to_string()
)

print("\nTotal missing values after cleaning:",
      df_clean.isna().sum().sum())

print("\nYears:")
print(
    df_clean["time"]
    .dt.year
    .value_counts()
    .sort_index()
)

print("\nLocations:",
      df_clean[["latitude", "longitude"]]
      .drop_duplicates()
      .shape[0])

print("\nOutput:")
print(OUTPUT)

print("\n" + "=" * 70)
print("SHIMLA BASELINE PREPARATION COMPLETE")
print("=" * 70)