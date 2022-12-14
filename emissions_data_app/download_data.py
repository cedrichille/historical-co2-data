import io

import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import requests


pd.options.display.width = 0
pd.options.display.max_rows = 90
pd.set_option('display.float_format', lambda x: '%0.2f' % x)

# download the csv file from the co2-data repository on GitHub

url = "https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv"
download = requests.get(url).content

# save the contents of the csv to a pd DataFrame

co2_data = pd.DataFrame(pd.read_csv(io.StringIO(download.decode('utf-8'))))
#co2_data.to_excel(r'C:\Users\chille\Python\historical-co2-data\emissions_data_app\co2_data.xlsx')
co2_data_countries = co2_data[~co2_data['iso_code'].isnull()]
co2_data_regions = co2_data[co2_data['iso_code'].isnull()]

# download codebook for dataset definitions
url_codebook = "https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-codebook.csv"
download_codebook = requests.get(url_codebook).content

#save codebook to a df
codebook = pd.DataFrame(pd.read_csv(io.StringIO(download_codebook.decode('utf-8'))))
