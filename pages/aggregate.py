import pandas as pd
import dash
from dash import html, dcc, Input, Output, callback, ctx, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import plotly.express as px
from download_data import co2_data_countries, codebook
import utils as u

# Purpose:
# (i) contributions of individual countries to total emissions in a year or range of years as 100% stacked bar chart
# (ii) contributions of groups of countries to total emissions in a year or range of years as 100% stacked bar chart
# (iii) Aggregate countries into percentiles for a column and year and visualize the summary statistics of another column as box plot
# for now, don't complicate with multipliers. Can add later if needed.

# Graphs needed:
# Graph 1 = stacked bar chart for individual countries in a year range (can be a single year too)
# Graph 2 = same as Graph 1 but with an option to group selected countries into percentiles based on another column
# Graph 3 = box plot with grouped countries by percentile based on another column

# # Selection options:
# - Countries (including select all if all removed)
# - Year range
# - Dataset (only one for now, but maybe more than that for stacked bar as % total)
# - Group countries (y/n)
# - Group by dataset (only one, same year range will apply)


dash.register_page(__name__, order=3)

# Palette:
# #002B36 - dark blue
# #A4C9D7 - light blue
# #D07C2E - orange
# #F1F1E6 - gray

initial_country_selection = co2_data_countries.country.unique()[:10]
initial_year_range = list(range(co2_data_countries['year'].max() - 20, co2_data_countries['year'].max()))

# Build sidebar
agg_sidebar_style = \
    {
        "position": "relative",
        "top": 0,
        "left": 0,
        "bottom": 0,
        "padding": "1rem 1rem",
        # "background-color": "#002b36",
        # "color": "#D07C2E",
    }

agg_sidebar = \
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
                        initial_country_selection,
                        id='agg-country-selector',
                        placeholder='All countries selected',
                        multi=True
                    ),
                    html.P(children="", id='agg-country-error-display',
                           style={'font-weight': 'bold', 'font-style': 'italics'}),
                    html.P(
                        "Dataset", className="lead"
                    ),
                    dcc.Dropdown(
                        co2_data_countries.loc[:, ~co2_data_countries.columns.isin(
                            ['country', 'year', 'iso_code'])].columns,
                        'co2',
                        id='agg-dataset-selector',
                        placeholder='Select a dataset to plot...'
                    ),
                    html.P(children="", style={'font-weight': 'bold', 'font-style': 'italics'},
                           id='agg-dataset-error-display'),
                    html.P(
                        "Grouping", className="lead"
                    ),
                    dbc.ButtonGroup(
                        [
                            dbc.Button("On", active=False, outline=True, color="secondary", id='agg-group-button-on'),
                            dbc.Button("Off", active=True, outline=True, color="secondary", id='agg-group-button-off')
                        ], id='agg-grouping-button-group'
                    ),
                    html.Br(),
                    dbc.ButtonGroup(
                        [
                            dbc.Button("Stacked Bar", active=False, outline=True, color="secondary",
                                       id='agg-stacked-bar-button'),
                            dbc.Button("Box Plot", active=False, outline=True, color="secondary",
                                       id='agg-box-plot-button')
                        ], id='agg-plot-type-button-group'
                    ),
                    html.Br(),
                    dbc.Input(placeholder='Number of groups', id='n-groups-input'),
                    html.Br(),
                    dcc.Dropdown(
                        co2_data_countries.loc[:, ~co2_data_countries.columns.isin(
                            ['country', 'year', 'iso_code'])].columns,
                        id='agg-grouping-selector',
                        placeholder='Select a dataset to group by...',
                    ),
                    html.A("Dataset definitions",
                           href='https://github.com/owid/co2-data/blob/master/owid-co2-codebook.csv',
                           target="_blank"),
                    html.P(id='agg-grouping-error-display'),
                    dbc.Button("Generate Chart", active=False, outline=True, color="secondary",
                               id='agg-generate'),
                ],
                vertical=True,
                pills=True
            ),
        ],
        style=agg_sidebar_style,
        fluid=True
    )

layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            agg_sidebar, style={'margin-left': '-20px', 'margin-right': '-20px'}
                        )
                    ),
                    width=3
                ),
                dbc.Col(
                    [
                        html.H2(style={'textAlign': 'left', 'margin-left': '7px', 'margin-top': '1rem',
                                       'color': '#D07C2E', 'font-weight': 'bold'},
                                children='Aggregate'),
                        html.P(style={'textAlign': 'left', 'margin-left': '7px', 'margin-top': '7px',
                                      'color': '#D07C2E', 'font-style': 'italics'},
                               children=
                               '''
                               Group countries by their characteristics to learn more about their tendencies and 
                               how similarities and differences affect their contributions to climate change.
                               Countries are selected into evenly distributed groups by percentile
                               (e.g., selecting 5 groups will let you analyze countries grouped into quintiles). 
                               '''),
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
                            id='agg-year-slider'
                        ),
                        html.Br(),
                        dcc.Graph(
                            id='agg-plot'
                        ),
                        html.A(id='agg-dataset-explainer'),
                        html.Hr(),
                        html.A(id='agg-grouping-dataset-explainer')
                    ]
                )
            ]
        )
    ],
    fluid=True,
    class_name="g-0"
)


# callback to update button active status
@callback(
    Output('agg-group-button-on', 'active'),
    Output('agg-group-button-off', 'active'),
    Output('agg-stacked-bar-button', 'active'),
    Output('agg-box-plot-button', 'active'),
    Input('agg-group-button-on', 'n_clicks'),
    Input('agg-group-button-off', 'n_clicks'),
    Input('agg-stacked-bar-button', 'n_clicks'),
    Input('agg-box-plot-button', 'n_clicks'),
    State('agg-group-button-on', 'active'),
    State('agg-group-button-off', 'active'),
    State('agg-stacked-bar-button', 'active'),
    State('agg-box-plot-button', 'active'),
    config_prevent_initial_callbacks=True)
def update_agg_button_status(on_clicks, off_clicks, stacked_clicks, box_clicks, on_status, off_status,
                             stacked_status, box_status):
    if ctx.states['agg-group-button-on.active'] and ctx.triggered_id == 'agg-group-button-on':
        raise PreventUpdate
    elif ctx.triggered_id == 'agg-group-button-on':
        return True, False, True, False
    elif ctx.states['agg-group-button-off.active'] and ctx.triggered_id == 'agg-group-button-off':
        raise PreventUpdate
    elif ctx.triggered_id == 'agg-group-button-off':
        return False, True, False, False

    if ctx.states['agg-group-button-on.active'] and ctx.triggered_id == 'agg-stacked-bar-button':
        return True, False, True, False
    elif ctx.states['agg-group-button-on.active'] and ctx.triggered_id == 'agg-box-plot-button':
        return True, False, False, True
    elif not ctx.states['agg-group-button-on.active'] and \
            (ctx.triggered_id == 'agg-stacked-bar-button' or ctx.triggered_id == 'agg-box-plot-button'):
        raise PreventUpdate


