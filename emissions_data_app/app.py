import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
import dash_bootstrap_templates as dbt


# Palette:
# #002B36 - dark blue
# #A4C9D7 - light blue
# #D07C2E - orange
# #F1F1E6 - gray

app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.SOLAR])

dbt.load_figure_template('SOLAR')

navbar_image = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                dbc.Row(
                    [
                        dbc.Col(html.Img(src=navbar_image, height="30px")),
                        dbc.Col(dbc.NavbarBrand("Explore the History of Greenhouse Gas Emissions", class_name="ms-2")),
                    ],
                    align="center",
                    class_name="g-0"
                ),
                href=dash.page_registry['pages.analyze']['path'],
                style={'textDecoration': 'none'}
            ),
            dbc.Nav(
                [
                    dbc.NavItem(dbc.NavLink(f"{page['name']} ", href=page["relative_path"]))
                    for page in dash.page_registry.values()
                ],
                pills=False,
                navbar=True
            )
        ]
    ),
    dark=True,
    color="#D07C2E"
)


# create layout that allows for multiple pages taken from files in pages directory
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(navbar, width=12)
        ]),
    dbc.Row([
        dbc.Col(dash.page_container,
                width=12
                )
        ])
    ])


if __name__ == '__main__':
    app.run_server(debug=True)
