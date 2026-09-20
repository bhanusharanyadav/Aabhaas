import os
import cfgrib

base_path = r"DATA\Raw\Landslide event"

events = [
    ("Shimla", r"Shimla"),
    ("Chamoli", r"chamoli uttrakhand"),
    ("Kinnaur", r"kinnaur himachal"),
    ("Uttarkashi", r"uttarkashi , uttrakhand"),
]

print("=" * 70)
print("LANDSLIDE EVENT SUMMARY")
print("=" * 70)

for event_name, folder in events:

    folder_path = os.path.join(base_path, folder)

    files = [
        f for f in os.listdir(folder_path)
        if f.lower().endswith(".grib")
    ]

    for filename in files:

        file_path = os.path.join(folder_path, filename)
        datasets = cfgrib.open_datasets(file_path)

        print(f"\nEVENT: {event_name}")
        print(f"FILE: {filename}")
        print(f"DATASETS: {len(datasets)}")

        for i, ds in enumerate(datasets):

            time_start = ds.time.values[0] if "time" in ds.coords else "N/A"
            time_end = ds.time.values[-1] if "time" in ds.coords else "N/A"

            lat = ds.latitude.values.tolist() if "latitude" in ds.coords else []
            lon = ds.longitude.values.tolist() if "longitude" in ds.coords else []

            print(
                f"Dataset {i}: "
                f"time={time_start} -> {time_end} | "
                f"lat={lat} | lon={lon}"
            )

print("\n" + "=" * 70)
print("COMPLETE")
print("=" * 70)