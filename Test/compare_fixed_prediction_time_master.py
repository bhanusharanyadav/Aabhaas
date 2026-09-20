import pandas as pd

path = r"DATA\processed\shimla_master_dataset.csv"

df = pd.read_csv(path)
df["time"] = pd.to_datetime(df["time"])

# Representative Shimla grid cell
lat = 31.0
lon = 77.0

cell = df[
    (df["latitude"] == lat) &
    (df["longitude"] == lon)
].copy()

cell = cell.sort_values("time").reset_index(drop=True)

print("=" * 70)
print("FIXED 72-HOUR WINDOW — MASTER DATASET")
print("=" * 70)

for year in sorted(cell["time"].dt.year.unique()):

    prediction_time = pd.Timestamp(
        f"{year}-08-14 00:00:00"
    )

    start_time = prediction_time - pd.Timedelta(hours=72)

    window = cell[
        (cell["time"] >= start_time) &
        (cell["time"] < prediction_time)
    ].copy()

    print(f"\n{year}")
    print("-" * 70)

    print(
        "Window:",
        start_time,
        "->",
        prediction_time - pd.Timedelta(hours=1)
    )

    print("Observations:", len(window))

    if len(window) != 72:
        print("STATUS: INVALID")
        continue

    print("STATUS: VALID")

    # Calculate rainfall features directly from hourly rainfall
    rain = window["rainfall_mm"]

    print(f"Rain total: {rain.sum():.3f} mm")
    print(f"Max hourly rain: {rain.max():.3f} mm")

    print(
        f"Max 3h rain: "
        f"{rain.rolling(3).sum().max():.3f} mm"
    )

    print(
        f"Max 6h rain: "
        f"{rain.rolling(6).sum().max():.3f} mm"
    )

    print(
        f"Max 12h rain: "
        f"{rain.rolling(12).sum().max():.3f} mm"
    )

    print(
        f"Max 24h rain: "
        f"{rain.rolling(24).sum().max():.3f} mm"
    )

    print(
        f"Max 72h rain: "
        f"{rain.sum():.3f} mm"
    )

    print(
        f"Mean soil moisture: "
        f"{window[['swvl1','swvl2','swvl3','swvl4']].mean().mean():.4f}"
    )

    print(
        f"Mean temperature: "
        f"{window['temperature_c'].mean():.2f} °C"
    )

    print(
        f"Max temperature: "
        f"{window['temperature_c'].max():.2f} °C"
    )

    print(
        f"Mean wind speed: "
        f"{window['wind_speed'].mean():.2f} m/s"
    )

print("\n" + "=" * 70)
print("MASTER WINDOW CHECK COMPLETE")
print("=" * 70)