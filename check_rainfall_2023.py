import pandas as pd


file_path = r"C:\Users\bhanu\OneDrive\Desktop\AI-Hybrid-Landslide Prediction\DATA\processed\shimla_2023_rainfall.csv"

df = pd.read_csv(file_path)

df["time"] = pd.to_datetime(df["time"])

print("=" * 70)
print("RAINFALL CONTINUITY CHECK - 2023")
print("=" * 70)


# ------------------------------------------------------------
# Check time intervals for each grid cell
# ------------------------------------------------------------

df = df.sort_values(
    ["latitude", "longitude", "time"]
)

df["time_diff_hours"] = (
    df.groupby(["latitude", "longitude"])["time"]
    .diff()
    .dt.total_seconds() / 3600
)

print("\nTime interval counts:")

print(
    df["time_diff_hours"]
    .value_counts(dropna=True)
    .sort_index()
)


# ------------------------------------------------------------
# Check rainfall statistics
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("RAINFALL STATISTICS")
print("=" * 70)

rain_cols = [
    "rainfall_mm",
    "rain_3h",
    "rain_6h",
    "rain_12h",
    "rain_24h",
    "rain_72h"
]

print(
    df[rain_cols].describe().T[
        ["count", "min", "max", "mean"]
    ]
)


# ------------------------------------------------------------
# Check rainfall around forecast boundaries
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("RAINFALL AROUND FORECAST BOUNDARIES")
print("=" * 70)

boundary_times = [
    "2023-08-09 05:00:00",
    "2023-08-09 06:00:00",
    "2023-08-09 07:00:00",
    "2023-08-09 17:00:00",
    "2023-08-09 18:00:00",
    "2023-08-09 19:00:00",
    "2023-08-13 17:00:00",
    "2023-08-13 18:00:00",
    "2023-08-13 19:00:00",
    "2023-08-14 05:00:00",
    "2023-08-14 06:00:00",
    "2023-08-14 07:00:00"
]

boundary_df = df[
    df["time"].isin(pd.to_datetime(boundary_times))
]

print(
    boundary_df[
        [
            "time",
            "latitude",
            "longitude",
            "rainfall_mm",
            "rain_3h",
            "rain_6h",
            "rain_12h",
            "rain_24h"
        ]
    ].to_string(index=False)
)


# ------------------------------------------------------------
# Check impossible negative rainfall
# ------------------------------------------------------------

negative_count = (
    df["rainfall_mm"] < 0
).sum()

print("\nNegative rainfall values:", negative_count)

if negative_count == 0:
    print("Negative rainfall check: ✅")
else:
    print("Negative rainfall check: ❌")


# ------------------------------------------------------------
# Final
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("CHECK COMPLETE")
print("=" * 70)