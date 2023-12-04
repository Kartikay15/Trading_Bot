import os
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce, QueryOrderStatus
from alpaca.trading.requests import GetOrdersRequest
from dotenv import load_dotenv, dotenv_values

config=dotenv_values(".env")

# paper = True enables paper trading
trading_client = TradingClient(config['API_KEY'], config['SECRET_KEY'], paper=True)

# Get and print account Details
account = dict(trading_client.get_account())
print()
for k,v in account.items():
  print(f"{k:30}{v}")

# Function to create and place order
def place_order(trading_client, symbol, qty, side):
  market_order_data = MarketOrderRequest(
        symbol=symbol,
        qty=qty,
        side=side,
        time_in_force=TimeInForce.DAY
        )

# Preparing Market order
  market_order = trading_client.submit_order(
        order_data=market_order_data
        )

# Function to cancel all open orders
def cancel_all_orders(trading_client):
    cancel_statuses = trading_client.cancel_orders()
    print(cancel_statuses)

# Function to get all orders
def get_orders(trading_client, status, side):
   # params to filter orders by
    request_params = GetOrdersRequest(
                    status=status,
                    side=side
                 )
    # orders that satisfy params
    orders = trading_client.get_orders(filter=request_params)
    print(orders)

# Place the order
place_order('AAPL',20,OrderSide.BUY)
place_order('SPY',10,OrderSide.BUY)

# Get Orders
get_orders(QueryOrderStatus.OPEN,OrderSide.BUY)