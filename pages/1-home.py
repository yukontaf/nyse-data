import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
from styles import *
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
from dash.dash_table import DataTable
import sys

nyse = pd.read_csv("/Users/glebsokolov/nyse-data/nyse.csv")

dash.register_page(__name__, name='Home')

prod = 1

if prod:
    nyse = pd.read_csv("nyse.csv")
else:
    nyse = pd.read_csv("nyse-data/nyse.csv")

nyse["Period Ending"] = nyse["Period Ending"].apply(pd.to_datetime)
nyse["Year"] = nyse["Period Ending"].apply(lambda x: x.year)

nyse["Total Revenue_pct_change"] = nyse.groupby(["Ticker Symbol"])[
    "Total Revenue"
].transform("pct_change")
nyse["Total Revenue_pct_change"] = nyse["Total Revenue_pct_change"].apply(
    lambda x: 100 * x
)
revenue_pct_change = nyse.dropna(subset=["Total Revenue_pct_change"])


def budget():
    t = nyse.groupby(["GICS Sector"])[numerical_sum].sum().reset_index()


def filter_q(col):
    return nyse[[col]][nyse[col] < nyse[col].quantile(0.95)]


def table_temp(cols, table, style_cond=[]):
    table = table[cols]
    columns = [{"name": x, "id": x} for x in table.columns]
    return DataTable(
        style_table={"overflowX": "auto"},
        style_cell={
            "height": "auto",
            "textAlign": "center",
            # all three widths are needed
            # 'minWidth': '15px', 'width': '15px', 'maxWidth': '15px',
            "whiteSpace": "normal",
        },
        columns=columns,
        data=table.to_dict("records"),
        sort_action="native",
        filter_action="native",
        page_size=8,
        page_current=0,
        page_action="native",
        style_cell_conditional=style_cond,
    )


numerical = [
    "Total Revenue",
    "Cost of Goods Sold",
    "Sales, General and Admin.",
    "Research and Development",
    "Other Operating Items",
]
numerical_sum = [i + "_sum" for i in numerical]

total_revenue_hist = ff.create_distplot(
    hist_data=[
        filter_q("Total Revenue").values.reshape(
            -1,
        )
    ],
    group_labels=["Distribution of Total Revenues"],
    bin_size=5,
)
total_revenue_hist.update_layout(template="ggplot2")

scatter_general = px.scatter(
    data_frame=nyse,
    title="Total Sales by Country and Month",
    y="Total Revenue",
    x="Research and Development",
    color="GICS Sector",
    template="ggplot2",
)
heatmap = px.imshow(
    nyse.drop("Unnamed: 0", axis=1).corr(),
    aspect="auto",
    height=600,
    template="ggplot2",
)
heatmap.update_layout(font_size=8)

scatter_matrix = px.scatter_matrix(nyse[numerical], height=600)
scatter_matrix.update_layout(font_size=6, template="ggplot2")
revenue_pct_change_histogram = px.histogram(
    revenue_pct_change,
    x="Total Revenue_pct_change",
    labels={
        "Total " "Revenue_pct_change": "Change " "of total " "revenue (%)"},
)

total_sales = px.bar(
    data_frame=nyse[["GICS Sector", "Cost of Goods Sold", "Years"]]
    .groupby(["GICS Sector", "Years"])
    .agg(total_sales=("Cost of Goods Sold", "sum"))
    .reset_index()
    .rename(columns={"total_sales": "Total Sales"}),
    y="Total Sales",
    x="GICS Sector",
    color="Years",
    barmode="group",
    title="Sum of Total Sales for each Sector, yearly",
    template="ggplot2",
)

counts = (
    nyse.groupby(["GICS Sub Industry"])[["Unnamed: 0"]]
    .count()
    .rename(columns={"Unnamed: 0": "count"})
    .reset_index()
)

d_columns = [{"name": x, "id": x} for x in counts.columns]

