import os
import numpy as np
import pandas as pd
import cfgrib


# ============================================================
# PATHS
# ============================================================

grib_file = r"C:\Users\bhanu\OneDrive\Desktop\AI-Hybrid-Landslide Prediction\DATA\Raw\historical data\2023\c1cdc1cdec6e393a8e5f14b76a4598ee (1).grib"

input_csv = r"C:\Users\bhanu\OneDrive\Desktop\AI-Hybrid-Landslide Prediction\DATA\processed\shimla_2023_processed.csv"

output_csv = r"C:\Users\bhanu\OneDrive\Desktop\AI-Hybrid-Landslide Prediction\DATA\processed\shimla_2023_rainfall.csv"


# ============================================================
# OPEN GRIB
# ============================================================

datasets = cfgrib.open_datasets(grib_file)

tp_ds = None

for ds in datasets:
    if "tp" in ds.data_vars:
        tp_ds = ds
        break

if tp_ds is None:
    raise ValueError("TP dataset not found.")


tp = tp_ds["tp"]


# ============================================================
# CREATE PRECIPITATION DATAFRAME
# ============================================================

records = []

for i in range(tp_ds.sizes["time"]):

    for j in range(tp_ds.sizes["step"]):

        valid_time = tp_ds["valid_time"].values[i, j]

        for lat_index in range(tp_ds.sizes["latitude"]):

            for lon_index in range(tp_ds.sizes["longitude"]):

                value_m = tp.values[
                    i,
                    j,
                    lat_index,
                    lon_index
                ]

                if np.isnan(value_m):
                    rainfall_mm = np.nan
                else:
                    rainfall_mm = value_m * 1000

                records.append({
                    "time": pd.Timestamp(valid_time),
                    "latitude": float(
                        tp_ds["latitude"].values[lat_index]
                    ),
                    "longitude": float(
                        tp_ds["longitude"].values[lon_index]
                    ),
                    "rainfall_mm": rainfall_mm
                })


rain_df = pd.DataFrame(records)


# ============================================================
# REMOVE OUTSIDE WEATHER PERIOD
# ============================================================

start_time = "2023-08-09 00:00:00"
end_time = "2023-08-15 23:00:00"

rain_df = rain_df[
    (rain_df["time"] >= start_time) &
    (rain_df["time"] <= end_time)
].copy()


# ============================================================
# SORT
# ============================================================

rain_df = rain_df.sort_values(
    ["latitude", "longitude", "time"]
).reset_index(drop=True)


# ============================================================
# CHECK BASIC DATA
# ============================================================

print("=" * 70)
print("RAINFALL EXTRACTION - 2023")
print("=" * 70)

print("\nRows:", len(rain_df))

print("\nMissing rainfall values:")
print(rain_df["rainfall_mm"].isna().sum())

print("\nRainfall range:")
print(
    rain_df["rainfall_mm"].min(),
    "to",
    rain_df["rainfall_mm"].max(),
    "mm"
)


# ============================================================
# ROLLING RAINFALL FEATURES
# ============================================================

grouped = rain_df.groupby(
    ["latitude", "longitude"],
    group_keys=False
)

rain_df["rain_3h"] = grouped["rainfall_mm"].transform(
    lambda x: x.rolling(3, min_periods=3).sum()
)

rain_df["rain_6h"] = grouped["rainfall_mm"].transform(
    lambda x: x.rolling(6, min_periods=6).sum()
)

rain_df["rain_12h"] = grouped["rainfall_mm"].transform(
    lambda x: x.rolling(12, min_periods=12).sum()
)

rain_df["rain_24h"] = grouped["rainfall_mm"].transform(
    lambda x: x.rolling(24, min_periods=24).sum()
)

rain_df["rain_72h"] = grouped["rainfall_mm"].transform(
    lambda x: x.rolling(72, min_periods=72).sum()
)


# ============================================================
# LOAD ORIGINAL WEATHER DATA
# ============================================================

weather_df = pd.read_csv(input_csv)

weather_df["time"] = pd.to_datetime(weather_df["time"])

weather_df["latitude"] = weather_df["latitude"].astype(float)

weather_df["longitude"] = weather_df["longitude"].astype(float)


# ============================================================
# MERGE
# ============================================================

final_df = weather_df.merge(
    rain_df,
    on=["time", "latitude", "longitude"],
    how="left"
)


# ============================================================
# SORT
# ============================================================

final_df = final_df.sort_values(
    ["time", "latitude", "longitude"]
).reset_index(drop=True)


# ============================================================
# SAVE
# ============================================================

final_df.to_csv(
    output_csv,
    index=False
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("RAINFALL MERGE COMPLETE")
print("=" * 70)

print("\nFinal rows:", len(final_df))

print("Final columns:", len(final_df.columns))

print("\nRainfall columns:")

print([
    "rainfall_mm",
    "rain_3h",
    "rain_6h",
    "rain_12h",
    "rain_24h",
    "rain_72h"
])

print("\nMissing values in rainfall columns:")

print(
    final_df[
        [
            "rainfall_mm",
            "rain_3h",
            "rain_6h",
            "rain_12h",
            "rain_24h",
            "rain_72h"
        ]
    ].isna().sum()
)

print("\nOutput:")
print(output_csv)

print("\nFirst 10 rainfall records:")

print(
    final_df[
        [
            "time",
            "latitude",
            "longitude",
            "rainfall_mm",
            "rain_3h",
            "rain_6h",
            "rain_12h",
            "rain_24h",
            "rain_72h"
        ]
    ].head(10).to_string(index=False)
)

print("\n" + "=" * 70)
print("DONE")
print("=" * 70)