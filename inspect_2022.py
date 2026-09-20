import cfgrib

file_path = r"C:\Users\bhanu\OneDrive\Desktop\AI-Hybrid-Landslide Prediction\DATA\Raw\historical data\2022\3aaab7469f0ab887e3536bb97fa524eb.grib"

print("=" * 70)
print("2022 GRIB INSPECTION")
print("=" * 70)

datasets = cfgrib.open_datasets(file_path)

print("\nNumber of datasets:", len(datasets))

for i, ds in enumerate(datasets):

    print("\n" + "-" * 70)
    print(f"DATASET {i}")
    print("-" * 70)

    print("Variables:")
    print(list(ds.data_vars))

    print("Dimensions:")
    print(dict(ds.sizes))

    print("Coordinates:")

    for coord in ds.coords:
        values = ds[coord].values

        if hasattr(values, "shape"):
            print(
                f"  {coord}: shape={values.shape}"
            )
        else:
            print(
                f"  {coord}: {values}"
            )

print("\n" + "=" * 70)
print("2022 INSPECTION COMPLETE")
print("=" * 70)