count_table_conds = [
    {
        "if": {"column_id": "GICS Sub Industry"},
        "minWidth": "100px",
        "width": "100px",
        "maxWidth": "100px",
        "whiteSpace": "normal",
    },
    {
        "if": {"column_id": "count"},
        "minWidth": "50px",
        "width": "50px",
        "maxWidth": "50px",
        "whiteSpace": "normal",
        "textAlign": "center",
    },
]
pd.set_option("display.precision", 4)
overview_table_conds = [
    {"if": {"column_id": col}, "width": "50px",
        "maxWidth": "50px", "minWidth": "50px"}
    for col in numerical
]

overview = table_temp(
    ["Ticker Symbol", "Year", "GICS Sector", "GICS Sub Industry"] + numerical,
    nyse.drop("Unnamed: 0", axis=1),
    style_cond=[],
)

temp = nyse.drop("Unnamed: 0", axis=1).describe().reset_index().round(3)
summary = table_temp(["index"] + numerical, temp)

d_table = DataTable(
    columns=d_columns,
    data=counts.to_dict("records"),
    sort_action="native",
    filter_action="native",
    page_current=0,
    page_size=10,
    page_action="native",
    style_cell_conditional=count_table_conds,
)
means_by_cat = px.histogram(
    data_frame=nyse.sort_values(by="Total Revenue", ascending=False),
    x="GICS Sector",
    template="ggplot2",
)


# grouped = nyse.drop("Unnamed: 0", axis=1).groupby("GICS Sector")


def selector_sector(x):
    return html.Div(
        dcc.Dropdown(
            nyse["GICS Sector"].unique(),
            "Industrials",
            id=x,
        ),
    )


def selector(x):
    return html.Div(
        dcc.Dropdown(
            [
                "Total Revenue",
                "Cost of Goods Sold",
                "Sales, General and Admin.",
                "Research and Development",
                "Other Operating Items",
            ],
            "Total Revenue",
            id=x,
        ),
        style={"width": "30%"},
    )


def breaks(num):
    return [html.Br()] * num


# @callback(
#     Output("page-content", "children"),
#     [Input("url", "pathname")]
# )
# def render_page_content(pathname):
#     if pathname == '/page-1':
#         return [
#             html.H2('P&L Statement'),
#         ]
#     elif pathname == '/':
#         return [
#             html.H2("Lets have a look at some graphs", className="card-title"),
#             cards
#         ]


def drawFigure(content, header_text):
    return html.Div(
        [
            dbc.Card([dbc.CardHeader(header_text), dbc.CardBody([content])]),
        ]
    ), *breaks(2)


fig1 = html.Div(
    dcc.Graph(figure=scatter_general, id="scatter_general"),
)
fig2 = html.Div(
    dcc.Graph(figure=total_revenue_hist, id="revenue_hist"),
    # style={"display": "inline-block", "width": "80%"},
)
fig4 = html.Div(
    dcc.Graph(figure=total_sales, id="total-sales"),
)

tabs1 = html.Div(
    [
        dbc.Tabs(
            [
                dbc.Tab(label="Overview", tab_id="tab-1"),
                dbc.Tab(label="Summary", tab_id="tab-2"),
            ],
            id="tabs1",
            active_tab="tab-1",
        ),
        html.Div(id="content1"),
    ]
)

tabs2 = html.Div(
    [
        dbc.Tabs(
            [
                dbc.Tab(label="Total Sales", tab_id="tab-3"),
                dbc.Tab(label="Total Revenue", tab_id="tab-4"),
            ],
            id="tabs2",
            active_tab="tab-3",
        ),
        html.Div(id="content2"),
    ]
)

card2a = drawFigure(fig1, "Distribution of Total Sales")

card2b = dbc.Card(
    [
        dbc.CardHeader("Total Revenue Distribution"),
        dbc.CardBody(
            [
                html.P(
                    "Obviously, we are mostly interested in total revenues and total sales and how are they impacted by other variables. So, first, let's see how is this most important value  distributed",
                    className="card-text",
                ),
                fig2,
            ]
        ),
    ],
)
fig3 = html.Div(
    dcc.Graph(id="scatter-graph"),
)


sector_checklist = dbc.RadioItems(
    id="sector-dd",
    options=[
        {"label": sector, "value": num + 1}
        for num, sector in enumerate(nyse["GICS Sector"].unique())
    ],
    label_checked_style={"color": "red"},
    input_checked_style={
        "backgroundColor": "#fa7268",
        "borderColor": "#ea6258",
    },
    value=1,
)

