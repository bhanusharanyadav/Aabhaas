import numpy as np
import pandas as pd
import cfgrib


grib_file = r"C:\Users\bhanu\OneDrive\Desktop\AI-Hybrid-Landslide Prediction\DATA\Raw\historical data\2023\c1cdc1cdec6e393a8e5f14b76a4598ee (1).grib"


# ============================================================
# OPEN TP DATA
# ============================================================

datasets = cfgrib.open_datasets(grib_file)

tp_ds = None

for ds in datasets:
    if "tp" in ds.data_vars:
        tp_ds = ds
        break

tp = tp_ds["tp"]


# ============================================================
# CREATE INSPECTION TABLE
# ============================================================

records = []

for i in range(tp_ds.sizes["time"]):

    for j in range(tp_ds.sizes["step"]):

        reference_time = tp_ds["time"].values[i]
        step = tp_ds["step"].values[j]
        valid_time = tp_ds["valid_time"].values[i, j]

        # First grid cell
        value_m = tp.values[i, j, 0, 0]

        if np.isnan(value_m):
            value_mm = np.nan
        else:
            value_mm = value_m * 1000

        records.append({
            "reference_time": reference_time,
            "step": step,
            "valid_time": valid_time,
            "tp_mm": value_mm
        })


df = pd.DataFrame(records)


# ============================================================
# STEP IN HOURS
# ============================================================

df["step_hours"] = (
    pd.to_timedelta(df["step"]).dt.total_seconds() / 3600
)


# ============================================================
# SORT
# ============================================================

df = df.sort_values("valid_time").reset_index(drop=True)


# ============================================================
# DISPLAY
# ============================================================

print("=" * 70)
print("TP STEP ANALYSIS - 2023")
print("=" * 70)

print("\nTotal records:", len(df))

print("\nUnique step values (hours):")
print(df["step_hours"].unique())


print("\nFirst 30 records:")
print(
    df[
        [
            "reference_time",
            "step_hours",
            "valid_time",
            "tp_mm"
        ]
    ].head(30).to_string(index=False)
)


# ============================================================
# CHECK TIME DIFFERENCE
# ============================================================

df["time_difference_hours"] = (
    df["valid_time"]
    .diff()
    .dt.total_seconds() / 3600
)


print("\n" + "=" * 70)
print("VALID TIME DIFFERENCE")
print("=" * 70)

print(
    df["time_difference_hours"]
    .value_counts(dropna=True)
    .sort_index()
)


# ============================================================
# CHECK VALUES BY STEP
# ============================================================

print("\n" + "=" * 70)
print("PRECIPITATION STATISTICS BY STEP")
print("=" * 70)

print(
    df.groupby("step_hours")["tp_mm"]
    .agg(["count", "min", "max", "mean"])
    .to_string()
)


# ============================================================
# CHECK 1-HOUR STEPS
# ============================================================

print("\n" + "=" * 70)
print("STEP = 1 HOUR CHECK")
print("=" * 70)

one_hour = df[df["step_hours"] == 1]

print("\nNumber of 1-hour records:", len(one_hour))

print("\nFirst 20:")
print(
    one_hour[
        [
            "reference_time",
            "valid_time",
            "tp_mm"
        ]
    ].head(20).to_string(index=False)
)


print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)