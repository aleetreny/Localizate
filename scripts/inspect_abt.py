import pandas as pd

path = "data/features/local_survival_abt.csv"
print("reading", path)
df = pd.read_csv(path, usecols=["id_local", "first_seen_period", "event_observed"])
print("rows", len(df))
print("unique locales", df["id_local"].nunique())
print("events", int(df["event_observed"].sum()))
print("event_rate", float(df["event_observed"].mean()))

by_period = df.groupby("first_seen_period", sort=True)["event_observed"].agg(rows="size", events="sum").reset_index()
print("\nLast 10 periods (rows, events):")
print(by_period.tail(10).to_string(index=False))
print("\nLast 10 periods with >0 events:")
print(by_period[by_period["events"] > 0].tail(10).to_string(index=False))
