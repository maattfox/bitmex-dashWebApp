import dash
import dash_core_components as dcc
import dash_html_components as html

import numpy as np
import pandas as pd
from dash.dependencies import Input, Output

import pymongo


# CONFIG ---------------------------------------------------------------------------------------

NUMBER_OF_QUOTES = 1000


# Databases ------------------------------------------------------------------------------------

# TODO: try catch database handling
client = pymongo.MongoClient()
database = client.bitmexOrderBook

quotesCollection = database.quotes
tradesCollection = database.trades

obUpdatesCollection = database.ob_update



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
        interval=2 * 1000,  # in milliseconds
        n_intervals=0
    )
])



# CALLBACKS ------------------------------------------------------------------------------------

# Update Quotes
@app.callback(Output('live-update-quotes-graph', 'figure'), [Input('interval-component', 'n_intervals')])
def update_graph_live(n):

    # Collect quotes

    quotesData = quotesCollection.find().skip(quotesCollection.count() - NUMBER_OF_QUOTES)
    quotesDF = pd.DataFrame(quotesData)


    ylim = [quotesDF.tail(1).bidPrice.values[0] - 20, quotesDF.tail(1).askPrice.values[0] + 20 ]


    # Collect trades
    tradesData = tradesCollection.find({"timestamp": {"$gt": quotesDF.head(1).timestamp.values[0] }})
    tradesDF = pd.DataFrame(tradesData)

    sellTrades = tradesDF[tradesDF['side'] == "Sell"]
    buyTrades = tradesDF[tradesDF['side'] == "Buy"]


    # Orderbook Updates

    obUpdatesData = obUpdatesCollection.find({"timestamp": {"$gt": quotesDF.head(1).timestamp.values[0]}, "price": {"$lt": ylim[1], "$gt": ylim[0]}})
    obUpdatesDF = pd.DataFrame(obUpdatesData)



    # Chart options




    # Create the graph with subplots
    figure ={
            "data": [
                {
                    "x": obUpdatesDF["timestamp"],
                    "y": obUpdatesDF["price"],
                    "name": "Orderbook Updates",
                    "mode": "markers",
                    "text": obUpdatesDF['size'],
                    "marker":
                        { "color": obUpdatesDF['size'],
                            "size": 5,
                            "colorscale": 'Jet',
                            "cmin" : 0,
                            "cmax": 1000000
                        }
                },
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
                },
                {
                    "x": sellTrades["timestamp"],
                    "y": sellTrades["price"],
                    "name": "Sell Trades",
                    "mode": "markers",
                    "marker_color": sellTrades['size'],
                    "text": sellTrades['size']
                },
                {
                    "x": buyTrades["timestamp"],
                    "y": buyTrades["price"],
                    "name": "Buy Trades",
                    "mode": "markers",
                    "marker_color": sellTrades['size'],
                    "text": sellTrades['size']
                }
            ],

            "layout": {
                "showlegend": True,

                "xaxis": {
                    "automargin": True,
                    "title": {"text": "Timestamp"},
                    "linecolor": 'white',
                    "showgrid": False

                },
                "yaxis": {
                    "automargin": True,
                    "title": {"text": "Price"},
                    "range": ylim,
                    "linecolor": 'white',
                    "dtick": 1,
                    "showgrid": True
                    },
                "height": 800,
                "margin": {"t": 10, "l": 10, "r": 10},
                "plot_bgcolor": "rgb(0, 0, 0)",
                "autosize": True
            }
        }


    return figure

# Update Trades


# START ------------------------------------------------------------------------------------

if __name__ == '__main__':
    app.run_server(debug=True)