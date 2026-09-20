import os
import cfgrib

base_path = r"C:\Users\bhanu\OneDrive\Desktop\AI-Hybrid-Landslide Prediction\DATA\Raw\historical data"

years = [2016, 2017, 2018, 2019, 2020, 2021, 2023, 2024, 2025, 2026]

for year in years:
    folder = os.path.join(base_path, str(year))

    print("\n" + "=" * 70)
    print("YEAR:", year)
    print("=" * 70)

    if not os.path.exists(folder):
        print("Folder not found:", folder)
        continue

    grib_files = [
        f for f in os.listdir(folder)
        if f.lower().endswith((".grib", ".grb", ".grib2"))
    ]

    if not grib_files:
        print("No GRIB file found")
        continue

    print("GRIB file:", grib_files[0])

    file_path = os.path.join(folder, grib_files[0])

    try:
        ds_list = cfgrib.open_datasets(file_path)

        print("Number of datasets:", len(ds_list))

        for i, ds in enumerate(ds_list):
            print(
                f"  Dataset {i}: "
                f"dimensions={dict(ds.sizes)}, "
                f"variables={list(ds.data_vars)}"
            )

    except Exception as e:
        print("ERROR:", type(e).__name__, e)

print("\nInspection complete.")