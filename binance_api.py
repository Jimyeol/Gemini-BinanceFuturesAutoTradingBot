import os
from dotenv import load_dotenv
load_dotenv()
import json
from binance.um_futures import UMFutures
from binance.error import ClientError
import pandas as pd
import pandas_ta as ta
import time
from binance.enums import *

# Binance Test Futures Connect Client
# um_futures_client = UMFutures(
#     key=os.getenv("BINANCE_TEST_NET_ACCESS_KEY"), 
#     secret=os.getenv("BINANCE_TEST_NET_SECRET_KEY"),
#     base_url="https://testnet.binancefuture.com")

um_futures_client = UMFutures(
    key=os.getenv("BINANCE_ACCESS_KEY"), 
    secret=os.getenv("BINANCE_SECREY_KEY"))


"""
----------------------------------------------------
내 잔고를 가져온다.
"""
def get_asset_summary():
    account_info = um_futures_client.balance()
    
    summary = []
    
    for asset in account_info:
        balance = float(asset.get("balance", 0))
        if balance != 0:
            summary.append({
                "accountAlias": asset.get("accountAlias"),
                "asset": asset.get("asset"),
                "balance": asset.get("balance"),
                "crossWalletBalance": asset.get("crossWalletBalance"),
                "crossUnPnl": asset.get("crossUnPnl"),
                "availableBalance": asset.get("availableBalance"),
                "maxWithdrawAmount": asset.get("maxWithdrawAmount"),
                "marginAvailable": asset.get("marginAvailable"),
                "updateTime": asset.get("updateTime")
            })
    
    return json.dumps(summary, indent=4)


"""
----------------------------------------------------
주어진 symbol에 대한 가격 정보를 반환하는 함수
"""
def get_coin_price(symbol):
    data = um_futures_client.ticker_price(symbol)
    result = {
        "symbol": data['symbol'],
        "price": data['price']
    }
    return json.dumps(result, indent=4)


"""
----------------------------------------------------
현재 포지션에서 필요한 정보를 추출하여 JSON으로 반환하는 함수

:param positions: 리스트 형태의 포지션 데이터
:return: 필요한 정보를 추출한 JSON 문자열
"""
def get_position_summary():
    try:
        account_data = um_futures_client.account()

        # 전체 계정 데이터를 필터링하여 필요한 부분만 추출
        summary = {
            "totalInitialMargin": account_data["totalInitialMargin"],
            "totalMaintMargin": account_data["totalMaintMargin"],
            "totalWalletBalance": account_data["totalWalletBalance"],
            "totalUnrealizedProfit": account_data["totalUnrealizedProfit"],
            "totalMarginBalance": account_data["totalMarginBalance"],
            "totalPositionInitialMargin": account_data["totalPositionInitialMargin"],
            "totalOpenOrderInitialMargin": account_data["totalOpenOrderInitialMargin"],
            "totalCrossWalletBalance": account_data["totalCrossWalletBalance"],
            "totalCrossUnPnl": account_data["totalCrossUnPnl"],
            "availableBalance": account_data["availableBalance"],
            "maxWithdrawAmount": account_data["maxWithdrawAmount"],
            "assets": [],
            "positions": []
        }

        # USDT 자산 정보만 추가
        for asset in account_data["assets"]:
            if asset["asset"] == "USDT":
                summary["assets"].append(asset)
                break  # USDT 정보만 추가하면 되므로 루프 종료

        # BTCUSDT 포지션 정보만 추가
        for position in account_data["positions"]:
            if position["symbol"] == "BTCUSDT":
                summary["positions"].append(position)
                break  # BTCUSDT 정보만 추가하면 되므로 루프 종료

        return json.dumps(summary, indent=4)
    except Exception as e:
        print(f"Error fetching account data: {e}")
        return None


# 바이낸스 선물 시장 주문서 데이터를 받아오는 함수
def get_order_book(symbol, limit):
    try:
        # 바이낸스 선물 API를 사용하여 주문서 데이터를 가져오기
        order_book = um_futures_client.depth(symbol=symbol, limit=limit)
        
        # 주문서 데이터를 JSON 형식으로 변환
        order_book_json = json.dumps(order_book, indent=4)
        
        return order_book_json
    except Exception as e:
        print(f"Error fetching order book data: {e}")
        return None


