import pandas as pd

path = r"DATA\processed\shimla_baseline_dataset.csv"

df = pd.read_csv(path)
df["time"] = pd.to_datetime(df["time"])

print("=" * 70)
print("72-HOUR WINDOW FEATURE INSPECTION")
print("=" * 70)

# Make sure data is ordered
df = df.sort_values(
    ["latitude", "longitude", "time"]
).reset_index(drop=True)

# Select one location for inspection
lat = df["latitude"].iloc[0]
lon = df["longitude"].iloc[0]

cell = df[
    (df["latitude"] == lat) &
    (df["longitude"] == lon)
].copy()

cell = cell.sort_values("time").reset_index(drop=True)

print("\nInspection location:")
print("Latitude :", lat)
print("Longitude:", lon)

print("\nTotal timestamps:", len(cell))

# Find complete 72-hour windows
windows = []

for i in range(len(cell) - 71):

    window = cell.iloc[i:i + 72]

    if (
        window["time"].iloc[-1]
        - window["time"].iloc[0]
        == pd.Timedelta(hours=71)
    ):

        windows.append(window)

print("Complete 72-hour windows:", len(windows))

# Inspect first 5 windows
print("\nFIRST 5 WINDOWS")
print("-" * 70)

for i, window in enumerate(windows[:5], start=1):

    print(f"\nWindow {i}")

    print(
        "Start:",
        window["time"].iloc[0]
    )

    print(
        "End  :",
        window["time"].iloc[-1]
    )

    print(
        "Rainfall total:",
        round(window["rainfall_mm"].sum(), 3),
        "mm"
    )

    print(
        "Maximum hourly rainfall:",
        round(window["rainfall_mm"].max(), 3),
        "mm"
    )

    print(
        "Maximum 3h rainfall:",
        round(window["rain_3h"].max(), 3),
        "mm"
    )

    print(
        "Maximum 6h rainfall:",
        round(window["rain_6h"].max(), 3),
        "mm"
    )

    print(
        "Maximum 12h rainfall:",
        round(window["rain_12h"].max(), 3),
        "mm"
    )

    print(
        "Maximum 24h rainfall:",
        round(window["rain_24h"].max(), 3),
        "mm"
    )

    print(
        "Maximum 72h rainfall:",
        round(window["rain_72h"].max(), 3),
        "mm"
    )

    print(
        "Mean soil moisture:",
        round(
            window[
                ["swvl1", "swvl2", "swvl3", "swvl4"]
            ].mean().mean(),
            4
        )
    )

    print(
        "Mean temperature:",
        round(window["temperature_c"].mean(), 2),
        "°C"
    )

print("\n" + "=" * 70)
print("WINDOW INSPECTION COMPLETE")
print("=" * 70)