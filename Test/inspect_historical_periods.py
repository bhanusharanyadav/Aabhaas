import os
import pandas as pd

BASE = r"DATA\processed"

years = list(range(2016, 2027))

print("=" * 70)
print("HISTORICAL SHIMLA PERIOD INSPECTION")
print("=" * 70)

for year in years:

    path = os.path.join(BASE, f"shimla_{year}_rainfall.csv")

    if not os.path.exists(path):
        print(f"\n{year}: FILE NOT FOUND")
        continue

    df = pd.read_csv(path)
    df["time"] = pd.to_datetime(df["time"])

    print(f"\n{'-' * 60}")
    print("YEAR:", year)
    print("Rows:", len(df))

    # Daily regional rainfall
    daily = (
        df.groupby(df["time"].dt.date)["rainfall_mm"]
        .mean()
        .reset_index(name="mean_hourly_rainfall")
    )

    daily["date"] = pd.to_datetime(daily["time"])
    daily["daily_rainfall_mm"] = (
        df.assign(date=df["time"].dt.date)
          .groupby("date")["rainfall_mm"]
          .sum()
          .values
    )

    print("\nDaily rainfall:")
    print(
        daily[["date", "daily_rainfall_mm"]]
        .to_string(index=False)
    )

    print("\nWettest day:")
    wettest = daily.loc[daily["daily_rainfall_mm"].idxmax()]
    print(
        wettest["date"],
        "->",
        round(wettest["daily_rainfall_mm"], 3),
        "mm"
    )

print("\n" + "=" * 70)
print("HISTORICAL PERIOD INSPECTION COMPLETE")
print("=" * 70)