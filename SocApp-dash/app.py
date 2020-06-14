# Import required libraries
import pickle
import copy
import pathlib
import dash
import math
import datetime as dt
#import pandas as pd
import modin.pandas as pd
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_core_components as dcc
import dash_html_components as html
from plotly.subplots import make_subplots

#from plotly.offline import plot
import plotly.graph_objs as go
from plotly import tools

import random
# Multi-dropdown options
from controls import COUNTIES, STATUSES, WELL_TYPES, COLORS

# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server

# Create controls
county_options = [
    {"label": str(COUNTIES[county]), "value": str(county)} for county in COUNTIES
]

well_status_options = [
    {"label": str(STATUSES[well_status]), "value": str(well_status)}
    for well_status in STATUSES
]

well_type_options = [
    {"label": str(WELL_TYPES[well_type]), "value": str(well_type)}
    for well_type in WELL_TYPES
]


# Load data

# Load data
df_soc = pd.read_excel('data/Continual monitoring data both areas-small.xlsx' , header=0, parse_dates=[0], index_col=0)#, squeeze=True
#df.index = pd.to_datetime(df['Date'])
x_col = 'Date (MM/DD/YYYY).1'

def get_options_dic():
    numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
    newdf = df_soc.select_dtypes(include=numerics)
    option_list = []
    for col in newdf.columns:
        option_list.append({'label': col, 'value': col})
    return option_list  

def get_options_list():
    numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
    newdf = df_soc.select_dtypes(include=numerics)
    option_list = []
    for col in newdf.columns:
        option_list.append( col)
    return option_list  

def get_datetime_col():
    datetime = ['datetime64']
    newdf = df_soc.select_dtypes(include=datetime)
    option_list = []
    for col in newdf.columns:
        option_list.append( col)
    return option_list  

numerical_col = ['Battery V',   'Temp °C', 'Cond µS/cm', 'SpCond µS/cm', 'Sal psu', 'nLF Cond µS/cm', 
                    'ODO % sat', 'ODO mg/L', 'Turbidity FNU', 'TSS mg/L', 'pH', 'pH mV', 'ORP mV', 'ORP raw mV', 'Press psi a', 'Depth m']

numerical_cols_high_range = ['Cond µS/cm', 'SpCond µS/cm', 'nLF Cond µS/cm']

def get_options_high_range_dic():
    option_list = []
    for col in numerical_cols_high_range:
        option_list.append({'label': col, 'value': col})
    return option_list  


numerical_cols_low_range = ['Battery V',   'Temp °C', 'Sal psu', 
                    'ODO % sat', 'ODO mg/L', 'Turbidity FNU', 'TSS mg/L', 'pH', 'pH mV', 'ORP mV', 'ORP raw mV', 'Press psi a', 'Depth m']

def get_options_low_range_dic():
    option_list = []
    for col in numerical_cols_low_range:
        option_list.append({'label': col, 'value': col})
    return option_list




# Create global chart template
mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNrOWJqb2F4djBnMjEzbG50amg0dnJieG4ifQ.Zme1-Uzoi75IaFbieBDl3A"

layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h"),
    title="Satellite Overview",
    mapbox=dict(
        accesstoken=mapbox_access_token,
        style="light",
        center=dict(lon=-78.05, lat=42.54),
        zoom=7,
    ),
)

