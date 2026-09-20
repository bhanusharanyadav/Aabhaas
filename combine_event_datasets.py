import os
import pandas as pd
import cfgrib

BASE = r"C:\Users\bhanu\OneDrive\Desktop\AI-Hybrid-Landslide Prediction"
EVENT_BASE = os.path.join(BASE, "DATA", "Raw", "Landslide event")
OUTPUT_DIR = os.path.join(EVENT_BASE, "processed")

events = {
    "Shimla": os.path.join(
        EVENT_BASE, "Shimla",
        "c1cdc1cdec6e393a8e5f14b76a4598ee.grib"
    ),
    "Kinnaur": os.path.join(
        EVENT_BASE, "kinnaur himachal",
        "4cf1e423cff3176d2b3a862fb20dba3c.grib"
    ),
    "Chamoli": os.path.join(
        EVENT_BASE, "chamoli uttrakhand",
        "292f75f24341a9832c6c4bb7113a8499.grib"
    )
}

rainfall_files = {
    "Shimla": "shimla_event_rainfall.csv",
    "Kinnaur": "kinnaur_event_rainfall.csv",
    "Chamoli": "chamoli_event_rainfall.csv"
}

for event, grib_path in events.items():

    print("\n" + "=" * 70)
    print("EVENT:", event)
    print("=" * 70)

    # -----------------------------
    # Read GRIB datasets
    # -----------------------------
    datasets = cfgrib.open_datasets(
        grib_path,
        backend_kwargs={"indexpath": ""}
    )

    weather = datasets[5]

    # -----------------------------
    # Select environmental variables
    # -----------------------------
    variables = [
        "t2m",
        "d2m",
        "u10",
        "v10",
        "sp",
        "tcrw",
        "cvl",
        "cvh",
        "lai_lv",
        "lai_hv"
    ]

    weather_df = weather[variables].to_dataframe().reset_index()

    # Keep only useful columns
    weather_df = weather_df[
        [
            "time",
            "latitude",
            "longitude",
            "t2m",
            "d2m",
            "u10",
            "v10",
            "sp",
            "tcrw",
            "cvl",
            "cvh",
            "lai_lv",
            "lai_hv"
        ]
    ]

    # -----------------------------
    # Convert temperature
    # Kelvin -> Celsius
    # -----------------------------
    weather_df["temperature_c"] = (
        weather_df["t2m"] - 273.15
    )

    weather_df["dewpoint_c"] = (
        weather_df["d2m"] - 273.15
    )

    # -----------------------------
    # Calculate wind speed
    # -----------------------------
    weather_df["wind_speed"] = (
        weather_df["u10"] ** 2 +
        weather_df["v10"] ** 2
    ) ** 0.5

    # -----------------------------
    # Soil moisture
    # -----------------------------
    soil_dfs = []

    for i in range(4):

        soil_var = f"swvl{i + 1}"

        soil_df = datasets[i][soil_var].to_dataframe().reset_index()

        soil_df = soil_df[
            [
                "time",
                "latitude",
                "longitude",
                soil_var
            ]
        ]

        soil_dfs.append(soil_df)

    # Merge soil layers
    environmental_df = weather_df.copy()

    for soil_df in soil_dfs:

        environmental_df = environmental_df.merge(
            soil_df,
            on=["time", "latitude", "longitude"],
            how="left"
        )

    # -----------------------------
    # Load rainfall
    # -----------------------------
    rainfall_path = os.path.join(
        OUTPUT_DIR,
        rainfall_files[event]
    )

    rainfall_df = pd.read_csv(rainfall_path)

    rainfall_df["time"] = pd.to_datetime(
        rainfall_df["time"]
    )

    # -----------------------------
    # Merge rainfall
    # -----------------------------
    final_df = environmental_df.merge(
        rainfall_df,
        on=["time", "latitude", "longitude"],
        how="left"
    )

    # -----------------------------
    # Sort
    # -----------------------------
    final_df = final_df.sort_values(
        ["latitude", "longitude", "time"]
    ).reset_index(drop=True)

    # -----------------------------
    # Basic checks
    # -----------------------------
    print("Rows:", len(final_df))
    print("Columns:", len(final_df.columns))
    print("Missing values:", final_df.isna().sum().sum())
    print("Duplicate rows:", final_df.duplicated().sum())
    print(
        "Unique locations:",
        final_df[["latitude", "longitude"]]
        .drop_duplicates()
        .shape[0]
    )
    print(
        "Unique timestamps:",
        final_df["time"].nunique()
    )

    print("\nColumns:")
    print(list(final_df.columns))

    # -----------------------------
    # Save
    # -----------------------------
    output_file = os.path.join(
        OUTPUT_DIR,
        f"{event.lower()}_event_dataset.csv"
    )

    final_df.to_csv(
        output_file,
        index=False
    )

    print("\nSaved:")
    print(output_file)


print("\n" + "=" * 70)
print("EVENT DATASET COMBINATION COMPLETE")
print("=" * 70)