import os
import pandas as pd


# ============================================================
# PATHS
# ============================================================

processed_folder = r"C:\Users\bhanu\OneDrive\Desktop\AI-Hybrid-Landslide Prediction\DATA\processed"


# ============================================================
# YEARS
# ============================================================

years = [
    2016,
    2017,
    2018,
    2019,
    2020,
    2021,
    2023,
    2024,
    2025,
    2026
]


# ============================================================
# EXPECTED COLUMNS
# ============================================================

expected_columns = [
    "time",
    "latitude",
    "longitude",
    "t2m",
    "d2m",
    "u10",
    "v10",
    "sp",
    "tcrw",
    "tcc",
    "cvl",
    "cvh",
    "lai_lv",
    "lai_hv",
    "number",
    "step",
    "surface",
    "valid_time",
    "swvl1",
    "swvl2",
    "swvl3",
    "swvl4",
    "temperature_c",
    "dewpoint_c",
    "wind_speed",
    "total_column_rain_water"
]


# ============================================================
# VALIDATION
# ============================================================

all_good = True
dataframes = []

print("=" * 70)
print("VALIDATING ALL PROCESSED YEARS")
print("=" * 70)


for year in years:

    print("\n" + "-" * 70)
    print("YEAR:", year)
    print("-" * 70)

    file_path = os.path.join(
        processed_folder,
        f"shimla_{year}_processed.csv"
    )

    # --------------------------------------------------------
    # Check file
    # --------------------------------------------------------

    if not os.path.exists(file_path):
        print("❌ FILE NOT FOUND")
        all_good = False
        continue

    print("File found: ✅")

    # --------------------------------------------------------
    # Read CSV
    # --------------------------------------------------------

    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print("❌ Could not read file:", e)
        all_good = False
        continue

    dataframes.append(df)

    # --------------------------------------------------------
    # Shape
    # --------------------------------------------------------

    print("Rows:", len(df))
    print("Columns:", len(df.columns))

    if len(df) == 672:
        print("Row count: ✅")
    else:
        print("Row count: ❌ Expected 672")
        all_good = False

    # --------------------------------------------------------
    # Columns
    # --------------------------------------------------------

    if list(df.columns) == expected_columns:
        print("Columns: ✅")
    else:
        print("Columns: ❌")

        print("\nExpected:")
        print(expected_columns)

        print("\nActual:")
        print(list(df.columns))

        all_good = False

    # --------------------------------------------------------
    # Missing values
    # --------------------------------------------------------

    missing = df.isnull().sum().sum()

    print("Missing values:", missing)

    if missing == 0:
        print("Missing values: ✅")
    else:
        print("Missing values: ❌")
        all_good = False

    # --------------------------------------------------------
    # Duplicate rows
    # --------------------------------------------------------

    duplicate_rows = df.duplicated().sum()

    print("Duplicate rows:", duplicate_rows)

    if duplicate_rows == 0:
        print("Duplicate rows: ✅")
    else:
        print("Duplicate rows: ❌")
        all_good = False

    # --------------------------------------------------------
    # Duplicate time + location
    # --------------------------------------------------------

    duplicate_keys = df.duplicated(
        subset=["time", "latitude", "longitude"]
    ).sum()

    print("Duplicate time + location:", duplicate_keys)

    if duplicate_keys == 0:
        print("Time + location uniqueness: ✅")
    else:
        print("Time + location uniqueness: ❌")
        all_good = False

    # --------------------------------------------------------
    # Unique timestamps
    # --------------------------------------------------------

    unique_times = df["time"].nunique()

    print("Unique timestamps:", unique_times)

    if unique_times == 168:
        print("Timestamp count: ✅")
    else:
        print("Timestamp count: ❌ Expected 168")
        all_good = False

    # --------------------------------------------------------
    # Grid cells
    # --------------------------------------------------------

    grid_cells = df[
        ["latitude", "longitude"]
    ].drop_duplicates()

    print("Grid cells:", len(grid_cells))

    if len(grid_cells) == 4:
        print("Grid cells: ✅")
    else:
        print("Grid cells: ❌ Expected 4")
        all_good = False

    # --------------------------------------------------------
    # Time range
    # --------------------------------------------------------

    print(
        "Time range:",
        df["time"].min(),
        "to",
        df["time"].max()
    )

    # --------------------------------------------------------
    # Temperature
    # --------------------------------------------------------

    print(
        "Temperature:",
        round(df["temperature_c"].min(), 2),
        "to",
        round(df["temperature_c"].max(), 2),
        "°C"
    )

    # --------------------------------------------------------
    # Soil moisture
    # --------------------------------------------------------

    print(
        "Soil moisture:",
        round(df["swvl1"].min(), 3),
        "to",
        round(df["swvl1"].max(), 3)
    )


# ============================================================
# CROSS-YEAR VALIDATION
# ============================================================

print("\n")
print("=" * 70)
print("CROSS-YEAR VALIDATION")
print("=" * 70)


if len(dataframes) > 0:

    # --------------------------------------------------------
    # Check column consistency
    # --------------------------------------------------------

    first_columns = list(dataframes[0].columns)

    columns_same = all(
        list(df.columns) == first_columns
        for df in dataframes
    )

    print("\nAll years have same columns:", columns_same)

    if not columns_same:
        all_good = False

    # --------------------------------------------------------
    # Check grid consistency
    # --------------------------------------------------------

    first_grid = set(
        zip(
            dataframes[0]["latitude"],
            dataframes[0]["longitude"]
        )
    )

    grid_same = True

    for df in dataframes[1:]:

        current_grid = set(
            zip(
                df["latitude"],
                df["longitude"]
            )
        )

        if current_grid != first_grid:
            grid_same = False

    print("All years have same grid:", grid_same)

    if not grid_same:
        all_good = False

    # --------------------------------------------------------
    # Total rows
    # --------------------------------------------------------

    total_rows = sum(len(df) for df in dataframes)

    print("Total rows across all files:", total_rows)

    if total_rows == 6720:
        print("Total row count: ✅")
    else:
        print("Total row count: ❌ Expected 6720")
        all_good = False


# ============================================================
# FINAL RESULT
# ============================================================

print("\n")
print("=" * 70)

if all_good:
    print("🎉 VALIDATION SUCCESSFUL")
    print("All processed datasets passed the checks.")
else:
    print("⚠ VALIDATION FOUND PROBLEMS")
    print("Review the errors above before merging.")

print("=" * 70)