card3 = dbc.Card(
    [
        dbc.CardHeader("Total Revenue Distribution"),
        dbc.CardBody(
            [
                html.P(
                    "Now let's see how does the distribution of total revenue behave when changing an economic sector from one to another based on the amount of research and development expenses, <br> In a dropdown list here you can choose an industrial sector and view scatterplot of a relation between the relation of research and developement amount of a company and its total sales",
                    className="card-text",
                ),
                dbc.Row([dbc.Col(sector_checklist, width=2),
                         dbc.Col(fig3, width=6)]),
                html.Span(
                    "As we can see here, there are industries where the impact of the research and developement amount is obvious (i.e. Industrials) and where it doesn't play any role (Consumer Discretionary)"
                ),
            ]
        ),
    ],
)
card4 = dbc.Card(
    [
        # dbc.CardHeader("Total Revenue Distribution"),
        dbc.CardBody(
            [
                dbc.Row([dbc.Col(fig4)]),
            ]
        ),
    ],
)

card6 = dbc.Card(
    dbc.CardBody(
        [html.Span(
            "Here you can choose a variable and view its distribution, the most important features of the variable are summarized in the upper-right angle of the plot"
        ),
            html.Br(),
            selector("var-dd"),
            dcc.Graph(id="hist", style={"width": "80%"}),
        ]
    )
)

card7 = dbc.Card(
    dbc.CardBody([
        html.Span("Number of tickers by Industry (table is sortable)"),
        dbc.Row([dbc.Col(d_table), dbc.Col(
            dcc.Graph(id="mean-num", figure=means_by_cat)), ])
    ])
)
card8 = dbc.Card(
    dbc.CardBody(
        [
            html.Span(
                "Here you can choose two different sectors and compare their key metrics (revenue, expences, etc.)\
        Note that you can scale the picture removing outliers (top 5 % tickers with max metric value)"
            ),
            *breaks(1),
            html.Span(
                "The Table below contains ticker symbols for outlier values"),
            *breaks(2),
            html.Div(
                dcc.Dropdown(
                    nyse["GICS Sector"].unique(),
                    "Industrials",
                    id="select-sector",
                ), style={"display": "inline-block", "width": "30%"}),
            html.Div(
                dcc.Dropdown(
                    nyse["GICS Sector"].unique(),
                    "Industrials",
                    id="select-sector2",
                ),
                style={"display": "inline-block", "width": "30%"},
            ),
            html.Div(
                dcc.Dropdown(
                    numerical,
                    "Total Revenue",
                    id="select2",
                ),
                style={"display": "inline-block", "width": "30%"},
            ),
            dcc.RadioItems(
                ["with outliers", "without outliers"], "with outliers", id="outliers"
            ),
            html.Div(
                [
                    html.Div(
                        dcc.Graph(id="boxpl"),
                        style={"display": "inline-block", "width": "75%"},
                        className="eight columns",
                    ),
                    html.Div(
                        DataTable(
                            sort_action="native",
                            filter_action="native",
                            page_size=5,
                            page_current=0,
                            page_action="native",
                            id="outliers_table",
                            columns=[
                                {"name": "Total Revenue", "id": "Total Revenue"},
                                {"name": "Ticker Symbol", "id": "Ticker Symbol"},
                            ],
                        ),
                        style={
                            "display": "inline-block",
                            "width": "15%",
                            "margin-top": "100px",
                        },
                        className="four columns",
                    ),
                ],
                className="container",
            ),
        ]

    )
)

