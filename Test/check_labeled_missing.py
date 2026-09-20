import pandas as pd

path = r"DATA\Raw\Landslide event\processed\labeled\initial_landslide_labeled_dataset.csv"

df = pd.read_csv(path)

print("=" * 70)
print("LABELED DATASET - MISSING VALUE CHECK")
print("=" * 70)

print("Rows:", len(df))
print("Columns:", len(df.columns))

print("\nMissing values by column:")

missing = df.isna().sum()

print(
    missing[missing > 0]
    .sort_values(ascending=False)
    .to_string()
)

print("\nTotal missing values:", missing.sum())

print("\nColumns with NO missing values:")

print(
    missing[missing == 0]
    .index
    .tolist()
)

print("\n" + "=" * 70)
print("MISSING VALUE CHECK COMPLETE")
print("=" * 70)