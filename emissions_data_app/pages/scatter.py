import dash
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
from emissions_data_app.download_data import co2_data_countries, codebook
import emissions_data_app.utils as u

dash.register_page(__name__)

# Build sidebar
sidebar_style = \
    {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "24rem",
    "padding": "2rem 1rem",
    "background-color": "#002b36",
    "color": "#D07C2E"
}

sidebar = \
    html.Div(
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
                html.Br(),
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
                html.Br(),
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
            pills=True,
        ),
    ],
    style=sidebar_style
)

# Create app layout

layout = html.Div(children=[
    dbc.Row([
        dbc.Col(),
        dbc.Col()
    ]),
    # Title
    dbc.Row([
        dbc.Col(),
        dbc.Col(
            html.H1(style={'textAlign': 'center', 'margin-left': '7px', 'margin-top': '7px'},
                    children='Historical CO2 and GHG Emissions by Country'),
            width=9,
            style={'margin-left': '7px', 'margin-top': '7px'})
    ]),

    # Sidebar and subtitle
    dbc.Row([
        dbc.Col(),
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

    # Scatter plot, slider, caption
    dbc.Row([
        dbc.Col(sidebar),
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


# Callback to update scatter plot with changes to dropdown selections or slider adjustments
@callback(
    Output('co2-scatter-plot', 'figure'),
    Output('country-error-display', 'children'),
    Output('dataset-error-display', 'children'),
    Output('bubble-size-error-display', 'children'),
    Output('dataset-explainer', 'children'),
    Input('year-slider', 'value'),
    Input('country-selector', 'value'),
    Input('dataset-selector', 'value'),
    Input('bubble-size-selector', 'value'))
def update_scatter_plot(selected_year, country_value, dataset_value, bubble_size_value):
    # check if more than one country has been passed
    if isinstance(country_value, list):
        # if country-selector value is a list, there is more than one country selected, then .isin() should be used
        selected_country_df = co2_data_countries[co2_data_countries['country'].isin(country_value)]
    else:
        # if it's not a list, only one country is selected, which means we should use boolean comparison to select
        selected_country_df = co2_data_countries[co2_data_countries['country'] == country_value]

    # use the utils function to find the dataset for only the selected countries and years
    df = u.find_all_data_for_year(selected_country_df, selected_year)

    # check if no countries provided, return an error and don't update dashboard
    if not country_value:
        return dash.no_update, html.P(f'Please select one or more countries.', style={
            'font-weight': 'bold', 'font-style': 'italics'}), dash.no_update, dash.no_update, dash.no_update

    # check if no dataset selected, return an error and don't update dashboard
    if not dataset_value:
        return dash.no_update, dash.no_update, html.P(f'Please select a dataset.', style={
            'font-weight': 'bold', 'font-style': 'italics'}), dash.no_update, dash.no_update

    # check if any data in bubble_size set is NaN, and return an error and don't update dashboard
    if bubble_size_value and df[bubble_size_value].isnull().values.any():
        return dash.no_update, dash.no_update, dash.no_update, \
               html.P(f'At least one {bubble_size_value} value is unavailable for this year, '
                      f'please select another Bubble size dataset or year.', style=
                      {'font-weight': 'bold', 'font-style': 'italics'}), dash.no_update

    # check if any data in bubble_size set is negative, and return an error and don't update dashboard
    if bubble_size_value and df[bubble_size_value].isnull().values.any():
        return dash.no_update, dash.no_update, dash.no_update, \
               html.P(f'At least one {bubble_size_value} value is unavailable for this year, '
                      f'please select another Bubble size dataset or year.', style=
                      {'font-weight': 'bold', 'font-style': 'italics'}), dash.no_update

    # define the parameters of the scatter plot and update the data
    fig = px.scatter(df, x='country', y=dataset_value, size=bubble_size_value, size_max=70,
                     labels={'country': 'Country', dataset_value: f"{dataset_value} *"})
    fig.update_layout(transition_duration=100)

    # access codebook for full description of selected dataset to be updated under scatter plot
    dataset_codebook_description = codebook.loc[codebook['column'] == dataset_value]['description'].values[0]
    dataset_def = f"* {dataset_value}: {dataset_codebook_description}"

    return fig, None, None, None, dataset_def

