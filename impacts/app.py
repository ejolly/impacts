import dash
import dash_core_components as dcc
import dash_table
import dash_html_components as html
import pandas as pd
import os

# Prep local data
df = pd.read_csv(os.path.join('data', 'scimagojr_2017.csv'), delimiter=';')


def gen_table(dataframe, max_rows=5):
    return html.Table(
        # Header
       [html.Tr([html.Th(col) for col in dataframe.columns])] +
       # Body
       [html.Tr([
           html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
       ]) for i in range(min(len(dataframe), max_rows))]
    )

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='Hello World'),
    html.H4(children='Scimago Journal Citation Counts'),
    #gen_table(df)
    dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.head().to_dict("rows"),
        sorting=True,
        style_cell={
        'whiteSpace': 'no-wrap',
        'overflow': 'hidden',
        'textOverflow': 'ellipsis',
        'maxWidth': 0,
    },
        css=[{
               'selector': '.dash-cell div.dash-cell-value',
               'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'
           }],
    )

    # dcc.Graph(
    #     id='example-graph',
    #     figure={
    #         'data': [
    #             {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
    #             {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
    #         ],
    #         'layout': {
    #             'title': 'Dash Data Visualization'
    #         }
    #     }
    # )
])

if __name__ == '__main__':
    app.run_server(debug=True)
