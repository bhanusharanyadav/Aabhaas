import pandas as pd

path = r"DATA\Raw\Landslide event\processed\labeled\labeled_with_rainfall_features.csv"

df = pd.read_csv(path)
df["time"] = pd.to_datetime(df["time"])

print("=" * 70)
print("LABELED DATASET DISTRIBUTION CHECK")
print("=" * 70)

print("\nTotal rows:", len(df))

print("\nClass distribution:")
print(df["landslide"].value_counts())

print("\nClass percentage:")
print(
    (df["landslide"].value_counts(normalize=True) * 100)
    .round(2)
)

print("\nRows by event and class:")
print(
    df.groupby(["event", "landslide"])
      .size()
)

print("\nRows by sample type:")
print(
    df.groupby(["sample_type", "landslide"])
      .size()
)

print("\nLocations by event:")

for event, group in df.groupby("event"):

    locations = (
        group[["latitude", "longitude"]]
        .drop_duplicates()
        .sort_values(["latitude", "longitude"])
    )

    print("\n", event)
    print("Number of locations:", len(locations))
    print(locations.to_string(index=False))

print("\nTime ranges by event:")

for event, group in df.groupby("event"):

    print(
        f"{event}: "
        f"{group['time'].min()} -> "
        f"{group['time'].max()}"
    )

print("\nRainfall feature missing values:")

rain_features = [
    "rain_3h",
    "rain_6h",
    "rain_12h",
    "rain_24h",
    "rain_72h"
]

print(df[rain_features].isna().sum())

print("\n" + "=" * 70)
print("DISTRIBUTION CHECK COMPLETE")
print("=" * 70)