from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
import dash_bootstrap_templates as dbt
import plotly.express as px
import pandas as pd
from download_data import co2_data_countries
import utils as u


def main() -> None:
    app = Dash(external_stylesheets=[dbc.themes.SOLAR])

    dbt.load_figure_template('SOLAR')

    # Build sidebar
    sidebar_style = {
        "position": "fixed",
        "top": 0,
        "left": 0,
        "bottom": 0,
        "width": "24rem",
        "padding": "2rem 1rem",
        "background-color": "#f8f9fa",
    }

    sidebar = html.Div(
        [
            html.H2("Filters"),
            html.Hr(),
            html.P(
                "A simple sidebar layout with filters", className="lead"
            ),
            dbc.Nav(
                [
                    dcc.Dropdown(id='one'),
                    html.Br(),
                    dcc.Dropdown(id='two'),
                    html.Br(),
                    dcc.Dropdown(id='three')

                ],
                vertical=True,
                pills=True,
            ),
        ],
        style=sidebar_style,
    )

    # Build scatter plot figure

    df = u.find_all_data_for_year(co2_data_countries, 1990)

    fig = px.scatter(df, x='country', y='co2')

    app.layout = html.Div(children=[
        dbc.Row([
            dbc.Col(),
            dbc.Col(
                html.H1(style={'textAlign': 'center', 'margin-left':'7px', 'margin-top':'7px'},
                        children='Historical CO2 and GHG Emissions by Country'),
                width=9,
                style={'margin-left':'7px', 'margin-top':'7px'})
            ]),

        dbc.Row([
            dbc.Col(sidebar),
            dbc.Col(
                html.Div(
                    style={'textAlign': 'center'},
                    children=
                    '''
                    Dashboard to explore the CO2 and greenhouse gas emissions of countries through history. 
                    Based on Our World in Data (OWID) data from the owid/co2-data GitHub repository. 
                    '''),
                width=9,
                style={'margin-left':'7px', 'margin-top':'7px'}
            )
        ]),
        dbc.Row([
            dbc.Col(),
            dbc.Col(
                dcc.Graph(
                    id='co2-scatter-plot',
                    figure=fig),
                width=9,
                style={'margin-left':'7px', 'margin-top':'7px'})
        ])


    ])

    app.run_server(debug=True)


if __name__ == '__main__':
    main()
