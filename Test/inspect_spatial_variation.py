import pandas as pd

path = r"DATA\processed\shimla_master_dataset.csv"

df = pd.read_csv(path)
df["time"] = pd.to_datetime(df["time"])

print("=" * 70)
print("SHIMLA SPATIAL VARIATION ANALYSIS")
print("=" * 70)

# Calculate daily rainfall for each grid cell
df["date"] = df["time"].dt.date

daily = (
    df.groupby(
        ["date", "latitude", "longitude"]
    )["rainfall_mm"]
    .sum()
    .reset_index()
)

print("\nDaily rainfall spatial statistics")
print("-" * 70)

for year in sorted(df["time"].dt.year.unique()):

    year_daily = daily[
        pd.to_datetime(daily["date"]).dt.year == year
    ]

    spatial_stats = (
        year_daily
        .groupby("date")["rainfall_mm"]
        .agg(["min", "max", "mean"])
    )

    spatial_range = (
        spatial_stats["max"] -
        spatial_stats["min"]
    )

    print(
        f"{year}: "
        f"mean spatial range = "
        f"{spatial_range.mean():.3f} mm | "
        f"max spatial range = "
        f"{spatial_range.max():.3f} mm"
    )

print("\n2023 EVENT PERIOD")
print("-" * 70)

event = daily[
    (pd.to_datetime(daily["date"]) >= pd.Timestamp("2023-08-11")) &
    (pd.to_datetime(daily["date"]) <= pd.Timestamp("2023-08-13"))
]

print(event.to_string(index=False))

print("\n" + "=" * 70)
print("SPATIAL ANALYSIS COMPLETE")
print("=" * 70)