card9 = dbc.Card(
    dbc.CardBody([
        html.Span(
            "Let's calculate total sum for all the years present in the table for each ticker (these values will have postfix _sum)\
            and then, let's have a look at the heatmap, depicting correlation table for the numerical variables"
        ),
        html.Div(
            dcc.Graph(figure=heatmap),
            style={"margin-left": "auto",
                   "margin-right": "auto", "width": "80%"},
        ),
        html.Span(
            "Now let's have a look at the scatter matrix for the numerical variables of the dataset"
        ),
        html.Div(
            dcc.Graph(figure=scatter_matrix),
            style={
                "margin-left": "auto",
                "margin-right": "auto",
                "width": "80%",
                "height": "140%",
            },
        ),
    ])
)
card10 = dbc.Card(
    dbc.CardBody([
        html.Span(
            "Now let's build a histogram, depicting the frequencies of change "
            "in total revenue over years"
        ),
        dcc.Graph(figure=revenue_pct_change_histogram, style={"width": "80%"})
    ])
)
layout = html.Div([tabs1, tabs2, card3, *breaks(2), card4,
                  *breaks(2), card6, *breaks(2), card7, *breaks(2), card8, *breaks(2), card9, *breaks(2), card10])


@callback(Output("content1", "children"), [Input("tabs1", "active_tab")])
def switch_tab1(at):
    if at == "tab-1":
        return drawFigure(overview, "NYSE Stock Data")
    elif at == "tab-2":
        return drawFigure(summary, "Statistical Summary")
    return html.P("This shouldn't ever be displayed...")


@callback(Output("content2", "children"), [Input("tabs2", "active_tab")])
def switch_tab2(at):
    if at == "tab-3":
        return card2a
    elif at == "tab-4":
        return card2b
    return html.P("This shouldn't ever be displayed...")

@callback(
    Output(component_id="scatter-graph", component_property="figure"),
    Input(component_id="sector-dd", component_property="value"),
)
def update_plot(selection):
    data = nyse.copy(deep=True)
    sectors = data["GICS Sector"].unique()
    if selection:
        choice = data[data["GICS Sector"] == sectors[selection - 1]]

        return px.scatter(
            data_frame=choice,
            title=f"Total Sales by Country and Month in <br> the {sectors[selection - 1]} sector",
            y="Total Revenue",
            x="Research and Development",
            width=800,
            template="ggplot2",
        )

@callback(
    Output(component_id="hist", component_property="figure"),
    Input(component_id="var-dd", component_property="value"),
)
def update_hist(selection):
    data = nyse.copy(deep=True)
    if selection:
        variable = selection
        choice = data.iloc[filter_q("Total Revenue").index][[variable]]
        summary = choice[variable].describe()
        summary["mode"] = choice[variable].mode()[0]
        # summary["skew"] = stats.skew(choice)
        fig = go.Figure()
        f = data.iloc[filter_q("Total Revenue").index][[variable]].values.reshape(
            -1,
        )
        fig = fig.add_trace(go.Histogram(x=f))
        text = "<br>".join(
            [f"{list(summary.index)[i]}:{round(list(summary)[i], 2)}" for i in range(9)]
        )
        fig.add_annotation(text=text, showarrow=False)
        annotation = {"xref": "paper", "yref": "paper",
                      "x": 1, "y": 1, "align": "left"}
        fig.update_annotations(annotation)
        fig.update_layout(
            title=f"Histogram of Distribution of {selection}",
            xaxis_title=selection,
            yaxis_title="Count",
            template="ggplot2",
        )
        return fig

@callback(
    Output(component_id="boxpl", component_property="figure"),
    Output(component_id="outliers_table", component_property="data"),
    Input(component_id="select-sector", component_property="value"),
    Input(component_id="select-sector2", component_property="value"),
    Input(component_id="outliers", component_property="value"),
    Input(component_id="select2", component_property="value"),
)
def update_means(selection1, selection2, outliers, metric):
    data = nyse.copy(deep=True).rename({"GICS Sector": "GICS_Sector"}, axis=1)
    if selection1 and selection2 and outliers and metric:
        choice = data.query(
            f"GICS_Sector=='{selection1}' or GICS_Sector=='{selection2}'"
        )
        outl = choice[choice[metric] > choice[metric].quantile(0.95)]
        if outliers == "with outliers":
            pass
        else:
            choice = choice[choice[metric] < choice[metric].quantile(0.95)]
        return (
            px.box(
                data_frame=choice,
                title=f"Comparison of {metric} in {selection1} and <br> {selection2} sectors, yearly",
                x="Year",
                y=metric,
                color="GICS_Sector",
                template="ggplot2",
            ),
            outl.to_dict("records"),
        )

