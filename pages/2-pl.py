import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
nyse = pd.read_csv("/Users/glebsokolov/nyse-data/nyse.csv")

dash.register_page(__name__, name='P&L statement')



layout = html.Div(children=[
    html.H1(children='P&L statement'),
    dcc.Dropdown(
        nyse['Ticker Symbol'].unique(),
        'AAPL',
        id='db-dd'),
    html.Br(),
    html.Div(id='db'),
])


@callback(
    Output(component_id='db', component_property='children'),
    Input(component_id='db-dd', component_property='value')
)
def select_ticker(ticker):
    db_df = nyse.query(f'`Ticker Symbol`=="{ticker}"')
    db_df = db_df.fillna(0)

    pd.set_option("display.precision", 3)
    db_df['Gross Profit'] = db_df['Total Revenue'] - db_df['Cost of Goods Sold'] 
    db_df['Operating Profit'] = db_df['Gross Profit'] - db_df['Research and Development'] - db_df['Other Operating Items']
    return  dbc.Card([
        dbc.CardHeader(f'{ticker}'),
        dbc.CardBody([ dbc.Table.from_dataframe(db_df[['Years', 'Gross Profit', 'Operating Profit', ]], striped=True, bordered=True, hover=True)])
   ])