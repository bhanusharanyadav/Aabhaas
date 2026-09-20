import os
import hashlib
import cfgrib

BASE = r"C:\Users\bhanu\OneDrive\Desktop\AI-Hybrid-Landslide Prediction\DATA\Raw\Landslide event"

events = {
    "Shimla": os.path.join(
        BASE, "Shimla",
        "c1cdc1cdec6e393a8e5f14b76a4598ee.grib"
    ),
    "Chamoli": os.path.join(
        BASE, "chamoli uttrakhand",
        "292f75f24341a9832c6c4bb7113a8499.grib"
    ),
    "Kinnaur": os.path.join(
        BASE, "kinnaur himachal",
        "4cf1e423cff3176d2b3a862fb20dba3c.grib"
    ),
    "Uttarkashi": os.path.join(
        BASE, "uttarkashi , uttrakhand",
        "292f75f24341a9832c6c4bb7113a8499.grib"
    ),
}


def sha256_file(path):
    h = hashlib.sha256()

    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)

    return h.hexdigest()


print("=" * 70)
print("LANDSLIDE EVENT METADATA CHECK")
print("=" * 70)

for event, path in events.items():

    print("\n" + "-" * 70)
    print(f"EVENT: {event}")
    print(f"FILE: {path}")

    if not os.path.exists(path):
        print("STATUS: FILE NOT FOUND")
        continue

    print(f"SIZE: {os.path.getsize(path):,} bytes")
    print(f"SHA256: {sha256_file(path)}")

    try:
        datasets = cfgrib.open_datasets(
    path,
    backend_kwargs={"indexpath": ""}
)

        print(f"DATASETS: {len(datasets)}")

        # Main weather dataset
        ds = datasets[5]

        print("\nMAIN WEATHER DATASET")
        print("Variables:")
        print(list(ds.data_vars))

        print("\nCoordinates:")
        print("Time:",
              ds.time.values[0],
              "->",
              ds.time.values[-1])

        print("Latitude:", ds.latitude.values)
        print("Longitude:", ds.longitude.values)

        print("\nDataset attributes:")
        for key, value in ds.attrs.items():
            if key in [
                "GRIB_centre",
                "GRIB_centreDescription",
                "GRIB_subCentre",
                "GRIB_dataType",
                "GRIB_typeOfLevel",
                "GRIB_stepType",
                "GRIB_gridType",
                "GRIB_edition",
            ]:
                print(f"{key}: {value}")

        # Temperature metadata
        if "t2m" in ds:
            print("\nt2m metadata:")
            for key, value in ds["t2m"].attrs.items():
                if key.startswith("GRIB_") or key in [
                    "long_name",
                    "units",
                ]:
                    print(f"{key}: {value}")

        # Soil moisture metadata
        if "swvl1" in datasets[0]:
            print("\nswvl1 metadata:")
            for key, value in datasets[0]["swvl1"].attrs.items():
                if key.startswith("GRIB_") or key in [
                    "long_name",
                    "units",
                ]:
                    print(f"{key}: {value}")

        # Precipitation metadata
        tp_ds = datasets[6]

        print("\nPRECIPITATION DATASET")
        print("Variables:", list(tp_ds.data_vars))
        print("Reference time:",
              tp_ds.time.values[0],
              "->",
              tp_ds.time.values[-1])

        if "tp" in tp_ds:
            print("\ntp metadata:")
            for key, value in tp_ds["tp"].attrs.items():
                if key.startswith("GRIB_") or key in [
                    "long_name",
                    "units",
                ]:
                    print(f"{key}: {value}")

    except Exception as e:
        print("ERROR:", type(e).__name__, str(e))

print("\n" + "=" * 70)
print("METADATA CHECK COMPLETE")
print("=" * 70)