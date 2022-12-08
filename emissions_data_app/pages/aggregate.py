import dash
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
from emissions_data_app.download_data import co2_data_countries, codebook
import emissions_data_app.utils as u

dash.register_page(__name__, order=3)

layout = dbc.Container(
    html.H1("Aggregate")
)