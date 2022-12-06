import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
import dash_bootstrap_templates as dbt


# Palette:
# 002B36 - dark blue
# A4C9D7 - light blue
# D07C2E - orange
# F1F1E6 - gray

app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.SOLAR])

dbt.load_figure_template('SOLAR')

nav_style = \
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

page_nav = html.Div([
    html.H2("Navigation"),
    html.Hr(),
    html.Div([
            html.Div(
                dcc.Link(
                    f"""{page['name']} \n""", href=page["relative_path"]
                ),

            )
            for page in dash.page_registry.values()
        ]),
    ],
    style=nav_style
)

# create layout that allows for multiple pages taken from files in pages directory
app.layout = html.Div([
    # Title
    dbc.Row([
        dbc.Col(),
        dbc.Col(
            html.H1(style={'textAlign': 'center', 'margin-left': '7px', 'margin-top': '7px'},
                    children='Explore the History of Greenhouse Gas Emissions'),
            width=9,
            style={'margin-left': '7px', 'margin-top': '7px'})
    ]),

    # Sidebar and subtitle
    dbc.Row([
        dbc.Col(page_nav),
        dbc.Col(
            html.Div(
                style={'textAlign': 'center'},
                children=
                '''
                Dashboard to explore the greenhouse gas emissions of countries through history. 
                Based on Our World in Data (OWID) data from the owid/co2-data GitHub repository. 
                '''),
            width=9,
            style={'margin-left': '7px', 'margin-top': '7px'}
        )
    ]),

    # home page content
    dbc.Row([
        dbc.Col(),
        dbc.Col(dash.page_container,
                width=9,
                style={'margin-left': '7px', 'margin-top': '7px'}
                )
    ])
])

if __name__ == '__main__':
    app.run_server(debug=True)