def get_open_orders(symbol="BTCUSDT"):
    try:
        open_orders = um_futures_client.get_orders()

        return json.dumps(open_orders, indent=4)
    except Exception as e:
        print(f"Error fetching open orders: {e}")
        return None


"""
----------------------------------------------------
바이낸스에서 봉 캔들 데이터를 가져옵니다.
"""
def get_candles(symbol, interval, limit):

    klines = um_futures_client.klines(
        symbol=symbol,
        interval=interval,
        limit=limit
    )
    
    # 데이터를 DataFrame으로 변환
    columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 
               'close_time', 'quote_asset_volume', 'number_of_trades', 
               'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore']
    df = pd.DataFrame(klines, columns=columns)
    df['close'] = df['close'].astype(float)
    return df


"""
----------------------------------------------------
바이낸스 캔들 데이터를 Json형태로 합쳐 반환 합니다.
"""
def get_candles_to_join(symbol, intervals, limit):
    combined_data = {}

    for interval in intervals:
        df = get_candles(symbol, interval, limit)
        candles_json = df.to_json(orient='records')
        combined_data[f"candles_{interval}"] = json.loads(candles_json)
    
    return json.dumps(combined_data, indent=4)


"""
----------------------------------------------------
주어진 DataFrame에 대해 RSI를 계산합니다.
"""
# 주어진 DataFrame에 대해 RSI를 계산하는 함수
def calculate_rsi(candles_df, period=14):
    df = candles_df.copy()
    df['RSI_14'] = ta.rsi(df['close'], length=period)
    result_df = df[['timestamp', 'close', 'RSI_14']]
    return result_df

# JSON 형식의 캔들 데이터를 받아 RSI를 계산하여 JSON으로 반환하는 함수
def get_rsi_data(candle_json, limit, period=14):
    candles_data = json.loads(candle_json)
    rsi_data = {}

    for key, candles in candles_data.items():
        df = pd.DataFrame(candles)
        df['close'] = df['close'].astype(float)
        rsi_df = calculate_rsi(df, period)
        rsi_df = rsi_df.tail(limit).copy()  # 마지막 limit 개수만큼의 데이터만 사용
        rsi_json = rsi_df.to_json(orient='records')
        rsi_data[f"rsi_14_{key.split('_')[-1]}"] = json.loads(rsi_json)
    
    return json.dumps(rsi_data, indent=4)

"""
----------------------------------------------------
주어진 DataFrame에 대해 이동 평균을 계산합니다.
"""
def calculate_moving_averages(candles_df, limit):
    df = candles_df.tail(limit).copy()
    
    df['MA_5'] = ta.sma(df['close'], length=5)
    df['MA_20'] = ta.sma(df['close'], length=20)
    df['MA_60'] = ta.sma(df['close'], length=60)
    df['MA_120'] = ta.sma(df['close'], length=120)
    df['MA_200'] = ta.sma(df['close'], length=200)
    
    result_df = df[['timestamp', 'close', 'MA_5', 'MA_20', 'MA_60', 'MA_120', 'MA_200']]
    return result_df

def get_moving_averages_data(candle_json, limit):
    candles_data = json.loads(candle_json)
    ma_data = {}

    for key, candles in candles_data.items():
        df = pd.DataFrame(candles)
        df['close'] = df['close'].astype(float)
        ma_df = calculate_moving_averages(df, limit)
        ma_json = ma_df.to_json(orient='records')
        ma_data[f"ma_{key.split('_')[-1]}"] = json.loads(ma_json)
    
    return json.dumps(ma_data, indent=4)


"""
----------------------------------------------------
주어진 DataFrame에 대해 MACD를 계산합니다.
"""
# 주어진 DataFrame에 대해 MACD를 계산하는 함수
def calculate_macd(candles_df, limit):
    df = candles_df.tail(limit).copy()
    
    macd = ta.macd(df['close'], fast=12, slow=26, signal=9)
    if macd is not None and 'MACD_12_26_9' in macd.columns and 'MACDs_12_26_9' in macd.columns and 'MACDh_12_26_9' in macd.columns:
        df['MACD'] = macd['MACD_12_26_9']
        df['Signal_Line'] = macd['MACDs_12_26_9']
        df['MACD_Histogram'] = macd['MACDh_12_26_9']
    else:
        df['MACD'] = None
        df['Signal_Line'] = None
        df['MACD_Histogram'] = None

    df['Cross'] = df.apply(
        lambda row: 'Golden Cross' if row['MACD'] is not None and row['Signal_Line'] is not None and row['MACD'] > row['Signal_Line'] else 
                    ('Dead Cross' if row['MACD'] is not None and row['Signal_Line'] is not None and row['MACD'] < row['Signal_Line'] else 'No Cross'), axis=1)
    
    result_df = df[['timestamp', 'close', 'MACD', 'Signal_Line', 'MACD_Histogram', 'Cross']]
    return result_df