# Create app layout
app.layout = html.Div(
    [
    #main body


            dcc.Tabs(
                id="tabs-with-classes",
                value='tab-1',
                parent_className='custom-tabs',
                className='custom-tabs-container',
                children = [  # tabs
                dcc.Tab(label='Moniroting',
                        value='tab-1',
                        className='custom-tab',
                        selected_className='custom-tab--selected', 
                        children=[


                    dcc.Store(id="aggregate_data"),
                    # empty Div to trigger javascript file for graph resizing
                    html.Div(id="output-clientside"),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Img(
                                        src=app.get_asset_url("socorro.png"),
                                        id="plotly-image",
                                        style={
                                            "height": "60px",
                                            "width": "auto",
                                            "margin-bottom": "25px",
                                        },
                                    )
                                ],
                                className="one-third column",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.H3(
                                                "SOCORRO",
                                                style={"margin-bottom": "0px"},
                                            ),
                                            html.H5(
                                                "Seeking out corrosion, before it is too late.", style={"margin-top": "0px"}
                                            ),
                                        ]
                                    )
                                ],
                                className="one-half column",
                                id="title",
                            ),
                            html.Div(
                                [
                                    html.A(
                                        html.Button("SOCORRO Home", id="learn-more-button"),
                                        href="https://www.socorro.eu/",
                                    )
                                ],
                                className="one-third column",
                                id="button",
                            ),
                        ],
                        id="header",
                        className="row flex-display",
                        style={"margin-bottom": "25px"},
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.P(
                                        "Filter by construction date (or select range in histogram):",
                                        className="control_label",
                                    ),
                                    dcc.RangeSlider(
                                        id="year_slider",
                                        min=2012,
                                        max=2020,
                                        step=None,
                                        marks={
                                            2012: {'label': '2012', 'style': {'color': '#77b0b1'}},
                                            2014: '2014',
                                            2016: '2016',
                                            2018: '2018',
                                            2020: {'label': '2020', 'style': {'color': '#f50'}}
                                        },
                                        value=[2012, 2014],
                                        className="dcc_control",





                                    ),
                                    html.P("Choose y-axis:", className="control_label"),
                                    # dcc.RadioItems(
                                    #     id="well_status_selector",
                                    #     options=[
                                    #         {"label": "All ", "value": "all"},
                                    #         {"label": "Active only ", "value": "active"},
                                    #         {"label": "Customize ", "value": "custom"},
                                    #     ],
                                    #     value="active",
                                    #     labelStyle={"display": "inline-block"},
                                    #     className="dcc_control",
                                    # ),
                                    dcc.Dropdown(
                                        id="xaxis-column",
                                        options=get_options_dic(),
                                        #multi=True,
                                        value= get_datetime_col()[0],#list(STATUSES.keys()),
                                        className="dcc_control",
                                    ),
                                    dcc.Dropdown(
                                        id="yaxis-column",
                                        options=get_options_dic(),
                                        #multi=True,
                                        value='Temp °C', #get_datetime_col()[0],#list(STATUSES.keys()),
                                        className="dcc_control",
                                    ),
                                    # dcc.Checklist(
                                    #     id="lock_selector",
                                    #     options=[{"label": "Lock camera", "value": "locked"}],
                                    #     className="dcc_control",
                                    #     value=[],
                                    # ),
                                    # html.P("Filter by well type:", className="control_label"),
                                    # dcc.RadioItems(
                                    #     id="well_type_selector",
                                    #     options=[
                                    #         {"label": "All ", "value": "all"},
                                    #         {"label": "Productive only ", "value": "productive"},
                                    #         {"label": "Customize ", "value": "custom"},
                                    #     ],
                                    #     value="productive",
                                    #     labelStyle={"display": "inline-block"},
                                    #     className="dcc_control",
                                    # ),
                                    # dcc.Dropdown(
                                    #     id="well_types",
                                    #     options=well_type_options,
                                    #     multi=True,
                                    #     value=list(WELL_TYPES.keys()),
                                    #     className="dcc_control",
                                    # ),
                                ],
                                className="pretty_container four columns",
                                id="cross-filter-options",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            # html.Div(
                                            #     [html.H6(id="well_text"), html.P("No. of Wells")],
                                            #     id="wells",
                                            #     className="mini_container",
                                            # ),
                                            # html.Div(
                                            #     [html.H6(id="gasText"), html.P("Gas")],
                                            #     id="gas",
                                            #     className="mini_container",
                                            # ),
                                            # html.Div(
                                            #     [html.H6(id="oilText"), html.P("Oil")],
                                            #     id="oil",
                                            #     className="mini_container",
                                            # ),
                                            # html.Div(
                                            #     [html.H6(id="waterText"), html.P("Water")],
                                            #     id="water",
                                            #     className="mini_container",
                                            # ),
                                        ],
                                        id="info-container",
                                        className="row container-display",
                                    ),
                                    html.Div(
                                        [dcc.Graph(id="count_graph"
                                        

                                            )],
                                        id="countGraphContainer",
                                        className="pretty_container",
                                    ),
                                ],
                                id="right-column",
                                className="eight columns",
                            ),
                        ],
                        className="row flex-display",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                        dcc.Dropdown(
                                        id="yaxis-column-high",
                                        options=get_options_high_range_dic(),
                                        multi=True,
                                        value=numerical_cols_high_range,
                                        className="dcc_control",
                                    ),
                                    dcc.Graph(id="high_range_graph"),
                                
                                dcc.Dropdown(
                                        id="yaxis-column-low",
                                        options=get_options_low_range_dic(),
                                        multi=True,
                                        value=numerical_cols_low_range,
                                        className="dcc_control",
                                    ),
                                dcc.Graph(id="low_range_graph")
                                ],
                                className="pretty_container twelve columns",
                            ),
                        ],
                        className="row flex-display",
                    ),
                    # html.Div(
                    #     [
                    #         html.Div(
                    #             [dcc.Graph(id="pie_graph")],
                    #             className="pretty_container seven columns",
                    #         ),
                    #         html.Div(
                    #             [dcc.Graph(id="aggregate_graph")],
                    #             className="pretty_container five columns",
                    #         ),
                    #     ],
                    #     className="row flex-display",
                    # ),




                ]),
                dcc.Tab(label='Analysis',
                        value='tab-2',
                        className='custom-tab',
                        selected_className='custom-tab--selected', 
                        children=[
                        html.Div(
                                        [
                                            html.H3(
                                                "Comming soon",
                                                style={"margin-bottom": "0px"},
                                            ),
                                            html.H5(
                                                "functionalities to be added", style={"margin-top": "0px"}
                                            ),
                                        ]
                                    )
                    # dcc.Graph(
                    #     figure={
                    #         'data': [
                    #             {'x': [1, 2, 3], 'y': [1, 4, 1],
                    #                 'type': 'bar', 'name': 'SF'},
                    #             {'x': [1, 2, 3], 'y': [1, 2, 3],
                    #              'type': 'bar', 'name': u'Montréal'},
                    #         ]
                    #     }
                    # )
                ]),
                dcc.Tab(label='About SOCORRO',
                        value='tab-3',
                        className='custom-tab',
                        selected_className='custom-tab--selected', 
                        children=[
                        html.Div(
                                        [
                                            html.H3(
                                                "Comming soon",
                                                style={"margin-bottom": "0px"},
                                            ),
                                            html.H5(
                                                "functionalities to be added", style={"margin-top": "0px"}
                                            ),
                                        ]
                                    )
                    # dcc.Graph(
                    #     figure={
                    #         'data': [
                    #             {'x': [1, 2, 3], 'y': [2, 4, 3],
                    #                 'type': 'bar', 'name': 'SF'},
                    #             {'x': [1, 2, 3], 'y': [5, 4, 3],
                    #              'type': 'bar', 'name': u'Montréal'},
                    #         ]
                    #     }
                    # )
                ]),
            ])#end of tabs




    ], #end of main body

    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
)


