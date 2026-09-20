import pandas as pd
import os

INPUT = r"DATA\Raw\Landslide event\processed\labeled\initial_landslide_labeled_dataset.csv"

OUTPUT = r"DATA\Raw\Landslide event\processed\labeled\labeled_with_rainfall_features.csv"

print("=" * 70)
print("ADDING RAINFALL ACCUMULATION FEATURES")
print("=" * 70)

df = pd.read_csv(INPUT)

df["time"] = pd.to_datetime(df["time"])

# Sort separately for each geographic location
df = df.sort_values(
    ["latitude", "longitude", "time"]
).reset_index(drop=True)

# Calculate rolling rainfall for each location
for window in [3, 6, 12, 24, 72]:

    column = f"rain_{window}h"

    df[column] = (
        df.groupby(["latitude", "longitude"])["rainfall_mm"]
        .transform(
            lambda x: x.rolling(
                window=window,
                min_periods=window
            ).sum()
        )
    )

# Save
df.to_csv(OUTPUT, index=False)

print("\nRows:", len(df))
print("Columns:", len(df.columns))

print("\nNew rainfall features:")
print([
    "rain_3h",
    "rain_6h",
    "rain_12h",
    "rain_24h",
    "rain_72h"
])

print("\nMissing values in rainfall features:")

for window in [3, 6, 12, 24, 72]:

    column = f"rain_{window}h"

    print(
        f"{column}:",
        df[column].isna().sum()
    )

print("\nRainfall feature ranges:")

for window in [3, 6, 12, 24, 72]:

    column = f"rain_{window}h"

    print(
        f"{column}: "
        f"min={df[column].min():.3f}, "
        f"max={df[column].max():.3f}"
    )

print("\nOutput:")
print(OUTPUT)

print("\n" + "=" * 70)
print("RAINFALL FEATURE CREATION COMPLETE")
print("=" * 70)