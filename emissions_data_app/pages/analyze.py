import random

import dash
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
from emissions_data_app.download_data import co2_data_countries, codebook
import emissions_data_app.utils as u

dash.register_page(__name__, order=1, path='/')

# Palette:
# #002B36 - dark blue
# #A4C9D7 - light blue
# #D07C2E - orange
# #F1F1E6 - gray

# Build sidebar
sidebar_style = \
    {
        "position": "relative",
        "top": 0,
        "left": 0,
        "bottom": 0,
        "padding": "1rem 1rem",
        #"background-color": "#002b36",
        #"color": "#D07C2E",
    }

sidebar = \
    dbc.Container(
        [
            html.H2("Filters"),
            html.Hr(),
            dbc.Nav(
                [
                    html.P(
                        "Countries", className="lead"
                    ),
                    dcc.Dropdown(
                        co2_data_countries.country.unique(),
                        co2_data_countries.country.unique()[0],
                        id='country-selector',
                        placeholder='Select one or more countries...',
                        multi=True
                    ),
                    html.P(children="", id='country-error-display',
                           style={'font-weight': 'bold', 'font-style': 'italics'}),
                    html.P(
                        "Dataset", className="lead"
                    ),
                    dcc.Dropdown(
                        co2_data_countries.loc[:, ~co2_data_countries.columns.isin(
                            ['country', 'year', 'iso_code'])].columns,
                        'co2',
                        id='dataset-selector',
                        placeholder='Select a dataset to plot...'
                    ),
                    html.P(children="", style={'font-weight': 'bold', 'font-style': 'italics'},
                           id='dataset-error-display'),
                    html.P(
                        "Bubble size", className="lead"
                    ),
                    dcc.Dropdown(
                        co2_data_countries.loc[:, ~co2_data_countries.columns.isin(
                            ['country', 'year', 'iso_code'])].columns,
                        id='bubble-size-selector',
                        placeholder='Select a dataset to represent size...'
                    ),
                    html.A("Dataset definitions",
                           href='https://github.com/owid/co2-data/blob/master/owid-co2-codebook.csv',
                           target="_blank"),
                    html.P(id='bubble-size-error-display')
                ],
                vertical=True,
                pills=True
            ),
        ],
        style=sidebar_style,
        fluid=True
    )

# Create app layout

layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            sidebar, style={'margin-left': '-20px', 'margin-right': '-20px'}
                            )
                        ),
                    width=3
                ),
                dbc.Col(
                    [
                        html.H2(style={'textAlign': 'left', 'margin-left': '7px', 'margin-top': '1rem',
                                       'color': '#D07C2E', 'font-weight': 'bold'},
                                children='Analyze'),
                        html.P(style={'textAlign': 'left', 'margin-left': '7px', 'margin-top': '7px',
                                      'color': '#D07C2E', 'font-style': 'italics'},
                               children=
                               '''
                               Analyze countries' GHG emissions and how they are influenced by various characteristics
                               '''),
                        html.Hr(),
                        dcc.Graph(
                            id='scatter-plot',
                        ),
                        dcc.Slider(
                            co2_data_countries['year'].min(),
                            co2_data_countries['year'].max(),
                            step=None,
                            value=co2_data_countries['year'].max(),
                            marks={str(year): str(year) for year in co2_data_countries['year'].unique()
                                   if year % 10 == 0},
                            id='year-slider'
                        ),
                        html.A(id='dataset-explainer'),
                        html.Hr(),
                        html.A(id='bubble-dataset-explainer')
                    ],
                    width=9
                    )
            ]
        ),
    ],
    fluid=True,
    class_name="g-0"
)


# Callback to update scatter plot with changes to dropdown selections or slider adjustments
@callback(
    Output('scatter-plot', 'figure'),
    Output('country-error-display', 'children'),
    Output('dataset-error-display', 'children'),
    Output('bubble-size-error-display', 'children'),
    Output('dataset-explainer', 'children'),
    Output('bubble-dataset-explainer', 'children'),
    Input('year-slider', 'value'),
    Input('country-selector', 'value'),
    Input('dataset-selector', 'value'),
    Input('bubble-size-selector', 'value'))
def update_scatter_plot(selected_year, country_value, dataset_value, bubble_size_value):
    if not country_value:
        selected_country_df = co2_data_countries
    # check if more than one country has been passed
    elif isinstance(country_value, list):
        # if country-selector value is a list, there is more than one country selected, then .isin() should be used
        selected_country_df = co2_data_countries[co2_data_countries['country'].isin(country_value)]
    else:
        # if it's not a list, only one country is selected, which means we should use boolean comparison to select
        selected_country_df = co2_data_countries[co2_data_countries['country'] == country_value]

    # use the utils function to find the dataset for only the selected countries and years
    df = u.find_all_data_for_year(selected_country_df, selected_year)

    # check if no dataset selected, return an error and don't update dashboard
    if not dataset_value:
        return dash.no_update, dash.no_update, html.P(f'Please select a dataset.', style={
            'font-weight': 'bold', 'font-style': 'italics', 'color': '#D07C2E'}), dash.no_update, dash.no_update, dash.no_update

    # check if any data in bubble_size set is NaN, and return an error and don't update dashboard
    if bubble_size_value and (df[bubble_size_value].isnull().values.any() or (df[bubble_size_value] < 0).any()):
        df = df.copy()
        df[bubble_size_value].fillna(0, inplace=True)
        df[bubble_size_value] = df[bubble_size_value].apply(lambda x: 0 if x < 0 else x)

    # define the parameters of the scatter plot and update the data
    fig = px.scatter(df, x='country', y=dataset_value, size=bubble_size_value, size_max=70,
                     labels={'country': 'Country', dataset_value: f"{dataset_value} *"})
    fig.update_layout(transition_duration=100)

    # access codebook for full description of selected dataset to be updated under scatter plot
    dataset_codebook_description = codebook.loc[codebook['column'] == dataset_value]['description'].values[0]
    dataset_def = f"* {dataset_value}: {dataset_codebook_description}"

    # access codebook for full description of selected bubble size dataset, if selected
    if bubble_size_value:
        bubble_size_codebook_description = codebook.loc[codebook['column'] ==
                                                        bubble_size_value]['description'].values[0]
        bubble_size_def = f"** {bubble_size_value}: {bubble_size_codebook_description}"
        return fig, None, None, None, dataset_def, bubble_size_def

    return fig, None, None, None, dataset_def, None


