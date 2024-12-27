# Dash WebSocket Live Data App

This Dash application connects to a WebSocket server to display live data and provides interactive controls to send commands to the server. The app is built using Python, Dash, and Bootstrap for styling.

## Features

- **Live Data Display**: Continuously receives and displays live data from a WebSocket server.
- **Interactive Controls**: Includes buttons to send specific commands to the WebSocket server.
  - Start Counter
  - Stop Counter
  - Start Motor Test
- **Task Counters and Encoder Values**: Displays task counters and encoder values updated in real-time.
- **Connection Status**: Shows the current connection status to the WebSocket server.

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/your-username/your-repository-name.git
   cd your-repository-name

Install the required Python packages:
Usage
Run the Dash app:

Open your web browser and navigate to http://127.0.0.1:8050 to view the app.

Code Overview
Dash App Initialization: The app is initialized with Bootstrap for styling.
Layout: The layout includes a header, connection status, live data display, and interactive buttons.
WebSocket Handler: An asynchronous function handles WebSocket communication and updates the live data.
Callbacks: Dash callbacks update the live data display, task counters, encoder values, and connection status.
Contributing
Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

License
This project is licensed under the MIT License. See the LICENSE file for details.
