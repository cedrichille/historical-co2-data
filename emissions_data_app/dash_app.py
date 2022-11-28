from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import dash_bootstrap_templates as dbt
import plotly.express as px
import pandas as pd
from download_data import co2_data_countries
import utils as u

# Palette:
    #002B36 - dark blue
    #A4C9D7 - light blue
    #D07C2E - orange
    #F1F1E6 - gray


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
        "background-color": "#002b36",
        "color": "#D07C2E"
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
        style=sidebar_style
    )

    # Build scatter plot figure

    #df = u.find_all_data_for_year(co2_data_countries, 1990)
    #fig = px.scatter(df, x='country', y='co2')

    # Create app layout

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
                [dcc.Graph(
                    id='co2-scatter-plot',
                    #figure=fig
                ),
                dcc.Slider(
                    co2_data_countries['year'].min(),
                    co2_data_countries['year'].max(),
                    step=None,
                    value=co2_data_countries['year'].max(),
                    marks={str(year): str(year) for year in co2_data_countries['year'].unique() if year % 10 == 0},
                    id='year-slider'
                )],
                width=9,
                style={'margin-left':'7px', 'margin-top':'7px'})
        ])


    ])

    @app.callback(
        Output('co2-scatter-plot','figure'),
        Input('year-slider','value'))
    def update_co2_scatter_plot(selected_year):
        df = u.find_all_data_for_year(co2_data_countries, selected_year)
        fig = px.scatter(df, x='country', y='co2', labels={'country':'Country', 'co2':'CO2 emissions (million tonnes)'})

        fig.update_layout(transition_duration=50)

        return fig

    app.run_server(debug=True)


if __name__ == '__main__':
    main()
