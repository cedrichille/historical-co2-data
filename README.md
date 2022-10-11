# Historical CO2 Data Repository

Based on the owid/co2-data repository, this project provides tools for analyzing and visualizing the data on CO2 emissions by country and year, with the aim of identifying correlations between economic development, population, industry activity, and climate impact. 

## Main features
Import data from a local file in CSV format

Define function to summarize data at the country level, including timespan of available data and growth rates for selected columns from the data

Retrieve growth rates only for defined columns at the country level

Calculate growth factors to describe the relationship between data, e.g. how are GDP and CO2 emissions related?

Calculate growth factors for subsets of the data, e.g. how do relationships between data change for top and bottom quantiles?


## Features to be developed
API connection to data

JSON ingestion

CAGR 

Projections for data

GUI with column selection, visualization, exporting capabilities

Webpage/dashboard 


### Analyses to be conducted using the app
How are population and emissions related at different country sizes?

How are GDP and emissions related at different economic development levels? Is there a decoupling? 

Ranking cumulative emissions contributors

Ranking net importers and exporters of emissions

Trends in import and export of emissions, e.g. do countries switch as they develop?
