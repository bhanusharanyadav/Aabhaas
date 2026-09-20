import pandas as pd

path = r"DATA\processed\shimla_baseline_dataset.csv"

df = pd.read_csv(path)
df["time"] = pd.to_datetime(df["time"])

df = df.sort_values(
    ["latitude", "longitude", "time"]
).reset_index(drop=True)

print("=" * 70)
print("CANDIDATE SHIMLA CONTROL WINDOWS")
print("=" * 70)

# Use one representative grid cell
lat = 31.0
lon = 77.0

cell = df[
    (df["latitude"] == lat) &
    (df["longitude"] == lon)
].copy()

cell = cell.sort_values("time").reset_index(drop=True)

windows = []

for i in range(len(cell) - 71):

    window = cell.iloc[i:i + 72]

    # Require 72 consecutive hourly observations
    if (
        window["time"].iloc[-1]
        - window["time"].iloc[0]
        != pd.Timedelta(hours=71)
    ):
        continue

    windows.append({
        "start": window["time"].iloc[0],
        "end": window["time"].iloc[-1],

        "rain_3h_max": window["rain_3h"].max(),
        "rain_6h_max": window["rain_6h"].max(),
        "rain_12h_max": window["rain_12h"].max(),
        "rain_24h_max": window["rain_24h"].max(),
        "rain_72h_max": window["rain_72h"].max(),

        "rain_total": window["rainfall_mm"].sum(),

        "soil_mean": window[
            ["swvl1", "swvl2", "swvl3", "swvl4"]
        ].mean().mean(),

        "temperature_mean": window["temperature_c"].mean(),
        "temperature_max": window["temperature_c"].max(),

        "wind_mean": window["wind_speed"].mean(),
        "wind_max": window["wind_speed"].max()
    })

windows = pd.DataFrame(windows)

print("\nTotal complete windows:", len(windows))

# Show the 20 windows with the highest 72-hour rainfall
top = windows.sort_values(
    "rain_72h_max",
    ascending=False
).head(20)

print("\nTOP 20 WINDOWS BY 72-HOUR RAINFALL")
print("-" * 70)

for _, row in top.iterrows():

    print(
        f"{row['start']} -> {row['end']} | "
        f"72h={row['rain_72h_max']:.2f} mm | "
        f"24h={row['rain_24h_max']:.2f} mm | "
        f"12h={row['rain_12h_max']:.2f} mm | "
        f"6h={row['rain_6h_max']:.2f} mm | "
        f"3h={row['rain_3h_max']:.2f} mm"
    )

print("\n" + "=" * 70)
print("CONTROL CANDIDATE ANALYSIS COMPLETE")
print("=" * 70)