import pandas as pd
import os

files = os.listdir("tx_2020_early_voting")

election_day = pd.to_datetime("2020-11-03")

data = []
for file in files:
    if file.endswith(".csv"):
        df = pd.read_csv(os.path.join("tx_2020_early_voting", file))
        df["date_2020"] = pd.to_datetime(file.split(".csv")[0])
        df["days_til_eday"] = (election_day - df["date_2020"]).dt.days
        df["date_2024"] = df["date_2020"] + pd.Timedelta(days=1463)
        df = df[df["County"] != "TOTAL"]
        data.append(df)

df = pd.concat(data)
df = df[
    [
        "County",
        "Registered Voters",
        "Cumulative In-Person Voters",
        "Cumulative % In-Person",
        "Cumulative By Mail Voters",
        "Cumulative In-Person And Mail Voters",
        "Cumulative Percent Early Voting",
        "date_2020",
        "date_2024",
        "days_til_eday",
    ]
]
df.to_csv("2020_election_timeline_texas.csv", index=False)

