import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import asyncio
import websockets
import threading

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout of the app
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Live Data from WebSocket"), className="mb-2")
    ]),
    dbc.Row([
        dbc.Col(html.Div(id='live-data', style={'height': '300px', 'overflowY': 'scroll', 'border': '1px solid #ccc'}), className="mb-2")
    ]),
    dbc.Row([
        dbc.Col(dbc.Button("Start Counter", id='start-counter', color="primary"), className="mb-2"),
        dbc.Col(dbc.Button("Stop Counter", id='stop-counter', color="danger"), className="mb-2"),
        dbc.Col(dbc.Button("Start Motor Test", id='start-motor-test', color="success"), className="mb-2")
    ])
])

# WebSocket URL
ws_url = "ws://192.168.4.1/ws"

# Global variable to store live data
live_data = []

# Function to handle WebSocket communication
async def websocket_handler():
    global live_data
    async with websockets.connect(ws_url) as websocket:
        while True:
            message = await websocket.recv()
            live_data.append(message)
            if len(live_data) > 100:  # Limit the number of messages to 100
                live_data.pop(0)

# Start WebSocket handler in a separate thread
def start_websocket_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(websocket_handler())

threading.Thread(target=start_websocket_thread, daemon=True).start()

# Callback to update live data
@app.callback(Output('live-data', 'children'), [Input('start-counter', 'n_clicks'),
                                                Input('stop-counter', 'n_clicks'),
                                                Input('start-motor-test', 'n_clicks')])
def update_live_data(start_counter, stop_counter, start_motor_test):
    ctx = dash.callback_context

    if not ctx.triggered:
        button_id = 'No clicks yet'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'start-counter':
        asyncio.run(send_message("Task_counter_start"))
    elif button_id == 'stop-counter':
        asyncio.run(send_message("Task_counter_stop"))
    elif button_id == 'start-motor-test':
        asyncio.run(send_message("Motor_Test_Start"))

    return [html.Div(msg) for msg in live_data]

# Function to send message to WebSocket
async def send_message(message):
    async with websockets.connect(ws_url) as websocket:
        await websocket.send(message)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)