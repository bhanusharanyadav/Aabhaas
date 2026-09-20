import os
import pandas as pd
import xarray as xr
import cfgrib

# --------------------------------------------------
# PATHS
# --------------------------------------------------

grib_file = r"C:\Users\bhanu\OneDrive\Desktop\AI-Hybrid-Landslide Prediction\DATA\Raw\historical data\2023\c1cdc1cdec6e393a8e5f14b76a4598ee (1).grib"

output_folder = r"C:\Users\bhanu\OneDrive\Desktop\AI-Hybrid-Landslide Prediction\DATA\processed"

os.makedirs(output_folder, exist_ok=True)

# --------------------------------------------------
# OPEN GRIB DATASETS
# --------------------------------------------------

datasets = cfgrib.open_datasets(grib_file)

print("Number of datasets:", len(datasets))

# Main hourly weather dataset
weather = datasets[5]

# Soil moisture datasets
swvl1 = datasets[0]["swvl1"]
swvl2 = datasets[1]["swvl2"]
swvl3 = datasets[2]["swvl3"]
swvl4 = datasets[3]["swvl4"]

# --------------------------------------------------
# CONVERT MAIN WEATHER DATA TO DATAFRAME
# --------------------------------------------------

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

# --------------------------------------------------
# ADD SOIL MOISTURE
# --------------------------------------------------

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

# --------------------------------------------------
# DERIVED FEATURES
# --------------------------------------------------

# Temperature Celsius
df["temperature_c"] = df["t2m"] - 273.15

# Dew point Celsius
df["dewpoint_c"] = df["d2m"] - 273.15

# Wind speed
df["wind_speed"] = (
    df["u10"] ** 2 + df["v10"] ** 2
) ** 0.5

# Precipitation / rain water in mm
df["rain_water_mm"] = df["tcrw"]

# --------------------------------------------------
# SORT DATA
# --------------------------------------------------

df = df.sort_values(
    ["time", "latitude", "longitude"]
).reset_index(drop=True)

# --------------------------------------------------
# SAVE
# --------------------------------------------------

output_file = os.path.join(
    output_folder,
    "shimla_2023_processed.csv"
)

df.to_csv(output_file, index=False)

print("\nExtraction successful!")
print("Rows:", len(df))
print("Columns:", len(df.columns))
print("Output:", output_file)

print("\nFirst 5 rows:")
print(df.head())