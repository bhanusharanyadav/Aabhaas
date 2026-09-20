import os
import pandas as pd

BASE = r"DATA\Raw\Landslide event\processed"

files = [
    "shimla_event_dataset.csv",
    "kinnaur_event_dataset.csv",
    "chamoli_event_dataset.csv"
]

for file in files:

    path = os.path.join(BASE, file)

    print("\n" + "=" * 70)
    print("FILE:", file)
    print("=" * 70)

    if not os.path.exists(path):
        print("FILE NOT FOUND")
        continue

    df = pd.read_csv(path)
    df["time"] = pd.to_datetime(df["time"])

    print("Rows:", len(df))
    print("Columns:", len(df.columns))

    print("\nColumn names:")
    print(list(df.columns))

    print("\nTime:")
    print("Start:", df["time"].min())
    print("End  :", df["time"].max())

    print("\nLocations:")
    print("Unique locations:", df[["latitude", "longitude"]].drop_duplicates().shape[0])

    print(df[["latitude", "longitude"]].drop_duplicates().to_string(index=False))

    print("\nEvent values:")
    print(df["event"].value_counts())

    print("\nMissing values:")
    print(df.isna().sum().sum())

    print("\nDuplicate rows:")
    print(df.duplicated().sum())

    print("\nRainfall:")
    print("Minimum:", df["rainfall_mm"].min())
    print("Maximum:", df["rainfall_mm"].max())
    print("Mean   :", df["rainfall_mm"].mean())

    print("\nSample:")
    print(df.head(3).to_string(index=False))

print("\n" + "=" * 70)
print("EVENT DATASET INSPECTION COMPLETE")
print("=" * 70)