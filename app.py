import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import json
from data import get_energyreporter_data, get_switzerland_geojson
import dash_bootstrap_components as dbc


app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

df = get_energyreporter_data()
geojson = get_switzerland_geojson()

canton_mapping = {
    "AG": "Aargau", "AI": "Appenzell Innerrhoden", "AR": "Appenzell Ausserrhoden",
    "BE": "Bern", "BL": "Basel-Landschaft", "BS": "Basel-Stadt",
    "FR": "Fribourg", "GE": "Genève", "GL": "Glarus", "GR": "Graubünden",
    "JU": "Jura", "LU": "Luzern", "NE": "Neuchâtel", "NW": "Nidwalden",
    "OW": "Obwalden", "SG": "St. Gallen", "SH": "Schaffhausen",
    "SO": "Solothurn", "SZ": "Schwyz", "TG": "Thurgau", "TI": "Ticino",
    "UR": "Uri", "VD": "Vaud", "VS": "Valais", "ZG": "Zug", "ZH": "Zürich"
}

df['canton_full'] = df['canton'].map(canton_mapping)

energy_types = {
    'Total Renewable Energy': 'renelec_production_mwh_per_year',
    'Water Production': 'renelec_production_water_mwh_per_year',
    'Solar Production': 'renelec_production_solar_mwh_per_year',
    'Wind Production': 'renelec_production_wind_mwh_per_year',
    'Biomass Production': 'renelec_production_biomass_mwh_per_year',
    'Waste Production': 'renelec_production_waste_mwh_per_year'
}

canton_energy = df.groupby(['canton', 'canton_full'])[list(energy_types.values())].sum().reset_index()

app.layout = html.Div([
    html.H1("Energy Production in Switzerland"),
    dcc.Dropdown(
        id='energy-type-dropdown',
        options=[{'label': key, 'value': value} for key, value in energy_types.items()],
        value='renelec_production_mwh_per_year',
        clearable=False
    ),
    html.Div([
        dcc.Graph(id='bar-chart', style={'flex': '1', 'height': '80vh'}),
        dcc.Graph(id='switzerland-map', style={'flex': '2', 'height': '80vh'})
    ], style={'display': 'flex'})
])

@app.callback(
    [Output('switzerland-map', 'figure'),
     Output('bar-chart', 'figure')],
    [Input('energy-type-dropdown', 'value')]
)
def update_charts(selected_energy_type):
    map_data = canton_energy.copy()
    map_data[selected_energy_type] = map_data[selected_energy_type].replace(0, 1e-10)
    bar_data = canton_energy[canton_energy[selected_energy_type] > 0]

    map_fig = px.choropleth(
        map_data,
        geojson=geojson,
        locations='canton_full',
        featureidkey="properties.name",
        color=selected_energy_type,
        color_continuous_scale="greens",
        scope="europe",
        labels={selected_energy_type: "Production in MWh"}
    )
    map_fig.update_geos(fitbounds="locations", visible=False)

    sorted_bar_data = bar_data.sort_values(by=selected_energy_type)
    bar_fig = px.bar(
        sorted_bar_data,
        x=selected_energy_type,
        y='canton',
        orientation='h',
        color_discrete_sequence=['green'],
        labels={'canton': 'Canton', selected_energy_type: selected_energy_type.replace('_', ' ').title()},
    )
    bar_fig.update_layout(
        xaxis={'categoryorder': 'total descending'},
        height=650
    )

    return map_fig, bar_fig

if __name__ == '__main__':
    app.run_server(debug=True)
