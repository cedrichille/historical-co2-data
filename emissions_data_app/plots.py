import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import requests
from download_data import co2_data_regions, co2_data_countries
import summary_growth as sg
import utils as u
import growth_analysis as ga


def group_boxplot(original_data, year, column_to_group, number_of_groups, column_to_plot):
    """
    Takes a year of data, groups countries based on percentiles in a certain column's values, and draws boxplots of
    each group's values in a (potentially different) column.
    :param original_data:
    :param year:
    :param column_to_group:
    :param number_of_groups:
    :param column_to_plot:
    :return:
    """
    # create df with a column denoting group for chosen column
    grouped_df = u.divide_data_into_groups_for_year(original_data, year, column_to_group, number_of_groups)

    # set a variable to store the name of column denoting groups
    group_column_name = str(column_to_group) + " Group"

    # create a plot with n= number_of_groups subplots
    fig, axes = plt.subplots(ncols=number_of_groups, sharey=True)
    fig.subplots_adjust(wspace=0)

    for ax, group in zip(axes, range(1, number_of_groups + 1)):
        ax.boxplot(grouped_df[grouped_df[group_column_name] == group][column_to_plot],
                   showfliers=True)
        ax.set(xlabel=group)

    plt.show()


def plot_grouped_descriptive_stats(original_data, year, column_to_group, number_of_groups,
                                   column_to_summarize, stat_to_plot):
    """
    Takes a year from original data, groups countries by percentiles of a chosen column,
    and plots a chosen descriptive statistic for each group for a (potentially different) chosen column

    Options of statistics to plot are: mean, std, min, 25%, 50%, 75%, max

    :param stat_to_plot:
    :param original_data:
    :param year:
    :param column_to_group:
    :param number_of_groups:
    :param column_to_summarize:
    :return:
    """
    # generate descriptive stat dictionary
    descriptive_stat_dictionary = u.find_summary_statistics_per_group(original_data, year, column_to_group,
                                                                    number_of_groups, column_to_summarize)

    # save values of chosen statistic to a dictionary
    chosen_stat_dict = {}
    for group in range(1, number_of_groups + 1):
        chosen_stat_dict[group] = descriptive_stat_dictionary[group][stat_to_plot]

    # plot the dictionary by sorting items into tuples, unpacking and unzipping their elements
    plt.plot(*zip(*sorted(chosen_stat_dict.items())))
    plt.show()


def plot_pct_of_total(original_data, year, column_to_group, number_of_groups, pct_of_total_column):
    """
    Takes a year from original data, groups countries by percentiles of a chosen column,
    and plots the contribution of each group to the total of a (potentially different) chosen column
    :param original_data:
    :param year:
    :param column_to_group:
    :param number_of_groups:
    :param pct_of_total_column:
    :return:
    """
    # generate pct_of_total dictionary
    pct_of_total_dict = u.group_pct_of_total(original_data, year, column_to_group, number_of_groups, pct_of_total_column)

    # plot the dictionary by sorting items into tuples, unpacking and unzipping their elements
    plt.scatter(*zip(*sorted(pct_of_total_dict.items())))
    plt.xlabel(str(column_to_group) + " group")
    plt.ylabel("% of total " + str(pct_of_total_column))
    plt.xticks(range(1, number_of_groups + 1))
    plt.show()


# ------------- MULTIPLIER-SPECIFIC PLOTS ----------------
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
    mean_multiplier_dict = ga.find_grouped_mean_multiplier(original_data, mult_columns, number_of_groups)

    # plot the dictionary items

    plt.bar(*zip(*mean_multiplier_dict.items()))
    # plt.title(result_text)
    plt.xlabel(str(mult_columns[0]) + ' Growth Rate Group')
    plt.ylabel('Mean Multiplier between ' + str(mult_columns[0]) + ' Growth Rate and '
               + str(mult_columns[1]) + ' Growth Rate')
    plt.show()


def grouped_multiplier_boxplot(original_data, mult_columns, number_of_groups):
    """

    :param original_data:
    :param mult_columns:
    :param number_of_groups:
    :return:
    """
    # create df with the growth rate multipliers and groups the countries belong to
    grouped_multiplier_df = ga.grouped_growth_rate_multipliers(original_data, mult_columns, number_of_groups)

    # save column name for multiplier to a variable to match grouped_df output
    mult_col_name = (str(mult_columns[1]) + ' / ' + str(mult_columns[0]) + ' multiplier')

    # split df into separate dfs for each group
    # df_group_name_dict = {}
    # for group in range(1, number_of_groups+1):
    #    df_group_name_dict[group] = grouped_multiplier_df[grouped_multiplier_df['Growth Rate Group'] == group]

    # create a plot with n= number_of_groups subplots
    fig, axes = plt.subplots(ncols=number_of_groups, sharey=True)
    fig.subplots_adjust(wspace=0)

    for ax, group in zip(axes, range(1, number_of_groups+1)):
        ax.boxplot(grouped_multiplier_df[grouped_multiplier_df['Growth Rate Group'] == group][mult_col_name],
                   showfliers=True)
        ax.set(xlabel=group)


    # show a box plot that summarizes multipliers for each group
    # plt.boxplot(x='Growth Rate Groups', y=mult_col_name, data=grouped_multiplier_df)
    plt.show()

