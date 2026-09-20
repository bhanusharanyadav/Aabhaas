import pandas as pd

path = r"DATA\processed\shimla_72h_feature_table.csv"

df = pd.read_csv(path)

print("=" * 70)
print("SHIMLA 72-HOUR FEATURE TABLE VALIDATION")
print("=" * 70)

print("\nShape:")
print("Rows   :", len(df))
print("Columns:", len(df.columns))

print("\nDuplicate rows:")
print(df.duplicated().sum())

print("\nDuplicate year + location:")
print(
    df.duplicated(
        subset=["year", "latitude", "longitude"]
    ).sum()
)

print("\nRows by year:")
print(df.groupby("year").size())

print("\nRows by location:")
print(
    df.groupby(
        ["latitude", "longitude"]
    ).size()
)

print("\nMissing values:")
missing = df.isna().sum()
print(missing[missing > 0])

print("\nFeature summary:")
feature_columns = [
    "rain_total_72h",
    "rain_max_1h",
    "rain_max_3h",
    "rain_max_6h",
    "rain_max_12h",
    "rain_max_24h",
    "temperature_mean",
    "temperature_min",
    "temperature_max",
    "dewpoint_mean",
    "wind_mean",
    "wind_max",
    "pressure_mean",
    "pressure_min",
    "swvl1_mean",
    "swvl1_max",
    "swvl2_mean",
    "swvl2_max",
    "swvl3_mean",
    "swvl3_max",
    "swvl4_mean",
    "swvl4_max",
    "lai_lv_mean",
    "lai_hv_mean",
    "cvl_mean",
    "cvh_mean"
]

print(
    df[feature_columns]
    .describe()
    .T
    .round(3)
    .to_string()
)

print("\n2023 event rows:")
print(
    df[df["year"] == 2023]
    .to_string(index=False)
)

print("\n" + "=" * 70)
print("FEATURE TABLE VALIDATION COMPLETE")
print("=" * 70)