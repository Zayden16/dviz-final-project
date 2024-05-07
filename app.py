from dash import Dash, html, dcc, Input, Output, callback, ctx
import dash_bootstrap_components as dbc
from datetime import datetime, date, timedelta
import os
from charts import create_elec_prod_bar_chart, create_elec_prod_heatmap, create_elec_prod_line_chart, create_elec_prod_pie_chart

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
app.title = 'Energy Production in Switzerland'

today = date.today()
seven_days_ago = today - timedelta(days=7)

SIDEBAR_STYLE = {
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "250px",
    "padding": "1rem 1rem",
    "background-color": "#f8f9fa",
}

CONTENT_STYLE = {
    "flex-grow": 1,
    "padding": "1rem 1rem",
    "width": "100%"
}

MAIN_LAYOUT_STYLE = {
    "display": "flex",
    "flex-direction": "row",
    "height": "100vh",
}

sidebar = html.Div(
    [
        html.P(
            "Electricity Production in Switzerland", className="h3"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Line Chart", href="/elec-prod-line", active="exact"),
                dbc.NavLink("Bar Chart", href="/elec-prod-bar", active="exact"),
                dbc.NavLink("Pie Chart", href="/elec-prod-pie", active="exact"),
                dbc.NavLink("Heatmap", href="/heatmap", active="exact"),

            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

date_pickers = html.Div([
    html.Label('Start Date:'),
    dcc.DatePickerSingle(
        id='start-date-picker',
        min_date_allowed=datetime(2020, 1, 1),
        max_date_allowed=datetime.today(),
        initial_visible_month=datetime.today(),
        date=seven_days_ago,
        display_format='DD.MM.YYYY'
    ),
    html.Label('End Date:'),
    dcc.DatePickerSingle(
        id='end-date-picker',
        min_date_allowed=datetime(2020, 1, 1),
        max_date_allowed=datetime.today(),
        initial_visible_month=datetime.today(),
        date=today,
        display_format='DD.MM.YYYY'
    )
], style={'display': 'flex', 'align-items':'center', 'padding': '5px', 'margin-bottom': '15px'})

content = html.Div(
    [
        date_pickers,
        html.Div(id="page-content", style=CONTENT_STYLE)
    ],
    style=CONTENT_STYLE
)
app.layout = html.Div([dcc.Location(id="url"), sidebar, content], style=MAIN_LAYOUT_STYLE)

@app.callback(Output("page-content", "children"),
              [Input('url', 'pathname'), Input('start-date-picker', 'date'), Input('end-date-picker', 'date')])
def display_page(pathname, start_date, end_date):
    if pathname == '/elec-prod-line':
        return create_elec_prod_line_chart(start_date, end_date)
    elif pathname == '/elec-prod-bar':
        return create_elec_prod_bar_chart(start_date, end_date)
    elif pathname == '/elec-prod-pie':
        return create_elec_prod_pie_chart(start_date, end_date)
    elif pathname == '/heatmap':
        return create_elec_prod_heatmap(start_date, end_date)
    else:
        return create_elec_prod_bar_chart(start_date, end_date)
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=int(os.environ.get('PORT', 8050)))
