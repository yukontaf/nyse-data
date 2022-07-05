from styles import *
import dash
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash.dash_table import DataTable

import dash_bootstrap_components as dbc
import sys

pd.set_option("display.precision", 3)

sys.path.append("/Users/glebsokolov/stockPlot")

stylesheet1 = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(external_stylesheets=[
                stylesheet1, dbc.themes.ZEPHYR], use_pages=True)
server = app.server

sidebar = html.Div(
    [
        html.H2("Sidebar"),
        html.Hr(),
        html.Div(
        dbc.Nav(
            [
                dbc.NavLink(
                    [
                        html.Div(page["name"], className="ms-2"),
                    ],
                    href=page["path"],
                    active="exact",
                )
                for page in dash.page_registry.values()
            ],
            vertical=True,
            pills=True,
            className="bg-light",
        )
    ),
        html.Hr(),
    ],
    style=SIDEBAR_STYLE,
)


content = html.Div(
    dash.page_container,

    style=CONTENT_STYLE,
)
app.layout = html.Div(
    children=[
        dcc.Location(id='url'),
        sidebar,
        content,
    ],
)



if __name__ == "__main__":
    app.run_server(debug=True, use_reloader=True)
