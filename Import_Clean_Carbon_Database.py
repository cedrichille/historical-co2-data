import pandas as pd
import numpy as np
import datetime
import time
import easygui
from matplotlib import pyplot as plt

pd.options.display.width = 0
pd.options.display.max_rows = 90
pd.set_option('display.float_format', lambda x: '%0.2f' % x)
# save the data to a DataFrame - for now read from excel, later learn how to read from JSON
co2_data = pd.DataFrame(pd.read_excel(
    r'C:\Users\chille\OneDrive - Digimarc Corporation\00 - Admin\Other\Python\Carbon projects\owid-co2-data.xlsx'))


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

# ------------- GUI to find summary table for desired info for desired country -------------------------


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


def growth_quantile(original_data, factor_columns, start_quantile, end_quantile):
    col_growth_names = []
    for col in factor_columns:
        col_growth_names.append(str(col + ' % growth'))
    factor_df = growth_factor(original_data, factor_columns)
    quantile_df = factor_df.loc[(np.quantile(factor_df[col_growth_names[0]].dropna(), q=start_quantile) <=
                                 factor_df[col_growth_names[0]]) &
                                (factor_df[col_growth_names[0]] <=
                                 np.quantile(factor_df[col_growth_names[0]].dropna(), q=end_quantile))]
    return quantile_df


def growth_quantile_mean_factor(original_data, factor_columns, start_quantile, end_quantile):
    quantile_df = growth_quantile(original_data, factor_columns, start_quantile, end_quantile)
    quantile_mean_factor = np.mean(quantile_df.iloc[:, 2])
    # print('For countries between the ' + str(start_quantile * 100) + ' and ' + str(end_quantile * 100) +
    #      ' quantiles in ' + str(factor_columns[0]) + ' growth rates, the ' + str(factor_columns[0]) + ' and '
    #      + str(factor_columns[1]) + ' growth rates are related by a factor of ' + str(round(quantile_mean_factor, 2)))
    return quantile_mean_factor


def quintile_growth_factors(original_data, factor_columns):
    quint_quant = {1: (0, 0.2), 2: (.21, .4), 3: (.41, .6), 4: (.61, .8), 5: (.81, 1)}
    quintile_results = {}
    for element in quint_quant:
        mean_factor = growth_quantile_mean_factor(original_data, factor_columns,
                                                  quint_quant[element][0], quint_quant[element][1])
        quintile_results[element] = mean_factor.round(2)
    result_text = ('The average growth rates of ' + str(factor_columns[0]) + ' and ' + str(factor_columns[1]) +
                   ' in each quintile of ' + str(factor_columns[0]) +
                   ' growth rates are related by the following factors:')

    plt.bar(*zip(*quintile_results.items()))
    plt.title(result_text)
    plt.xlabel(str(factor_columns[0]) + ' Growth Rate Quintile')
    plt.ylabel('Average Multiplication Factor of ' + str(factor_columns[1]) + ' Growth Rate')
    plt.show()

    return result_text, quintile_results


def quartile_growth_factors(original_data, factor_columns):
    quart_quant = {1: (0, 0.25), 2: (.26, .5), 3: (.51, .75), 4: (.76, 1)}
    quartile_results = {}
    for element in quart_quant:
        mean_factor = growth_quantile_mean_factor(original_data, factor_columns,
                                                  quart_quant[element][0], quart_quant[element][1])
        quartile_results[element] = mean_factor.round(2)
    result_text = ('The average growth rates of ' + str(factor_columns[0]) + ' and ' + str(factor_columns[1]) +
                   ' in each quintile of ' + str(factor_columns[0]) +
                   ' growth rates are related by the following factors:')

    plt.bar(*zip(*quartile_results.items()))
    plt.title(result_text)
    plt.xlabel(str(factor_columns[0]) + ' Growth Rate Quartile')
    plt.ylabel('Average Multiplication Factor of ' + str(factor_columns[1]) + ' Growth Rate')
    plt.show()

    return result_text, quartile_results


def quantile_growth_factors(original_data, factor_columns, no_quantiles):
    quantiles = pd.qcut(range(2), no_quantiles)
    quartile_results = {}
    for element in quantiles:
        mean_factor = growth_quantile_mean_factor(original_data, factor_columns,
                                                  quantiles[element][0], quantiles[element][1])
        quartile_results[element] = mean_factor.round(2)
    result_text = ('The average growth rates of ' + str(factor_columns[0]) + ' and ' + str(factor_columns[1]) +
                   ' in each quintile of ' + str(factor_columns[0]) +
                   ' growth rates are related by the following factors:')

    plt.bar(*zip(*quartile_results.items()))
    plt.title(result_text)
    plt.xlabel(str(factor_columns[0]) + ' Growth Rate Quartile')
    plt.ylabel('Average Multiplication Factor of ' + str(factor_columns[1]) + ' Growth Rate')
    plt.show()


# print(quintile_growth_factors(co2_data, ['population', 'co2']))
# print(quintile_growth_factors(co2_data, ['gdp', 'co2']))
# print(quartile_growth_factors(co2_data, ['population', 'gdp']))
# print(quintile_growth_factors(co2_data, ['population','co2_per_capita']))
print(quantile_growth_factors(co2_data,['population', 'co2'],4))


# def plot_quantile_growth_factors(original_data, factor_columns):



# ---------------------------------- CO2 per GDP trends - trends in most efficient producers --------------------------
# Find correlation between CO2 and GDP trends

# Find correlation between CO2 per GDP and GDP trends
# (Is there a point at which GDP decouples? Is it most CO2 intensive to earn first $1bn in GDP, or the last?)

# --------------------------------- Biggest cumulative CO2 contributors --------------------------------------------


# ----------------------------------- Biggest Net Importers and Exporters of Emissions ------------------------


# -------------------------------------- Trends in Import and Export of Emissions ---------------------------------
# --------------------------------------- including projected changes in balance of emission trade ----------------
