import pandas as pd

path = r"DATA\processed\shimla_master_dataset.csv"

df = pd.read_csv(path)
df["time"] = pd.to_datetime(df["time"])

print("=" * 70)
print("SHIMLA TEMPORAL WINDOW ANALYSIS")
print("=" * 70)

print("\nTotal rows:", len(df))

# Unique timestamps
times = (
    df["time"]
    .drop_duplicates()
    .sort_values()
    .reset_index(drop=True)
)

print("Unique timestamps:", len(times))

print("\nTime periods by year:")

for year, group in df.groupby(df["time"].dt.year):

    start = group["time"].min()
    end = group["time"].max()
    timestamps = group["time"].nunique()

    print(
        f"{year}: "
        f"{start} -> {end} | "
        f"{timestamps} hourly timestamps"
    )

# Check gaps between timestamps
time_diff = times.diff().dropna()

print("\nTime gap statistics:")
print(time_diff.value_counts().head(10))

# Number of complete 72-hour windows per year
print("\nComplete 72-hour windows per year:")

for year, group in df.groupby(df["time"].dt.year):

    timestamps = (
        group["time"]
        .drop_duplicates()
        .sort_values()
    )

    if len(timestamps) > 72:
        windows = len(timestamps) - 72
    else:
        windows = 0

    print(year, "->", windows)

print("\n" + "=" * 70)
print("WINDOW ANALYSIS COMPLETE")
print("=" * 70)