import pandas as pd

INPUT = r"DATA\processed\shimla_master_dataset.csv"
OUTPUT = r"DATA\processed\shimla_72h_feature_table.csv"

df = pd.read_csv(INPUT)
df["time"] = pd.to_datetime(df["time"])

rows = []

for year in sorted(df["time"].dt.year.unique()):

    prediction_time = pd.Timestamp(
        f"{year}-08-14 00:00:00"
    )

    start_time = prediction_time - pd.Timedelta(hours=72)

    data = df[
        (df["time"] >= start_time) &
        (df["time"] < prediction_time)
    ].copy()

    for (lat, lon), cell in data.groupby(
        ["latitude", "longitude"]
    ):

        cell = cell.sort_values("time")

        if len(cell) != 72:
            continue

        rain = cell["rainfall_mm"]

        row = {
            "year": year,
            "prediction_time": prediction_time,
            "latitude": lat,
            "longitude": lon,

            # Rainfall
            "rain_total_72h": rain.sum(),
            "rain_max_1h": rain.max(),
            "rain_max_3h": rain.rolling(3).sum().max(),
            "rain_max_6h": rain.rolling(6).sum().max(),
            "rain_max_12h": rain.rolling(12).sum().max(),
            "rain_max_24h": rain.rolling(24).sum().max(),

            # Temperature
            "temperature_mean": cell["temperature_c"].mean(),
            "temperature_min": cell["temperature_c"].min(),
            "temperature_max": cell["temperature_c"].max(),

            # Dew point
            "dewpoint_mean": cell["dewpoint_c"].mean(),

            # Wind
            "wind_mean": cell["wind_speed"].mean(),
            "wind_max": cell["wind_speed"].max(),

            # Surface pressure
            "pressure_mean": cell["sp"].mean(),
            "pressure_min": cell["sp"].min(),

            # Soil moisture
            "swvl1_mean": cell["swvl1"].mean(),
            "swvl1_max": cell["swvl1"].max(),

            "swvl2_mean": cell["swvl2"].mean(),
            "swvl2_max": cell["swvl2"].max(),

            "swvl3_mean": cell["swvl3"].mean(),
            "swvl3_max": cell["swvl3"].max(),

            "swvl4_mean": cell["swvl4"].mean(),
            "swvl4_max": cell["swvl4"].max(),

            # Vegetation-related variables
            "lai_lv_mean": cell["lai_lv"].mean(),
            "lai_hv_mean": cell["lai_hv"].mean(),

            # Cloud / convection related
            "cvl_mean": cell["cvl"].mean(),
            "cvh_mean": cell["cvh"].mean(),
        }

        rows.append(row)

features = pd.DataFrame(rows)

features.to_csv(OUTPUT, index=False)

print("=" * 70)
print("FIRST SHIMLA 72-HOUR FEATURE TABLE")
print("=" * 70)

print("\nRows:", len(features))
print("Columns:", len(features.columns))

print("\nRows by year:")
print(features.groupby("year").size())

print("\nLocations:")
print(
    features[
        ["latitude", "longitude"]
    ].drop_duplicates().to_string(index=False)
)

print("\nMissing values:")
print(features.isna().sum())

print("\nFeature columns:")
for col in features.columns:
    print("-", col)

print("\nOutput:")
print(OUTPUT)

print("\n" + "=" * 70)
print("FEATURE TABLE CREATION COMPLETE")
print("=" * 70)