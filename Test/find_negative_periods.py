import os
import pandas as pd

BASE = r"DATA\processed"

years = list(range(2016, 2027))

# Known documented Shimla event
known_event_date = pd.Timestamp("2023-08-14")

print("=" * 70)
print("CANDIDATE NON-EVENT PERIODS")
print("=" * 70)

all_daily = []

for year in years:

    path = os.path.join(BASE, f"shimla_{year}_rainfall.csv")

    if not os.path.exists(path):
        continue

    df = pd.read_csv(path)
    df["time"] = pd.to_datetime(df["time"])
    df["date"] = df["time"].dt.normalize()

    # Daily regional rainfall
    daily = (
        df.groupby("date")["rainfall_mm"]
        .sum()
        .reset_index(name="daily_rainfall_mm")
    )

    daily["year"] = year

    all_daily.append(daily)

daily_all = pd.concat(all_daily, ignore_index=True)

# Remove the known Shimla event day
candidates = daily_all[
    daily_all["date"] != known_event_date
].copy()

# Sort by rainfall
candidates = candidates.sort_values("daily_rainfall_mm")

print("\nAll candidate dates excluding known Shimla event:")
print(
    candidates[
        ["date", "year", "daily_rainfall_mm"]
    ].to_string(index=False)
)

print("\n" + "-" * 70)
print("LOW-RAINFALL CANDIDATES")
print("-" * 70)

print(
    candidates
    .sort_values("daily_rainfall_mm")
    .head(10)[
        ["date", "year", "daily_rainfall_mm"]
    ]
    .to_string(index=False)
)

print("\n" + "-" * 70)
print("HIGH-RAINFALL NON-EVENT CANDIDATES")
print("-" * 70)

print(
    candidates
    .sort_values("daily_rainfall_mm", ascending=False)
    .head(10)[
        ["date", "year", "daily_rainfall_mm"]
    ]
    .to_string(index=False)
)

print("\n" + "=" * 70)
print("CANDIDATE PERIOD SEARCH COMPLETE")
print("=" * 70)