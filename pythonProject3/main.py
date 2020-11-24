import dash
import numpy as np
import pandas as pd
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import plotly.express as px
from PIL import Image
import matrix_engine as mg
import concurrent

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
paths = ['assets/Mapa_MD_no_terrain_low_res_dark_Gray.bmp',
         'assets/Mapa_MD_no_terrain_low_res_Gray.bmp',
         'assets/monkePOG.png',
         'assets/Astronaut.jpg']
# frames_list = [30, 60, 120, 440]
play_global = False
n = 0
image_global = np.array(Image.open(paths[0]).convert('L'))
tensor = []
# frames_global = 10
humidity_global = 10
s = 1
grid = mg.get_forest(image_global)
# grid[100, 371].state = 2
# grid[100, 371].RGB = [255, 213, 97]
image_global = mg.map_to_picture(grid)
image_global_copy = np.copy(image_global)
humidity_list = [0, 50, 100]
waypoint_on = False
waypoint_n = 0
wind_global = ''
x_waypoint = 0
y_waypoint = 0
############################# --------------------- layout ---------------------------- #####################

app.layout = html.Div([
    html.Div([
        html.Div([dcc.Graph(id='img', figure={})], style={'margin-left': '2%', 'margin-top': '5%', 'float': 'left'}),
        html.Div([
            ## DROPDOWN
            dcc.Dropdown(
                id='img-dropdown',
                options=[{'label': path, 'value': path} for path in paths],
                value=paths[0]),

            ## SLIDER LABEL
            html.Div([
                html.Div(id='humidity-slider-output-container')
            ], style={'color': 'cyan', 'margin-top': '20px'}),

            # SLIDER
            html.Div([
                dcc.Slider(
                    id='humidity-slider',
                    min=0,
                    max=100,
                    marks={i: '{}'.format(i) for i in humidity_list},
                    value=10),
            ], style={'width': '100%', 'font-color': '#0097a7', 'margin-top': '1%'}),

            ## CONTROL BUTTONS
            html.Div([
                # dbc.Button('calculate', id='calculate', color="dark", className="b-1"),
                dbc.Button('play', id='play', color="dark", className="b-1"),
                dbc.Button('stop', id='stop', color="dark", className="b-1"),
            ], style={'margin-top': "5%"}),

            html.Div([
                dbc.Button('send chopper', id='waypoint', color="dark", className="b-1"),
            ], style={'margin-top': "5%"}),

            html.Div([dbc.RadioItems(
                options=[
                    {'label': 'North', 'value': 'n'},
                    {'label': 'South', 'value': 's'},
                    {'label': 'West', 'value': 'w'},
                    {'label': 'East', 'value': 'e'}
                ],
                id='wind-buttons',
                labelStyle={'color': "cyan"},
                className='b-1'
            )
            ], style={'margin-top': "5%"}),

        ], style={'width': '25%', 'float': 'right', 'margin-top': '5%', 'margin-right': '5%'}),

    ], className="block-wide", style={'float': 'center', 'backgroundImage': 'url("assets/tile.jpg")'}),

    # interval
    dcc.Interval(
        id='interval-component',
        interval=(1 * 1000),  # in milliseconds
        n_intervals=0
    ),

    # refresh
    html.Div(id='hidden-div-1', style={'display': 'none'}),
    html.Div(id='hidden-div-2', style={'display': 'none'}),
    html.Div(id='hidden-div-3', style={'display': 'none'}),
    html.Div(id='hidden-div-4', style={'display': 'none'}),
    html.Div(id='hidden-div-5', style={'display': 'none'}),
    html.Div(id='hidden-div-6', style={'display': 'none'}),
    html.Div(id='hidden-div-7', style={'display': 'none'}),
    html.Div(id='hidden-div-8', style={'display': 'none'}),
    html.Div(id='hidden-div-9', style={'display': 'none'}),

])


############################# --------------------- callbacks ---------------------------- #####################

############################################## stop play controls
@app.callback(
    Output("hidden-div-1", "children"),
    [Input('stop', 'n_clicks')]
    , prevent_initial_call=True)
def refresh_stop(plus):
    global play_global
    play_global = False
    raise dash.exceptions.PreventUpdate("cancel the callback")


@app.callback(
    Output("hidden-div-2", "children"),
    [Input('play', 'n_clicks')]
    , prevent_initial_call=True)
def refresh_play(plus):
    global play_global
    play_global = True
    raise dash.exceptions.PreventUpdate("cancel the callback")


############################################################################################
############################################################################################

############################################################################################ plane controls
@app.callback(
    Output("hidden-div-7", "children"),
    [Input('waypoint', 'n_clicks')]
    , prevent_initial_call=True)
