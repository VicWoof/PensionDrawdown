from dash import Dash, dcc, Output, Input, html  # pip install dash
import dash_bootstrap_components as dbc    # pip install dash-bootstrap-components
import plotly.express as px
import pandas as pd

# create initial data
def create_data(potsize, apr, monthly_withdrawal, years_to_forecast, start_age):
    df = pd.DataFrame()

    data = []
    balance = potsize
    age = start_age
    data.append([str(start_age)+'.0', balance])
    while age <= (start_age + years_to_forecast + 1):
        month = 1
        while month <= 12:
            balance = (balance - monthly_withdrawal) * (1 + apr/100/12)
            if balance <= 0 : balance = 0
            item = [str(age)+'.'+str(month), balance]
            month += 1
            data.append(item)
        age += 1

    df = pd.DataFrame(data, columns=['Age', 'Balance'])
    return df

df = create_data(500000,5,2000,50,57)

# Build your components
app = Dash(__name__, external_stylesheets=[dbc.themes.VAPOR])
server = app.server
mygraph = dcc.Graph(figure={})
potsize = dcc.Input(type='number', min=1, step=1, value=500000, debounce=True, required=True)
apr = dcc.Input(type='number', value=5, debounce=True)
monthly_withdrawal = dcc.Input(type='number', min=0, step=1, value=2000, debounce=True)
years_to_forecast = dcc.Input(type='number', min=1, step=1, value=50, debounce=True)
start_age = dcc.Input(type='number', min=1, step=1, value=57, debounce=True)

# Customize your own Layout
app.layout = html.Div(children=[
    html.H1(
        children='Pension Drawdown',
        style={
            'textAlign': 'center'
        }
    ),
        
    mygraph,

    html.Div(children=[
        html.Div(children=[
            html.Label('Pot Size'),
            potsize
        ]),
        html.Div(children=[
            html.Label('Annual Return Rate'),
            apr
        ]),
        html.Div(children=[
            html.Label('Monthly Withdrawl'),
            monthly_withdrawal
        ]),
        html.Div(children=[
            html.Label('Years to Forecast'),
            years_to_forecast,
        ]),
        html.Div(children=[
            html.Label('Starting Age'),
            start_age
        ])
    ])
])

# Callback allows components to interact
@app.callback(
    Output(mygraph, component_property='figure'),
    [Input(potsize, component_property='value'),
     Input(apr, component_property='value'),
     Input(monthly_withdrawal, component_property='value'),
     Input(years_to_forecast, component_property='value'),
     Input(start_age, component_property='value')]
)
def update_graph(potsize, apr, monthly_withdrawal, years_to_forecast, start_age):  # function arguments come from the component property of the Input
    df = create_data(potsize, apr, monthly_withdrawal, years_to_forecast, start_age)
    fig = px.line(data_frame=df, x="Age", y="Balance")

    return fig  # returned objects are assigned to the component property of the Output


# Run app
if __name__=='__main__':
    app.run_server()