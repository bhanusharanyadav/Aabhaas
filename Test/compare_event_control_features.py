import pandas as pd

path = r"DATA\Raw\Landslide event\processed\labeled\labeled_with_rainfall_features.csv"

df = pd.read_csv(path)

df["time"] = pd.to_datetime(df["time"])

features = [
    "rainfall_mm",
    "rain_3h",
    "rain_6h",
    "rain_12h",
    "rain_24h",
    "rain_72h",
    "temperature_c",
    "dewpoint_c",
    "wind_speed",
    "sp",
    "swvl1",
    "swvl2",
    "swvl3",
    "swvl4"
]

print("=" * 70)
print("EVENT vs CONTROL FEATURE COMPARISON")
print("=" * 70)

# Only use rows where all selected features are available
data = df.dropna(subset=features).copy()

print("\nRows used:", len(data))

print("\nFeature statistics:")
print("-" * 70)

for feature in features:

    positive = data.loc[
        data["landslide"] == 1,
        feature
    ]

    negative = data.loc[
        data["landslide"] == 0,
        feature
    ]

    print(f"\n{feature}")

    print(
        f"  EVENT   : "
        f"mean={positive.mean():.4f}, "
        f"median={positive.median():.4f}, "
        f"min={positive.min():.4f}, "
        f"max={positive.max():.4f}"
    )

    print(
        f"  CONTROL : "
        f"mean={negative.mean():.4f}, "
        f"median={negative.median():.4f}, "
        f"min={negative.min():.4f}, "
        f"max={negative.max():.4f}"
    )

print("\n" + "=" * 70)
print("COMPARISON COMPLETE")
print("=" * 70)