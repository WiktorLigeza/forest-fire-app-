#from dash_canvas import DashCanvas
import dash
import numpy as np
import pandas as pd
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import plotly.express as px
from PIL import Image
import dash_daq as daq
#from base64 import decodestring
import datetime
import matrix_engine as mg
from pyorbital.orbital import Orbital


############################# --------------------- init ---------------------------- #####################
img_global = None
plus_global = False
minus_global = False
play_global = False
game_buttons_global = ''
hand_grid = np.zeros((12, 12))

filename = '/assets/monkePOG.png'
canvas_width = 600
canvas_height = 600
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
options = ['normal', 'bright', 'dark', 'binary', 'dilation/erosion', 'up', 'down', 'gauss']
paths = ['assets/Mapa_MD_no_terrain_low_res_dark_Gray.bmp',
         'assets/Mapa_MD_no_terrain_low_res_Gray.bmp',
         'assets/monkePOG.png',
         'assets/Astronaut.jpg']
a = []
tensor = [a, a, a, a, a]
n = 0
slider_range = {0, 255}
rule_range = [30, 60, 90, 120, 225]
width_range = [144, 240, 360, 480, 720, 1080]

kernel_down = np.array([
    [1 / 9, 1 / 9, 1 / 9],
    [1 / 9, 1 / 9, 1 / 9],
    [1 / 9, 1 / 9, 1 / 9]])

kernel_up = np.array([
    [-1, -1, -1],
    [-1, 9, -1],
    [-1, -1, -1]])

kernel_gauss = np.array([
    [1, 4, 1],
    [4, 32, 4],
    [1, 4, 1]])


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

############################# --------------------- layout ---------------------------- #####################

