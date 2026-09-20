import pandas as pd

path = r"DATA\processed\shimla_master_dataset.csv"

df = pd.read_csv(path)
df["time"] = pd.to_datetime(df["time"])

# 72-hour antecedent period
start = pd.Timestamp("2023-08-11 00:00:00")
end = pd.Timestamp("2023-08-14 00:00:00")

window = df[
    (df["time"] >= start) &
    (df["time"] < end)
].copy()

print("=" * 70)
print("2023 SHIMLA EVENT WINDOW — ALL GRID CELLS")
print("=" * 70)

print("\nWindow:")
print(start, "->", end - pd.Timedelta(hours=1))

print("\nTotal rows:", len(window))

for (lat, lon), cell in window.groupby(
    ["latitude", "longitude"]
):

    print("\n" + "-" * 70)
    print(
        f"Location: latitude={lat}, longitude={lon}"
    )

    print("Observations:", len(cell))

    rain = cell["rainfall_mm"]

    print(
        f"72h rainfall total : {rain.sum():.3f} mm"
    )

    print(
        f"Max hourly rainfall: {rain.max():.3f} mm"
    )

    print(
        f"Max 3h rainfall    : "
        f"{rain.rolling(3).sum().max():.3f} mm"
    )

    print(
        f"Max 6h rainfall    : "
        f"{rain.rolling(6).sum().max():.3f} mm"
    )

    print(
        f"Max 12h rainfall   : "
        f"{rain.rolling(12).sum().max():.3f} mm"
    )

    print(
        f"Max 24h rainfall   : "
        f"{rain.rolling(24).sum().max():.3f} mm"
    )

    print(
        f"Mean soil moisture : "
        f"{cell[['swvl1', 'swvl2', 'swvl3', 'swvl4']].mean().mean():.4f}"
    )

    print(
        f"Mean temperature   : "
        f"{cell['temperature_c'].mean():.2f} °C"
    )

    print(
        f"Max temperature    : "
        f"{cell['temperature_c'].max():.2f} °C"
    )

    print(
        f"Mean wind speed    : "
        f"{cell['wind_speed'].mean():.2f} m/s"
    )

print("\n" + "=" * 70)
print("2023 EVENT CELL INSPECTION COMPLETE")
print("=" * 70)