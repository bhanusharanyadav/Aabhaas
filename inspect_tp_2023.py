import os
import numpy as np
import pandas as pd
import cfgrib


# ============================================================
# PATH
# ============================================================

grib_file = r"C:\Users\bhanu\OneDrive\Desktop\AI-Hybrid-Landslide Prediction\DATA\Raw\historical data\2023\c1cdc1cdec6e393a8e5f14b76a4598ee (1).grib"


# ============================================================
# OPEN GRIB
# ============================================================

datasets = cfgrib.open_datasets(grib_file)

print("=" * 70)
print("TP PRECIPITATION INSPECTION - 2023")
print("=" * 70)

print("\nNumber of datasets:", len(datasets))


# ============================================================
# FIND TP DATASET
# ============================================================

tp_ds = None

for i, ds in enumerate(datasets):

    if "tp" in ds.data_vars:

        tp_ds = ds

        print("\nTP found in Dataset:", i)

        print("Dimensions:")
        print(dict(ds.sizes))

        print("\nVariables:")
        print(list(ds.data_vars))

        break


if tp_ds is None:

    print("\n❌ TP variable not found.")
    exit()


# ============================================================
# TP INFORMATION
# ============================================================

tp = tp_ds["tp"]

print("\n" + "=" * 70)
print("TP INFORMATION")
print("=" * 70)

print("\nUnits:", tp.attrs.get("units"))

print("Long name:", tp.attrs.get("long_name"))

print("Data type:", tp.attrs.get("GRIB_dataType"))

print("Step type:", tp.attrs.get("GRIB_stepType"))

print("\nShape:", tp.shape)


# ============================================================
# TIME
# ============================================================

print("\n" + "=" * 70)
print("REFERENCE TIMES")
print("=" * 70)

print(tp_ds["time"].values)


# ============================================================
# STEP
# ============================================================

print("\n" + "=" * 70)
print("FORECAST STEPS")
print("=" * 70)

print(tp_ds["step"].values)


# ============================================================
# VALID TIME
# ============================================================

print("\n" + "=" * 70)
print("VALID TIME")
print("=" * 70)

valid_time = tp_ds["valid_time"]

print("Shape:", valid_time.shape)

print("\nFirst 20 valid times:")

print(valid_time.values.flatten()[:20])

print("\nLast 20 valid times:")

print(valid_time.values.flatten()[-20:])


# ============================================================
# TP VALUES
# ============================================================

print("\n" + "=" * 70)
print("TP VALUES")
print("=" * 70)

values = tp.values

print("\nMinimum:", np.nanmin(values))

print("Maximum:", np.nanmax(values))

print("Mean:", np.nanmean(values))

print("NaN count:", np.isnan(values).sum())


# ============================================================
# FIRST GRID CELL
# ============================================================

print("\n" + "=" * 70)
print("FIRST GRID CELL")
print("=" * 70)

first_cell = values[:, :, 0, 0]

print("\nShape:", first_cell.shape)

print("\nValues:")

print(first_cell)


# ============================================================
# CONVERT TO MILLIMETERS
# ============================================================

tp_mm = tp * 1000

print("\n" + "=" * 70)
print("PRECIPITATION IN MILLIMETERS")
print("=" * 70)

print("Minimum:", float(tp_mm.min()))

print("Maximum:", float(tp_mm.max()))

print("Mean:", float(tp_mm.mean()))


print("\n" + "=" * 70)
print("INSPECTION COMPLETE")
print("=" * 70)