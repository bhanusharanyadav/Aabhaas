import os
import pandas as pd

base_path = r"C:\Users\bhanu\OneDrive\Desktop\AI-Hybrid-Landslide Prediction"
processed_path = os.path.join(base_path, "DATA", "processed")

years = [
    2016, 2017, 2018, 2019, 2020,
    2021, 2023, 2024, 2025, 2026
]

rainfall_columns = [
    "rainfall_mm",
    "rain_3h",
    "rain_6h",
    "rain_12h",
    "rain_24h",
    "rain_72h"
]

print("=" * 70)
print("VALIDATING ALL RAINFALL DATASETS")
print("=" * 70)

all_passed = True

for year in years:

    print("\n" + "=" * 70)
    print(f"YEAR: {year}")
    print("=" * 70)

    file_path = os.path.join(
        processed_path,
        f"shimla_{year}_rainfall.csv"
    )

    if not os.path.exists(file_path):
        print("❌ FILE NOT FOUND")
        all_passed = False
        continue

    df = pd.read_csv(file_path)

    df["time"] = pd.to_datetime(df["time"])

    print("Rows:", len(df))
    print("Columns:", len(df.columns))

    # --------------------------------------------------------
    # Required rainfall columns
    # --------------------------------------------------------

    missing_columns = [
        col for col in rainfall_columns
        if col not in df.columns
    ]

    if missing_columns:
        print("❌ Missing rainfall columns:", missing_columns)
        all_passed = False
    else:
        print("Rainfall columns: ✅")

    # --------------------------------------------------------
    # Expected rows
    # --------------------------------------------------------

    if len(df) == 672:
        print("672 rows: ✅")
    else:
        print("❌ Unexpected row count")

        all_passed = False

    # --------------------------------------------------------
    # Missing raw rainfall
    # --------------------------------------------------------

    missing_rainfall = df["rainfall_mm"].isna().sum()

    print("Missing rainfall_mm:", missing_rainfall)

    if missing_rainfall == 0:
        print("Raw rainfall completeness: ✅")
    else:
        print("❌ Missing raw rainfall values")
        all_passed = False

    # --------------------------------------------------------
    # Duplicate rows
    # --------------------------------------------------------

    duplicates = df.duplicated().sum()

    print("Duplicate rows:", duplicates)

    if duplicates == 0:
        print("Duplicates: ✅")
    else:
        print("❌ Duplicate rows found")
        all_passed = False

    # --------------------------------------------------------
    # Duplicate time + location
    # --------------------------------------------------------

    duplicate_keys = df.duplicated(
        subset=["time", "latitude", "longitude"]
    ).sum()

    print("Duplicate time+location:", duplicate_keys)

    if duplicate_keys == 0:
        print("Time/location uniqueness: ✅")
    else:
        print("❌ Duplicate time/location records")
        all_passed = False

    # --------------------------------------------------------
    # Time intervals
    # --------------------------------------------------------

    df = df.sort_values(
        ["latitude", "longitude", "time"]
    )

    df["time_diff_hours"] = (
        df.groupby(
            ["latitude", "longitude"]
        )["time"]
        .diff()
        .dt.total_seconds() / 3600
    )

    intervals = df["time_diff_hours"].dropna().unique()

    print("Time intervals:", intervals)

    if set(intervals) == {1.0}:
        print("Hourly continuity: ✅")
    else:
        print("❌ Time continuity problem")
        all_passed = False

    # --------------------------------------------------------
    # Grid
    # --------------------------------------------------------

    print(
        "Latitude:",
        sorted(df["latitude"].unique())
    )

    print(
        "Longitude:",
        sorted(df["longitude"].unique())
    )

    # --------------------------------------------------------
    # Negative rainfall
    # --------------------------------------------------------

    negative = (
        df["rainfall_mm"] < 0
    ).sum()

    print("Negative rainfall:", negative)

    if negative == 0:
        print("Negative rainfall check: ✅")
    else:
        print("❌ Negative rainfall detected")
        all_passed = False

    # --------------------------------------------------------
    # Rainfall statistics
    # --------------------------------------------------------

    print("\nRainfall statistics:")

    print(
        df[
            rainfall_columns
        ].describe().T[
            ["count", "min", "max", "mean"]
        ]
    )

print("\n" + "=" * 70)

if all_passed:
    print("✅ ALL RAINFALL DATASETS PASSED VALIDATION")
else:
    print("❌ SOME DATASETS FAILED VALIDATION")

print("=" * 70)