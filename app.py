import dash
import dash_core_components as dcc
import dash_html_components as html

import numpy as np
import pandas as pd
from dash.dependencies import Input, Output

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='BitMEX Orderbook Viewer'),
    html.Div(children='''Shows orderbook, quotes and trades activity over time.''')
])


if __name__ == '__main__':
    app.run_server(debug=True)