# # Helper functions
# def human_format(num):
#     if num == 0:
#         return "0"

#     magnitude = int(math.log(num, 1000))
#     mantissa = str(int(num / (1000 ** magnitude)))
#     return mantissa + ["", "K", "M", "G", "T", "P"][magnitude]


def filter_dataframe(df, year_slider):


    dff = df[
         (df[get_datetime_col()[0]] > dt.datetime(year_slider[0], 1, 1))
        & (df[get_datetime_col()[0]] < dt.datetime(year_slider[1], 1, 1))
    ]
    return dff


# def produce_individual(api_well_num):
#     try:
#         points[api_well_num]
#     except:
#         return None, None, None, None

#     index = list(
#         range(min(points[api_well_num].keys()), max(points[api_well_num].keys()) + 1)
#     )
#     gas = []
#     oil = []
#     water = []

#     for year in index:
#         try:
#             gas.append(points[api_well_num][year]["Gas Produced, MCF"])
#         except:
#             gas.append(0)
#         try:
#             oil.append(points[api_well_num][year]["Oil Produced, bbl"])
#         except:
#             oil.append(0)
#         try:
#             water.append(points[api_well_num][year]["Water Produced, bbl"])
#         except:
#             water.append(0)

#     return index, gas, oil, water


# def produce_aggregate(selected, year_slider):

