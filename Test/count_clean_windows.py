import pandas as pd

path = r"DATA\processed\shimla_baseline_dataset.csv"

df = pd.read_csv(path)
df["time"] = pd.to_datetime(df["time"])

print("=" * 70)
print("CLEAN 72-HOUR WINDOW COUNT")
print("=" * 70)

for year, group in df.groupby(df["time"].dt.year):

    times = (
        group["time"]
        .drop_duplicates()
        .sort_values()
        .reset_index(drop=True)
    )

    print(
        f"\n{year}: "
        f"{len(times)} usable timestamps"
    )

    # A complete 72-hour window requires 72 consecutive timestamps
    windows = 0

    for i in range(len(times) - 71):

        window = times.iloc[i:i + 72]

        if (
            window.iloc[-1] - window.iloc[0]
            == pd.Timedelta(hours=71)
        ):
            windows += 1

    print("Complete 72-hour windows:", windows)

print("\n" + "=" * 70)
print("WINDOW COUNT COMPLETE")
print("=" * 70)