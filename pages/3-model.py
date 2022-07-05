import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
from styles import *
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
from dash.dash_table import DataTable
from scipy.stats import linregress
import numpy as np


dash.register_page(__name__, name='Prediction Model')

nyse = pd.read_csv("/Users/glebsokolov/nyse-data/nyse.csv")
nyse['Gross Profit'] = nyse['Total Revenue'] - nyse['Cost of Goods Sold'] 
nyse['Operating Profit'] = nyse['Gross Profit'] - nyse['Research and Development'] - nyse['Other Operating Items']
nyse['Years'] = nyse['Years'].apply(lambda x:int(x[-1]))


layout = html.Div(children=[
    html.H1(children='Prediction Model'),
    dcc.Dropdown(
        nyse['Ticker Symbol'].unique(),
        'AAPL',
        id='mdd'),
    html.Br(),
    html.Div(id='m'),
])


@callback(
    Output(component_id='m', component_property='children'),
    Input(component_id='mdd', component_property='value')
)
def select_ticker(ticker):
    m_df = nyse.query(f'`Ticker Symbol`=="{ticker}"')
    m_df = m_df.fillna(0)
    x, y = m_df['Years'], m_df['Gross Profit']
    b1, b0, r_value, p_value, std_err = linregress(x, y)
    yhat = b0 + b1 * x
    sum_errs = np.sum((y - yhat)**2)
    stdev = np.sqrt(1/(len(y)-2) * sum_errs)
    interval = 1.96 * stdev
    yhat = b0 + b1 * np.array([5, 6])
    pd.options.display.float_format = '${:,.2f}'.format
    df = pd.DataFrame([yhat-interval, yhat, yhat+interval], columns=['Year', 'Year 6'], index=['Weak Case', 'Base Case', 'Best Case']).reset_index()
    df['Year 5'] = df['Year 5'].map('{:.2f}'.format)
    df['Year 6'] = df['Year 6'].map('{:.2f}'.format)
    pred = dbc.Table.from_dataframe(df)


    return  dbc.Card([
        dbc.CardHeader(f'{ticker}'),
        dbc.CardBody([
            pred, 
	        dcc.Graph(figure = px.scatter(
	        		    data_frame=m_df,
	        		    y="Gross Profit",
	        		    x="Years",
	        		    trendline='ols',
	        		    template="ggplot2",), 
)])
   ])