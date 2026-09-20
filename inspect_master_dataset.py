import pandas as pd

file_path = r"C:\Users\bhanu\OneDrive\Desktop\AI-Hybrid-Landslide Prediction\DATA\processed\shimla_master_dataset.csv"

df = pd.read_csv(file_path)

df["time"] = pd.to_datetime(df["time"])

print("=" * 70)
print("MASTER DATASET INSPECTION")
print("=" * 70)

print("\nShape:")
print(df.shape)

print("\n" + "=" * 70)
print("COLUMN NAMES")
print("=" * 70)

for i, col in enumerate(df.columns, start=1):
    print(f"{i:02d}. {col}")

print("\n" + "=" * 70)
print("DATA TYPES")
print("=" * 70)

print(df.dtypes)

print("\n" + "=" * 70)
print("FIRST 5 ROWS")
print("=" * 70)

print(df.head().to_string())

print("\n" + "=" * 70)
print("LAST 5 ROWS")
print("=" * 70)

print(df.tail().to_string())

print("\n" + "=" * 70)
print("MISSING VALUES")
print("=" * 70)

missing = df.isna().sum()

print(
    missing[missing > 0]
    .sort_values(ascending=False)
)

print("\n" + "=" * 70)
print("NUMERICAL SUMMARY")
print("=" * 70)

print(
    df.describe().T[
        ["count", "mean", "min", "max"]
    ].to_string()
)

print("\n" + "=" * 70)
print("MASTER DATASET INSPECTION COMPLETE")
print("=" * 70)