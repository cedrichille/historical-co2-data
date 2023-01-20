import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, order=5)

about_sidebar_style = \
    {
        "position": "relative",
        "top": 0,
        "left": 0,
        "bottom": 0,
        "padding": "1rem 1rem",
        # "background-color": "#002b36",
        # "color": "#D07C2E",
    }

about_sidebar = \
    dbc.Container(
        [
            html.P("Other Interesting Links", className="lead"),
            html.Hr(),
            dbc.Nav(
                [
                    html.A("Our World in Data",
                           href='https://ourworldindata.org/',
                           target="_blank"),
                    html.Br(),
                    html.A("OWID CO2-Data GitHub",
                           href='https://github.com/owid/co2-data',
                           target="_blank"),
                    html.Br(),
                    html.A("EU EDGAR",
                           href='https://edgar.jrc.ec.europa.eu/',
                           target="_blank"),
                    html.Br(),
                    html.A("IEA Data",
                           href='https://www.iea.org/data-and-statistics',
                           target="_blank"),
                    html.Br()
                ],
                vertical=True,
                pills=True
            ),
        ],
        style=about_sidebar_style,
        fluid=True
    )


layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            about_sidebar, style={'margin-left': '-20px', 'margin-right': '-20px'}
                        )
                    ),
                    width=3
                ),
                dbc.Col(
                    [
                        html.H2(
                            style={'textAlign': 'left', 'margin-left': '7px', 'margin-top': '1rem', 'color': '#D07C2E',
                                   'font-weight': 'bold'},
                            children='About'),
                        html.P(
                            style={'textAlign': 'left', 'margin-left': '7px', 'margin-top': '7px', 'color': '#D07C2E',
                                   'font-style': 'italics'},
                            children=
                            '''
                            This app was developed in 2022-2023 to enable improve our understanding of complex datasets
                            related to global greenhouse gas (GHG) emissions. 
                            '''
                        ),
                        html.Hr(),
                        html.A(
                            '''
                           Based on the Our World in Data (OWID) CO2 database, this app uncovers new insights 
                           about how countries have contributed to climate change and what kind of characteristics
                           can help understand trends in GHG emissions.
                            '''),
                        html.Br(),
                        html.Br(),
                        html.A("The app was developed by "),
                        html.A("Cedric Hille. ",
                               href='https://www.linkedin.com/in/cedric-hille-613166b9/',
                               target="_blank"),
                        html.A("The code is available on GitHub at "),
                        html.A("historical-co2-data.",
                               href='https://github.com/cedrichille/historical-co2-data',
                               target="_blank"),
                        html.Br(),
                        html.Br(),
                        html.A("Your feedback is welcome on GitHub or via LinkedIn.")
                    ],
                    width=9
                )
            ]
        )
    ],
    fluid=True,
    class_name="g-0"
)



