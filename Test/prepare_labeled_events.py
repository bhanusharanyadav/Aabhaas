import os
import pandas as pd

BASE = r"DATA\Raw\Landslide event\processed"
HISTORICAL_BASE = r"DATA\processed"
OUT = os.path.join(BASE, "labeled")

os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------
# POSITIVE EVENT DATASETS
# ---------------------------------------------------------

positive_files = {
    "Shimla": "shimla_event_dataset.csv",
    "Kinnaur": "kinnaur_event_dataset.csv",
    "Chamoli": "chamoli_event_dataset.csv"
}

# ---------------------------------------------------------
# NEGATIVE CONTROL DATASETS
# ---------------------------------------------------------

HISTORICAL_BASE = r"DATA\processed"

negative_controls = {
    "Control_2017": {
        "file": os.path.join(HISTORICAL_BASE, "shimla_2017_rainfall.csv"),
        "start": "2017-08-10 00:00:00",
        "end": "2017-08-13 00:00:00"
    },
    "Control_2021": {
        "file": os.path.join(HISTORICAL_BASE, "shimla_2021_rainfall.csv"),
        "start": "2021-08-10 00:00:00",
        "end": "2021-08-13 00:00:00"
    },
    "Control_2022": {
        "file": os.path.join(HISTORICAL_BASE, "shimla_2022_rainfall.csv"),
        "start": "2022-08-08 00:00:00",
        "end": "2022-08-11 00:00:00"
    }
}

print("=" * 70)
print("PREPARING LABELED DATASETS")
print("=" * 70)

positive_frames = []

# ---------------------------------------------------------
# PROCESS POSITIVE EVENTS
# ---------------------------------------------------------

for event, filename in positive_files.items():

    path = os.path.join(BASE, filename)

    df = pd.read_csv(path)
    df["time"] = pd.to_datetime(df["time"])

    df["landslide"] = 1
    df["sample_type"] = "documented_event"

    positive_frames.append(df)

    print("\nPositive:", event)
    print("Rows:", len(df))
    print("Label:", df["landslide"].iloc[0])

# ---------------------------------------------------------
# PROCESS NEGATIVE CONTROLS
# ---------------------------------------------------------

negative_frames = []

for name, info in negative_controls.items():

    path = info["file"]


    df = pd.read_csv(path)
    df["time"] = pd.to_datetime(df["time"])

    start = pd.Timestamp(info["start"])
    end = pd.Timestamp(info["end"])

    df = df[
        (df["time"] >= start) &
        (df["time"] < end)
    ].copy()

    df["event"] = "none_documented"
    df["landslide"] = 0
    df["sample_type"] = "control"

    negative_frames.append(df)

    print("\nNegative:", name)
    print("Rows:", len(df))
    print("Label:", df["landslide"].iloc[0])

# ---------------------------------------------------------
# COMBINE
# ---------------------------------------------------------

positive = pd.concat(positive_frames, ignore_index=True)
negative = pd.concat(negative_frames, ignore_index=True)

combined = pd.concat(
    [positive, negative],
    ignore_index=True
)

# Sort
combined = combined.sort_values(
    ["time", "latitude", "longitude"]
).reset_index(drop=True)

# Save
output_path = os.path.join(
    OUT,
    "initial_landslide_labeled_dataset.csv"
)

combined.to_csv(output_path, index=False)

# ---------------------------------------------------------
# SUMMARY
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("FINAL SUMMARY")
print("=" * 70)

print("Total rows:", len(combined))
print("Total columns:", len(combined.columns))

print("\nClass distribution:")
print(combined["landslide"].value_counts())

print("\nSample type:")
print(combined["sample_type"].value_counts())

print("\nEvent field:")
print(combined["event"].value_counts())

print("\nRows by event:")
print(
    combined.groupby(
        ["event", "landslide"]
    ).size()
)

print("\nMissing values:", combined.isna().sum().sum())

print("\nOutput:")
print(output_path)

print("\n" + "=" * 70)
print("INITIAL LABELING COMPLETE")
print("=" * 70)