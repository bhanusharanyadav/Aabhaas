import os
import pandas as pd

BASE = r"DATA\processed"

controls = {
    "Control_2017": {
        "file": "shimla_2017_rainfall.csv",
        "date": "2017-08-13"
    },
    "Control_2021": {
        "file": "shimla_2021_rainfall.csv",
        "date": "2021-08-13"
    },
    "Control_2022": {
        "file": "shimla_2022_rainfall.csv",
        "date": "2022-08-11"
    }
}

for name, info in controls.items():

    print("\n" + "=" * 70)
    print(name)
    print("=" * 70)

    path = os.path.join(BASE, info["file"])

    df = pd.read_csv(path)
    df["time"] = pd.to_datetime(df["time"])

    target_date = pd.Timestamp(info["date"])

    # 72 hours before selected date
    start = target_date - pd.Timedelta(hours=72)
    end = target_date

    period = df[
        (df["time"] >= start) &
        (df["time"] < end)
    ].copy()

    print("Control date:", target_date.date())
    print("Period:", start, "->", end)

    print("\nRows:", len(period))
    print("Unique timestamps:", period["time"].nunique())
    print(
        "Unique locations:",
        period[["latitude", "longitude"]].drop_duplicates().shape[0]
    )

    print("\nRainfall:")
    print("Total:", round(period["rainfall_mm"].sum(), 3), "mm")
    print("Maximum hourly:",
          round(period["rainfall_mm"].max(), 3), "mm")
    print("Mean hourly:",
          round(period["rainfall_mm"].mean(), 3), "mm")

    print("\nSoil moisture:")
    for col in ["swvl1", "swvl2", "swvl3", "swvl4"]:
        print(
            f"{col}: "
            f"mean={period[col].mean():.6f}, "
            f"min={period[col].min():.6f}, "
            f"max={period[col].max():.6f}"
        )

    print("\nTemperature:")
    print("Mean:", round(period["temperature_c"].mean(), 3))
    print("Min :", round(period["temperature_c"].min(), 3))
    print("Max :", round(period["temperature_c"].max(), 3))

    print("\nWind speed:")
    print("Mean:", round(period["wind_speed"].mean(), 3))
    print("Max :", round(period["wind_speed"].max(), 3))

print("\n" + "=" * 70)
print("CONTROL PERIOD INSPECTION COMPLETE")
print("=" * 70)