import dash
from dash import html, dcc

dash.register_page(__name__, path='/')

layout = html.Div(children=[
    html.H1(children='This is our Home page', style={'textAlign': 'center'}),

    html.Div(children='''
        This is our Home page content.
    ''',
             style={'textAlign': 'center'}),

])