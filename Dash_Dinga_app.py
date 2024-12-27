import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import asyncio
import websockets
import threading
from queue import Queue

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
    ]),
    dbc.Row([
        dbc.Col(dcc.Interval(id='interval-component', interval=500, n_intervals=0), className="mb-2")  # Update every 500ms
    ])
])

# WebSocket URL
ws_url = "ws://192.168.4.1/ws"

# Thread-safe queue to store live data
live_data_queue = Queue()

# Function to handle WebSocket communication
async def websocket_handler():
    async with websockets.connect(ws_url) as websocket:
        while True:
            message = await websocket.recv()
            live_data_queue.put(message)
            if live_data_queue.qsize() > 100:  # Limit the number of messages to 100
                live_data_queue.get()
                print(f"Received message: {message}")


# Function to send message to WebSocket
async def send_message(message):
    async with websockets.connect(ws_url) as websocket:
        await websocket.send(message)

# Start WebSocket handler in a separate thread
def start_websocket_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(websocket_handler())

threading.Thread(target=start_websocket_thread, daemon=True).start()

# Callback to update live data
@app.callback(Output('live-data', 'children'), [Input('interval-component', 'n_intervals')])
def update_live_data(n_intervals):
    live_data = []
    print(f"Interval triggered: {n_intervals}")
    print(f"Queue size: {live_data_queue.qsize()}")

    while not live_data_queue.empty():
        live_data.append(live_data_queue.get())
    print(f"Updating live-data with: {live_data}")
    return [html.Div(msg) for msg in live_data]

# Callback to handle button interactions
@app.callback([Output('interval-component', 'disabled')], 
              [Input('start-counter', 'n_clicks'), Input('stop-counter', 'n_clicks'), Input('start-motor-test', 'n_clicks')])
def handle_buttons(start_counter, stop_counter, start_motor_test):
    ctx = dash.callback_context
    if ctx.triggered:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if button_id == 'start-counter':
            threading.Thread(target=asyncio.run, args=(send_message("Task_counter_start"),)).start()
        elif button_id == 'stop-counter':
            threading.Thread(target=asyncio.run, args=(send_message("Task_counter_stop"),)).start()
        elif button_id == 'start-motor-test':
            threading.Thread(target=asyncio.run, args=(send_message("Motor_Test_Start"),)).start()

    return [False]  # Ensure interval is always enabled for live updates

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
