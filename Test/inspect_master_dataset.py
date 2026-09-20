import pandas as pd

path = r"DATA\processed\shimla_master_dataset.csv"

df = pd.read_csv(path)

print("=" * 70)
print("SHIMLA MASTER DATASET INSPECTION")
print("=" * 70)

print("\nRows:", len(df))
print("Columns:", len(df.columns))

print("\nColumns:")
for i, col in enumerate(df.columns, 1):
    print(f"{i:2d}. {col}")

print("\nTime:")
print("Start:", df["time"].min())
print("End  :", df["time"].max())

print("\nYears:")
print(
    pd.to_datetime(df["time"])
    .dt.year
    .value_counts()
    .sort_index()
)

print("\nLocations:")
print(
    df[["latitude", "longitude"]]
    .drop_duplicates()
    .sort_values(["latitude", "longitude"])
    .to_string(index=False)
)

print("\nRows by year:")
print(
    pd.to_datetime(df["time"])
    .dt.year
    .value_counts()
    .sort_index()
)

print("\nMissing values:")
missing = df.isna().sum()

print(
    missing[missing > 0]
    .sort_values(ascending=False)
    .to_string()
)

print("\nTotal missing values:", missing.sum())

print("\nDuplicate rows:", df.duplicated().sum())

print("\nDuplicate time + location:")
print(
    df.duplicated(
        subset=["time", "latitude", "longitude"]
    ).sum()
)

print("\n" + "=" * 70)
print("MASTER DATASET INSPECTION COMPLETE")
print("=" * 70)