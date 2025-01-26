import requests
import pandas as pd
import zipfile
import io
import os
from google.cloud import storage

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "creds.json"
URL = "https://votetravis.gov/wp-content/uploads/G24-Voter-Rosters.zip"


def upload_dataframe_to_gcs(dataframe, bucket_name, file_name):
    # Create a storage client
    client = storage.Client()

    # Get the bucket
    bucket = client.get_bucket(bucket_name)

    # Convert DataFrame to CSV string
    csv_data = dataframe.to_csv(index=False)

    # Create a blob object and upload the CSV data
    blob = bucket.blob(file_name)
    blob.upload_from_string(csv_data, content_type="text/csv")

    print(f"File {file_name} uploaded in Google Cloud Storage.")


def get_voter_roster_data():
    res = requests.get(URL)
    res.raise_for_status()
    zip_file = zipfile.ZipFile(io.BytesIO(res.content))
    return zip_file


def comparison_to_2020(df):
    # produce day-to-day comparison to past election year
    daily = df.pivot_table(
        index="date", values="VUID", aggfunc="count"
    )
    idx = pd.date_range(start=daily.index.min(), end=daily.index.max())
    daily = daily.reindex(idx, fill_value=0)
    daily["VUID"] = daily["VUID"].cumsum()
    daily.reset_index(inplace=True)
    daily.rename(columns={"VUID": "count_votes_2024", "index": "date_2024"}, inplace=True)
    daily["date_2024"] = daily["date_2024"].dt.strftime("%m/%-d/%y")
    daily["turnout_2024"] = daily["count_votes_2024"] / 925171  # retrieved 10/21/24

    historical_data = pd.read_csv("travis_county_roster_scrape/travis_county_2020_election_timeline.csv")
    historical_data = historical_data.merge(daily, on="date_2024", how="left")
    return historical_data


def daily_vote_totals(df):
    output = df.pivot_table(
        index="date", columns="vote_type", values="VUID", aggfunc="count"
    )
    if "early" not in output.columns:
        output["early"] = 0
    else:
        output["early"] = output["early"].fillna(0)
        output["mail"] = output["mail"].fillna(0)

    output["early"] = output["early"].cumsum()
    output["mail"] = output["mail"].cumsum()
    output = output.reset_index()

    output["date"] = output["date"].dt.strftime("%Y-%m-%d")
    return output


def get_vote_by_pct_count(df):
    count_registered = pd.read_csv("travis_county_roster_scrape/registered_by_pct.csv")
    precincts = df.groupby(["Precinct"])["VUID"].count()
    precincts = precincts.reset_index()
    precincts = precincts.merge(count_registered, on="Precinct")
    precincts["pct_voted"] = precincts["VUID"] / precincts["count_voters"]
    precincts["pct_voted"] = precincts["pct_voted"] * 100
    return precincts


def main():
    zip_file = get_voter_roster_data()
    data = []
    for file in zip_file.namelist():
        with zip_file.open(file) as f:
            df = pd.read_excel(f, skiprows=[0, 1, 2])
        if "mail" in file.lower():
            df["vote_type"] = "mail"
        else:
            df["vote_type"] = "early"
            df.rename(columns={"PCT": "Precinct"}, inplace=True)
        date = pd.to_datetime(file.split(" ")[0])
        df["date"] = date
        data.append(df)

    df = pd.concat(data, ignore_index=True)

    historical = comparison_to_2020(df)
    upload_dataframe_to_gcs(historical, bucket_name="aus-dashboard", file_name="compare_2024_to_2020.csv")

    output = daily_vote_totals(df)
    upload_dataframe_to_gcs(
        output, bucket_name="aus-dashboard", file_name="vote_type_by_date.csv"
    )

    precincts = get_vote_by_pct_count(df)
    upload_dataframe_to_gcs(
        precincts, bucket_name="aus-dashboard", file_name="precinct_vote_count.csv"
    )


if __name__ == "__main__":
    main()
