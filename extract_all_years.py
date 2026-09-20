import os
import pandas as pd
import cfgrib


# ============================================================
# PATHS
# ============================================================

base_path = r"C:\Users\bhanu\OneDrive\Desktop\AI-Hybrid-Landslide Prediction\DATA\Raw\historical data"

output_folder = r"C:\Users\bhanu\OneDrive\Desktop\AI-Hybrid-Landslide Prediction\DATA\processed"

os.makedirs(output_folder, exist_ok=True)


# ============================================================
# YEARS
# ============================================================

years = [
     2016, 2017, 2018, 2019, 2020,
    2021, 2022, 2023, 2024, 2025, 2026
]


# ============================================================
# PROCESS EACH YEAR
# ============================================================

for year in years:

    print("\n" + "=" * 70)
    print("PROCESSING YEAR:", year)
    print("=" * 70)

    year_folder = os.path.join(base_path, str(year))

    if not os.path.exists(year_folder):
        print("❌ Folder not found:", year_folder)
        continue

    # Find GRIB files
    grib_files = [
        f for f in os.listdir(year_folder)
        if f.lower().endswith((".grib", ".grb", ".grib2"))
    ]

    if not grib_files:
        print("❌ No GRIB file found")
        continue

    if len(grib_files) > 1:
        print("⚠ Multiple GRIB files found:")
        for f in grib_files:
            print("   ", f)

    grib_file = os.path.join(year_folder, grib_files[0])

    print("GRIB file:", grib_files[0])

    try:

        # ----------------------------------------------------
        # OPEN GRIB
        # ----------------------------------------------------

        datasets = cfgrib.open_datasets(grib_file)

        print("Number of datasets:", len(datasets))

        if len(datasets) < 8:
            print("❌ Unexpected dataset structure")
            continue

        # ----------------------------------------------------
        # DATASETS
        # ----------------------------------------------------

        weather = datasets[5]

        swvl1 = datasets[0]["swvl1"]
        swvl2 = datasets[1]["swvl2"]
        swvl3 = datasets[2]["swvl3"]
        swvl4 = datasets[3]["swvl4"]

        # ----------------------------------------------------
        # MAIN WEATHER DATA
        # ----------------------------------------------------

        df = weather[
            [
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
            ]
        ].to_dataframe().reset_index()

        # ----------------------------------------------------
        # SOIL MOISTURE
        # ----------------------------------------------------

        soil1 = swvl1.to_dataframe(name="swvl1").reset_index()
        soil2 = swvl2.to_dataframe(name="swvl2").reset_index()
        soil3 = swvl3.to_dataframe(name="swvl3").reset_index()
        soil4 = swvl4.to_dataframe(name="swvl4").reset_index()

        keys = ["time", "latitude", "longitude"]

        df = df.merge(
            soil1[keys + ["swvl1"]],
            on=keys,
            how="left"
        )

        df = df.merge(
            soil2[keys + ["swvl2"]],
            on=keys,
            how="left"
        )

        df = df.merge(
            soil3[keys + ["swvl3"]],
            on=keys,
            how="left"
        )

        df = df.merge(
            soil4[keys + ["swvl4"]],
            on=keys,
            how="left"
        )

        # ----------------------------------------------------
        # DERIVED FEATURES
        # ----------------------------------------------------

        df["temperature_c"] = df["t2m"] - 273.15

        df["dewpoint_c"] = df["d2m"] - 273.15

        df["wind_speed"] = (
            df["u10"] ** 2 +
            df["v10"] ** 2
        ) ** 0.5

        # Keep original meaning:
        # tcrw = Total Column Rain Water
        df["total_column_rain_water"] = df["tcrw"]

        # ----------------------------------------------------
        # SORT
        # ----------------------------------------------------

        df = df.sort_values(
            ["time", "latitude", "longitude"]
        ).reset_index(drop=True)

        # ----------------------------------------------------
        # SAVE
        # ----------------------------------------------------

        output_file = os.path.join(
            output_folder,
            f"shimla_{year}_processed.csv"
        )

        df.to_csv(output_file, index=False)

        # ----------------------------------------------------
        # SUMMARY
        # ----------------------------------------------------

        print("\n✅ Extraction successful")

        print("Rows:", len(df))
        print("Columns:", len(df.columns))

        print(
            "Time:",
            df["time"].min(),
            "to",
            df["time"].max()
        )

        print("Missing values:", df.isnull().sum().sum())

        print("Output:", output_file)

    except Exception as e:

        print("\n❌ ERROR processing", year)
        print(type(e).__name__, e)


print("\n" + "=" * 70)
print("ALL YEARS PROCESSING COMPLETE")
print("=" * 70)