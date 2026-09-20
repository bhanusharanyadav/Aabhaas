import pandas as pd
import os

BASE = r"DATA\Raw\Landslide event\processed"

events = {
    "Shimla": {
        "file": "shimla_event_rainfall.csv",
        "event_date": "2023-08-14"
    },
    "Kinnaur": {
        "file": "kinnaur_event_rainfall.csv",
        "event_date": "2021-08-11"
    },
    "Chamoli": {
        "file": "chamoli_event_rainfall.csv",
        "event_date": "2021-02-07"
    }
}

for event, info in events.items():

    print("\n" + "=" * 70)
    print("EVENT:", event)
    print("KNOWN LANDSLIDE DATE:", info["event_date"])
    print("=" * 70)

    path = os.path.join(BASE, info["file"])

    df = pd.read_csv(path)
    df["time"] = pd.to_datetime(df["time"])

    event_date = pd.Timestamp(info["event_date"])

    # Show 3 days before and 1 day after the event
    start = event_date - pd.Timedelta(days=3)
    end = event_date + pd.Timedelta(days=1)

    subset = df[
        (df["time"] >= start) &
        (df["time"] < end)
    ].copy()

    # Average rainfall across all grid cells
    hourly = (
        subset
        .groupby("time")["rainfall_mm"]
        .mean()
        .reset_index()
    )

    print("\nHourly rainfall:")
    print(hourly.to_string(index=False))

    print("\nDaily rainfall:")
    daily = (
        subset
        .assign(date=subset["time"].dt.date)
        .groupby("date")["rainfall_mm"]
        .sum()
    )

    print(daily)

    print("\nMaximum hourly rainfall:",
          hourly["rainfall_mm"].max())

    print("Total rainfall in window:",
          hourly["rainfall_mm"].sum())

print("\n" + "=" * 70)
print("EVENT RAINFALL INSPECTION COMPLETE")
print("=" * 70)