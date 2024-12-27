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
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                background-color: #f0f0f0;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# WebSocket URL
default_ws_url = "ws://192.168.4.1/ws"
ws_url = default_ws_url

# Thread-safe queue to store live data
live_data_queue = Queue()

# Connection status
connection_status = "Not connected"

# Initialize task counters
task_counter_1 = 0
task_counter_2 = 0
task_counter_3 = 0

# Initialize encoder values
encoder1_ticks = 0
encoder2_ticks = 0

# Function to handle WebSocket communication
async def websocket_handler():
    global connection_status, task_counter_1, task_counter_2, task_counter_3, encoder1_ticks, encoder2_ticks
    try:
        async with websockets.connect(ws_url) as websocket:
            connection_status = "Connected"
            while True:
                message = await websocket.recv()
                live_data_queue.put(message)
                # Parse the message to extract task counters and encoder values
                if "task1Counter" in message or "encoder1Ticks" in message:
                    data = eval(message)
                    task_counter_1 = data.get("task1Counter", task_counter_1)
                    task_counter_2 = data.get("task2Counter", task_counter_2)
                    task_counter_3 = data.get("task3Counter", task_counter_3)
                    encoder1_ticks = data.get("encoder1Ticks", encoder1_ticks)
                    encoder2_ticks = data.get("encoder2Ticks", encoder2_ticks)
                if live_data_queue.qsize() > 100:  # Limit the number of messages to 100
                    live_data_queue.get()
    except Exception as e:
        connection_status = f"Not connected: {str(e)}"

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

# Persistent list to store all messages (history)
live_data_history = []

# Layout of the app
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Dinga -ESP32 : Websocket Dashboard"), className="mb-2")
    ]),
    dbc.Row([
        dbc.Col(html.Div("Input the IP address:"), width=2),
        dbc.Col(dcc.Input(id='ip-address', type='text', placeholder='Enter IP address', value='192.168.4.1'), width=4),
        dbc.Col(dbc.Button("Connect", id='connect-button', color="primary"), width=2),
        dbc.Col(html.Div(id='connection-status', children=connection_status), width=4)
    ],className="mb-2"),
    dbc.Row([
        dbc.Col(dbc.Button("Get Task Counter", id='get-task-counter', color="secondary"), className="mb-2"),
        dbc.Col(dbc.Button("Stop Task Counter", id='stop-task-counter', color="secondary"), className="mb-2"),
        dbc.Col(html.Div(id='task-counter-1', children="Task Counter 1: 0", style={'border': '2px solid #000', 'padding': '10px', 'border-radius': '5px'}), width=2),
        dbc.Col(html.Div(id='task-counter-2', children="Task Counter 2: 0", style={'border': '2px solid #000', 'padding': '10px', 'border-radius': '5px'}), width=2),
        dbc.Col(html.Div(id='task-counter-3', children="Task Counter 3: 0", style={'border': '2px solid #000', 'padding': '10px', 'border-radius': '5px'}), width=2)
    ]),
    dbc.Row([
        dbc.Col(html.Hr(), className="mb-2")
    ]),
    dbc.Row([
        dbc.Col(dbc.Button("Start Motor Test", id='start-motor-test', color="primary"), className="mb-2"),
        dbc.Col(dbc.Button("Forward", id='forward-button', color="primary", size="sm"), className="mb-2"),
        dbc.Col(dbc.Button("Reverse", id='reverse-button', color="primary", size="sm"), className="mb-2"),
        dbc.Col(dbc.Button("Left", id='left-button', color="primary", size="sm"), className="mb-2"),
        dbc.Col(dbc.Button("Right", id='right-button', color="primary", size="sm"), className="mb-2"),
        dbc.Col(dbc.Button("Stop", id='stop-button', color="danger", size="sm"), className="mb-2")
    ]),
    dbc.Row([
        dbc.Col(html.Div(id='encoder-1', children="Encoder 1 Ticks: 0", style={'border': '2px solid #000', 'padding': '10px', 'border-radius': '5px'}), width=2),
        dbc.Col(html.Div(id='encoder-2', children="Encoder 2 Ticks: 0", style={'border': '2px solid #000', 'padding': '10px', 'border-radius': '5px'}), width=2)
    ]),
    dbc.Row([
        dbc.Col(html.Hr(), className="mb-2")
    ]),
    dbc.Row([
        dbc.Col(dcc.Interval(id='interval-component', interval=500, n_intervals=0), className="mb-2")  # Update every 500ms
    ]),
    dbc.Row([
        dbc.Col(html.Div(id='live-data', style={'height': '300px', 'overflowY': 'scroll', 'border': '1px solid #ccc'}), className="mb-2")
    ])
], style={'backgroundColor': '#f0f0f0'})  # Light grey background color

