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


