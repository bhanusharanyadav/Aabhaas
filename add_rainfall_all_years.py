import os
import pandas as pd
import cfgrib

# ============================================================
# SETTINGS
# ============================================================

base_path = r"C:\Users\bhanu\OneDrive\Desktop\AI-Hybrid-Landslide Prediction"

years = [
    2016, 2017, 2018, 2019, 2020,
    2021, 2022, 2023, 2024, 2025, 2026
]

processed_path = os.path.join(base_path, "DATA", "processed")
raw_path = os.path.join(base_path, "DATA", "Raw", "historical data")

# ============================================================
# PROCESS EACH YEAR
# ============================================================

print("=" * 70)
print("ADDING RAINFALL FEATURES - ALL YEARS")
print("=" * 70)

for year in years:

    print("\n" + "=" * 70)
    print(f"PROCESSING YEAR: {year}")
    print("=" * 70)

    # --------------------------------------------------------
    # Find GRIB file
    # --------------------------------------------------------

    year_folder = os.path.join(raw_path, str(year))

    grib_files = [
        f for f in os.listdir(year_folder)
        if f.lower().endswith((".grib", ".grb", ".grib2", ".grb2"))
    ]

    if not grib_files:
        print(f"ERROR: No GRIB file found for {year}")
        continue

    grib_file = os.path.join(year_folder, grib_files[0])

    print("GRIB file:")
    print(grib_file)

    # --------------------------------------------------------
    # Open GRIB datasets
    # --------------------------------------------------------

    datasets = cfgrib.open_datasets(grib_file)

    print(f"GRIB datasets found: {len(datasets)}")

    # Dataset 6 contains total precipitation
    tp_ds = datasets[6]

    print("Variables:", list(tp_ds.data_vars))
    print("Dimensions:", dict(tp_ds.sizes))

    # --------------------------------------------------------
    # Convert precipitation to dataframe
    # --------------------------------------------------------

    records = []

    for i in range(len(tp_ds.time)):

        reference_time = pd.to_datetime(tp_ds.time.values[i])

        for j in range(len(tp_ds.step)):

            step_value = tp_ds.step.values[j]

            valid_time = (
                reference_time +
                pd.to_timedelta(step_value)
            )

            for lat in tp_ds.latitude.values:

                for lon in tp_ds.longitude.values:

                    value = tp_ds["tp"].sel(
                        time=reference_time,
                        step=step_value,
                        latitude=lat,
                        longitude=lon
                    ).values

                    if pd.isna(value):
                        rainfall_mm = None
                    else:
                        # GRIB precipitation is in metres
                        # Convert metres → millimetres
                        rainfall_mm = float(value) * 1000

                    records.append({
                        "time": valid_time,
                        "latitude": float(lat),
                        "longitude": float(lon),
                        "rainfall_mm": rainfall_mm
                    })

    rainfall_df = pd.DataFrame(records)

    # --------------------------------------------------------
    # Keep the same weather period as processed dataset
    # --------------------------------------------------------

    weather_file = os.path.join(
        processed_path,
        f"shimla_{year}_processed.csv"
    )

    weather_df = pd.read_csv(weather_file)

    weather_df["time"] = pd.to_datetime(weather_df["time"])
    rainfall_df["time"] = pd.to_datetime(rainfall_df["time"])

    start_time = weather_df["time"].min()
    end_time = weather_df["time"].max()

    rainfall_df = rainfall_df[
        (rainfall_df["time"] >= start_time) &
        (rainfall_df["time"] <= end_time)
    ]

    # --------------------------------------------------------
    # Sort before calculating rolling rainfall
    # --------------------------------------------------------

    rainfall_df = rainfall_df.sort_values(
        ["latitude", "longitude", "time"]
    )

    # --------------------------------------------------------
    # Rolling rainfall features
    # --------------------------------------------------------

    rainfall_df["rain_3h"] = (
        rainfall_df
        .groupby(["latitude", "longitude"])["rainfall_mm"]
        .transform(lambda x: x.rolling(3, min_periods=3).sum())
    )

    rainfall_df["rain_6h"] = (
        rainfall_df
        .groupby(["latitude", "longitude"])["rainfall_mm"]
        .transform(lambda x: x.rolling(6, min_periods=6).sum())
    )

    rainfall_df["rain_12h"] = (
        rainfall_df
        .groupby(["latitude", "longitude"])["rainfall_mm"]
        .transform(lambda x: x.rolling(12, min_periods=12).sum())
    )

    rainfall_df["rain_24h"] = (
        rainfall_df
        .groupby(["latitude", "longitude"])["rainfall_mm"]
        .transform(lambda x: x.rolling(24, min_periods=24).sum())
    )

    rainfall_df["rain_72h"] = (
        rainfall_df
        .groupby(["latitude", "longitude"])["rainfall_mm"]
        .transform(lambda x: x.rolling(72, min_periods=72).sum())
    )

    # --------------------------------------------------------
    # Merge rainfall with weather dataset
    # --------------------------------------------------------

    final_df = weather_df.merge(
        rainfall_df,
        on=["time", "latitude", "longitude"],
        how="left"
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    output_file = os.path.join(
        processed_path,
        f"shimla_{year}_rainfall.csv"
    )

    final_df.to_csv(output_file, index=False)

    # --------------------------------------------------------
    # Report
    # --------------------------------------------------------

    print("\nRainfall rows:", len(rainfall_df))
    print("Final rows:", len(final_df))

    print(
        "Rainfall range:",
        final_df["rainfall_mm"].min(),
        "to",
        final_df["rainfall_mm"].max(),
        "mm"
    )

    print(
        "Missing rainfall:",
        final_df["rainfall_mm"].isna().sum()
    )

    print("Output:")
    print(output_file)

print("\n" + "=" * 70)
print("ALL YEARS RAINFALL PROCESSING COMPLETE")
print("=" * 70)