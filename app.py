from dash import Dash, html, dcc, Input, Output, callback, ctx
import plotly.express as px
from api.public_power import get_public_power
import os
from datetime import datetime, date, timedelta

app = Dash(__name__)
server = app.server

app.title = 'Energy Production in Switzerland'

today = date.today()
seven_days_ago = today - timedelta(days=7)

def serve_layout():
    return html.Div([
        dcc.Location(id='url', refresh=False),
        html.Div([
            html.H1('Energy Production in Switzerland', style={'textAlign': 'center'}),
            dcc.Link('Line Chart', href='/line'),
            html.Br(),
            dcc.Link('Bar Chart', href='/bar'),
        ]),
        html.Div([
            html.Label('Select Start Date:'),
            dcc.DatePickerSingle(
                id='start-date-picker',
                min_date_allowed=datetime(2020, 1, 1),
                max_date_allowed=datetime.today(),
                initial_visible_month=datetime.today(),
                date = seven_days_ago,
                display_format='DD.MM.YYYY'
            ),
            html.Label('Select End Date:'),
            dcc.DatePickerSingle(
                id='end-date-picker',
                min_date_allowed=datetime(2020, 1, 1),
                max_date_allowed=datetime.today(),
                initial_visible_month=datetime.today(),
                date = today,
                display_format='DD.MM.YYYY'
            )
        ], style={'padding': 10}),
        html.Div(id='page-content')
    ])

app.layout = serve_layout

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname'), Input('start-date-picker', 'date'), Input('end-date-picker', 'date')])
def display_page(pathname, start_date, end_date):
    if pathname == '/line':
        return line_chart_layout(start_date, end_date)
    elif pathname == '/bar':
        return bar_chart_layout(start_date, end_date)
    else:
        return "Welcome! Please select a chart type from the menu."

def line_chart_layout(start_date, end_date):
    df = get_public_power(start_date, end_date)
    fig = px.line(df, x='Time', y='Power (MW)', color='Production Type',
                  labels={'Time': 'Time of Day', 'Power (MW)': 'Power in MW'},
                  title='Line Chart: Energy Production Types Over Time')
    fig.update_xaxes(rangeslider_visible=True)
    return dcc.Graph(figure=fig)

# Define the bar chart layout
def bar_chart_layout(start_date, end_date):
    df = get_public_power(start_date, end_date)
    fig = px.bar(df, x='Time', y='Power (MW)', color='Production Type',
                 labels={'Time': 'Time of Day', 'Power (MW)': 'Power in MW'},
                 title='Bar Chart: Energy Production Types Over Time')
    return dcc.Graph(figure=fig)

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=int(os.environ.get('PORT', 8050)))
