# atx-elections-data
 
A repo holding scripts for processing and visualization elections in Austin, Texas.

## prior_results_estimation

This directory stores scripts that estimate 2020 election results in the 2024-era election precincts.

![visual of each source layer](prior_results_estimation/intermediate_steps.png)

## visualization

### 20_to_24 shifts

Scripts for visualizing the shift in election results from 2020 to 2024.

![A map of 2020 to 2024 election shifts in Austin. Downtown and the east side generally shifted rightwards.](visualization/20_to_24_shifts/2020_vs_2024_tx.png)

### registration_vs_population_growth

A bivariate choropleth map comparing voter registration growth and population growth across Texas.

![Map of Texas Counties shaded by their population and registration growth.](visualization/registration_vs_population_growth/bivariate_choropleth.png)

### suspense_voters

Choropleth maps exploring the voter file in Travis County Texas. With a map looking at the percent of voters who were in
suspense status prior to the November 2024 election.

![Map of Travis County emphasizing west campus as a suspense voter hotspot](visualization/suspense_voters/suspended_voters_by_pct.png)

### 24_primary_results

Visualizations made during the night of the 2024 Texas Primaries. 

![A map of the combined 2024 primaries for Travis County.](visualization/24_primary_election_results/combined_results.png)

### 24_coa_council_elections

Precinct election maps for the 2024 Austin City Council elections

![A map showing Kirk Watson winning most precincts in the 2024 mayor's race.](visualization/24_coa_council_elections/mayor.png)

## etl

### travis_county_roster_scrape

This ETL was used during the 2024 early voting period to download data from the Travis County website and update a visualization
[on my blog](https://modalshift.co/early-voting/) of the turnout relative to 2020's turnout. 

![Relative turnout during early voting 2024 versus 2020](etl/travis_county_roster_scrape/2024-voter-turnout-timeline.png)