# Callback to update aggregate plot with changes to dropdown selections or slider adjustments
@callback(
    Output('agg-plot', 'figure'),
    Output('agg-country-error-display', 'children'),
    Output('agg-dataset-error-display', 'children'),
    Output('agg-grouping-error-display', 'children'),
    Output('agg-dataset-explainer', 'children'),
    Output('agg-grouping-dataset-explainer', 'children'),
    Input('agg-generate', 'n_clicks'),
    State('agg-year-slider', 'value'),
    State('agg-country-selector', 'value'),
    State('agg-dataset-selector', 'value'),
    State('agg-group-button-on', 'active'),
    State('agg-group-button-off', 'active'),
    State('agg-stacked-bar-button', 'active'),
    State('agg-box-plot-button', 'active'),
    State('n-groups-input', 'value'),
    State('agg-grouping-selector', 'value')
)
def update_agg_plot(agg_generate, year_range, country_value, dataset_value, group_on, group_off, stacked_bar_on,
                    box_plot_on, n_groups, grouping_dataset_value):
    # check if no dataset selected, return an error and don't update dashboard
    if not dataset_value:
        return dash.no_update, dash.no_update, html.P(f'Please select a dataset.', style={
            'font-weight': 'bold', 'font-style': 'italics', 'color': '#D07C2E'}), dash.no_update, dash.no_update, \
               dash.no_update

    # access codebook for full description of selected dataset to be updated under scatter plot
    dataset_codebook_description = codebook.loc[codebook['column'] == dataset_value]['description'].values[0]
    dataset_def = f"* {dataset_value}: {dataset_codebook_description}"

    # if no countries selected, all countries are included
    if not country_value:
        selected_country_df = co2_data_countries
        country_value = list(co2_data_countries['country'].unique())
    # check if more than one country has been passed
    elif isinstance(country_value, list):
        # if country-selector value is a list, there is more than one country selected, then .isin() should be used
        selected_country_df = co2_data_countries[co2_data_countries['country'].isin(country_value)]
    else:
        # if it's not a list, only one country is selected, which means we should use boolean comparison to select
        selected_country_df = co2_data_countries[co2_data_countries['country'] == country_value]

    # if grouping is not active, build a normal stacked bar chart
    if group_off:

        # use the utils function to find the dataset for only the selected countries and years
        df = u.find_all_data_for_year_range(selected_country_df, year_range[0], year_range[1])
        aggregated_df = pd.DataFrame(df.groupby('country')[dataset_value].sum())
        aggregated_df['year_range'] = f"{year_range[0]} - {year_range[1]}"

        fig = px.bar(aggregated_df, x='year_range', y=dataset_value, color=aggregated_df.index)
        fig.update_xaxes(
            title_text='Year Range',
            title_standoff=25
        )
        fig.update_yaxes(
            title_text=f"{dataset_value} *",
            title_standoff=25
        )
        fig.update_layout(transition_duration=100)

        return fig, None, None, None, dataset_def, None

    # if grouping is active and stacked bar is selected, create a stacked bar chart based on country groups
    elif group_on and stacked_bar_on:
        # use utils to get grouped df
        if (isinstance(country_value, list) and int(n_groups) > len(country_value)-1) or \
                ((not isinstance(country_value, list)) and int(n_groups) > 1) or (int(n_groups) <= 0):
            return dash.no_update, dash.no_update, dash.no_update, \
                   "Groups must be greater than 0 and fewer than number of countries", dash.no_update, dash.no_update
        else:
            df, grouped_column_name = u.divide_data_into_groups_for_year_range(selected_country_df, year_range[0],
                                                                               year_range[1], grouping_dataset_value,
                                                                               int(n_groups))
            df = pd.DataFrame(df.groupby(grouped_column_name)[dataset_value].sum())
            df['year_range'] = f"{year_range[0]} - {year_range[1]}"

            # use px to plot stacked chart by group
            fig = px.bar(df, x='year_range', y=dataset_value, color=df.index)
            fig.update_xaxes(
                title_text='Year Range',
                title_standoff=25
            )
            fig.update_yaxes(
                title_text=f"{dataset_value} *",
                title_standoff=25
            )
            fig.update_layout(transition_duration=100)

            # access codebook for full description of grouping dataset to be updated under plot
            group_codebook_description = codebook.loc[codebook['column'] ==
                                                      grouping_dataset_value]['description'].values[0]
            grouped_def = f"** {grouping_dataset_value}: {group_codebook_description} " \
                          f"Please note that there may be fewer groups than requested due to data availability."

            return fig, None, None, None, dataset_def, grouped_def

    elif group_on and box_plot_on:
        # use utils to get grouped df
        if (isinstance(country_value, list) and int(n_groups) > len(country_value)-1) or \
                ((not isinstance(country_value, list)) and int(n_groups) > 1) or (int(n_groups) <= 0):
            return dash.no_update, dash.no_update, dash.no_update, \
                   "Groups must be greater than 0 and fewer than number of countries", dash.no_update, dash.no_update
        else:
            try:
                df, grouped_column_name = u.divide_data_into_groups_for_year_range(selected_country_df, year_range[0],
                                                                                   year_range[1], grouping_dataset_value,
                                                                                   int(n_groups))
                df['year_range'] = f"{year_range[0]} - {year_range[1]}"

                # use px to draw box plots for each group
                fig = px.box(df, x=grouped_column_name, y=dataset_value, color=grouped_column_name, notched=False)
                fig.update_xaxes(
                    title_text=grouped_column_name,
                    title_standoff=25,
                    showgrid=True, gridcolor='#1e434a', tickfont=dict(color='#839496'), title_font=dict(color='#839496')
                )
                fig.update_yaxes(
                    title_text=f"{dataset_value} *",
                    title_standoff=25,
                    showgrid=True, gridcolor='#1e434a', tickfont=dict(color='#839496'), title_font=dict(color='#839496')
                )
                fig.update_layout(transition_duration=100, showlegend=False, plot_bgcolor= "#002b36", paper_bgcolor="#1e434a")

            except KeyError:
                raise PreventUpdate

            # access codebook for full description of grouping dataset to be updated under plot
            group_codebook_description = codebook.loc[codebook['column'] ==
                                                      grouping_dataset_value]['description'].values[0]
            grouped_def = f"** {grouping_dataset_value}: {group_codebook_description} " \
                          f"Please note that there may be fewer groups than requested due to data availability."

            return fig, None, None, None, dataset_def, grouped_def

    raise PreventUpdate
