import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, order=5)

layout = dbc.Container(children=[
    html.H1(children='This is our About page', style={'textAlign': 'center'}),

    html.Div(children='''
        This is our About page content.
    ''',
             style={'textAlign': 'center'}),

])