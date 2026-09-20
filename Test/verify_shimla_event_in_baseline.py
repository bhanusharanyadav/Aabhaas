import pandas as pd

path = r"DATA\processed\shimla_baseline_dataset.csv"

df = pd.read_csv(path)
df["time"] = pd.to_datetime(df["time"])

event_date = pd.Timestamp("2023-08-14")

start = event_date - pd.Timedelta(hours=72)
end = event_date

event_period = df[
    (df["time"] >= start) &
    (df["time"] < end)
].copy()

print("=" * 70)
print("SHIMLA EVENT IN BASELINE DATASET")
print("=" * 70)

print("\nEvent date:", event_date.date())
print("72-hour period:", start, "->", end)

print("\nRows:", len(event_period))
print("Unique timestamps:", event_period["time"].nunique())

print(
    "Unique locations:",
    event_period[["latitude", "longitude"]]
    .drop_duplicates()
    .shape[0]
)

print("\nMissing values:")
print(event_period.isna().sum().sum())

print("\nRainfall features:")
for col in [
    "rain_3h",
    "rain_6h",
    "rain_12h",
    "rain_24h",
    "rain_72h"
]:
    print(
        f"{col}: "
        f"min={event_period[col].min():.3f}, "
        f"max={event_period[col].max():.3f}, "
        f"mean={event_period[col].mean():.3f}"
    )

print("\n" + "=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)