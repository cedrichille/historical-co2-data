import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import requests

# ---------------------------------------------SUMMARY TABLE------------------------------------------------------------
# create a table that summarizes average population and GDP, min and max population and GDP for each country
# and shows the max and min years of available data + min and max population and gdp years

# find average population and gdp per country
# ave_pop = pd.DataFrame(co2_data.groupby('country')['population'].mean()) \
#     .rename(columns={'population': 'average population'})
# ave_gdp = pd.DataFrame(co2_data.groupby('country')['gdp'].mean()) \
#     .rename(columns={'gdp': 'average gdp'})
# # find min and max year of available data per country
# min_year = pd.DataFrame(co2_data.groupby('country')['year'].min()) \
#     .rename(columns={'year': 'first year'})
# max_year = pd.DataFrame(co2_data.groupby('country')['year'].max()) \
#     .rename(columns={'year': 'last year'})


# - function to find year of earliest and latest available data for a certain column, and corresponding data points -
def summary_data(original_data, column_names):
    df_dict = {}
    for col in column_names:
        # remove nulls from column so only years with data are available
        drop_nan = original_data[~original_data[col].isnull()]
        # find indexes of earliest and latest data for each country
        earliest_year_idx = drop_nan.groupby('country')['year'].idxmin()
        latest_year_idx = drop_nan.groupby('country')['year'].idxmax()
        # extract rows from original dataframe using the earliest indexes and save as new df
        earl_data = pd.DataFrame(original_data.iloc[earliest_year_idx][['country', 'year', col]])
        earl_data.rename(columns={'year': 'earliest ' + col + ' year',
                                  col: 'earliest ' + col}, inplace=True)
        earl_data.set_index('country', inplace=True)
        # extract rows from original dataframe using the latest indexes and save as new df
        late_data = pd.DataFrame(original_data.iloc[latest_year_idx][['country', 'year', col]])
        late_data.rename(columns=
                         {'year': 'latest ' + col + ' year', col: 'latest ' + col}, inplace=True)
        late_data.set_index('country', inplace=True)
        # concat dataframes to create a summary
        df_dict['summary_' + col] = pd.concat([earl_data, late_data], join='outer', axis=1)
        cols_int = ['earliest ' + col + ' year', 'latest ' + col + ' year']
        df_dict['summary_' + col][cols_int] = df_dict['summary_' + col][cols_int].astype(pd.Int64Dtype())
        # add a growth % column
        df_dict['summary_' + col][col + ' % growth'] = ((df_dict['summary_' + col]['latest ' + col] -
                                                         df_dict['summary_' + col]['earliest ' + col]) /
                                                        df_dict['summary_' + col]['earliest ' + col])
    #                                                        .apply('{:,.2%}'.format)
    summary = pd.concat(df_dict, join='outer', axis=1)
    summary = summary.droplevel(level=0, axis=1)
    summary = summary.replace(np.inf, np.NaN)
    return summary


def growth_rates(original_data, column_names):
    col_growth_names = []
    for col in column_names:
        col_growth_names.append(str(col + ' % growth'))
    growth_columns = summary_data(original_data, column_names)[col_growth_names]
    return growth_columns


# reference dataframe
# print(summary_data(co2_data,['population', 'gdp', 'co2']).loc['Montenegro'])
# print(growth_rates(co2_data,['population','gdp','co2']))


# -------------------------------- CO2 and CO2 per Capita Growth ----------------------------------
# Find correlation between CO2 and population trends
def growth_factor(original_data, factor_columns):
    if len(factor_columns) != 2:
        raise ValueError('factor_columns must contain only two columns')
    col_growth_names = []
    for col in factor_columns:
        col_growth_names.append(str(col + ' % growth'))
    factor_df = growth_rates(original_data, factor_columns)
    factor_col_name = (str(factor_columns[1]) + ' / ' + str(factor_columns[0]) + ' growth factor')
    factor_df[factor_col_name] = \
        (factor_df[col_growth_names[1]] / factor_df[col_growth_names[0]])
    neg_growth = factor_df[col_growth_names[0]] > 0
    factor_df[factor_col_name].where(neg_growth, -factor_df[factor_col_name], inplace=True)
    return factor_df
