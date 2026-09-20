import os
import cfgrib

base_path = r"C:\Users\bhanu\OneDrive\Desktop\AI-Hybrid-Landslide Prediction\DATA\Raw\historical data"

years = [2016, 2017, 2018, 2019, 2020, 2021, 2023, 2024, 2025, 2026]

for year in years:

    print("\n" + "=" * 70)
    print("YEAR:", year)
    print("=" * 70)

    folder = os.path.join(base_path, str(year))

    grib_files = [
        f for f in os.listdir(folder)
        if f.lower().endswith((".grib", ".grb", ".grib2"))
    ]

    if not grib_files:
        print("No GRIB file found")
        continue

    file_path = os.path.join(folder, grib_files[0])

    print("File:", grib_files[0])

    try:
        datasets = cfgrib.open_datasets(file_path)

        # Main weather dataset
        weather = datasets[5]

        print("\nVariables:")
        print(list(weather.data_vars))

        print("\nDimensions:")
        print(dict(weather.sizes))

        print("\nLatitude:")
        print(weather.latitude.values)

        print("\nLongitude:")
        print(weather.longitude.values)

        print("\nTime:")
        print("Start:", weather.time.values[0])
        print("End  :", weather.time.values[-1])

        # Soil moisture
        print("\nSoil moisture layers:")

        for i in range(4):
            ds = datasets[i]

            var = list(ds.data_vars)[0]

            if "depthBelowLandLayer" in ds.coords:
                depth = ds.depthBelowLandLayer.values
            else:
                depth = "Not available"

            print(
                var,
                "| depth =",
                depth,
                "| units =",
                ds[var].attrs.get("units")
            )

        # Important weather variables
        print("\nImportant variable units:")

        for var in ["t2m", "d2m", "u10", "v10", "sp", "tcrw"]:
            if var in weather:
                print(
                    var,
                    "| units =",
                    weather[var].attrs.get("units")
                )

        # Precipitation dataset
        precip = datasets[6]

        print("\nPrecipitation dataset:")
        print("Dimensions:", dict(precip.sizes))

        print("TP units:", precip["tp"].attrs.get("units"))

        print(
            "Valid time start:",
            precip.valid_time.values.flatten()[0]
        )

        print(
            "Valid time end:",
            precip.valid_time.values.flatten()[-1]
        )

    except Exception as e:
        print("\nERROR:", type(e).__name__, e)

print("\n" + "=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)