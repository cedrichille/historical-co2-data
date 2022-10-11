import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import requests

pd.options.display.width = 0
pd.options.display.max_rows = 90
pd.set_option('display.float_format', lambda x: '%0.2f' % x)
# save the data to a DataFrame - for now read from excel, later learn how to read from JSON
co2_data = pd.DataFrame(pd.read_excel(
    r'C:\Users\chille\OneDrive - Digimarc Corporation\00 - Admin\Other\Python\Carbon projects\owid-co2-data.xlsx'))













# --------------------------------- Biggest cumulative CO2 contributors --------------------------------------------


# ----------------------------------- Biggest Net Importers and Exporters of Emissions ------------------------


# -------------------------------------- Trends in Import and Export of Emissions ---------------------------------
# --------------------------------------- including projected changes in balance of emission trade ----------------
