import dash
from dash import dcc, html
import plotly.express as px
from api.public_power import get_public_power

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1('Energy Production in Switzerland', style={'textAlign': 'center'}),
    dcc.Graph(id='energy-production-chart')
])

@app.callback(
    dash.dependencies.Output('energy-production-chart', 'figure'),
    dash.dependencies.Input('energy-production-chart', 'id')
)
def update_graph(_):
    df = get_public_power('2023-01-01T00:00+01:00', '2023-01-01T23:45+01:00')
    fig = px.line(df, x='Time', y='Power (MW)', color='Production Type',
                  labels={'Time': 'Time of Day', 'Power (MW)': 'Power in MW'},
                  title='Energy Production Types Over Time')
    fig.update_xaxes(rangeslider_visible=True)
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
