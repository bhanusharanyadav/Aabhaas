import os
import numpy as np
import pandas as pd
import cfgrib

BASE = r"C:\Users\bhanu\OneDrive\Desktop\AI-Hybrid-Landslide Prediction\DATA\Raw\Landslide event"

events = {
    "Shimla": os.path.join(
        BASE, "Shimla",
        "c1cdc1cdec6e393a8e5f14b76a4598ee.grib"
    ),
    "Kinnaur": os.path.join(
        BASE, "kinnaur himachal",
        "4cf1e423cff3176d2b3a862fb20dba3c.grib"
    ),
    "Chamoli": os.path.join(
        BASE, "chamoli uttrakhand",
        "292f75f24341a9832c6c4bb7113a8499.grib"
    ),
}

output_dir = os.path.join(BASE, "processed")
os.makedirs(output_dir, exist_ok=True)

for event, path in events.items():

    print("\n" + "=" * 70)
    print("EVENT:", event)
    print("=" * 70)

    datasets = cfgrib.open_datasets(
        path,
        backend_kwargs={"indexpath": ""}
    )

    tp_ds = datasets[6]
    tp = tp_ds["tp"]

    print("Original dimensions:", dict(tp.sizes))
    print("Units:", tp.attrs.get("units"))

    values = tp.values
    valid_times = tp_ds["valid_time"].values

    rows = []

    for i in range(values.shape[0]):
        for j in range(values.shape[1]):

            valid_time = pd.Timestamp(valid_times[i, j])

            for lat_idx in range(values.shape[2]):
                for lon_idx in range(values.shape[3]):

                    rainfall_m = values[i, j, lat_idx, lon_idx]

                    if np.isnan(rainfall_m):
                        continue

                    rows.append({
                        "event": event,
                        "time": valid_time,
                        "latitude": float(
                            tp_ds.latitude.values[lat_idx]
                        ),
                        "longitude": float(
                            tp_ds.longitude.values[lon_idx]
                        ),
                        "rainfall_mm": float(rainfall_m * 1000)
                    })

    df = pd.DataFrame(rows)

    df = df.drop_duplicates(
        subset=["event", "time", "latitude", "longitude"]
    )

    df = df.sort_values(
        ["latitude", "longitude", "time"]
    ).reset_index(drop=True)

    print("Rows:", len(df))
    print("Unique timestamps:", df["time"].nunique())
    print(
        "Unique locations:",
        df[["latitude", "longitude"]].drop_duplicates().shape[0]
    )
    print("Time:", df["time"].min(), "->", df["time"].max())
    print("Rainfall min:", df["rainfall_mm"].min())
    print("Rainfall max:", df["rainfall_mm"].max())
    print("Rainfall mean:", df["rainfall_mm"].mean())

    negative = (df["rainfall_mm"] < 0).sum()
    print("Negative rainfall values:", negative)

    output_file = os.path.join(
        output_dir,
        f"{event.lower()}_event_rainfall.csv"
    )

    df.to_csv(output_file, index=False)

    print("Saved:", output_file)


print("\n" + "=" * 70)
print("EVENT RAINFALL EXTRACTION COMPLETE")
print("=" * 70)