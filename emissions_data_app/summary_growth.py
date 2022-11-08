import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import requests
from download_data import co2_data
import utils as u


def find_earliest_data(original_data, column_name):
    """
    Takes the full data set and a column, returns the earliest available non-zero data and corresponding year
    for each country

    The function removes nulls and zeros from the column, so only rows with available non-zero data are shown.
    Then, the index of the earliest data point is found by identifying the index of the minimum year of available data.
    Finally, the earliest data point itself is found.

    The function returns a dataframe with the earliest data point and corresponding year for each country.
    :param original_data: pass the original, unaltered owid co2 data dataframe that was downloaded from the owid GitHub
    :param column_name: the name of the column in the co2 data set for which you want the earliest available data
    :return: dataframe with the earliest data and corresponding year for each country in the data set
    """
    # remove nulls and zeros from the selected column in the original data set and assign to a new df

    drop_nan = original_data[~(original_data[column_name].isnull() | (original_data[column_name] == 0))]

    #  find the index of the minimum year for each country and assign to df

    earliest_year_index = drop_nan.groupby('country')['year'].idxmin()

    # extract rows from original dataframe using the earliest indexes and save as new df
    # with renamed columns labeling as earliest data and country as index

    earliest_data_df = pd.DataFrame(original_data.iloc[earliest_year_index][['country', 'year', column_name]])
    earliest_data_df.rename(columns={'year': 'earliest ' + column_name + ' year',
                                     column_name: 'earliest ' + column_name}, inplace=True)
    earliest_data_df.set_index('country', inplace=True)

    return earliest_data_df


def find_latest_data(original_data, column_name):
    """
    Takes the full data set and a column, returns the latest available non-zero data and corresponding year
    for each country

    The function removes nulls and zeros from the column, so only rows with available non-zero data are shown.
    Then, the index of the latest data point is found by identifying the index of the maximum year of available data.
    Finally, the latest data point itself is found.

    Note that, since zero values are removed, the function will define the latest available data point as the latest
    available non-zero value, even in the case where a country's actual latest available data has gone to zero.

    The function returns a dataframe with the latest data point and corresponding year for each country.
    :param original_data: pass the original, unaltered owid co2 data dataframe that was downloaded from the owid GitHub
    :param column_name: the name of the column in the co2 data set for which you want the latest available data
    :return: dataframe with the latest data and corresponding year for each country in the data set
    """
    # remove nulls from the selected column in the original data set and assign to a new df
    drop_nan = original_data[~(original_data[column_name].isnull() | (original_data[column_name] == 0))]

    #  find the index of the minimum year for each country and assign to df

    latest_year_index = drop_nan.groupby('country')['year'].idxmax()

    # extract rows from original dataframe using the latest indexes and save as new df with
    # renamed columns labeling as latest data and country as index

    latest_data_df = pd.DataFrame(original_data.iloc[latest_year_index][['country', 'year', column_name]])
    latest_data_df.rename(columns={'year': 'latest ' + column_name + ' year',
                                   column_name: 'latest ' + column_name}, inplace=True)
    latest_data_df.set_index('country', inplace=True)

    return latest_data_df


def column_summary(original_data, column_name):
    """
    Takes the full data set and a column, returns a df summarizing data and its availability for all countries

    :param original_data: pass the original, unaltered owid co2 data dataframe that was downloaded from the owid GitHub
    :param column_name: the name of the column in the co2 data set for which you want the summary
    :return: dataframe summarizing the earliest and latest available data and corresponding years for each country
    """

    # find the earliest available data and corresponding year for each column
    earliest_data_df = find_earliest_data(original_data, column_name)

    # find the latest available data and corresponding year for each column
    latest_data_df = find_latest_data(original_data, column_name)

    # concatenate dataframes to create a summary
    summary_df = pd.concat([earliest_data_df, latest_data_df], join='outer', axis=1)
    columns_to_int = ['earliest ' + column_name + ' year', 'latest ' + column_name + ' year']
    summary_df[columns_to_int] = summary_df[columns_to_int].astype(pd.Int64Dtype())

    return summary_df


