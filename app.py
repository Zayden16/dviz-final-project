import os
from datetime import datetime, date, timedelta

import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, Input, Output, callback

from charts import create_elec_prod_bar_chart, create_elec_prod_line_chart, create_elec_prod_pie_chart, create_elec_prod_heatmap, create_energy_treemap

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
        html.P("Electricity Production in Switzerland", className="h3"),
        dbc.Nav(
            [
                dbc.NavLink("Line Chart", href="/elec-prod-line", active="exact"),
                dbc.NavLink("Bar Chart", href="/elec-prod-bar", active="exact"),
                dbc.NavLink("Pie Chart", href="/elec-prod-pie", active="exact"),
                dbc.NavLink("Heatmap", href="/elec-prod-heatmap", active="exact"),
                dbc.NavLink("Treemap", href="/elec-prod-treemap", active="exact"),
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
], style={'display': 'flex', 'align-items': 'center', 'padding': '5px', 'margin-bottom': '15px'}, id="date-picker-container")

treemap_options = html.Div(
    [
        dcc.Checklist(
            id="energy-source-selector",
            options=[
                {"label": "Include Water", "value": "water"},
                {"label": "Include Solar", "value": "solar"},
                {"label": "Include Wind", "value": "wind"},
                {"label": "Include Biomass", "value": "biomass"},
                {"label": "Include Waste", "value": "waste"},
            ],
            value=["solar", "wind", "biomass", "waste"],
            style={"margin": "-60px 0px 20px 80px", "z-index": "1000", "position": "relative"},
        ),
        dcc.Checklist(
            id="per-capita-toggle",
            options=[{"label": "Show per capita values", "value": "per_capita"}],
            value=["per_capita"],
            style={"margin": "10px 0px 20px 80px", "z-index": "1000", "position": "relative"},
        ),
    ],
    style={"display": "none"},
    id="treemap-content"
)

content = html.Div(
    [
        date_pickers,
        html.Div(id="page-content", style=CONTENT_STYLE),
        html.Div(id="conditional-content"),
        treemap_options
    ],
    style=CONTENT_STYLE
)
app.layout = html.Div([dcc.Location(id="url"), sidebar, content], style=MAIN_LAYOUT_STYLE)

@app.callback(
    Output("date-picker-container", "style"),
    Input("url", "pathname")
)
def toggle_date_pickers_visibility(pathname):
    if pathname == "/elec-prod-treemap":
        return {"display": "none"}
    return {'display': 'flex', 'align-items': 'center', 'padding': '5px', 'margin-bottom': '15px'}

@app.callback(
    Output("treemap-content", "style"),
    Input("url", "pathname")
)
def toggle_treemap_options_visibility(pathname):
    if pathname == "/elec-prod-treemap":
        return {"display": "block"}
    return {"display": "none"}

@app.callback(
    Output("page-content", "children"),
    [
        Input('url', 'pathname'),
        Input('start-date-picker', 'date'),
        Input('end-date-picker', 'date'),
        Input('energy-source-selector', 'value'),
        Input('per-capita-toggle', 'value')
    ]
)
def display_page(pathname, start_date, end_date, selected_sources, per_capita_values):
    if pathname == '/elec-prod-line':
        return create_elec_prod_line_chart(start_date, end_date)
    elif pathname == '/elec-prod-bar':
        return create_elec_prod_bar_chart(start_date, end_date)
    elif pathname == '/elec-prod-pie':
        return create_elec_prod_pie_chart(start_date, end_date)
    elif pathname == '/elec-prod-heatmap':
        return create_elec_prod_heatmap(start_date, end_date)
    elif pathname == '/elec-prod-treemap':
        return create_energy_treemap(selected_sources, 'per_capita' in per_capita_values)
    return create_elec_prod_bar_chart(start_date, end_date)

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=int(os.environ.get('PORT', 8050)))