#     index = list(range(max(year_slider[0], 1985), 2016))
#     gas = []
#     oil = []
#     water = []

#     for year in index:
#         count_gas = 0
#         count_oil = 0
#         count_water = 0
#         for api_well_num in selected:
#             try:
#                 count_gas += points[api_well_num][year]["Gas Produced, MCF"]
#             except:
#                 pass
#             try:
#                 count_oil += points[api_well_num][year]["Oil Produced, bbl"]
#             except:
#                 pass
#             try:
#                 count_water += points[api_well_num][year]["Water Produced, bbl"]
#             except:
#                 pass
#         gas.append(count_gas)
#         oil.append(count_oil)
#         water.append(count_water)

#     return index, gas, oil, water


# # Create callbacks
# app.clientside_callback(
#     ClientsideFunction(namespace="clientside", function_name="resize"),
#     Output("output-clientside", "children"),
#     [Input("count_graph", "figure")],
# )


# @app.callback(
#     Output("aggregate_data", "data"),
#     [
#         Input("STATUSES", "value"),
#         Input("well_types", "value"),
#         Input("year_slider", "value"),
#     ],
# )
# def update_production_text(STATUSES, well_types, year_slider):

#     dff = filter_dataframe(df, STATUSES, well_types, year_slider)
#     selected = dff["API_WellNo"].values
#     index, gas, oil, water = produce_aggregate(selected, year_slider)
#     return [human_format(sum(gas)), human_format(sum(oil)), human_format(sum(water))]


# # Radio -> multi
# @app.callback(
#     Output("STATUSES", "value"), [Input("well_status_selector", "value")]
# )
# def display_status(selector):
#     if selector == "all":
#         return list(STATUSES.keys())
#     elif selector == "active":
#         return ["AC"]
#     return []


# # Radio -> multi
# @app.callback(Output("well_types", "value"), [Input("well_type_selector", "value")])
# def display_type(selector):
#     if selector == "all":
#         return list(WELL_TYPES.keys())
#     elif selector == "productive":
#         return ["GD", "GE", "GW", "IG", "IW", "OD", "OE", "OW"]
#     return []


# Slider -> count graph
@app.callback(Output("year_slider", "value"), [Input("count_graph", "selectedData")])
def update_year_slider(count_graph_selected):

    if count_graph_selected is None:
        return [2012, 2016]



# # Selectors -> well text
# @app.callback(
#     Output("well_text", "children"),
#     [
#         Input("STATUSES", "value"),
#         Input("well_types", "value"),
#         Input("year_slider", "value"),
#     ],
# )
# def update_well_text(STATUSES, well_types, year_slider):

#     dff = filter_dataframe(df, STATUSES, well_types, year_slider)
#     return dff.shape[0]


# @app.callback(
#     [
#         Output("gasText", "children"),
#         Output("oilText", "children"),
#         Output("waterText", "children"),
#     ],
#     [Input("aggregate_data", "data")],
# )
# def update_text(data):
#     return data[0] + " mcf", data[1] + " bbl", data[2] + " bbl"


#Selectors -> main graph
@app.callback(
    Output(component_id='count_graph', component_property='figure'),
    [
        Input("xaxis-column", "value"),
        Input("yaxis-column", "value"),
        Input("year_slider", "value"),
    ],
    #[#State("lock_selector", "value"), 
    #State("low_range_graph", "relayoutData")],
)
def make_main_figure(
    x_col,y_col,  year_slider#, selector, low_range_graph_layout
):
    dff =  filter_dataframe(df_soc,  year_slider)


    colors = []
    for i in range(2012, 2020):
        if i >= int(year_slider[0]) and i < int(year_slider[1]):
            colors.append("rgb(123, 199, 255)")
        else:
            colors.append("rgba(123, 199, 255, 0.2)")


    layout_count_graph = copy.deepcopy(layout)



    data = [
        dict(
            type="Scattergl",
            mode="markers",#lines+
            name="Gas Produced (mcf)",
            x=dff[x_col],
            y=dff[y_col],
            line=dict(shape="spline", smoothing=2, width=1, color="#fac1b7"),
            #marker=dict(symbol="diamond-open"),
            #opacity=0,
            hoverinfo="skip",
            marker=dict(color=colors),
        )]

    layout_count_graph["title"] = y_col
    layout_count_graph["dragmode"] = "select"
    layout_count_graph["showlegend"] = False
    layout_count_graph["autosize"] = True
    figure = dict(data=data, layout=layout_count_graph)
    return figure


