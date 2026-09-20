import os
import cfgrib

BASE = r"C:\Users\bhanu\OneDrive\Desktop\AI-Hybrid-Landslide Prediction\DATA\Raw\Landslide event"

events = {
    "Shimla": os.path.join(
        BASE, "Shimla",
        "c1cdc1cdec6e393a8e5f14b76a4598ee.grib"
    ),
    "Kinnaur": os.path.join(
        BASE, "kinnaur himachal",
        "4cf1e423cff3176d2b3a862fb20dba3c.grib"
    ),
    "Chamoli": os.path.join(
        BASE, "chamoli uttrakhand",
        "292f75f24341a9832c6c4bb7113a8499.grib"
    ),
}

for event, path in events.items():

    print("\n" + "=" * 70)
    print("EVENT:", event)
    print("=" * 70)

    datasets = cfgrib.open_datasets(
        path,
        backend_kwargs={"indexpath": ""}
    )

    weather = datasets[5]

    print("Time:", weather.time.values[0], "->", weather.time.values[-1])
    print("Latitude:", weather.latitude.values)
    print("Longitude:", weather.longitude.values)

    print("\nVARIABLE RANGES:")

    variables = [
        "t2m",
        "d2m",
        "u10",
        "v10",
        "sp",
        "tcrw",
        "cvl",
        "cvh",
        "lai_lv",
        "lai_hv",
    ]

    for var in variables:
        if var in weather:
            values = weather[var].values

            print(
                f"{var:10s} "
                f"min={values.min():.6f} "
                f"max={values.max():.6f} "
                f"mean={values.mean():.6f}"
            )

    print("\nSOIL MOISTURE:")

    for i in range(4):
        var = f"swvl{i + 1}"

        if var in datasets[i]:
            values = datasets[i][var].values

            print(
                f"{var:10s} "
                f"min={values.min():.6f} "
                f"max={values.max():.6f} "
                f"mean={values.mean():.6f}"
            )

    rainfall = datasets[6]["tp"].values

    print("\nPRECIPITATION:")
    print("Units:", datasets[6]["tp"].attrs.get("units"))
    print("Minimum:", rainfall.min())
    print("Maximum:", rainfall.max())
    print("Mean:", rainfall.mean())

print("\n" + "=" * 70)
print("EVENT VALUE INSPECTION COMPLETE")
print("=" * 70)