def waypoint(click):
    global waypoint_on
    waypoint_on = True
    raise dash.exceptions.PreventUpdate("cancel the callback")


@app.callback(
    dash.dependencies.Output('humidity-slider-output-container', 'children'),
    [dash.dependencies.Input('humidity-slider', 'value')])
def update_output(humidity):
    global humidity_global
    humidity_global = humidity
    return 'humidity: {}%'.format(humidity)


############################################################################################
############################################################################################


############################################################################################ wind controls
@app.callback(
    Output("hidden-div-9", "children"),
    [Input('wind-buttons', 'value')]
    , prevent_initial_call=True)
def waypoint(value):
    global wind_global
    wind_global = value
    raise dash.exceptions.PreventUpdate("cancel the callback")


############################################################################################
############################################################################################


############################################################################################ dropdown controls
@app.callback(
    Output(component_id="hidden-div-3", component_property='children'),
    [Input(component_id='img-dropdown', component_property='value')],
    prevent_initial_call=True
)
def show_img(path):
    global image_global
    image_global = np.array(Image.open(path).convert('L'))
    raise dash.exceptions.PreventUpdate("cancel the callback")


############################################################################################
############################################################################################


############################################################################################ main fun
@app.callback(
    Output(component_id='img', component_property='figure'),
    [Input('interval-component', 'n_intervals'),
     Input('img-dropdown', 'value'),
     Input('img', 'clickData')
     ])
def update_output(n_intervals, value, ignite):
    global play_global
    global n, image_global, humidity_global, grid
    global waypoint_n, waypoint_on, wind_global, y_waypoint, x_waypoint

    if play_global:
        if (n % 2) == 0:
            mg.forest_fire_even(grid, image_global, wind_global, humidity_global)
        else:
            mg.forest_fire_odd(grid, image_global, wind_global, humidity_global)
        n += 1

    if waypoint_n > 0:
        try:
            image_global[y_waypoint:y_waypoint + I.shape[0], x_waypoint: x_waypoint + I.shape[1]] = I
        except:pass
        waypoint_n += 1
        if waypoint_n > 5:
            try:
                grid[y_waypoint:y_waypoint + int(I.shape[0] / 4), x_waypoint: x_waypoint + int(I.shape[1] / 4)] = mg.cell(1, 0, 0, [255, 116, 23], 0)
            except:pass
            image_global = mg.map_to_picture(grid)
            waypoint_n = 0
    canvas = px.imshow(image_global, binary_string=True, template='plotly_dark')
    canvas.update_layout(title='frame: {}'.format(n),
                         font_color="cyan",
                         width=1250,
                         height=750,
                         clickmode='event+select',
                         margin=dict(l=0, r=0, b=0))

    return canvas


############################################################################################
############################################################################################
I = np.asarray(Image.open('assets/a.png'))


############################################################################################ on click
@app.callback(
    Output(component_id='hidden-div-6', component_property='children'),
    [Input('img', 'clickData')],
    prevent_initial_call=True)
def update_output(click):
    global grid, image_global, I
    global waypoint_on, waypoint_n, x_waypoint, y_waypoint

    x = click['points'][0]['x']
    y = click['points'][0]['y']
    if waypoint_on:
        y -= int(I.shape[1] / 8)
        x -= int(I.shape[1] / 8)
        y_waypoint, x_waypoint = y, x

        try:
            image_global[y:y + I.shape[0], x: x + I.shape[1]] = I
        except:
            pass
        try:
            grid[y:y + int(I.shape[0] / 4), x: x + int(I.shape[1] / 4)] = mg.cell(1, 0, 0, [255, 116, 23], 0)
        except:
            pass

        waypoint_n = 1
        waypoint_on = False


    else:
        grid[y, x].state = 2
        grid[y, x].ignition_factor = 1
        grid[y, x].RGB = [255, 213, 97]
        image_global = mg.map_to_picture(grid)

    raise dash.exceptions.PreventUpdate("cancel the callback")


############################################################################################
############################################################################################
############################################################################################
############################################################################################


# image_global = mg.map_to_picture(grid)
# @app.callback(
#     Output("hidden-div-4", "children"),
#     [Input('calculate', 'n_clicks')]
#     , prevent_initial_call=True)
# def refresh_refresh(click):
#     global tensor
#     global image_global
#     global frames_global
#     grid = mg.get_forest(image_global)
#     grid[100, 371].state = 2
#     image_global = mg.map_to_picture(grid)
#     tensor = mg.create_forestFire_animation(grid, frames_global)
#
#     raise dash.exceptions.PreventUpdate("cancel the callback")
#

if __name__ == '__main__':
    app.run_server(debug=True)
