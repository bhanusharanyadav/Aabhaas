import cfgrib

path = r"C:\Users\bhanu\OneDrive\Desktop\AI-Hybrid-Landslide Prediction\DATA\Raw\Landslide event\Shimla\c1cdc1cdec6e393a8e5f14b76a4598ee.grib"

print("Opening Shimla GRIB...")

datasets = cfgrib.open_datasets(
    path,
    backend_kwargs={"indexpath": ""}
)

print("SUCCESS")
print("Number of datasets:", len(datasets))

for i, ds in enumerate(datasets):
    print(
        f"Dataset {i}:",
        list(ds.data_vars),
        "dims=",
        dict(ds.sizes)
    )

print("TEST COMPLETE")