@app.callback(
    Output(component_id='low_range_graph', component_property='figure'),
    [
        Input("yaxis-column-low", "value"),
        Input("year_slider", "value"),
    ]#,
    #[State("lock_selector", "value"), State("low_range_graph", "relayoutData")],
)
def make_low_range_figure(
    y_col,  year_slider#, selector, low_range_graph_layout
):

    dff =  filter_dataframe(df_soc,  year_slider)

    layout_low_range_graph = copy.deepcopy(layout)
    #'Cond µS/cm', 'SpCond µS/cm', 'nLF Cond µS/cm'
    layout_low_range_graph["title"] = y_col
    layout_low_range_graph["dragmode"] = "select"
    layout_low_range_graph["showlegend"] = True
    layout_low_range_graph["autosize"] = True
 


    n_rows = len(y_col) # make_subplots breaks down if rows > 70

    fig = tools.make_subplots(rows=n_rows, cols=1)
    fig['layout'].update(height=4000, autosize = True, showlegend = True, dragmode = "select", title='Second Class of Parameters')#, title = y_col , width=1000
        

    #print(fig['layout'])

    for i in range(n_rows):
        trace = go.Scattergl(x = dff[get_datetime_col()[0]], y = dff[y_col[i]], 
                            name=y_col[i], 
                            mode="markers",#lines+
                            #line=dict(shape="spline", smoothing=2, width=1, color=(list(COLORS.values()))[i]),
                            marker=dict(symbol="circle"),
                            hoverinfo="skip",)
        fig.append_trace(trace, i+1, 1)
        fig['layout']['yaxis' + str(i+1)].update(title=y_col[i])

    return fig


    data = [ dict(
            type="scatter",
            mode="lines",#lines+
            name=y_col[i],
            x=dff[get_datetime_col()[0]],
            y=dff[y_col[i]],
            line=dict(shape="spline", smoothing=2, width=1, color=(list(COLORS.values()))[i]),
            marker=dict(symbol="diamond-open"),
            #opacity=0,
            hoverinfo="skip",
            #marker=dict(color=colors),
        ) 
            for i in range(len(y_col))]
    layout_low_range_graph["title"] = y_col
    layout_low_range_graph["dragmode"] = "select"
    layout_low_range_graph["showlegend"] = True
    layout_low_range_graph["autosize"] = True
    figure = dict(data=data, layout=layout_low_range_graph)
    return figure


@app.callback(
    Output(component_id='high_range_graph', component_property='figure'),
    [
        Input("yaxis-column-high", "value"),
        Input("year_slider", "value"),
    ]#,
    #[State("lock_selector", "value"), State("low_range_graph", "relayoutData")],
)
def make_low_range_figure(
    y_col,  year_slider#, selector, low_range_graph_layout
):
    dff =  filter_dataframe(df_soc,  year_slider)

    layout_high_range_graph = copy.deepcopy(layout)
    #'Cond µS/cm', 'SpCond µS/cm', 'nLF Cond µS/cm'



    n_rows = len(y_col) # make_subplots breaks down if rows > 70

    fig = tools.make_subplots(rows=n_rows, cols=1)
    fig['layout'].update(height=4000, autosize = True, showlegend = True, dragmode = "select", title='First Class of Parameters')#, title = y_col , width=1000


    #print(fig['layout'])

    for i in range(n_rows):
        trace = go.Scattergl(x = dff[get_datetime_col()[0]], y = dff[y_col[i]], 
                            name=y_col[i], 
                            mode="markers",#lines+
                            #line=dict(shape="spline", smoothing=2, width=1, color=(list(COLORS.values()))[i]),
                            marker=dict(symbol="circle"),
                            hoverinfo="skip",)
        fig.append_trace(trace, i+1, 1)
        fig['layout']['yaxis' + str(i+1)].update(title=y_col[i])

    return fig



    data = [ dict(
            type="scatter",
            mode="lines",#lines+
            name=y_col[i],
            x=dff[get_datetime_col()[0]],
            y=dff[y_col[i]],
            line=dict(shape="spline", smoothing=2, width=1, color=(list(COLORS.values()))[i]),
            marker=dict(symbol="diamond-open"),
            #opacity=0,
            hoverinfo="skip",
            #marker=dict(color=colors),
        ) 
            for i in range(len(y_col))]
    layout_high_range_graph["title"] = y_col
    layout_high_range_graph["dragmode"] = "select"
    layout_high_range_graph["showlegend"] = True
    layout_high_range_graph["autosize"] = True

    # layout_pie["title"] = "Production Summary: {} to {}".format(
    #     year_slider[0], year_slider[1]


    figure = dict(data=data, layout=layout_high_range_graph)
    return figure

