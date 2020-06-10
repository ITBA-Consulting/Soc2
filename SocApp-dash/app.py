import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import pandas as pd
from dash.dependencies import Input, Output
import dash_table
import matplotlib.colors as mcolors
import plotly.express as px
# Load data
df = pd.read_excel('data/Continual monitoring data both areas-small.xlsx', index_col=0, parse_dates=True)
#df.index = pd.to_datetime(df['Date'])

def get_options():
	option_list = []
	for col in df.columns:
		option_list.append({'label': col, 'value': col})
	return option_list	



def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])


def data_selector():
    columns=df.columns
    data_options= [{'label' :k, 'value' :k} for k in columns]
    return dcc.Dropdown(
            id='data_selector',
            options=data_options,
            multi=True,
            #setting a default value, this is not required, but makes development easier.
            value=['Location_X', 'Location_Y'])


colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

# Initialize the app
# external JavaScript files
# external JavaScript files
external_scripts = [
    'https://www.google-analytics.com/analytics.js',
    {'src': 'https://cdn.polyfill.io/v2/polyfill.min.js'},
    {
        'src': 'https://cdnjs.cloudflare.com/ajax/libs/lodash.js/4.17.10/lodash.core.js',
        'integrity': 'sha256-Qqd/EfdABZUcAxjOkMi8eGEivtdTkh3b65xCZL4qAQA=',
        'crossorigin': 'anonymous'
    }
]

# external CSS stylesheets
external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    {
        'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO',
        'crossorigin': 'anonymous'
    }
]

#,external_stylesheets=[dbc.themes.BOOTSTRAP
# app = dash.Dash(__name__,
#                 external_scripts=external_scripts,
#                 external_stylesheets=external_stylesheets)
# EXTERNAL_STYLESHEETS = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__)
#app.config.suppress_callback_exceptions = True
#app.config.suppress_callback_exceptions = True

#app.css.config.serve_locally = False
#app.scripts.config.serve_locally = False

app.layout = html.Div(
    children=[
        html.Div(className='row',
                 children=[
                    html.Div(className='three columns div-user-controls',
                             children=[
                                 html.H2('Socorro Application'),
                                 html.P('Visualization Tool for SOCORRO2'),
                                 html.P('Pick x and y axes to plot.'),
                                 html.Div(
                                     className='div-for-dropdown',
                                     children=[
	                                     dcc.Dropdown(
								                id='xaxis-column',
								                options=get_options(),
								                value='Date (MM/DD/YYYY).1',
                                              style={'backgroundColor': '#1E1E1E'},
                                              className='stockselector'
								            ),
	                   #                   dcc.RadioItems(
								            #     id='xaxis-type',
								            #     options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
								            #     value='Linear',
								            #     labelStyle={'display': 'inline-block'}
								            # ),
	                                     dcc.Dropdown(
							                id='yaxis-column',
							                options=get_options(),
							                value='Temp °C'
							            ),
							            # dcc.RadioItems(
							            #     id='yaxis-type',
							            #     options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
							            #     value='Linear',
							            #     labelStyle={'display': 'inline-block'}
							            # )
                                     ],
                                     style={'color': '#1E1E1E'})
                                ]
                             ),
                    html.Div(className='eight columns div-for-charts bg-grey',
                             children=[
                         		dcc.Graph(id='indicator-graphic')#, config={'displayModeBar': False}, animate=True
                             ])
                              ])
        ]

)

@app.callback(
        Output(component_id='indicator-graphic', component_property='figure'),
        [Input(component_id='xaxis-column', component_property='value'), 
        Input(component_id='yaxis-column', component_property='value')])
def scatter_plot(x_col, y_col):
    trace = go.Scatter(
            x = df[x_col],
            y = df[y_col],
            mode = 'markers'
            )
    
    layout = go.Layout(
            #title = 'Scatter plot',
            xaxis = dict(title = x_col.upper()),
            yaxis = dict(title = y_col.upper()),
            colorway=["#5E0DAC", '#FF4F00', '#375CB1', '#FF7400', '#FFF400', '#FF0056'],
	        template='plotly_dark',
			paper_bgcolor='rgba(0, 0, 0, 0)',
			plot_bgcolor='rgba(0, 0, 0, 0)',
			margin={'b': 15},
			hovermode='x',
			autosize=True,
			title={'text': y_col, 'font': {'color': 'white'}, 'x': 0.5}#,
            #xaxis={'range': [df[x_col].index.min(), df[y_col].index.max()]}
            )
    
    output_plot = go.Figure(
            data = [trace],
            layout = layout
            )
    
    return output_plot
 


if __name__ == '__main__':
    app.run_server(debug=True)