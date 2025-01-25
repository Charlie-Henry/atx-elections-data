import geopandas as gpd

from dasymetric_reaggregation import load_census_block_data, dasymetric_reagg

# 2020 results loading
# 2020 Precinct data https://doi.org/10.7910/DVN/K7760H
src_data = gpd.read_file("../data/tx_2020.zip")
# Filtering to Travis County
src_data = src_data[src_data["CNTY"] == 453]

# 2024 results loading
# From NYT https://github.com/nytimes/presidential-precinct-map-2024
dest_data = gpd.read_file("../data/TX-precincts-with-results.geojson")
# Filtering to Travis County
dest_data = dest_data[dest_data["GEOID"].str.startswith("48453")]


# load census block data
blocks_geo = load_census_block_data(state="TX", county="453")

# Transforming to projected coordinates
# NAD83 / Texas Central (ftUS)
src_data = src_data.to_crs(epsg=2277)
dest_data = dest_data.to_crs(epsg=2277)
blocks_geo = blocks_geo.to_crs(epsg=2277)

joined_dest = dasymetric_reagg(
    source=src_data, source_key="PCTKEY", blocks_geo=blocks_geo, destination=dest_data
)

# Calculating 2020 vote totals from the block weights
joined_dest["weighted_biden_2020"] = (
    joined_dest["G20PREDBID"] * joined_dest["POP20_block_weight"]
)
joined_dest["weighted_trump_2020"] = (
    joined_dest["G20PRERTRU"] * joined_dest["POP20_block_weight"]
)
joined_dest["weighted_other_2020"] = (
    joined_dest["G20PRELJOR"] * joined_dest["POP20_block_weight"]
    + joined_dest["G20PREGHAW"] * joined_dest["POP20_block_weight"]
    + joined_dest["G20PREOWRI"] * joined_dest["POP20_block_weight"]
)
joined_dest["total_vote_2020"] = (
    joined_dest["weighted_biden_2020"]
    + joined_dest["weighted_trump_2020"]
    + joined_dest["weighted_other_2020"]
)
joined_dest["weighted_POP20"] = joined_dest["POP20"] * joined_dest["POP20_block_weight"]

# Calculating totals
biden_20 = joined_dest.groupby("GEOID_left")["weighted_biden_2020"].sum()
trump_20 = joined_dest.groupby("GEOID_left")["weighted_trump_2020"].sum()
tot_20 = joined_dest.groupby("GEOID_left")["total_vote_2020"].sum()
pop_20 = joined_dest.groupby("GEOID_left")["weighted_POP20"].sum()

# Merging estimated 2020 totals back to 2024 precincts
dest_data = dest_data.merge(
    biden_20, left_on="GEOID", right_on="GEOID_left", how="left"
)
dest_data = dest_data.merge(
    trump_20, left_on="GEOID", right_on="GEOID_left", how="left"
)
dest_data = dest_data.merge(tot_20, left_on="GEOID", right_on="GEOID_left", how="left")
dest_data = dest_data.merge(pop_20, left_on="GEOID", right_on="GEOID_left", how="left")

# metrics
dest_data["dem_pct_24"] = dest_data["votes_dem"] / dest_data["votes_total"]
dest_data["dem_pct_20"] = (
    dest_data["weighted_biden_2020"] / dest_data["total_vote_2020"]
)
dest_data["change_dem_pct"] = dest_data["dem_pct_24"] - dest_data["dem_pct_20"]
dest_data.to_file("travis_county_20_24.geojson")
