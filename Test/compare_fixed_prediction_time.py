
import pandas as pd

path = r"DATA\processed\shimla_baseline_dataset.csv"

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
print("FIXED 72-HOUR PREDICTION-TIME COMPARISON")
print("=" * 70)

# We use Aug 14 00:00 as the prediction time in every year.
prediction_hour = "08-14 00:00:00"

for year in sorted(cell["time"].dt.year.unique()):

    prediction_time = pd.Timestamp(
        f"{year}-{prediction_hour}"
    )

    start_time = prediction_time - pd.Timedelta(hours=72)

    window = cell[
        (cell["time"] >= start_time) &
        (cell["time"] < prediction_time)
    ].copy()

    # Make sure exactly 72 hourly observations exist
    if len(window) != 72:
        print(
            f"{year}: INVALID WINDOW "
            f"({len(window)} observations)"
        )
        continue

    print(f"\n{year}")
    print("-" * 70)

    print(
        f"Window: {start_time} -> "
        f"{prediction_time - pd.Timedelta(hours=1)}"
    )

    print(
        f"Rain total: "
        f"{window['rainfall_mm'].sum():.3f} mm"
    )

    print(
        f"Max hourly rain: "
        f"{window['rainfall_mm'].max():.3f} mm"
    )

    print(
        f"Max 3h rain: "
        f"{window['rain_3h'].max():.3f} mm"
    )

    print(
        f"Max 6h rain: "
        f"{window['rain_6h'].max():.3f} mm"
    )

    print(
        f"Max 12h rain: "
        f"{window['rain_12h'].max():.3f} mm"
    )

    print(
        f"Max 24h rain: "
        f"{window['rain_24h'].max():.3f} mm"
    )

    print(
        f"Max 72h rain: "
        f"{window['rain_72h'].max():.3f} mm"
    )

    print(
        f"Mean soil moisture: "
        f"{window[['swvl1','swvl2','swvl3','swvl4']].mean().mean():.4f}"
    )

    print(
        f"Mean temperature: "
        f"{window['temperature_c'].mean():.2f} °C"
    )

print("\n" + "=" * 70)
print("FIXED-TIME COMPARISON COMPLETE")
print("=" * 70)