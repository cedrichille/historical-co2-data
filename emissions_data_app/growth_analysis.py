import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import requests


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

