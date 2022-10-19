# Development to-do

## download_data.py
- MT: JSON ingestion to learn how to transform JSON to dataframe

## summary_growth.py
- ST: add a feature to earliest data and latest data functions that checks if data is zero and finds first non-zero data point
- MT: add error handling for function inputs, such as if summary_dataframe is not type pd.df in add_growth_column or two many columns provided
- ST: functions like show_growth_rates should be able to handle no columns being provided, in which case they show all column growth rates

## growth_analysis.py
- ST: fix quantile selection
- MT: is it correct to dropna() in quantile group calculations?
- ST: support for pct change and CAGR calculations between given years
- MT: improve graphics output through better legends and adding lines of best fit
- MT: grouped mean multiplier output verification 


## other
- MT: Projections for data
- LT: GUI with column search and selection, visualization, exporting capabilities
- LT: Host dashboard on webpage 