def add_growth_column_to_summary_df(summary_dataframe, column_name):
    """
    Takes the summary table for a column and returns a dataframe with an added column calculating growth rate

    The growth rate refers to the simple percent change between the earliest available data and latest available
    data.

    :param summary_dataframe: the dataframe generated by the column_summary function
    :param column_name: name of the column for which a growth rate should be calculated
    :return: original summary dataframe with an added column showing growth rate for each country
    """

    # create a copy of the summary_df generated by column_summary function
    summary_df = summary_dataframe

    # add a column that calculates the percent change between earliest and latest available data
    summary_df[column_name + ' % growth'] = \
        ((summary_df['latest ' + column_name] - summary_df['earliest ' + column_name]) /
         summary_df['earliest ' + column_name])

    # rename dataframe to clarify that it contains a growth element
    summary_df_with_growth = summary_df

    return summary_df_with_growth


def create_combined_summary(original_data, column_names=None):
    """
    Takes the full data set and a set of columns, returns a df summarizing data for each country, including growth rates

    :param original_data: pass the original, unaltered owid co2 data dataframe that was downloaded from the owid GitHub
    :param column_names: the names of the columns in the co2 data set which you want to include in the summary table
    :return: a single dataframe with a summary of earliest and latest data and growth rates for the passed columns
    for all countries
    """
    # create a dictionary that will contain the names of the summary dataframes for each column
    df_dict = {}

    # if columns are passed, they should be stored in the columns_to_be_summarized variable
    if column_names is not None:
        columns_to_be_summarized = column_names
    # if no column names are passed, all columns from the original data should be stored in the variable
    else:
        columns_to_be_summarized = original_data.columns[~original_data.columns.isin(['country', 'year', 'iso_code'])]

    # iterate through the column names in the variable to create summary dataframes for each and add to the dictionary
    for col in columns_to_be_summarized:
        # create a summary dataframe for the columns
        summary_col_dataframe = column_summary(original_data, col)

        # add a growth % column
        df_dict['summary_' + col] = add_growth_column_to_summary_df(summary_col_dataframe, col)

    # concatenate the dataframes included in the dictionary
    combined_summary = pd.concat(df_dict, join='outer', axis=1)
    combined_summary = combined_summary.droplevel(level=0, axis=1)
    combined_summary = combined_summary.replace(np.inf, np.NaN)

    return combined_summary


def extract_growth_rates_from_summary_df(original_data, column_names=None):
    """
    Takes the full co2 data and a selection of columns, and returns only the growth rates for each column and country

    The purpose of the function is to give an easy one-step method to find just the percent change from earliest to
    latest available data for a certain column of data without the table being cluttered by the earliest and latest
    data and the corresponding years, as is the case in the combined_summary df.

    :param original_data: pass the original, unaltered owid co2 data dataframe that was downloaded from the owid GitHub
    :param column_names: the names of the columns in the co2 data set for which you want the growth rates
    :return: a single dataframe with the growth rates for the passed columns for all countries
    """
    # initiate a list to hold the names of the columns containing the growth % data in the combined_summary table from
    # the create_combined_summary function
    col_growth_names = []

    # if columns are passed, add them a variable
    if column_names is not None:
        columns_to_be_extracted = column_names
    # if no columns are passed, add all columns from original data to variable
    else:
        columns_to_be_extracted = original_data.columns[~original_data.columns.isin(['country', 'year', 'iso_code'])]

    # iterate through the variable containing column names to add the required growth % column names to the list
    for col in columns_to_be_extracted:
        col_growth_names.append(str(col + ' % growth'))

    # run the function to create the combined_summary dataframe, and then extract the growth % columns
    growth_columns = create_combined_summary(original_data, column_names)[col_growth_names]

    return growth_columns
