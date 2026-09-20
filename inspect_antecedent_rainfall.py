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
    print("KNOWN LANDSLIDE DATE:", info["event_date"])
    print("=" * 70)

    path = os.path.join(BASE, info["file"])

    df = pd.read_csv(path)
    df["time"] = pd.to_datetime(df["time"])

    event_date = pd.Timestamp(info["event_date"])

    # Use rainfall BEFORE the event date.
    # Event day itself is excluded.
    start = event_date - pd.Timedelta(hours=72)

    before = df[
        (df["time"] >= start) &
        (df["time"] < event_date)
    ].copy()

    print("\nAntecedent period:")
    print(start, "->", event_date)

    # Calculate accumulated rainfall for each grid cell
    results = []

    for (lat, lon), group in before.groupby(
        ["latitude", "longitude"]
    ):

        group = group.sort_values("time")

        results.append({
            "latitude": lat,
            "longitude": lon,

            "rain_6h_mm":
                group["rainfall_mm"].tail(6).sum(),

            "rain_12h_mm":
                group["rainfall_mm"].tail(12).sum(),

            "rain_24h_mm":
                group["rainfall_mm"].tail(24).sum(),

            "rain_72h_mm":
                group["rainfall_mm"].sum(),

            "max_hourly_mm":
                group["rainfall_mm"].max()
        })

    result = pd.DataFrame(results)

    print("\nAntecedent rainfall by grid cell:")
    print(result.to_string(index=False))

    print("\nRegional summary:")
    print(
        result[
            [
                "rain_6h_mm",
                "rain_12h_mm",
                "rain_24h_mm",
                "rain_72h_mm",
                "max_hourly_mm"
            ]
        ].describe().to_string()
    )

print("\n" + "=" * 70)
print("ANTECEDENT RAINFALL INSPECTION COMPLETE")
print("=" * 70)