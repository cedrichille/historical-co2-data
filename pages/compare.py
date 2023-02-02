import dash
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
from download_data import co2_data_countries, codebook
import utils as u

dash.register_page(__name__, order=2)

# Palette:
# #002B36 - dark blue
# #A4C9D7 - light blue
# #D07C2E - orange
# #F1F1E6 - gray

# Build sidebar
compare_sidebar_style = \
    {
        "position": "relative",
        "top": 0,
        "left": 0,
        "bottom": 0,
        "padding": "1rem 1rem",
        #"background-color": "#002b36",
        #"color": "#D07C2E",
    }

compare_sidebar = \
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
                        id='compare-country-selector',
                        placeholder='Select one or more countries...',
                        multi=True
                    ),
                    html.P(children="", id='compare-country-error-display',
                           style={'font-weight': 'bold', 'font-style': 'italics'}),
                    html.P(
                        "Dataset", className="lead"
                    ),
                    dcc.Dropdown(
                        co2_data_countries.loc[:, ~co2_data_countries.columns.isin(
                            ['country', 'year', 'iso_code'])].columns,
                        'co2',
                        id='compare-dataset-selector',
                        placeholder='Select a dataset to plot...'
                    ),
                    html.P(children="", style={'font-weight': 'bold', 'font-style': 'italics'},
                           id='compare-dataset-error-display'),
                    html.A("Dataset definitions",
                           href='https://github.com/owid/co2-data/blob/master/owid-co2-codebook.csv',
                           target="_blank")
                ],
                vertical=True,
                pills=True
            ),
        ],
        style=compare_sidebar_style,
        fluid=True
    )

layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            compare_sidebar, style={'margin-left': '-20px', 'margin-right': '-20px'}
                            )
                        ),
                    width=3
                ),
                dbc.Col(
                    [
                        html.H2(style={'textAlign': 'left', 'margin-left': '7px', 'margin-top': '1rem',
                                       'color': '#D07C2E', 'font-weight': 'bold'},
                                children='Compare'),
                        html.P(style={'textAlign': 'left', 'margin-left': '7px', 'margin-top': '7px',
                                      'color': '#D07C2E', 'font-style': 'italics'},
                               children=
                               '''
                               Compare countries' GHG emission trajectories over time
                               '''),
                        html.Hr(),
                        dcc.Graph(
                            id='compare-timeseries-plot',
                        ),
                        dcc.RangeSlider(
                            co2_data_countries['year'].min(),
                            co2_data_countries['year'].max(),
                            step=None,
                            value=[co2_data_countries['year'].max() - 20, co2_data_countries['year'].max()],
                            marks={str(year): str(year) for year in co2_data_countries['year'].unique()
                                   if year % 10 == 0},
                            allowCross=True,
                            included=True,
                            id='compare-year-slider'
                        ),
                        html.A(id='compare-dataset-explainer')
                    ]
                )
            ]
        )
    ],
    fluid=True,
    class_name="g-0"
)


@callback(
    Output('compare-timeseries-plot', 'figure'),
    Output('compare-country-error-display', 'children'),
    Output('compare-dataset-error-display', 'children'),
    Output('compare-dataset-explainer', 'children'),
    Input('compare-year-slider', 'value'),
    Input('compare-country-selector', 'value'),
    Input('compare-dataset-selector', 'value'))
def update_timeseries_plot(year_range, country_value, dataset_value):
    # check if more than one country has been passed
    if isinstance(country_value, list):
        # if country-selector value is a list, there is more than one country selected, then .isin() should be used
        selected_country_df = co2_data_countries[co2_data_countries['country'].isin(country_value)]
    else:
        # if it's not a list, only one country is selected, which means we should use boolean comparison to select
        selected_country_df = co2_data_countries[co2_data_countries['country'] == country_value]

    # check if no countries provided, return an error and don't update dashboard
    if not country_value:
        return dash.no_update, html.P(f'Please select one or more countries.', style={
            'font-weight': 'bold', 'font-style': 'italics', 'color': '#D07C2E'}), dash.no_update, dash.no_update

    # check if no dataset selected, return an error and don't update dashboard
    if not dataset_value:
        return dash.no_update, dash.no_update, html.P(f'Please select a dataset.', style={
            'font-weight': 'bold', 'font-style': 'italics', 'color': '#D07C2E'}), dash.no_update

    # use the utils function to find the dataset for only the selected countries and years
    df = u.find_country_range_data(selected_country_df, dataset_value, country_value, year_range[0], year_range[1])

    # define the parameters of the line plot and update the data
    fig = px.line(df, x='year', y=df.columns)
    
    fig.update_xaxes(
        title_text='Year',
        title_standoff=25,
        showgrid=True, gridcolor='#1e434a', tickfont=dict(color='#839496'), title_font=dict(color='#839496')
    )
    fig.update_yaxes(
        title_text=f"{dataset_value} *",
        title_standoff=25,
        showgrid=True, gridcolor='#1e434a', tickfont=dict(color='#839496'), title_font=dict(color='#839496')
    )
    fig.update_layout(transition_duration=100, plot_bgcolor= "#002b36", paper_bgcolor="#1e434a")

    # access codebook for full description of selected dataset to be updated under scatter plot
    dataset_codebook_description = codebook.loc[codebook['column'] == dataset_value]['description'].values[0]
    dataset_def = f"* {dataset_value}: {dataset_codebook_description}"

    return fig, None, None, dataset_def