# JSON 형식의 캔들 데이터를 받아 MACD를 계산하여 JSON으로 반환하는 함수
def get_macd_data(candle_json, limit):
    candles_data = json.loads(candle_json)
    macd_data = {}

    for key, candles in candles_data.items():
        df = pd.DataFrame(candles)
        df['close'] = df['close'].astype(float)
        macd_df = calculate_macd(df, limit)
        macd_json = macd_df.to_json(orient='records')
        macd_data[f"macd_{key.split('_')[-1]}"] = json.loads(macd_json)
    
    return json.dumps(macd_data, indent=4)


"""
----------------------------------------------------
주어진 DataFrame에 대해 볼린저 밴드를 계산합니다.
"""
# 주어진 DataFrame에 대해 볼린저 밴드를 계산하는 함수
def calculate_bollinger_bands(candles_df, limit):
    df = candles_df.tail(limit).copy()
    
    bollinger = ta.bbands(df['close'], length=20, std=2)
    if bollinger is not None and 'BBU_20_2.0' in bollinger.columns and 'BBM_20_2.0' in bollinger.columns and 'BBL_20_2.0' in bollinger.columns:
        df['Upper_Band'] = bollinger['BBU_20_2.0']
        df['Middle_Band'] = bollinger['BBM_20_2.0']
        df['Lower_Band'] = bollinger['BBL_20_2.0']
    else:
        df['Upper_Band'] = None
        df['Middle_Band'] = None
        df['Lower_Band'] = None

    result_df = df[['timestamp', 'close', 'Upper_Band', 'Middle_Band', 'Lower_Band']]
    return result_df

# JSON 형식의 캔들 데이터를 받아 볼린저 밴드를 계산하여 JSON으로 반환하는 함수
def get_bollinger_bands_data(candle_json, limit):
    candles_data = json.loads(candle_json)
    bollinger_data = {}

    for key, candles in candles_data.items():
        df = pd.DataFrame(candles)
        df['close'] = df['close'].astype(float)
        bollinger_df = calculate_bollinger_bands(df, limit)
        bollinger_json = bollinger_df.to_json(orient='records')
        bollinger_data[f"bollinger_{key.split('_')[-1]}"] = json.loads(bollinger_json)
    
    return json.dumps(bollinger_data, indent=4)


"""
----------------------------------------------------
주어진 심볼에 대한 Top Trader 롱/숏 비율(포지션)을 가져와 JSON으로 반환하는 함수
"""
# 주어진 심볼에 대해 top trader long/short ratio를 계산하는 함수
def get_top_trader_long_short_ratio(symbol, intervals, limit=1):
    long_short_data = {}
    
    for interval in intervals:
        try:
            long_short_ratio = um_futures_client.top_long_short_position_ratio(
                symbol=symbol,
                period=interval
            )
            
            # 필요한 데이터만 추출하여 DataFrame으로 변환
            # assuming the data is directly a list of dictionaries
            df = pd.DataFrame(long_short_ratio)
            df = df.tail(limit).copy()
            
            # 결과를 JSON 형식으로 변환
            result_json = df.to_json(orient='records')
            
            long_short_data[f"long_short_ratio_{interval}"] = json.loads(result_json)
        except Exception as e:
            print(f"Error fetching top trader long/short ratio for {interval}: {e}")
            long_short_data[f"long_short_ratio_{interval}"] = None
    
    # 현재 시간을 Unix 타임스탬프로 추가
    long_short_data["timestamp"] = int(time.time())
    
    return json.dumps(long_short_data, indent=4)


"""
----------------------------------------------------
주어진 심볼에 대한 최신 Funding Rate 정보를 가져와 JSON으로 반환하는 함수
"""
def get_latest_funding_rate(symbol):
    try:
        funding_rate_info = um_futures_client.funding_rate(
            symbol=symbol,
            limit=1
        )
        if funding_rate_info:
            latest_funding_rate = funding_rate_info[0]
            return json.dumps(latest_funding_rate, indent=4)
        else:
            return None
    except Exception as e:
        print(f"Error fetching funding rate info: {e}")
        return None


