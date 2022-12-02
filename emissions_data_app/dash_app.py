from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import dash_bootstrap_templates as dbt
import plotly.express as px
import pandas as pd
from download_data import co2_data_countries, codebook
import utils as u


# Palette:
# 002B36 - dark blue
# A4C9D7 - light blue
# D07C2E - orange
# F1F1E6 - gray


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
            dbc.Nav(
                [
                    html.P(
                        "Select one or more countries", className="lead"
                    ),
                    dcc.Dropdown(
                        co2_data_countries.country.unique(),
                        co2_data_countries.country.unique()[0],
                        id='country-selector',
                        placeholder='Select one or more countries...',
                        multi=True
                    ),
                    html.Br(),
                    html.P(
                        "Select a dataset to explore", className="lead"
                    ),
                    dcc.Dropdown(
                        co2_data_countries.loc[:, ~co2_data_countries.columns.isin(
                            ['country', 'year', 'iso_code'])].columns,
                        'co2',
                        id='dataset-selector',
                        placeholder='Select a dataset to explore...'
                    ),
                    html.A("Dataset definitions",
                           href='https://github.com/owid/co2-data/blob/master/owid-co2-codebook.csv',
                           target="_blank"),
                    ],
                vertical=True,
                pills=True,
            ),
        ],
        style=sidebar_style
    )

    # Build scatter plot figure

    # Create app layout

    app.layout = html.Div(children=[
        dbc.Row([
            dbc.Col(),
            dbc.Col(
                html.H1(style={'textAlign': 'center', 'margin-left': '7px', 'margin-top': '7px'},
                        children='Historical CO2 and GHG Emissions by Country'),
                width=9,
                style={'margin-left': '7px', 'margin-top': '7px'})
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
                style={'margin-left': '7px', 'margin-top': '7px'}
            )
        ]),
        dbc.Row([
            dbc.Col(),
            dbc.Col(
                [
                    dcc.Graph(
                        id='co2-scatter-plot',
                    ),
                    dcc.Slider(
                        co2_data_countries['year'].min(),
                        co2_data_countries['year'].max(),
                        step=None,
                        value=co2_data_countries['year'].max(),
                        marks={str(year): str(year) for year in co2_data_countries['year'].unique() if year % 10 == 0},
                        id='year-slider'
                    ),
                    html.A(id='dataset-explainer')
                ],
                width=9,
                style={'margin-left': '7px', 'margin-top': '7px'})
        ]),
    ])

    @app.callback(
        Output('co2-scatter-plot', 'figure'),
        Output('dataset-explainer','children'),
        Input('year-slider', 'value'),
        Input('country-selector', 'value'),
        Input('dataset-selector', 'value'))
    def update_co2_scatter_plot(selected_year, value_1, value_2):
        if isinstance(value_1, list):
            selected_country_df = co2_data_countries[co2_data_countries['country'].isin(value_1)]
        else:
            selected_country_df = co2_data_countries[co2_data_countries['country'] == value_1]

        df = u.find_all_data_for_year(selected_country_df, selected_year)
        fig = px.scatter(df, x='country', y=value_2,
                         labels={'country': 'Country', value_2: f"{value_2} *"})

        fig.update_layout(transition_duration=100)

        # access codebook for full description of selected dataset
        dataset_codebook_description = codebook.loc[codebook['column'] == value_2]['description'].values[0]
        dataset_def = f"* {value_2}: {dataset_codebook_description}"

        return fig, dataset_def

    app.run_server(debug=True)


if __name__ == '__main__':
    main()