app.layout = html.Div([
    # up left
    html.Div([
        html.Div([dcc.Dropdown(
            id='img-dropdown',
            options=[{'label': path, 'value': path} for path in paths],
            value=paths[0]
        )], style={'margin-left': "25px", "width": '850px', 'margin-top': '20px', 'backgroundColor': '#1E1E1E'}),

        html.Div([dcc.Graph(id='img', figure={})], style={'margin-left': "25px", }),

        html.Div([dcc.Dropdown(
            id='value-dropdown',
            options=[{'label': opt, 'value': opt} for opt in options],
            value=options[0]
        )], style={'margin-left': "25px", "width": '850px'}),

        # slider header
        dbc.Row([
            dbc.Col(dbc.Collapse(
                html.Div([
                    html.Div(id='img-slider-output-container')
                ], style={'margin-left': "25px", 'color': 'cyan', 'margin-top': '20px'}),
                id="collapse-img-slider-output-container", is_open=False), width=4),
        ]),
        # slider
        dbc.Row([
            dbc.Col(dbc.Collapse(
                html.Div([
                    dcc.Slider(
                        id='img-slider',
                        min=0,
                        max=255,
                        marks={i: '{}'.format(i) for i in slider_range},
                        value=100),
                ], style={'margin-left': "25px", "width": '850px'}),

                id="collapse-img-slider", is_open=False), width=4),
        ]),
        # buttons
        dbc.Row([
            dbc.Col(dbc.Collapse(
                dbc.Button('dilation', id='plus', color="dark", className="b-1"),
                id="buttons-plus", is_open=False), width=1, style={'margin-left': "25px"}),
            dbc.Col(dbc.Collapse(
                dbc.Button('erosion', id='minus', color="dark", className="b-1"),
                id="buttons-minus", is_open=False), width=1),
            dbc.Col(dbc.Collapse(
                dbc.Button('refresh', id='refresh', color="dark", className="b-1"),
                id="buttons-refresh", is_open=False), width=1),
        ]),

    ], className="block", style={'float': 'left', 'margin-top': '20px'}),

    # up right
    html.Div([
        html.Div([dcc.Graph(id='hist', figure={})], style={'margin-left': "25px", 'margin-top': '20px'}),
    ], className="block", style={'float': 'right', 'margin-top': '20px'}),

    # down left
    html.Div([
        html.Div([dcc.Graph(id='wagner', figure={})], style={'margin-left': "25px", 'margin-top': '20px'}),

        html.Div([
            html.Div(id='rule-slider-output-container')
        ], style={'margin-left': "25px", 'color': 'cyan', 'margin-top': '20px'}),

        html.Div([
            dcc.Slider(
                id='rule-slider',
                min=1,
                max=256,
                marks={i: '{}'.format(i) for i in rule_range},
                value=69),
        ], style={'margin-left': "25px", "width": '850px', 'font-color': '#0097a7'}),

        html.Div([
            html.Div(id='width-slider-output-container')
        ], style={'margin-left': "25px", 'color': 'cyan', 'margin-top': '20px'}),

        html.Div([
            dcc.Slider(
                id='width-slider',
                min=144,
                max=1080,
                marks={i: '{}'.format(i) for i in width_range},
                value=500),
        ], style={'margin-left': "25px", "width": '850px', 'font-color': '#0097a7'}),

        html.Div([dbc.RadioItems(
            options=[
                {'label': 'black edge', 'value': 'black-edge'},
                {'label': 'white edge', 'value': 'white-edge'},
                {'label': 'periodic', 'value': 'periodic'}
            ],
            id='r-buttons',
            value='black-edge',
            labelStyle={'color': "cyan"},
            className='b-1'
        )
        ], style={'margin-left': "25px"}),



    ], className="block", style={'float': 'left', 'margin-top': '20px', 'margin-bottom': '20px'}),

    # down right
    html.Div([
        html.Div([dcc.Graph(id='game', figure={})], style={'margin-left': "25px", 'margin-top': '20px'}),
        html.Div([
            dbc.Button('calculate', id='calculate', color="dark", className="b-1"),
            dbc.Button('play', id='play', color="dark", className="b-1"),
            dbc.Button('stop', id='stop', color="dark", className="b-1"),
        ], style={'margin-left': "25px"}),
        html.Div([dbc.RadioItems(
            options=[
                {'label': 'random', 'value': 'random'},
                {'label': 'oscillator', 'value': 'oscillator'},
                {'label': 'glider', 'value': 'glider'},
                {'label': 'unchanged', 'value': 'unchanged'},
                {'label': 'hand def', 'value': 'hand-def'},
            ],
            id='game-buttons',
            value='random',
            labelStyle={'color': "cyan"},
            className='b-1'
        )
        ], style={'margin-left': "25px"}),
        dbc.Row([
            dbc.Col(dbc.Collapse(
                dbc.Button('submit', id='submit', color="dark", className="b-1"),
                id="buttons-submit", is_open=False), width=1, style={'margin-left': "25px"}),
        ]),


    ], className="block", style={'float': 'right', 'margin-top': '20px'}),


    # interval
    dcc.Interval(
        id='interval-component',
        interval=1 * 100,  # in milliseconds
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
    html.Div(id='hidden-div-10', style={'display': 'none'}),
    html.Div(id='hidden-div-11', style={'display': 'none'}),

])


############################# --------------------- callbacks ---------------------------- #####################

# ----------------------------------------------------------------------- Refresh
#
#
@app.callback(
    Output("hidden-div-1", "children"),
    [Input('img-dropdown', 'value'),
     Input('value-dropdown', 'value')]
)
def refresh(path, value):
    global img_global
    img_global = np.array(Image.open(path).convert('L'))
    raise dash.exceptions.PreventUpdate("cancel the callback")


@app.callback(
    Output("hidden-div-4", "children"),
    [Input('img-dropdown', 'value'),
     Input('refresh', 'n_clicks')]
    , prevent_initial_call=True)
def refresh_refresh(path, click):
    global img_global
    img_global = np.array(Image.open(path).convert('L'))
    raise dash.exceptions.PreventUpdate("cancel the callback")


@app.callback(
    Output("hidden-div-2", "children"),
    [Input('plus', 'n_clicks')]
    , prevent_initial_call=True)
def refresh_plus(plus):
    global plus_global
    plus_global = True
    raise dash.exceptions.PreventUpdate("cancel the callback")


@app.callback(
    Output("hidden-div-3", "children"),
    [Input('minus', 'n_clicks')]
    , prevent_initial_call=True)
def refresh_minus(minus):
    global minus_global
    minus_global = True
    raise dash.exceptions.PreventUpdate("cancel the callback")


@app.callback(
    Output("hidden-div-6", "children"),
    [Input('stop', 'n_clicks')]
    , prevent_initial_call=True)
def refresh_stop(plus):
    global play_global
    play_global = False
    raise dash.exceptions.PreventUpdate("cancel the callback")


@app.callback(
    Output("hidden-div-7", "children"),
    [Input('play', 'n_clicks')]
    , prevent_initial_call=True)
def refresh_play(plus):
    global play_global
    play_global = True
    raise dash.exceptions.PreventUpdate("cancel the callback")


#########################################################################
#########################################################################
#########################################################################


# ----------------------------------------------------------------------- Buttons collapse
#
#
@app.callback(
    Output("buttons-submit", "is_open"),
    [Input("game-buttons", "value")],
)
def toggle_collapse(value):
    if value == 'hand-def' :
        return True
    return False

@app.callback(
    Output("buttons-plus", "is_open"),
    Output("buttons-minus", "is_open"),
    Output("buttons-refresh", "is_open"),
    [Input("value-dropdown", "value")],
)
def toggle_collapse(value):
    if value == 'dilation/erosion':
        return True, True, True

    return False, False, False
#########################################################################
#########################################################################
#########################################################################


# ----------------------------------------------------------------------- Sliders collapse
#
#
@app.callback(
    Output("collapse-img-slider", "is_open"),
    Output('collapse-img-slider-output-container', "is_open"),
    [Input("value-dropdown", "value")],
)
def toggle_collapse(value):
    if value != 'normal' and value != 'gauss' and value != 'up' and value != 'down':
        return True, True
    return False, False
#########################################################################
#########################################################################
#########################################################################


# ----------------------------------------------------------------------- Sliders
#
#
@app.callback(
    dash.dependencies.Output('img-slider-output-container', 'children'),
    dash.dependencies.Output('rule-slider-output-container', 'children'),
    dash.dependencies.Output('width-slider-output-container', 'children'),
    [dash.dependencies.Input('img-slider', 'value'),
     dash.dependencies.Input('rule-slider', 'value'),
     dash.dependencies.Input('value-dropdown', 'value'),
     dash.dependencies.Input('width-slider', 'value'), ])
def update_output(img_slider, rule, option, width):
    if option == 'dark':
        slider_name = 'shift'
    elif option == 'bright':
        slider_name = 'shift'
    else:
        slider_name = 'threshold'

    return '{}: {}'.format(slider_name, img_slider), 'rule: {}'.format(rule), 'width: {}'.format(width)
#########################################################################
#########################################################################
#########################################################################


# ----------------------------------------------------------------------- Image and histogram
#
#
@app.callback(
    Output(component_id='img', component_property='figure'),
    Output(component_id='hist', component_property='figure'),

    [Input(component_id='value-dropdown', component_property='value'),
     Input(component_id='img-dropdown', component_property='value'),
     Input(component_id='img-slider', component_property='value'),
     Input(component_id='minus', component_property='n_clicks'),
     Input(component_id='plus', component_property='n_clicks'),
     Input(component_id='refresh', component_property='n_clicks'),
     ],
    prevent_initial_call=False
)
def show_img(option, path, slider, minus, plus, refresh):
    data = np.array(Image.open(path).convert('L'))
    global img_global
    global plus_global
    global minus_global

    if option == 'normal':
        im = data

    if option == 'bright':
        bright = data.astype('float32')
        bright += slider
        bright = np.clip(bright, 0, 255)
        bright = bright.astype('uint8')
        im = Image.fromarray(bright)

    if option == 'dark':
        bright = data.astype('float32')
        bright -= slider
        bright = np.clip(bright, 0, 255)
        bright = bright.astype('uint8')
        im = Image.fromarray(bright)

    if option == 'binary':
        im = mg.binarize(data, slider)

    if option == 'dilation/erosion':
        if plus_global:
            img_global = mg.dilation(mg.binarize(img_global, slider))
        if minus_global:
            img_global = mg.erosion(mg.binarize(img_global, slider))
        im = img_global
        plus_global = False
        minus_global = False

    if option == 'up':
        im = mg.conv(data, kernel_up)

    if option == 'down':
        im = mg.conv(data, kernel_down)

    if option == 'gauss':
        im = mg.conv(data, kernel_gauss / 52)

    # count frequency of unique values
    frequencies = pd.DataFrame()
    (unique, counts) = np.unique(im, return_counts=True)
    frequencies['value'] = unique
    frequencies['counts'] = counts

    hist = px.histogram(frequencies, x='value', y='counts', nbins=255, template='plotly_dark',
                        color_discrete_sequence=['darkcyan'])
    hist.update_layout(title='RGB',
                       width=850,
                       font_color="cyan",
                       showlegend=False)

    fig = px.imshow(im, binary_string=True, template='plotly_dark')
    fig.update_layout(title=option,
                      width=850,
                      font_color="cyan",
                      margin=dict(l=0, r=0, b=0))

    return fig, hist
#########################################################################
#########################################################################
#########################################################################


# ----------------------------------------------------------------------- 1D cellular automata graph
#
#
@app.callback(
    Output(component_id='wagner', component_property='figure'),
    [dash.dependencies.Input('rule-slider', 'value'),
     dash.dependencies.Input('width-slider', 'value'),
     dash.dependencies.Input('r-buttons', 'value')])
def update_output(rule, width, option):
    canvas = px.imshow(mg.oneD_cellular_automata(rule, width, option), binary_string=True, template='plotly_dark')
    canvas.update_layout(title='rule {}'.format(rule),
                         width=850,
                         font_color="cyan",
                         margin=dict(l=0, r=0, b=0))
    return canvas
#########################################################################
#########################################################################
#########################################################################


# ----------------------------------------------------------------------- Game of life
#
#

@app.callback(
    Output("hidden-div-5", "children"),
    [Input('calculate', 'n_clicks')]
    , prevent_initial_call=True)
def refresh_refresh(click):
    global tensor
    random_size = (12, 12)
    rest_size = (12, 12)

    frames = 60
    random_grid = np.random.choice(2, random_size, p=[9/ 10, 1/ 10])

    unchanged_grid = np.zeros(rest_size)
    unchanged_grid[4][5] = 1
    unchanged_grid[4][6] = 1
    unchanged_grid[5][4] = 1
    unchanged_grid[5][7] = 1
    unchanged_grid[6][5] = 1
    unchanged_grid[6][6] = 1

    glider_grid = np.zeros(rest_size)
    glider_grid[4][5] = 1
    glider_grid[4][6] = 1
    glider_grid[5][4] = 1
    glider_grid[5][5] = 1
    glider_grid[6][6] = 1

    oscillator_grid = np.zeros(rest_size)
    oscillator_grid[3][5] = 1
    oscillator_grid[4][5] = 1
    oscillator_grid[5][5] = 1

    tensor[0] = mg.create_animation(random_size, random_grid, frames)
    tensor[1] = mg.create_animation(rest_size, oscillator_grid, frames)
    tensor[2] = mg.create_animation(rest_size, glider_grid, frames)
    tensor[3] = mg.create_animation(rest_size, unchanged_grid, frames)

    raise dash.exceptions.PreventUpdate("cancel the callback")

@app.callback(
    Output("hidden-div-9", "children"),
    [Input('submit', 'n_clicks')]
    , prevent_initial_call=True)
def refresh_refresh(click):
    global tensor
    global hand_grid
    size = (12, 12)
    tensor[4] = mg.create_animation(size, hand_grid , 60)
    raise dash.exceptions.PreventUpdate("cancel the callback")


@app.callback(
    Output("hidden-div-10", "children"),
    [Input('submit', 'n_clicks')]
    , prevent_initial_call=True)
def refresh_refresh(click):
    global tensor
    global hand_grid
    size = (12, 12)
    tensor[5] = mg.create_animation(size, hand_grid , 60)
    raise dash.exceptions.PreventUpdate("cancel the callback")


@app.callback(
    Output(component_id='game', component_property='figure'),
    [Input('interval-component', 'n_intervals'),
     Input('game-buttons', 'value'),
     Input('game', 'clickData')
     ])
def update_output(n_intervals, value, click):
    global n
    global tensor
    global play_global
    global game_buttons_global
    global hand_grid
    frames = 60

    if game_buttons_global != value: n = 0
    game_buttons_global = value

    if value == 'random':
        animation = tensor[0]
    if value == 'oscillator':
        animation = tensor[1]
    if value == 'glider':
        animation = tensor[2]
    if value == 'unchanged':
        animation = tensor[3]
    if value == 'hand-def':
        animation = tensor[4]

    if play_global and len(animation) > 0:
        if n > frames: n = 0
        grid = animation[n]
        n += 1

    else:
        if len(animation) > 0:
            grid = animation[n]
        elif value == 'hand-def': grid = hand_grid
        else:
            grid = np.zeros((12, 12))

    canvas = px.imshow(grid, binary_string=True, template='plotly_dark')
    canvas.update_layout(title='frame: {}'.format(n),
                         width=850,
                         font_color="cyan",
                         clickmode='event+select',
                         margin=dict(l=0, r=0, b=0))
    return canvas


@app.callback(
    Output(component_id='hidden-div-8', component_property='children'),
    [Input('game-buttons', 'value'),
     Input('game', 'clickData')])
def update_output(value, click):
    global hand_grid
    if value == 'hand-def' and click:
        x = click['points'][0]['x']
        y = click['points'][0]['y']
        if hand_grid[y, x] == 0: hand_grid[y, x] = 1
        else: hand_grid[y, x] = 0



    raise dash.exceptions.PreventUpdate("cancel the callback")


#########################################################################
#########################################################################
#########################################################################


#########################################################################
#########################################################################
#########################################################################


if __name__ == '__main__':
    app.run_server(debug=True)
