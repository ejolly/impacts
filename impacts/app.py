"""
Main app file
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from seaborn import color_palette
from dataio import load_scimagojr

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Load data into memory from disk
df = load_scimagojr()

# Set the different plotting dimensions
available_indicators = df['Dimension'].unique()
# Set the different colors/fields
fields = df['Field'].unique()

# Create the main page layout
app.layout = html.Div([
    html.Div([

        html.Div([
            dcc.Dropdown(
                id='xaxis-column',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value='Cites / Doc. (2years)'
            ),
            dcc.RadioItems(
                id='xaxis-type',
                options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                value='Linear',
                labelStyle={'display': 'inline-block'}
            )
        ],
            style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                id='yaxis-column',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value='SJR'
            ),
            dcc.RadioItems(
                id='yaxis-type',
                options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                value='Linear',
                labelStyle={'display': 'inline-block'}
            )
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                id='field-column',
                options=[{'label': i, 'value': i} for i in fields],
                value=['Psych', 'Psych & Neuro', 'Neuro', 'General'],
                multi=True
            ),
        ], style={'width': '100%'})
    ],
        style={
            'borderBottom': 'thin lightgrey solid',
            'backgroundColor': 'rgb(250, 250, 250)',
            'padding': '10px 5px'
        }),

    html.Div([
        dcc.Graph(
            id='indicator-graphic',
            hoverData={'points': [{'customdata': 'Psychological Science'}]}
        )
    ], style={'width': '100%', 'padding': '0 20'}),

    html.Div([
        dcc.Slider(
            id='year--slider',
            min=df['Year'].min(),
            max=df['Year'].max(),
            value=df['Year'].max(),
            marks={str(year): str(year) for year in df['Year'].unique()}
        )
    ], style={'width': '100%', 'padding': '0px 20px 40px 20px'}),

    html.Div([
        dcc.Graph(id='x-time-series'),
    ], style={'display': 'inline-block', 'width': '49%'}),

    html.Div([
        dcc.Graph(id='y-time-series'),
    ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'})

])


# Define callbacks for the core scatter plot
@app.callback(
    dash.dependencies.Output('indicator-graphic', 'figure'),
    [dash.dependencies.Input('xaxis-column', 'value'),
     dash.dependencies.Input('yaxis-column', 'value'),
     dash.dependencies.Input('xaxis-type', 'value'),
     dash.dependencies.Input('yaxis-type', 'value'),
     dash.dependencies.Input('year--slider', 'value'),
     dash.dependencies.Input('field-column', 'value')])
def update_graph(xaxis_column_name, yaxis_column_name,
                 xaxis_type, yaxis_type,
                 year_value, field_name):

    dff = df[df['Year'] == year_value]
    traces = []
    colors = color_palette(n_colors=dff['Field'].nunique()).as_hex()
    colors = dict(zip(dff['Field'].unique(), colors))
    for field in field_name:
        if field in dff['Field'].unique():
            color = colors[field]
            traces.append(
                go.Scatter(
                    x=dff.query("Dimension == @xaxis_column_name and Field == @field")['Value'],
                    y=dff.query("Dimension == @yaxis_column_name and Field == @field")['Value'],
                    text=dff.query("Dimension == @yaxis_column_name and Field == @field")['Title'],
                    customdata=dff.query("Dimension == @yaxis_column_name and Field == @field")['Title'],
                    mode='markers',
                    name=field,
                    marker={
                        'size': 12,
                        'opacity': 0.5,
                        'color': color,
                        'line': {'width': 0.5, 'color': 'white'}
                    }
                ),
            )
    return {
        'data': traces,
        'layout': go.Layout(
            xaxis={
                'title': xaxis_column_name,
                'type': 'linear' if xaxis_type == 'Linear' else 'log'
            },
            yaxis={
                'title': yaxis_column_name,
                'type': 'linear' if yaxis_type == 'Linear' else 'log'
            },
            margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
            hovermode='closest',
            showlegend=True
        )
    }


# Create a second plotting function that changes based on hover inputs
def create_time_series(dff, axis_type, title):
    return {
        'data': [go.Scatter(
            x=dff['Year'].sort_values(),
            y=dff['Value'],
            mode='lines+markers'
        )],
        'layout': {
            'height': 225,
            'margin': {'l': 20, 'b': 30, 'r': 10, 't': 25},
            'annotations': [{
                'x': 0, 'y': .95, 'xanchor': 'left', 'yanchor': 'bottom',
                'xref': 'paper', 'yref': 'paper', 'showarrow': False,
                'align': 'left', 'bgcolor': 'rgba(255, 255, 255, 0.5)',
                'text': title
            }],
            'yaxis': {'type': 'linear' if axis_type == 'Linear' else 'log'},
            'xaxis': {'showgrid': False, 'range': [dff.Year.min(), dff.Year.max() + 1], 'autorange': False}
        }
    }


# Define callbacks for the x-variable instance of the plot
@app.callback(
    dash.dependencies.Output('x-time-series', 'figure'),
    [dash.dependencies.Input('indicator-graphic', 'hoverData'),
     dash.dependencies.Input('xaxis-column', 'value'),
     dash.dependencies.Input('xaxis-type', 'value')])
def update_y_timeseries(hoverData, xaxis_column_name, axis_type):
    journal_name = hoverData['points'][0]['customdata']
    dffy = df[df['Title'] == journal_name]
    dffy = dffy[dffy['Dimension'] == xaxis_column_name]
    title = '<b>{}</b><br>{}'.format(journal_name, xaxis_column_name)
    return create_time_series(dffy, axis_type, title)


# Define callbacks for the y-variable instance of the plot
@app.callback(
    dash.dependencies.Output('y-time-series', 'figure'),
    [dash.dependencies.Input('indicator-graphic', 'hoverData'),
     dash.dependencies.Input('yaxis-column', 'value'),
     dash.dependencies.Input('yaxis-type', 'value')])
def update_x_timeseries(hoverData, yaxis_column_name, axis_type):
    journal_name = hoverData['points'][0]['customdata']
    dffx = df[df['Title'] == hoverData['points'][0]['customdata']]
    dffx = dffx[dffx['Dimension'] == yaxis_column_name]
    title = '<b>{}</b><br>{}'.format(journal_name, yaxis_column_name)
    return create_time_series(dffx, axis_type, title)


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
