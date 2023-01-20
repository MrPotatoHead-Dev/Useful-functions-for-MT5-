import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
import config

# establish a connection & login to DEMO account
mt5.initialize()
mt5.login(
    config.MT5_ACCOUNT_NUM, password=config.MT5_ACCOUNT_PASS, server="MetaQuotes-Demo"
)


# ************************************* Useful variables *******************************************
symbol = "XAGUSD"
timeframe = mt5.TIMEFRAME_M15  # use this format
num_bars = 20
side = True  # NOTE in the future side will be true for long, Flase for short
lot = 0.1
position_id = None
sl = 0.002
tp = 0.003
entry = 1.23615


def get_df(symbol=symbol, timeframe=timeframe, num_bars=num_bars):
    utc_now = datetime.now()
    df = mt5.copy_rates_from(symbol, timeframe, utc_now, num_bars)
    df = pd.DataFrame(df)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    df["time"] = pd.to_datetime(df["time"], format="%Y-%m-%d %H:%M")
    return df


def bid_ask(symbol=symbol):

    ask = mt5.symbol_info_tick(symbol).ask
    bid = mt5.symbol_info_tick(symbol).bid
    return bid, ask


price = bid_ask()[0]
bid = bid_ask()[0]
ask = bid_ask()[1]
print(f"this is the bid {bid} ask {ask} ")


# for market orders use this
def request_order(symbol=symbol, lot=lot, side=side):
    # static values used in the order request
    # filling_mode = mt5.symbol_info(symbol).filling_mode - 1
    # Initialize the connection if there is not
    if mt5.initialize() == False:
        mt5.initialize()
    point = mt5.symbol_info(symbol).point
    print(point)

    deviation = 20  # slippage
    if side == True:
        trade_type = mt5.ORDER_TYPE_BUY
        price = bid_ask()[1]
        sl = price - 4  # 20pip stoploss
        tp = price + 4
    if side == False:
        trade_type = mt5.ORDER_TYPE_SELL
        price = bid_ask()[0]
        sl = price + 4  # 20pip stoploss
        tp = price - 4
    else:
        print("Error: the side of the request wasnt specified")
    print(price)
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": trade_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": deviation,
        "magic": 234000,
        "comment": "python script open",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN,
    }
    result = mt5.order_send(request)
    position_id = result.order
    print(position_id)
    if position_id == 0:
        print("Error when sending order request")
        return position_id


def close_postion(side=side, lot=lot, position_id=position_id):
    # NOTE not working. Its not closing positions
    # static values used in the order request
    # Initialize the connection if there is not
    if mt5.initialize() == False:
        mt5.initialize()
    deviation = 20  # slippage
    if side == True:
        trade_type = mt5.ORDER_TYPE_SELL
        price = bid_ask()[0]

    if side == False:
        trade_type = mt5.ORDER_TYPE_BUY
        price = bid_ask()[1]

    else:
        print("Error: the side of the close wasnt specified")

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,  # float
        "type": trade_type,
        "position": position_id,  # from the order
        "price": price,
        "deviation": deviation,
        "magic": 234000,
        "comment": "python script open",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN,
    }
    result = mt5.order_send(request)
    position_id = result.order
    print(position_id)
    if position_id == 0:
        print("Error: order didnt close")


"""Returns the open positions"""


def open_positions():

    # Initialize the connection if there is not
    if mt5.initialize() == False:
        mt5.initialize()

    # Define the name of the columns that we will create
    colonnes = ["ticket", "position", "symbol", "volume"]

    # Go take the current open trades
    current = mt5.positions_get()

    # Create a empty dataframe
    summary = pd.DataFrame()

    # Loop to add each row in dataframe
    # (Can be ameliorate using of list of list)
    for element in current:
        element_pandas = pd.DataFrame(
            [element.ticket, element.type, element.symbol, element.volume],
            index=colonnes,
        ).transpose()
        summary = pd.concat((summary, element_pandas), axis=0)

    return summary


def market_order(symbol, lot, sl=sl, tp=tp, buy=True, id_position=None):
    """Send the order requests"""

    # Initialize the connection if there is not
    if mt5.initialize() == False:
        mt5.initialize()

    # get filling mode from symbol info
    filling_mode = mt5.symbol_info(symbol).filling_mode - 1

    # bid ask price
    bid_price = mt5.symbol_info_tick(symbol).bid
    ask_price = mt5.symbol_info_tick(symbol).ask

    # Take the point of the asset
    point = mt5.symbol_info(symbol).point

    deviation = 20  # mt5.getSlippage(symbol)

    if id_position == None:

        # Buy order Parameters
        if buy:
            type_trade = mt5.ORDER_TYPE_BUY
            sl = ask_price - sl
            tp = ask_price + tp
            price = ask_price

        # Sell order Parameters
        else:
            type_trade = mt5.ORDER_TYPE_SELL
            sl = bid_price + sl
            tp = bid_price - tp
            price = bid_price

        # Open the trade
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": type_trade,
            "price": price,
            "deviation": deviation,
            "sl": sl,
            "tp": tp,
            "magic": 234000,
            "comment": "python script order",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": filling_mode,
        }
        # send a trading request
        result = mt5.order_send(request)
        result_comment = result.comment
        position_id = result.order
        return position_id


def limit_order(symbol, lot, sl=sl, tp=tp, entry=entry, buy=True, id_position=None):

    # Initialize the connection if there is not
    if mt5.initialize() == False:
        mt5.initialize()

    # get filling mode from symbol info
    filling_mode = mt5.symbol_info(symbol).filling_mode - 1

    # bid ask price

    # Take the point of the asset
    point = mt5.symbol_info(symbol).point

    deviation = 20  # mt5.getSlippage(symbol)

    if id_position == None:

        # Buy order Parameters
        if buy:
            type_trade = mt5.ORDER_TYPE_BUY_LIMIT
            sl = entry - sl
            tp = entry + tp
            price = entry

        # Sell order Parameters
        else:
            type_trade = mt5.ORDER_TYPE_SELL_LIMIT
            sl = entry + sl
            tp = entry - tp
            price = entry

        # Open the trade
        request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": symbol,
            "volume": lot,
            "type": type_trade,
            "price": price,
            "deviation": deviation,
            "sl": sl,
            "tp": tp,
            "magic": 234000,
            "comment": "python script order",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": filling_mode,
        }
        # send a trading request

        result = mt5.order_send(request)
        result_comment = result.comment
        position_id = result.order


# def get_data(symbol==symbol, timeframe==timeframe, num_bars==num_bars):


# shut down connection to the MetaTrader 5 terminal
mt5.shutdown()