"""
----------------------------------------------------
슈퍼 트랜드
"""
# 주어진 DataFrame에 대해 슈퍼트렌드를 계산하는 함수
def calculate_supertrend(df, period=10, multiplier=3):
    df = df.copy()
    df['open'] = df['open'].astype(float)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    df['close'] = df['close'].astype(float)

    df['TR'] = ta.true_range(df['high'], df['low'], df['close'])
    df['ATR'] = ta.atr(df['high'], df['low'], df['close'], length=period)
    df['Upper_Band'] = ((df['high'] + df['low']) / 2) + (multiplier * df['ATR'])
    df['Lower_Band'] = ((df['high'] + df['low']) / 2) - (multiplier * df['ATR'])
    df['trend'] = 1  # 1 for long, -1 for short

    df.reset_index(drop=True, inplace=True)  # 인덱스를 재설정합니다

    for current in range(1, len(df.index)):
        previous = current - 1

        if df.loc[current, 'close'] > df.loc[previous, 'Upper_Band']:
            df.loc[current, 'trend'] = 1
        elif df.loc[current, 'close'] < df.loc[previous, 'Lower_Band']:
            df.loc[current, 'trend'] = -1
        else:
            df.loc[current, 'trend'] = df.loc[previous, 'trend']
            if df.loc[current, 'trend'] == 1 and df.loc[current, 'Lower_Band'] < df.loc[previous, 'Lower_Band']:
                df.loc[current, 'Lower_Band'] = df.loc[previous, 'Lower_Band']
            if df.loc[current, 'trend'] == -1 and df.loc[current, 'Upper_Band'] > df.loc[previous, 'Upper_Band']:
                df.loc[current, 'Upper_Band'] = df.loc[previous, 'Upper_Band']

    return df

# 주어진 DataFrame에 대해 매수/매도 신호를 생성하는 함수
def generate_signals(candles_df, limit):
    df = calculate_supertrend(candles_df.tail(limit))
    
    signals = []
    for current in range(1, len(df.index)):
        if df.loc[current, 'trend'] == 1 and df.loc[current - 1, 'trend'] == -1:
            signals.append({"signal": "long", "price": df.loc[current, 'close']})
        elif df.loc[current, 'trend'] == -1 and df.loc[current - 1, 'trend'] == 1:
            signals.append({"signal": "short", "price": df.loc[current, 'close']})
    
    # Return the most recent signal
    latest_signal = signals[-1] if signals else None
    return latest_signal

