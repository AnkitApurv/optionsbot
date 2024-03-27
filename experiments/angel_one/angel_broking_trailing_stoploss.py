import websocket
import json
import threading
import time

# Angel Broking WebSocket API details
ws_url = 'wss://angelbroking.com/NestHtml5Mobile/socket/stream'

# Angel Broking API credentials
api_key = 'YOUR_API_KEY'
access_token = 'YOUR_ACCESS_TOKEN'
client_code = 'YOUR_CLIENT_CODE'

# Trailing stop loss parameters
trail_percentage = 0.5  # trailing stop loss percentage
update_interval = 10  # time interval in seconds to update the stop loss

# Function to send a JSON request to the WebSocket server
def send_request(ws, request):
    ws.send(json.dumps(request))

# Function to handle incoming messages from the WebSocket server
def on_message(ws, message):
    data = json.loads(message)
    if 'type' in data and data['type'] == 'marketData':
        symbol = data['exchange'] + ':' + data['symbol']
        ltp = float(data['ltp'])
        stop_loss = ltp - (ltp * trail_percentage / 100)
        print(f'{symbol} - LTP: {ltp:.2f}, Stop Loss: {stop_loss:.2f}')

        # Update the stop loss after every interval
        threading.Timer(update_interval, update_stop_loss, args=[ws, symbol, stop_loss]).start()

# Function to update the stop loss for a symbol
def update_stop_loss(ws, symbol, stop_loss):
    request = {
        'task': 'order',
        'action': 'modify',
        'exchange': symbol.split(':')[0],
        'symbol': symbol.split(':')[1],
        'order_id': '',  # Provide the order ID of the trade
        'client_code': client_code,
        'variety': 'NORMAL',
        'validity': 'DAY',
        'trigger_price': stop_loss
    }
    send_request(ws, request)

# Function to authenticate and subscribe to market data
def authenticate_and_subscribe(ws):
    request = {
        'task': 'cn',
        'channel': 'mw',
        'token': access_token,
        'user': api_key,
        'account': client_code
    }
    send_request(ws, request)

# WebSocket connection handler
def on_open(ws):
    print('Connected to WebSocket')
    authenticate_and_subscribe(ws)

# WebSocket error handler
def on_error(ws, error):
    print(f'Error: {error}')

# WebSocket close handler
def on_close(ws):
    print('Connection closed')

# Main function
def main():
    # Create and connect the WebSocket
    ws = websocket.WebSocketApp(ws_url,
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)

    # Start the WebSocket connection
    ws.run_forever()

if __name__ == '__main__':
    main()