# # Main graph -> individual graph
# @app.callback(Output("high_range_graph", "figure"), [Input("low_range_graph", "hoverData")])
# def make_individual_figure(low_range_graph_hover):

#     layout_individual = copy.deepcopy(layout)

#     if low_range_graph_hover is None:
#         low_range_graph_hover = {
#             "points": [
#                 {"curveNumber": 4, "pointNumber": 569, "customdata": 31101173130000}
#             ]
#         }

#     chosen = [point["customdata"] for point in low_range_graph_hover["points"]]
#     index, gas, oil, water = produce_individual(chosen[0])

#     if index is None:
#         annotation = dict(
#             text="No data available",
#             x=0.5,
#             y=0.5,
#             align="center",
#             showarrow=False,
#             xref="paper",
#             yref="paper",
#         )
#         layout_individual["annotations"] = [annotation]
#         data = []
#     else:
#         data = [
#             dict(
#                 type="scatter",
#                 mode="lines+markers",
#                 name="Gas Produced (mcf)",
#                 x=index,
#                 y=gas,
#                 line=dict(shape="spline", smoothing=2, width=1, color="#fac1b7"),
#                 marker=dict(symbol="diamond-open"),
#             ),
#             dict(
#                 type="scatter",
#                 mode="lines+markers",
#                 name="Oil Produced (bbl)",
#                 x=index,
#                 y=oil,
#                 line=dict(shape="spline", smoothing=2, width=1, color="#a9bb95"),
#                 marker=dict(symbol="diamond-open"),
#             ),
#             dict(
#                 type="scatter",
#                 mode="lines+markers",
#                 name="Water Produced (bbl)",
#                 x=index,
#                 y=water,
#                 line=dict(shape="spline", smoothing=2, width=1, color="#92d8d8"),
#                 marker=dict(symbol="diamond-open"),
#             ),
#         ]
#         layout_individual["title"] = dataset[chosen[0]]["Well_Name"]

#     figure = dict(data=data, layout=layout_individual)
#     return figure


# # Selectors, main graph -> aggregate graph
# @app.callback(
#     Output("aggregate_graph", "figure"),
#     [
#         Input("STATUSES", "value"),
#         Input("well_types", "value"),
#         Input("year_slider", "value"),
#         Input("low_range_graph", "hoverData"),
#     ],
# )
# def make_aggregate_figure(STATUSES, well_types, year_slider, low_range_graph_hover):

#     layout_aggregate = copy.deepcopy(layout)

#     if low_range_graph_hover is None:
#         low_range_graph_hover = {
#             "points": [
#                 {"curveNumber": 4, "pointNumber": 569, "customdata": 31101173130000}
#             ]
#         }

#     chosen = [point["customdata"] for point in low_range_graph_hover["points"]]
#     well_type = dataset[chosen[0]]["Well_Type"]
#     dff = filter_dataframe(df, STATUSES, well_types, year_slider)

#     selected = dff[dff["Well_Type"] == well_type]["API_WellNo"].values
#     index, gas, oil, water = produce_aggregate(selected, year_slider)

#     data = [
#         dict(
#             type="scatter",
#             mode="lines",
#             name="Gas Produced (mcf)",
#             x=index,
#             y=gas,
#             line=dict(shape="spline", smoothing="2", color="#F9ADA0"),
#         ),
#         dict(
#             type="scatter",
#             mode="lines",
#             name="Oil Produced (bbl)",
#             x=index,
#             y=oil,
#             line=dict(shape="spline", smoothing="2", color="#849E68"),
#         ),
#         dict(
#             type="scatter",
#             mode="lines",
#             name="Water Produced (bbl)",
#             x=index,
#             y=water,
#             line=dict(shape="spline", smoothing="2", color="#59C3C3"),
#         ),
#     ]
#     layout_aggregate["title"] = "Aggregate: " + WELL_TYPES[well_type]

