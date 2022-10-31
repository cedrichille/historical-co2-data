import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import requests
from download_data import co2_data


def find_country_year_data(data, column_name, country, year):
    """
    Takes a data set, a column, country, and year, and returns the corresponding value from the data set

    :param data: dataframe with at least columns 'country', 'year', and a column with data you want to extract
    :param column_name: name of column in which you want to find a value
    :param country: country for which you want to find the value
    :param year: year for which you want to find the value
    :return: column value for country/year combination from dataframe
    """
    # find value given parameters, using .values[0] because conditional selection returns series
    # with IndexError exception for NaN, which would result in an empty series
    try:
        value = data[(data['country'] == country) & (data['year'] == year)][column_name].values[0]
    except IndexError:
        value = np.nan

    return value


def pct_change_formula(datapoint_1, datapoint_2):
    """
    Takes two datapoints, calculates the percent change between them

    :param datapoint_1: numeric datapoint representing old value
    :param datapoint_2: numeric datapoint representing new value
    :return: pct change as float
    """
    # calculate pct change using standard formula
    pct_change = (datapoint_2 - datapoint_1) / datapoint_1

    return pct_change


def find_pct_change_between_years(original_data, column_name, year_1, year_2):
    """
    Takes the full data set and two years, returns the percent change between the years for the chosen column

    :param original_data: pass the original, unaltered owid co2 data dataframe that was downloaded from the owid GitHub
    :param column_name: the name of the column in the co2 data set for which you want the percent change
    :param year_1: the start year for percent change calculation
    :param year_2: the end year for percent change calculation
    :return: df with percent change between year_1 and year_2 for all countries
    """
    # remove nulls and zeros from the selected column in the original data set and assign to a new df
    data_without_nan = original_data[~(original_data[column_name].isnull() | (original_data[column_name] == 0))]

    # create list of unique countries
    country_list = data_without_nan['country'].unique()

    # iterate through country list to find data in year_1, year_2 and calculate percent_change, and add to a dictionary
    pct_change_dict = {}
    for country in country_list:
        year_1_data = find_country_year_data(data_without_nan, column_name, country, year_1)
        year_2_data = find_country_year_data(data_without_nan, column_name, country, year_2)

        pct_change_dict[country] = pct_change_formula(year_1_data, year_2_data)
    print(pct_change_dict)
    pct_change_between_years_dataframe = pd.DataFrame.from_dict(pct_change_dict, orient='index',
                                                                columns=[(str(column_name) + ' pct_change')])

    return pct_change_between_years_dataframe


def add_yoy_pct_change(original_data):
    """
    Takes the full data set and returns it as a df with YoY growth rate for each column of data
    :param original_data: pass the original, unaltered owid co2 data df that as downloaded from the owid GitHub
    :return: df with original data and added columns showing the YoY growth rates for all data
    """
    # save a copy of original_data
    data_with_pct_change = original_data

    # iterate through columns to add a YoY % change column for each column of original data that contains ints or floats
    # default NaN fill method (pad) is used to fill forward the time series as if data had continued to accrue
    for col in data_with_pct_change.select_dtypes(include=['int64', 'float64']):
        # get the index of col
        col_index = data_with_pct_change.columns.get_loc(col)
        # insert a column to the right of col with the pct_change
        data_with_pct_change.insert(col_index + 1, str(col) + ' YoY_pct_change', data_with_pct_change[col].pct_change())

    return data_with_pct_change

