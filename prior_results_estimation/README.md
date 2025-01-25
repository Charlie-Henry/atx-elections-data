# Mapping 2020 election precincts to 2024 precincts

With population-weighted dasymetric reaggregation

The overall procedure from [Denise Lu](https://medium.com/@DeniseDSLu/dasymetric-reaggregation-using-mapshaper-218e87babaa3).

![visual of each source layer](intermediate_steps.png)

## Overview

Following the 2020 decennial Census, new election precincts were drawn in most parts of the country. It becomes a challenging
problem to analyze past elections with precinct-level data due to this geometry mismatch.

The [New York Times 2024 election map](https://github.com/nytimes/presidential-precinct-map-2024) estimated 2020-to-2024 
election shifts at the precinct level using dasymetric reaggregation. 

This repo intends to implement this procedure in python, specifically with geopandas.

The procedure uses 2020 census block population data as an intermediary to map 2020 results to a 2024 precinct geometry.

This is done by:
1. Spatially joining the 2020 precincts to the census blocks, then calculating a weight for each block's share of the precicnt's total population.
2. Joining these block weights to the 2024 precincts.
3. Multiply the 2020 results by the population weights then aggregate by 2024 precinct's ID.

## Caveats

Census blocks are spatially joined by using an `intersection` method. So, a census block may appear in multiple precincts.
This can cause blocks which are shared by multiple precincts to have their votes essentially be duplicated. So, do not expect 
the total of the 2020 estimation to equal the total votes cast.

## Reusing this code

If you would like to BYOD (bring your own data) to this:
1. Load the two sets of precinct results you would like to use.
2. Then use `load_census_block_data()` to load the census blocks and population data
3. Make sure that all three geospatial layers have the same projected coordinate system. I used NAD83 here in Texas.
4. Run `dasymetric_reagg()`
5. Process the results by grouping by your destination precinct ID.
