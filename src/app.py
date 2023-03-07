from dash import Dash, dcc, Output, Input, html  # pip install dash
import dash_bootstrap_components as dbc    # pip install dash-bootstrap-components
import plotly.express as px
import pandas as pd
import numpy_financial as npf
from datetime import datetime, timedelta

fixedmanagementfee = 0.01

# create initial data
def create_data(potsize, apr, monthly_withdrawal, inflation, years_to_forecast, start_age, sandp, sandphold, sandpdata):
    df = pd.DataFrame()

    data = []
    balance = potsize
    withdrawal = monthly_withdrawal
    if start_age < 0 : start_age = 0
    age = start_age
    if sandp:
        sandpdatarowcount = len(sandpdata.index)
        sandpdataindexpointer = sandpdatarowcount - (years_to_forecast * 12) - 12
        returnlist = [-sandpdata.loc[sandpdataindexpointer-sandphold*12, 'Close']]
        i = sandphold - 1
        while i > 0:
            returnlist.append(0)
            i -= 1
        returnlist.append(sandpdata.loc[sandpdataindexpointer, 'Close'])
        returnrate = npf.irr(returnlist)
    else:
        returnrate = apr/100

    data.append([str(start_age)+'.0', withdrawal, balance, returnrate])
    while age <= (start_age + years_to_forecast -1):
        month = 1
        while month <= 12:
            if sandp:
                sandpdataindexpointer += 1
                returnlist = [-sandpdata.loc[sandpdataindexpointer-sandphold*12, 'Close']]
                i = sandphold - 1
                while i > 0:
                    returnlist.append(0)
                    i -= 1
                returnlist.append(sandpdata.loc[sandpdataindexpointer, 'Close'])
                returnrate = npf.irr(returnlist)
                balance = (balance - withdrawal) * (1 + (returnrate - fixedmanagementfee)/12)
            else:
                balance = (balance - withdrawal) * (1 + apr/100/12)                
            if balance <= 0 :
                balance = 0
                withdrawal = 0
            item = [str(age)+'.'+str(month), withdrawal, balance, returnrate]
            month += 1
            data.append(item)
        age += 1
        withdrawal = withdrawal * (1 + inflation/100)

    df = pd.DataFrame(data, columns=['Age', 'Withdrawal', 'Balance', 'Return Rate'])
    df = df.astype({'Withdrawal':'int', 'Balance':'int'})
    return df

sandpdata = pd.read_csv('src/sandp500.csv')

df = create_data(500000, 5, 2000, 2, 50, 57, False, 5, sandpdata)

# Build your components
app = Dash(__name__, external_stylesheets=[dbc.themes.VAPOR])
server = app.server
mygraph = dcc.Graph(figure={})
mygraph2 = dcc.Graph(figure={})
potsize = dcc.Input(type='number', min=1, step=1, value=500000, debounce=True, required=True)
apr = dcc.Input(type='number', value=5, debounce=True)
inflation = dcc.Input(type='number', value=2, debounce=True)
monthly_withdrawal = dcc.Input(type='number', min=0, step=1, value=2000, debounce=True)
years_to_forecast = dcc.Slider(1, 100, 1, value=50)
start_age = dcc.Input(type='number', min=1, step=1, value=57, debounce=True)
sandp = dcc.RadioItems([
        {'label': 'Fixed Return', 'value' : False},
        {'label': 'S & P 500 Historic Return', 'value' : True}
    ],
    False, inline=True)
sandphold = dcc.Slider(0, 20, 1, value=5)

# Customize your own Layout
app.layout = html.Div(children=[
    html.H1(
        children='Pension Drawdown',
        style={
            'textAlign': 'center'
        }
    ),
        
    mygraph,

    mygraph2,

    html.Div(children=[
        html.Div(children=[
            html.Label('Pot Size'),
            potsize
        ]),
        html.Div(children=[
            html.Label('Monthly Withdrawl'),
            monthly_withdrawal
        ]),
        html.Div(children=[
            html.Label('Annual Return Rate'),
            apr,
            html.Label('%'),
            sandp,
            html.Label('Average years of holding S&P 500'),
            sandphold
        ]),
        html.Div(children=[
            html.Label('Inflation'),
            inflation,
            html.Label('%')
        ]),
        html.Div(children=[
            html.Label('Years to Forecast'),
            years_to_forecast
        ]),
        html.Div(children=[
            html.Label('Starting Age'),
            start_age
        ]),
        html.Div(children=[
            dcc.Markdown('''
                # Note:
                
                The Average years of holding S&P 500 is used to calculate the return rate. It looks at the price of S&P 500 the number of years before the month and the price at the month and calculating the IRR.'

                A fixed management fee of 1% is used.
                '''),
        ])
    ])
])

# Callback allows components to interact
@app.callback(
    Output(mygraph, component_property='figure'),
    Output(apr, component_property='disabled'),
    Output(mygraph2, component_property='figure'),
    Input(potsize, component_property='value'),
    Input(apr, component_property='value'),
    Input(monthly_withdrawal, component_property='value'),
    Input(inflation, component_property='value'),
    Input(years_to_forecast, component_property='value'),
    Input(start_age, component_property='value'),
    Input(sandp, component_property='value'),
    Input(sandphold, component_property='value')
)
def update_graph(potsize, apr, monthly_withdrawal, inflation, years_to_forecast, start_age, sandp, sandphold):  # function arguments come from the component property of the Input
    df = create_data(potsize, apr, monthly_withdrawal, inflation, years_to_forecast, start_age, sandp, sandphold, sandpdata)
    fig = px.line(data_frame=df, x="Age", y=["Balance", "Withdrawal"])

    aprdisabled = False
    if sandp:
        aprdisabled = True

    fig2 = px.line(data_frame=df, x="Age", y="Return Rate")
    fig2.update_layout(yaxis_tickformat=".1%")

    return fig, aprdisabled, fig2  # returned objects are assigned to the component property of the Output

# Run app
if __name__=='__main__':
    app.run_server()