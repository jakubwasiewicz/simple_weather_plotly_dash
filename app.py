# %%
#import packages
import pandas as pd
import requests
import plotly.express as px
import plotly.figure_factory as ff
from config import key # private API key to weatherapi is in file 'config.py'
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

# %%
#current temp data - connect to api and gather weather data
base_url='http://api.weatherapi.com/v1/'
mode_current = 'current'
cities = ['Cracow', 'Warsaw', 'Lublin', 'Rzeszow'] #choosing cities for weather data
data_current = []
for city in cities: #api loop for cities
    response_current = requests.get(base_url + mode_current + '.json?key=' + key + '&q=' + city + '&aqi=no').json() # private API key 
    data_current.append(response_current)
data_current = pd.json_normalize(data_current)
data_current['current.time'] = pd.to_datetime(data_current['current.last_updated']).dt.time.iloc[0] #creating new column with time
data_current['current.date'] = pd.to_datetime(data_current['current.last_updated']).dt.date.iloc[0] #creating new column with date
current_date = data_current['current.date'].iloc[0] #creating variable with current date
current_time = data_current['current.time'].iloc[0] #creating variable with cuttent time

# %%
#hourly weather data- connect to api and gather in loop data
mode_hours = 'history'
for city in cities:
    response_hours = requests.get(base_url + mode_hours + '.json?key=' + key + '&q=' + city + '&dt=' + str(current_date)).json() # private API key is in file 'config.py'
    data = pd.json_normalize(response_hours['forecast']['forecastday'], record_path=['hour'])
    df= pd.DataFrame(data)
    df['city'] = city
    globals()[city] = df
df_cities = [Rzeszow, Cracow, Warsaw, Lublin] #cities names definied in previous loop (globals)
hourly_df_cities = pd.concat(df_cities)
hourly_df_cities['time_hour'] = pd.to_datetime(hourly_df_cities['time']).dt.strftime('%H:%M')

# %%
#wind kph plot
df = hourly_df_cities.query('city == "Cracow"')
wind_city = px.line(df, x='time_hour', y="wind_kph", title = f'Hourly ({current_date}) wind speed in Cracow [km/h]',
              labels = {'wind_kph': 'Wind speed',
                        'time_hour': 'Hour'},
                        template = 'plotly_dark', width=600, height=400)
wind_city.update_layout(font_family='Arial', titlefont_size = 16)
wind_city.update_xaxes(dtick= 2)

# %%
#humidity and preassure table 
table = df[['time_hour', 'pressure_mb','humidity', 'cloud']]
table.columns = ['Hour', 'Pressure [mb]', 'Humidity[%]', 'Chance of rain [%]']
table_city = ff.create_table(table, height_constant=20)
table_city.layout.width=600

#current temp
current_temp = px.bar(data_current, x="location.name", y="current.temp_c", color = 'current.temp_c', 
                title=f"Current temperature ({current_date}, {current_time}) in Poland [C]:",
                labels = {'location.name': 'City in Poland',
                        'current.temp_c': 'Current Temperature'}, template = 'plotly_white', text = data_current['current.temp_c'], width=1200, height=600)
current_temp.update_layout(font_family='Arial', titlefont_size = 18, yaxis_range=[-20,40])
current_temp.update_traces(textposition='outside', textfont_size=14)

# %%
#dashboard
app = dash.Dash(__name__) #starting the app

#setting layout
app = dash.Dash(external_stylesheets=[dbc.themes.LITERA])
sidebar = html.Div([
    html.H5('Select city:', 
           className='text-dark font-italic',
           style={'margin-top': '16px'}),
    dcc.Dropdown(id='slct_city',
        options=[
            {'label':'Cracow', 'value': 'Cracow'},
            {'label':'Warsaw', 'value': 'Warsaw'},
            {'label':'Rzeszow', 'value': 'Rzeszow'},
            {'label':'Lublin', 'value': 'Lublin'}],
        multi=False,
        placeholder="Select a city",
        value='Warsaw',
        style = {'width': '50%'}),
    html.Div(id='output_container', children=[]),
    dcc.Graph(id='wind_city', figure=wind_city),
    html.Hr(),
    dcc.Graph(id='table_city', figure=table_city,
              style={'margin-bottom': '16px'}),
              html.Hr()
    ])


content = html.Div(
    [
        html.H2('Simple Weather Dashboard for main cities in Poland', style = {'textAlign' : 'center'}),
        html.Hr(),
        dcc.Graph(id='current_temp', figure=current_temp),
        html.Hr()
    ]
)

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(sidebar, width=4, className='bg-light'),
                dbc.Col(content, width=8, className = 'd-flex justify-content-md-center align-items-center')
                ],
            style={'display':'flex', "height": "100vh", 'justify-content':'left'}
            ),
        ],
    fluid=True
    )

@app.callback(
    [Output(component_id='output_container', component_property='children'),
    Output(component_id='current_temp', component_property='figure'),
    Output(component_id='wind_city', component_property='figure'),
    Output(component_id='table_city', component_property='figure')],
    [Input(component_id='slct_city', component_property='value')]
)
def update_graph(option_slctd): #returning output & graph modifications
    container = []

    dff = hourly_df_cities.copy()
    dff = dff[hourly_df_cities['city'] == option_slctd]
    #current_temp
    current_temp = px.bar(data_current, x="location.name", y="current.temp_c", color = 'current.temp_c', 
                title=f"Current temperature ({current_date}, {current_time}) in Poland [C]:",
                labels = {'location.name': 'City in Poland',
                        'current.temp_c': 'Current Temperature'}, template = 'plotly_white', text = data_current['current.temp_c'], width=1200, height=600)
    current_temp.update_layout(font_family='Arial', titlefont_size = 18, yaxis_range=[-20,40])
    current_temp.update_traces(textposition='outside', textfont_size=14)
    #wind kph plot
    wind_city = px.line(dff, x='time_hour', y="wind_kph", title = f'Hourly ({current_date}) wind speed in {option_slctd} [km/h]',
                labels = {'wind_kph': 'Wind speed',
                            'time_hour': 'Hour'},
                            template = 'plotly_white', width=600, height=400)
    wind_city.update_layout(font_family='Arial', titlefont_size = 16)
    wind_city.update_xaxes(dtick= 2)
    #humidity and preassure table 
    table = dff[['time_hour', 'pressure_mb','humidity', 'cloud']]
    table.columns = ['Hour', 'Pressure [mb]', 'Humidity[%]', 'Clouds on sky [%]']
    table_city = ff.create_table(table, height_constant=15)
    table_city.update_layout(width=600, font_family='Arial', template = 'plotly_white')

    return container, current_temp, wind_city, table_city #finally return the outoput

if __name__ == '__main__':
    app.run_server(debug=True)



