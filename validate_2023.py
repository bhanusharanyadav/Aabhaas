import pandas as pd

file_path = r"C:\Users\bhanu\OneDrive\Desktop\AI-Hybrid-Landslide Prediction\DATA\processed\shimla_2023_processed.csv"

df = pd.read_csv(file_path)

print("=" * 60)
print("2023 DATA VALIDATION")
print("=" * 60)

print("\nShape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nMissing values:")
print(df.isnull().sum())

print("\nDuplicate rows:")
print(df.duplicated().sum())

print("\nDuplicate time + location:")
print(
    df.duplicated(
        subset=["time", "latitude", "longitude"]
    ).sum()
)

print("\nUnique timestamps:")
print(df["time"].nunique())

print("\nUnique latitude:")
print(df["latitude"].unique())

print("\nUnique longitude:")
print(df["longitude"].unique())

print("\nTemperature range:")
print(df["temperature_c"].min(), "to", df["temperature_c"].max())

print("\nWind speed range:")
print(df["wind_speed"].min(), "to", df["wind_speed"].max())

print("\nSoil moisture ranges:")

for col in ["swvl1", "swvl2", "swvl3", "swvl4"]:
    print(
        col,
        ":",
        df[col].min(),
        "to",
        df[col].max()
    )

print("\nTime range:")
print(df["time"].min(), "to", df["time"].max())

print("\nValidation complete.")