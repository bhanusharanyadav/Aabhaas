import pandas as pd
from pathlib import Path

file_path = Path(
    r"C:\Users\bhanu\OneDrive\Desktop\AI-Hybrid-Landslide Prediction"
    r"\DATA\processed\shimla_2022_processed.csv"
)

if not file_path.exists():
    print("❌ 2022 processed file NOT found")
else:
    df = pd.read_csv(file_path)

    print("✅ 2022 processed file found")
    print("Rows:", len(df))
    print("Columns:", len(df.columns))
    print("Missing values:", df.isna().sum().sum())
    print("Time:", df["time"].min(), "to", df["time"].max())
    print("Unique locations:", df[["latitude", "longitude"]].drop_duplicates().shape[0])