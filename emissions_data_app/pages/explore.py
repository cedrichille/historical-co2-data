import dash
from dash import html, dcc, Input, Output, callback, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
from emissions_data_app.download_data import co2_data_countries, codebook
import emissions_data_app.utils as u

dash.register_page(__name__, order=4)

# Palette:
# #002B36 - dark blue
# #A4C9D7 - light blue
# #D07C2E - orange
# #F1F1E6 - gray


initial_dataset_selection = co2_data_countries.columns[:5]
initial_country_selection = co2_data_countries.country.unique()[:5]
initial_dataset_selection = initial_dataset_selection.append(co2_data_countries[['co2', 'co2_per_capita']].columns)
initial_year_range = list(range(co2_data_countries['year'].max() - 20, co2_data_countries['year'].max()))
table_columns = []
for col in initial_dataset_selection:
    table_columns.append({"name": str(col), "id": str(col)})
table_data = co2_data_countries[co2_data_countries['year'].isin(initial_year_range) &
                                co2_data_countries['country'].isin(initial_country_selection)].to_dict('records')

explore_sidebar_style = \
    {
        "position": "relative",
        "top": 0,
        "left": 0,
        "bottom": 0,
        "padding": "1rem 1rem",
        # "background-color": "#002b36",
        # "color": "#D07C2E",
    }

explore_sidebar = \
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
                        co2_data_countries.country.unique()[:5],
                        id='explore-country-selector',
                        placeholder='Please select a country',
                        multi=True
                    ),
                    html.P(children="", id='explore-country-error-display',
                           style={'font-weight': 'bold', 'font-style': 'italics'}),
                    html.P(
                        "Datasets", className="lead"
                    ),
                    dcc.Dropdown(
                        co2_data_countries.columns,
                        initial_dataset_selection,
                        multi=True,
                        id='explore-dataset-selector',
                        placeholder='All datasets selected'
                    ),
                    html.P(children="", style={'font-weight': 'bold', 'font-style': 'italics'},
                           id='explore-dataset-error-display'),
                    html.A("Dataset definitions",
                           href='https://github.com/owid/co2-data/blob/master/owid-co2-codebook.csv',
                           target="_blank")
                ],
                vertical=True,
                pills=True
            ),
        ],
        style=explore_sidebar_style,
        fluid=True
    )

layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            explore_sidebar, style={'margin-left': '-20px', 'margin-right': '-20px'}
                        )
                    ),
                    width=3
                ),
                dbc.Col(
                    [
                        html.H2(
                            style={'textAlign': 'left', 'margin-left': '7px', 'margin-top': '1rem', 'color': '#D07C2E',
                                   'font-weight': 'bold'},
                            children='Explore'),
                        html.P(
                            style={'textAlign': 'left', 'margin-left': '7px', 'margin-top': '7px', 'color': '#D07C2E',
                                   'font-style': 'italics'},
                            children=
                            '''
                       Explore the full dataset to dive into countries' GHG emissions and 
                       how they are influenced by various characteristics
                       '''
                        ),
                        html.Hr(),
                        dcc.RangeSlider(
                            co2_data_countries['year'].min(),
                            co2_data_countries['year'].max(),
                            step=None,
                            value=[co2_data_countries['year'].max() - 20, co2_data_countries['year'].max()],
                            marks={str(year): str(year) for year in co2_data_countries['year'].unique()
                                   if year % 10 == 0},
                            allowCross=True,
                            included=True,
                            id='explore-year-slider'
                        ),
                        dash_table.DataTable(data=table_data, columns=table_columns,
                                             style_header={
                                                 'backgroundColor': '#002B36',
                                                 'color': 'white',
                                                 'border': '1px solid #A4C9D7'
                                             },
                                             style_data={
                                                 'backgroundColor': '#A4C9D7',
                                                 'color': 'black',
                                                 'border': '1px solid #002B36'
                                             },
                                             style_cell={'textAlign': 'right'},
                                             style_cell_conditional=[
                                                 {
                                                     'if': {'column_id': ['country', 'year', 'iso_code']},
                                                     'textAlign': 'left'
                                                 }
                                             ],
                                             id='explore-table')
                    ],
                    width=9
                )
            ]
        )
    ],
    fluid=True,
    class_name="g-0"
)


@callback(
    Output('explore-table', 'data'),
    Output('explore-table', 'columns'),
    Output('explore-country-error-display', 'children'),
    Output('explore-dataset-error-display', 'children'),
    Input('explore-year-slider', 'value'),
    Input('explore-country-selector', 'value'),
    Input('explore-dataset-selector', 'value'), config_prevent_initial_callbacks=True)
def update_explore_table(year_range, country_value, dataset_value):
    # check if no countries provided, return an error
    if not country_value:
        return dash.no_update, dash.no_update, html.P(f'Please select one or more countries.', style={
            'font-weight': 'bold', 'font-style': 'italics', 'color': '#D07C2E'}), dash.no_update
    # check if no datasets selected, then return all columns
    if not dataset_value:
        dataset_value = co2_data_countries.columns

    # check if more than one country has been passed
    if isinstance(country_value, list):
        # if country-selector value is a list, there is more than one country selected, then .isin() should be used
        selected_country_df = co2_data_countries[co2_data_countries['country'].isin(country_value)]
    else:
        # if it's not a list, only one country is selected, which means we should use boolean comparison to select
        selected_country_df = co2_data_countries[co2_data_countries['country'] == country_value]

    # use the utils function to find the data for only the selected countries and years
    df = u.find_all_data_for_year_range(selected_country_df, year_range[0], year_range[1])
    # filter on only selected columns
    df = df[dataset_value]

    columns = []
    for column in df.columns:
        columns.append({"name": str(column), "id": str(column)})
    table = df.to_dict('records')

    # access codebook for full description of selected dataset to be updated under scatter plot
    # dataset_codebook_description = codebook.loc[codebook['column'] == dataset_value]['description'].values[0]
    # dataset_def = f"* {dataset_value}: {dataset_codebook_description}"

    return table, columns, None, None