#     figure = dict(data=data, layout=layout_aggregate)
#     return figure


# # Selectors, main graph -> pie graph
# @app.callback(
#     Output("pie_graph", "figure"),
#     [
#         Input("STATUSES", "value"),
#         Input("well_types", "value"),
#         Input("year_slider", "value"),
#     ],
# )
# def make_pie_figure(STATUSES, well_types, year_slider):

#     layout_pie = copy.deepcopy(layout)

#     dff = filter_dataframe(df, STATUSES, well_types, year_slider)

#     selected = dff["API_WellNo"].values
#     index, gas, oil, water = produce_aggregate(selected, year_slider)

#     aggregate = dff.groupby(["Well_Type"]).count()

#     data = [
#         dict(
#             type="pie",
#             labels=["Gas", "Oil", "Water"],
#             values=[sum(gas), sum(oil), sum(water)],
#             name="Production Breakdown",
#             text=[
#                 "Total Gas Produced (mcf)",
#                 "Total Oil Produced (bbl)",
#                 "Total Water Produced (bbl)",
#             ],
#             hoverinfo="text+value+percent",
#             textinfo="label+percent+name",
#             hole=0.5,
#             marker=dict(colors=["#fac1b7", "#a9bb95", "#92d8d8"]),
#             domain={"x": [0, 0.45], "y": [0.2, 0.8]},
#         ),
#         dict(
#             type="pie",
#             labels=[WELL_TYPES[i] for i in aggregate.index],
#             values=aggregate["API_WellNo"],
#             name="Well Type Breakdown",
#             hoverinfo="label+text+value+percent",
#             textinfo="label+percent+name",
#             hole=0.5,
#             marker=dict(colors=[COLORS[i] for i in aggregate.index]),
#             domain={"x": [0.55, 1], "y": [0.2, 0.8]},
#         ),
#     ]
#     layout_pie["title"] = "Production Summary: {} to {}".format(
#         year_slider[0], year_slider[1]
#     )
#     layout_pie["font"] = dict(color="#777777")
#     layout_pie["legend"] = dict(
#         font=dict(color="#CCCCCC", size="10"), orientation="h", bgcolor="rgba(0,0,0,0)"
#     )

#     figure = dict(data=data, layout=layout_pie)
#     return figure


# # Selectors -> count graph
# @app.callback(
#     Output("count_graph", "figure"),
#     [
#         Input("STATUSES", "value"),
#         Input("well_types", "value"),
#         Input("year_slider", "value"),
#     ],
# )
# def make_count_figure(STATUSES, well_types, year_slider):

#     layout_count = copy.deepcopy(layout)

#     dff = filter_dataframe(df, STATUSES, well_types, [1960, 2017])
#     g = dff[["API_WellNo", "Date_Well_Completed"]]
#     g.index = g["Date_Well_Completed"]
#     g = g.resample("A").count()

#     colors = []
#     for i in range(1960, 2018):
#         if i >= int(year_slider[0]) and i < int(year_slider[1]):
#             colors.append("rgb(123, 199, 255)")
#         else:
#             colors.append("rgba(123, 199, 255, 0.2)")

#     data = [
#         dict(
#             type="scatter",
#             mode="markers",
#             x=g.index,
#             y=g["API_WellNo"] / 2,
#             name="All Wells",
#             opacity=0,
#             hoverinfo="skip",
#         ),
#         dict(
#             type="bar",
#             x=g.index,
#             y=g["API_WellNo"],
#             name="All Wells",
#             marker=dict(color=colors),
#         ),
#     ]

#     layout_count["title"] = "Completed Wells/Year"
#     layout_count["dragmode"] = "select"
#     layout_count["showlegend"] = False
#     layout_count["autosize"] = True

#     figure = dict(data=data, layout=layout_count)
#     return figure





# Main
if __name__ == "__main__":


    app.run_server(debug=True, threaded=True)