# Callback to update live data
@app.callback(Output('live-data', 'children'), [Input('interval-component', 'n_intervals')])
def update_live_data(n_intervals):
    global live_data_history

    # Collect new messages from the queue
    new_messages = []
    while not live_data_queue.empty():
        new_messages.append(live_data_queue.get())

    # Add new messages to the top of the history
    live_data_history = new_messages + live_data_history

    # Optionally, limit the history size (e.g., keep only the latest 100 messages)
    max_history_size = 100
    if len(live_data_history) > max_history_size:
        live_data_history = live_data_history[:max_history_size]

    # Return the updated log with the latest message on top
    return [html.Div(msg) for msg in live_data_history]

# Callback to update task counters
@app.callback(
    [Output('task-counter-1', 'children'), Output('task-counter-2', 'children'), Output('task-counter-3', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_task_counters(n_intervals):
    global task_counter_1, task_counter_2, task_counter_3
    return [
        html.Div(["Task Counter 1: ", html.B(task_counter_1)]),
        html.Div(["Task Counter 2: ", html.B(task_counter_2)]),
        html.Div(["Task Counter 3: ", html.B(task_counter_3)])
    ]

# Callback to update encoder values
@app.callback(
    [Output('encoder-1', 'children'), Output('encoder-2', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_encoders(n_intervals):
    global encoder1_ticks, encoder2_ticks
    return [
        html.Div(["Encoder 1 Ticks: ", html.B(encoder1_ticks)]),
        html.Div(["Encoder 2 Ticks: ", html.B(encoder2_ticks)])
    ]

# Callback to handle button interactions
@app.callback([Output('interval-component', 'disabled')], 
              [Input('get-task-counter', 'n_clicks'), Input('stop-task-counter', 'n_clicks'), Input('start-motor-test', 'n_clicks'),
               Input('forward-button', 'n_clicks'), Input('reverse-button', 'n_clicks'), Input('left-button', 'n_clicks'), 
               Input('right-button', 'n_clicks'), Input('stop-button', 'n_clicks')])
def handle_buttons(get_task_counter, stop_task_counter, start_motor_test, forward, reverse, left, right, stop):
    ctx = dash.callback_context
    if ctx.triggered:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if button_id == 'get-task-counter':
            threading.Thread(target=asyncio.run, args=(send_message("Task_counter_start"),)).start()
        elif button_id == 'stop-task-counter':
            threading.Thread(target=asyncio.run, args=(send_message("Task_counter_stop"),)).start()
        elif button_id == 'start-motor-test':
            threading.Thread(target=asyncio.run, args=(send_message("Motor_Test_Start"),)).start()
        elif button_id == 'forward-button':
            threading.Thread(target=asyncio.run, args=(send_message("W"),)).start()
        elif button_id == 'reverse-button':
            threading.Thread(target=asyncio.run, args=(send_message("S"),)).start()
        elif button_id == 'left-button':
            threading.Thread(target=asyncio.run, args=(send_message("A"),)).start()
        elif button_id == 'right-button':
            threading.Thread(target=asyncio.run, args=(send_message("D"),)).start()
        elif button_id == 'stop-button':
            threading.Thread(target=asyncio.run, args=(send_message("X"),)).start()

    return [False]  # Ensure interval is always enabled for live updates

# Callback to handle IP address input and connect button
@app.callback(Output('connection-status', 'children'), [Input('connect-button', 'n_clicks')], [dash.dependencies.State('ip-address', 'value')])
def update_ws_url(n_clicks, ip_address):
    global ws_url, connection_status
    if n_clicks:
        ws_url = f"ws://{ip_address}/ws"
        threading.Thread(target=start_websocket_thread, daemon=True).start()
    return connection_status

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
