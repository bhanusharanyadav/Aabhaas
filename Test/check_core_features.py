import pandas as pd

path = r"DATA\Raw\Landslide event\processed\labeled\initial_landslide_labeled_dataset.csv"

df = pd.read_csv(path)

core_features = [
    "time",
    "latitude",
    "longitude",
    "t2m",
    "d2m",
    "u10",
    "v10",
    "sp",
    "tcrw",
    "cvl",
    "cvh",
    "lai_lv",
    "lai_hv",
    "temperature_c",
    "dewpoint_c",
    "wind_speed",
    "swvl1",
    "swvl2",
    "swvl3",
    "swvl4",
    "rainfall_mm",
    "landslide"
]

print("=" * 70)
print("CORE ML FEATURE CHECK")
print("=" * 70)

print("\nChecking columns...")

missing_columns = [
    col for col in core_features
    if col not in df.columns
]

if missing_columns:
    print("Missing columns:")
    print(missing_columns)
else:
    print("All core columns are present.")

print("\nMissing values in core features:")

missing = df[core_features].isna().sum()

print(missing.to_string())

print("\nTotal missing values in core features:", missing.sum())

print("\nRows with any missing core feature:",
      df[core_features].isna().any(axis=1).sum())

print("\nClass distribution:")
print(df["landslide"].value_counts())

print("\n" + "=" * 70)
print("CORE FEATURE CHECK COMPLETE")
print("=" * 70)