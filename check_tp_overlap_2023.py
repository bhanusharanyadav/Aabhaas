import pandas as pd
import cfgrib


grib_file = r"C:\Users\bhanu\OneDrive\Desktop\AI-Hybrid-Landslide Prediction\DATA\Raw\historical data\2023\c1cdc1cdec6e393a8e5f14b76a4598ee (1).grib"


datasets = cfgrib.open_datasets(grib_file)

tp_ds = None

for ds in datasets:
    if "tp" in ds.data_vars:
        tp_ds = ds
        break


tp = tp_ds["tp"]

# ------------------------------------------------------------
# Convert the 2D valid_time into a flat table
# ------------------------------------------------------------

valid_times = tp_ds["valid_time"].values.flatten()

print("=" * 70)
print("TP OVERLAP CHECK - 2023")
print("=" * 70)

print("\nTotal valid_time entries:", len(valid_times))

# Count how many times each valid_time occurs
time_counts = pd.Series(valid_times).value_counts().sort_index()

print("\nUnique valid times:", len(time_counts))

print("\nTimes occurring more than once:")

duplicates = time_counts[time_counts > 1]

print(duplicates)

print("\nNumber of duplicated timestamps:", len(duplicates))

print("\nMaximum number of forecasts for one timestamp:")

if len(duplicates) > 0:
    print(duplicates.max())
else:
    print(1)


# ------------------------------------------------------------
# Show one example
# ------------------------------------------------------------

if len(duplicates) > 0:

    example_time = duplicates.index[0]

    print("\n" + "=" * 70)
    print("EXAMPLE DUPLICATE TIME")
    print("=" * 70)

    print("\nTimestamp:", example_time)

    locations = []

    for i in range(tp_ds.sizes["time"]):

        for j in range(tp_ds.sizes["step"]):

            current_time = tp_ds["valid_time"].values[i, j]

            if current_time == example_time:

                locations.append(
                    (
                        i,
                        j,
                        tp_ds["time"].values[i],
                        tp_ds["step"].values[j]
                    )
                )

    for item in locations:
        print(
            "Reference index:",
            item[0],
            "| Step index:",
            item[1],
            "| Reference time:",
            item[2],
            "| Step:",
            item[3]
        )


print("\n" + "=" * 70)
print("CHECK COMPLETE")
print("=" * 70)