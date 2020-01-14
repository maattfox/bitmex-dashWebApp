import dash
import dash_core_components as dcc
import dash_html_components as html

import numpy as np
import pandas as pd
from dash.dependencies import Input, Output

import pymongo


# CONFIG ---------------------------------------------------------------------------------------

NUMBER_OF_QUOTES = 10000


# Databases ------------------------------------------------------------------------------------

# TODO: try catch database handling
client = pymongo.MongoClient()
database = client.bitmexOrderBook

quotesCollection = database.quotes
tradesCollection = database.trades



# APP SETUP ------------------------------------------------------------------------------------

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)



# APP LAYOUT ------------------------------------------------------------------------------------

app.layout = html.Div(children=[
    html.H1(children='BitMEX Orderbook Viewer'),
    html.Div(children='''Shows orderbook, quotes and trades activity over time.'''),

    dcc.Graph(id='live-update-quotes-graph'),
    dcc.Interval(
        id='interval-component',
        interval=10 * 1000,  # in milliseconds
        n_intervals=0
    )
])



# CALLBACKS ------------------------------------------------------------------------------------

# Update Quotes
@app.callback(Output('live-update-quotes-graph', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_graph_live(n):

    # Collect some data
    quotesData = quotesCollection.find().skip(quotesCollection.count() - NUMBER_OF_QUOTES)
    #quotesData = quotesCollection.find()
    quotesDF = pd.DataFrame(quotesData)

    # Create the graph with subplots
    figure ={
            "data": [
                {
                    "x": quotesDF["timestamp"],
                    "y": quotesDF["bidPrice"],
                    "name" : "Bid Price",
                    "type": "line",
                    "marker": {"color": "#00ff00"},
                },
                {
                    "x": quotesDF["timestamp"],
                    "y": quotesDF["askPrice"],
                    "name" : "Ask Price",
                    "type": "line",
                    "marker": {"color": "#ff0000"},
                }
            ],

            "layout": {
                "showlegend": True,

                "xaxis": {
                    "automargin": True,
                    "title": {"text": "Timestamp"}
                },
                "yaxis": {
                    "automargin": True,
                    "title": {"text": "Price"}
                    },
                "height": 250,
                "margin": {"t": 10, "l": 10, "r": 10}
            }
        }


    return figure

# Update Trades


# START ------------------------------------------------------------------------------------

if __name__ == '__main__':
    app.run_server(debug=True)