# JSON 형식의 캔들 데이터를 받아 슈퍼트렌드 신호를 생성하여 JSON으로 반환하는 함수
def get_supertrend_signals(candle_json, limit):
    candles_data = json.loads(candle_json)
    signals_data = {}

    for key, candles in candles_data.items():
        df = pd.DataFrame(candles)
        df['open'] = df['open'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        df['close'] = df['close'].astype(float)
        signal = generate_signals(df, limit)
        signals_data[f"supertrend_{key.split('_')[-1]}"] = signal
    
    return json.dumps(signals_data, indent=4)


# 주어진 DataFrame에 대해 스토캐스틱 오실레이터를 계산하는 함수
def calculate_stochastic_oscillator(candles_df, period=14, smooth_k=3, smooth_d=3):
    df = candles_df.copy()
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    df['close'] = df['close'].astype(float)

    # 스토캐스틱 오실레이터 계산
    stochastic = ta.stoch(df['high'], df['low'], df['close'], k=period, d=smooth_k, smooth_d=smooth_d)
    
    if stochastic is not None and 'STOCHk_14_3_3' in stochastic.columns and 'STOCHd_14_3_3' in stochastic.columns:
        df['%K'] = stochastic['STOCHk_14_3_3']
        df['%D'] = stochastic['STOCHd_14_3_3']
    else:
        df['%K'] = None
        df['%D'] = None
    
    result_df = df[['timestamp', 'close', '%K', '%D']]
    return result_df

# JSON 형식의 캔들 데이터를 받아 스토캐스틱 오실레이터를 계산하여 JSON으로 반환하는 함수
def get_stochastic_oscillator_data(candle_json, limit, period=14, smooth_k=3, smooth_d=3):
    candles_data = json.loads(candle_json)
    stochastic_data = {}

    for key, candles in candles_data.items():
        df = pd.DataFrame(candles)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        df['close'] = df['close'].astype(float)
        stochastic_df = calculate_stochastic_oscillator(df.tail(limit), period, smooth_k, smooth_d)
        stochastic_json = stochastic_df.to_json(orient='records')
        stochastic_data[f"stochastic_{key.split('_')[-1]}"] = json.loads(stochastic_json)
    
    return json.dumps(stochastic_data, indent=4)


# ----------Order---------------
#레버리지 설정
def set_leverage(symbol, leverage):
    try:
        response = um_futures_client.change_leverage(symbol=symbol, leverage=leverage)
        print(f"Leverage set to {leverage} for {symbol}: {response}")
    except Exception as e:
        print(f"Error setting leverage: {e}")

def get_balance():
    try:
        balance_info = um_futures_client.balance()
        for asset in balance_info:
            if asset['asset'] == 'USDT':
                return float(asset['balance'])
        return 0
    except Exception as e:
        print(f"Error fetching balance: {e}")
        return 0

def place_order(order_details):
    try:
        response = um_futures_client.new_order(**order_details)
        print(f"Order placed: {response}")
    except Exception as e:
        print(f"Error placing order: {e}")

def process_order(result):
    if 'type' in result['hold_order'] and result['hold_order']['type'] == 'hold':
        print("Holding position. No new orders will be placed.")
        return
    
    if 'type' in result['hold_order'] and result['hold_order']['type'] == 'close':
        print("Close All Position.")
        close_all_positions()
        return
    
    symbol = result['order']['symbol']
    leverage = result['order']['leverage']
    investment_percentage = result['order']['investment_percentage']
    side = result['order']['side']
    side_reverse = SIDE_SELL if side == SIDE_BUY else SIDE_BUY
    entry_price = result['order']['entryPrice']
    exit_price = result['order']['exitPrice']
    stoploss = result['order']['stoploss']
    
    # Set leverage
    set_leverage(symbol, leverage)
    
    # Calculate the quantity to order based on the investment percentage
    total_balance = get_balance()
    investment_amount = total_balance * (investment_percentage / 100)
    order_quantity = investment_amount / entry_price
    
    # Prepare the order details for entry
    entry_order_details = {
        "symbol": symbol,
        "side": side,
        "type": FUTURE_ORDER_TYPE_LIMIT,
        "timeInForce": TIME_IN_FORCE_GTC,
        "quantity": round(order_quantity, 3),
        "positionSide": "BOTH",
        "price": entry_price
    }

    # Place the entry order
    place_order(entry_order_details)

    # Delay to ensure orders are placed sequentially
    time.sleep(0.5)

    # Prepare the stop loss order details
    stop_loss_order_details = {
        "symbol": symbol,
        "side": side_reverse,
        "type": FUTURE_ORDER_TYPE_STOP_MARKET,
        "quantity": round(order_quantity, 3),
        "positionSide": "BOTH",
        "stopPrice": stoploss
    }

    # Place the stop loss order
    place_order(stop_loss_order_details)

    # Delay to ensure orders are placed sequentially
    time.sleep(0.5)

    # Prepare the exit order details
    exit_order_details = {
        "symbol": symbol,
        "side": side_reverse,
        "type": FUTURE_ORDER_TYPE_LIMIT,
        "timeInForce": TIME_IN_FORCE_GTC,
        "quantity": round(order_quantity, 3),
        "positionSide": "BOTH",
        "price": exit_price
    }
    
    place_order(exit_order_details)

def get_open_positions():
    try:
        positions = um_futures_client.account()['positions']
        open_positions = [pos for pos in positions if float(pos['positionAmt']) != 0]
        return open_positions
    except Exception as e:
        print(f"Error fetching open positions: {e}")
        return []

def close_position(symbol, side, quantity):
    try:
        response = um_futures_client.new_order(
            symbol=symbol,
            side=side,
            type=FUTURE_ORDER_TYPE_MARKET,
            quantity=quantity,
            reduceOnly=True
        )
        print(f"Closed position for {symbol}: {response}")
    except Exception as e:
        print(f"Error closing position for {symbol}: {e}")

def close_all_positions():
    open_positions = get_open_positions()
    for position in open_positions:
        symbol = position['symbol']
        quantity = abs(float(position['positionAmt']))
        side = SIDE_SELL if float(position['positionAmt']) > 0 else SIDE_BUY
        close_position(symbol, side, quantity)