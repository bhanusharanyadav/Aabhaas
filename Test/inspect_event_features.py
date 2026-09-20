import os
import pandas as pd

BASE = r"DATA\Raw\Landslide event\processed"

events = {
    "Shimla": {
        "file": "shimla_event_dataset.csv",
        "event_date": "2023-08-14"
    },
    "Kinnaur": {
        "file": "kinnaur_event_dataset.csv",
        "event_date": "2021-08-11"
    },
    "Chamoli": {
        "file": "chamoli_event_dataset.csv",
        "event_date": "2021-02-07"
    }
}

for name, info in events.items():

    print("\n" + "=" * 70)
    print("EVENT:", name)
    print("=" * 70)

    path = os.path.join(BASE, info["file"])
    df = pd.read_csv(path)
    df["time"] = pd.to_datetime(df["time"])

    event_date = pd.Timestamp(info["event_date"])

    # 72 hours before event
    start = event_date - pd.Timedelta(hours=72)
    end = event_date

    before = df[
        (df["time"] >= start) &
        (df["time"] < end)
    ].copy()

    print("Antecedent period:")
    print(start, "->", end)

    print("\nRows:", len(before))
    print("Unique timestamps:", before["time"].nunique())
    print("Unique locations:",
          before[["latitude", "longitude"]].drop_duplicates().shape[0])

    print("\nRainfall statistics:")
    print("Total rainfall:",
          before["rainfall_mm"].sum())
    print("Maximum hourly rainfall:",
          before["rainfall_mm"].max())
    print("Mean hourly rainfall:",
          before["rainfall_mm"].mean())

    print("\nSoil moisture means:")
    for col in ["swvl1", "swvl2", "swvl3", "swvl4"]:
        print(f"{col}: {before[col].mean():.6f}")

    print("\nTemperature:")
    print("Mean:", before["temperature_c"].mean())
    print("Min :", before["temperature_c"].min())
    print("Max :", before["temperature_c"].max())

    print("\nWind speed:")
    print("Mean:", before["wind_speed"].mean())
    print("Max :", before["wind_speed"].max())

print("\n" + "=" * 70)
print("EVENT FEATURE INSPECTION COMPLETE")
print("=" * 70)