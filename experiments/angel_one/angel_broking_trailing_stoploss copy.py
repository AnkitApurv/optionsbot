import websocket
import json
import talib
import requests

# write a python script which uses angel broking's websocket api to execute options trading and ta-lib to calculate EMA, 
# Following should be algorithm's conditions:
# 1. Entry conditions for placing an options Call:
# a. EMA 20 from 2 minutes ago > EMA 10 from 2 minutes ago
# b. EMA 20 from 1 minute ago < EMA 10 from 1 minute ago
# c. EMA 20 at the moment < EMA 10 at the moment
# d. Strike At the Money
# 2. Condition to exit from the call option: Trailing stoploss of INR 500/-
# 3. Condition to stop trading for the day: keep track of total profit/loss of the day, when profit crosses INR 3000/-, place a trailing stoploss of INR 1000/-

# Angel Broking WebSocket API details
ws_url = 'wss://angelbroking.com/NestHtml5Mobile/socket/stream'

# Angel Broking API credentials
api_key = 'YOUR_API_KEY'
access_token = 'YOUR_ACCESS_TOKEN'
client_code = 'YOUR_CLIENT_CODE'

# Trading parameters
strike_price = 1000  # At the money strike price
trailing_stop_loss = 500  # Trailing stop loss amount
stop_loss_limit = 1000  # Stop loss limit for the day
profit_limit = 3000  # Profit limit for the day

# TA-Lib parameters
ema_period = 10
ema_slow_period = 20

# Global variables
current_profit_loss = 0
in_trade = False
trade_order_id = None

# Function to send a JSON request to the WebSocket server
def send_request(ws, request):
    ws.send(json.dumps(request))

# Function to calculate the EMA for a given period and data
def calculate_ema(period, data):
    return talib.EMA(data, timeperiod=period)[-1]

# Function to place an options order
def place_options_order(symbol, transaction_type, quantity, price):
    order_data = {
        "variety": "NORMAL",
        "tradingsymbol": symbol,
        "symboltoken": get_symbol_token(symbol),
        "transactiontype": transaction_type,
        "exchange": "NSE",
        "ordertype": "LIMIT",
        "producttype": "INTRADAY",
        "duration": "DAY",
        "price": price,
        "quantity": quantity,
        "triggerprice": 0,
        "disclosedquantity": 0,
        "isclosed": False,
        "marketProtection": 0
    }
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }
    response = requests.post(place_order_url, json=order_data, headers=headers)
    if response.status_code == 200:
        return response.json()['data']['oms_order_id']
    else:
        print('Failed to place order!')
        return None

# Function to update the stop loss for an options order
def update_stop_loss(order_id, stop_loss):
    order_data = {
        "variety": "NORMAL",
        "orderid": order_id,
        "triggerprice": stop_loss
    }
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }
    response = requests.put(place_order_url, json=order_data, headers=headers)
    if response.status_code != 200:
        print('Failed to update stop loss!')

# Function to check the trading conditions and place options order
def check_and_place_order(ws, symbol, data):
    global in_trade
    global trade_order_id

    ema_20_2min_ago = calculate_ema(ema_slow_period, data[-3:-1])  # EMA 20 from 2 minutes ago
    ema_10_2min_ago = calculate_ema(ema_period, data[-3:-1])  # EMA 10 from 2 minutes ago
    ema_20_1min_ago = calculate_ema(ema_slow_period, data[-2:])  # EMA 20 from 1 minute ago
    ema_10_1min_ago = calculate_ema(ema_period, data[-2:])  # EMA 10 from 1 minute ago
    ema_20_now = calculate_ema(ema_slow_period, data)  # EMA 20 at the moment
    ema_10_now = calculate_ema(ema_period, data)  # EMA 10 at the moment

    # Entry conditions for placing an options Call
    if ema_20_2min_ago > ema_10_2min_ago and ema_20_1min_ago < ema_10_1min_ago and ema_20_now < ema_10_now:
        if not in_trade:
            # Place options order
            trade_order_id = place_options_order(symbol, 'BUY', 1, strike_price)
            if trade_order_id:
                in_trade = True
                print(f'Options order placed: {symbol} - Entry Price: {strike_price}')
        else:
            # Update stop loss
            stop_loss = strike_price - trailing_stop_loss
            update_stop_loss(trade_order_id, stop_loss)
            print(f'Stop loss updated: {stop_loss}')

# Function to handle incoming messages from the WebSocket server
def on_message(ws, message):
    data = json.loads(message)
    if 'type' in data and data['type'] == 'marketData':
        symbol = data['exchange'] + ':' + data['symbol']
        ltp = float(data['ltp'])

        # Add the latest price to the data array
        data.append(ltp)

        # Check and place options order
        check_and_place_order(ws, symbol, data)

        # Check stop loss and profit limit
        check_stop_loss(data[-1])
        check_profit_limit(data[-1])

# Function to get the symbol token
def get_symbol_token(symbol):
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }
    response = requests.get(base_url + '/rest/secure/angelbroking/search/scripts', headers=headers)
    if response.status_code == 200:
        symbols = response.json()
        for s in symbols:
            if s['symbol'].lower() == symbol.lower():
                return s['symboltoken']
        print('Symbol not found!')
    else:
        print('Failed to fetch symbol tokens!')

# Function to check the stop loss and exit the options trade if reached
def check_stop_loss(ltp):
    global in_trade
    global trade_order_id

    if in_trade:
        stop_loss = strike_price - trailing_stop_loss
        if ltp <= stop_loss:
            # Exit the trade
            print(f'Stop loss hit! Exiting trade: {stop_loss}')
            in_trade = False
            trade_order_id = None

# Function to check the profit limit and stop trading for the day if reached
def check_profit_limit(ltp):
    global current_profit_loss
    global in_trade

    if in_trade:
        current_profit_loss += (ltp - strike_price)
        if current_profit_loss >= profit_limit:
            # Place stop loss order
            stop_loss = strike_price - stop_loss_limit
            update_stop_loss(trade_order_id, stop_loss)
            print(f'Profit limit reached! Placed stop loss: {stop_loss}')
            in_trade = False
            trade_order_id = None

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
