import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import requests
from download_data import co2_data
import summary_growth as sg
import utils as u


def find_multiplier(original_data, mult_columns):
    """
    Takes the co2 data and two selected columns, returns the multiplier between the columns' growth rates

    :param original_data: pass the original, unaltered owid co2 data dataframe that was downloaded from the owid GitHub
    :param mult_columns: the names of the columns for which you want to calculate the growth rate multiplier
    :return: dataframe with growth rates for the selected columns for each country, in addition to a multiplier
    that shows the relationship between the growth rates
    """

    # error handling to raise error when more or less than two column names are passed
    if len(mult_columns) != 2:
        raise ValueError('factor_columns must contain two columns')

    # create an empty list to store the names of the columns containing the growth rates
    col_growth_names = []

    # iterate through the two passed columns and add a suffix to the name to match the output of sg.show_growth_rates
    for col in mult_columns:
        # add the amended column names to the list col_growth_names
        col_growth_names.append(str(col + ' % growth'))

    # run the sg.show_growth_rates function to find the growth rate data and copy to a df
    multiplier_df = sg.extract_growth_rates_from_summary_df(original_data, mult_columns)

    # create a column in the df that lets us calculate the multiplier between the 1st and 2nd column's growth rates
    # i.e. multiplier = 2nd column's growth rate divided by 1st column's growth rate
    # e.g. passing factor_columns = ['gdp','co2'] will calculate: multiplier = co2 growth rate / gdp growth rate
    mult_col_name = (str(mult_columns[1]) + ' / ' + str(mult_columns[0]) + ' multiplier')
    multiplier_df[mult_col_name] = \
        (multiplier_df[col_growth_names[1]] / multiplier_df[col_growth_names[0]])

    # if the denominator of the calculation is negative, then we need to reverse the sign of the multiplier
    # this is because, in previous example, if gdp growth rate has been negative but co2 growth has been positive,
    # it would be incorrect to interpret this as a negative multiplier (i.e. when gdp contracts, co2 contracts too),
    # even though the division results in a negative
    positive_denominator = multiplier_df[col_growth_names[0]] > 0
    multiplier_df[mult_col_name].where(positive_denominator, -multiplier_df[mult_col_name], inplace=True)

    return multiplier_df


def grouped_growth_rate_multipliers(original_data, mult_columns, number_of_groups):
    """
    Takes the full data set, chosen columns, and desired number of groups, returns df with multipliers and group labels
    for each country

    This function calculates the multipliers between the chosen columns' growth rates using find_multiplier(), then
    groups the resulting df into the chosen number of bins for the growth rate of the first passed column.

    For example, I want to find out how the gdp growth rates and co2 growth rates are related for countries where the
    gdp growth rate is within the first quartile. This function will take arguments:
    growth_quantile(original data, ['gdp', 'co2'], 4).

    The result is interesting because it lets us group the data into sets of countries with similar
    characteristics and learn whether relationships between data points change based on those characteristics.

    :param original_data: pass the original, unaltered owid co2 data dataframe that was downloaded from the owid GitHub
    :param mult_columns: the names of the columns for which you want to calculate the growth rate multiplier
    :param number_of_groups: the number of groups you want to split the data into. The set will be divided into chosen
     number of groups using the number_of_groups - 1 quantiles of the growth rates of the first passed column
    :return: dataframe with multiplier that shows the relationship between growth rates with labels of the group
     each denominator growth rate belongs to
    """

    # create an empty list to store the names of the columns containing the growth rates
    col_growth_names = []

    # iterate through the two passed columns and add a suffix to the name to match the output of sg.show_growth_rates
    for col in mult_columns:
        col_growth_names.append(str(col + ' % growth'))

    # run the find_multiplier function to find the growth rate data, calculate the multiplies, and copy to a df
    multiplier_df = find_multiplier(original_data, mult_columns)

    # slice df into specified number of equal groups based on first passed column's growth rate and
    # add a column that labels the group
    grouped_df = multiplier_df
    grouping_column_name = col_growth_names[0]
    grouped_df['Growth Rate Group'] = pd.qcut(grouped_df[grouping_column_name], q=number_of_groups,
                                              labels=range(1, number_of_groups + 1))

    return grouped_df


def find_grouped_mean_multiplier(original_data, mult_columns, number_of_groups):
    """
    Takes the full data set, chosen columns, and desired number of groups, returns the mean of multipliers for
    each group of growth rates of the first passed column

    :param original_data: pass the original, unaltered owid co2 data dataframe that was downloaded from the owid GitHub
    :param mult_columns: the names of the columns for which you want to calculate the mean growth rate multiplier
    :param number_of_groups: the number of groups you want to split the data into. The set will be divided into chosen
     number of groups using the number_of_groups - 1 quantiles of the growth rates of the first passed column
    :return: the mean of the multipliers for countries in each equal group based on growth rate of denominator
    """

    # create a copy of df showing multipliers between chosen quantiles
    grouped_multiplier_df = grouped_growth_rate_multipliers(original_data, mult_columns, number_of_groups)

    # define the multiplier column name that was generated by find_multiplier()
    mult_col_name = (str(mult_columns[1]) + ' / ' + str(mult_columns[0]) + ' multiplier')

    # create dictionary that will contain {group : mean multiplier}
    mean_multiplier_dict = {}

    # iterate through each group using number_of_groups and calculate mean multiplier for each group
    for group in range(1, number_of_groups + 1):
        group_df = grouped_multiplier_df[grouped_multiplier_df['Growth Rate Group'] == group]
        mean_group_multiplier = np.mean(group_df[mult_col_name])
        mean_multiplier_dict[group] = mean_group_multiplier

    return mean_multiplier_dict


def grouped_mean_multiplier_bar_chart(original_data, mult_columns, number_of_groups):
    """
    Takes the full data set, chosen columns, and desired number of groups of growth rates, and returns a bar chart
    visualizing the mean multiplier of column growth rates for each group

    :param original_data: pass the original, unaltered owid co2 data dataframe that was downloaded from the owid GitHub
    :param mult_columns: the names of the columns for which you want to calculate the mean growth rate multiplier
    :param number_of_groups: the number of groups you want to split the data into. The set will be divided into chosen
     number of groups using the number_of_groups - 1 quantiles of the growth rates of the first passed column
    :return: bar chart of the mean multiplier for each equal group of sorted growth rates of first passed column
    """

    # find the mean multiplier of each group
    mean_multiplier_dict = find_grouped_mean_multiplier(original_data, mult_columns, number_of_groups)

    # plot the dictionary items

    plt.bar(*zip(*mean_multiplier_dict.items()))
    # plt.title(result_text)
    plt.xlabel(str(mult_columns[0]) + ' Growth Rate Group')
    plt.ylabel('Mean Multiplier between ' + str(mult_columns[0]) + ' Growth Rate and '
               + str(mult_columns[1]) + ' Growth Rate')
    plt.show()

