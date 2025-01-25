import geopandas as gpd
from pygris import blocks
from pygris.data import get_census


def load_census_block_data(state, county):
    # Census Blocks
    blocks_geo = blocks(state="TX", county="453")
    # getting population data
    population_data = get_census(
        dataset="dec/pl",
        variables="P1_001N",
        params={
            "for": "block:*",
            "in": "state:48 county:453",
        },
        year=2020,
        return_geoid=True,
        guess_dtypes=True,
    )
    population_data.rename(columns={"P1_001N": "POP20"}, inplace=True)
    blocks_geo = blocks_geo.merge(
        population_data, left_on="GEOID20", right_on="GEOID", how="left"
    )
    return blocks_geo


def dasymetric_reagg(source, source_key, blocks_geo, destination):
    # Make sure you are providing a projected coordinate system and that all three layers are on the same CRS.
    assert source.crs == destination.crs == blocks_geo.crs

    # Spatial join source data to census blocks
    joined = gpd.sjoin(blocks_geo, source, how="left", predicate="intersects")

    # Getting the total census block population for each source polygon
    block_pop_20 = joined.groupby(source_key)["POP20"].sum()
    source = source.merge(block_pop_20, on=source_key, how="left")
    source.rename(columns={"POP20": "block_pop_20"}, inplace=True)
    joined = joined.merge(
        source[[source_key, "block_pop_20"]], on=source_key, how="left"
    )

    # calculating the census block weight based on the percent of the total population that lives in each census block
    joined["POP20_block_weight"] = joined["POP20"] / joined["block_pop_20"]

    # Now, spatial join destination data
    joined = joined.drop(columns=["index_right"])
    joined = gpd.sjoin(destination, joined, how="left", predicate="intersects")

    return joined

