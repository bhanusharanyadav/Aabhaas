import os
import pandas as pd

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
    print("KNOWN EVENT DATE:", info["event_date"])
    print("=" * 70)

    path = os.path.join(BASE, info["file"])

    df = pd.read_csv(path)
    df["time"] = pd.to_datetime(df["time"])

    print("\nDataset:")
    print("Start:", df["time"].min())
    print("End:", df["time"].max())

    print("\nLocations:")
    print(
        df[["latitude", "longitude"]]
        .drop_duplicates()
        .sort_values(["latitude", "longitude"])
        .to_string(index=False)
    )

    event_date = pd.Timestamp(info["event_date"])

    # Show each hourly timestamp on the event date
    event_day = df[df["time"].dt.date == event_date.date()].copy()

    print("\nEvent-day rainfall by location:")

    result = (
        event_day
        .groupby(["latitude", "longitude"])["rainfall_mm"]
        .agg(["count", "sum", "max", "mean"])
        .reset_index()
    )

    print(result.to_string(index=False))

    print("\nEvent-day timestamps:")
    print(
        event_day["time"]
        .drop_duplicates()
        .sort_values()
        .to_string(index=False)
    )

print("\n" + "=" * 70)
print("EVENT TIMING INSPECTION COMPLETE")
print("=" * 70)