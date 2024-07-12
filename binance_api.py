import os
from dotenv import load_dotenv
load_dotenv()
import json
from binance.um_futures import UMFutures
from binance.error import ClientError
import pandas as pd
import pandas_ta as ta

# Binance Test Futures Connect Client
um_futures_client = UMFutures(
    key=os.getenv("BINANCE_TEST_NET_ACCESS_KEY"), 
    secret=os.getenv("BINANCE_TEST_NET_SECRET_KEY"),
    base_url="https://testnet.binancefuture.com")


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
    accountData = um_futures_client.account()
    positions = [position for position in accountData['positions'] if float(position['positionAmt']) != 0]
    summary = []

    for position in positions:
        summary.append({
            "symbol": position.get("symbol"),
            "leverage": position.get("leverage"),
            "isolated": position.get("isolated"),
            "entryPrice": position.get("entryPrice"),
            "unrealizedProfit": position.get("unrealizedProfit"),
            "positionAmt": position.get("positionAmt")
        })

    return json.dumps(summary, indent=4)

"""
----------------------------------------------------
바이낸스에서 4시간 봉 캔들 데이터를 가져옵니다.
"""
def get_4h_candles(symbol, limit=100):

    klines = um_futures_client.klines(
        symbol=symbol,
        interval='4h',
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
주어진 DataFrame에 대해 RSI를 계산합니다.
"""
def calculate_rsi(symbol, limit, period=14):
    df = get_4h_candles(symbol, limit)

    df['RSI_14'] = ta.rsi(df['close'], length=period)
    
    # 필요한 열만 선택
    result_df = df[['timestamp', 'close', 'RSI_14']]
    
    # 결과를 JSON 형식으로 변환
    result_json = result_df.to_json(orient='records')
    return result_json

"""
----------------------------------------------------
주어진 DataFrame에 대해 이동 평균을 계산합니다.
"""
def calculate_moving_averages(symbol, limit):
    df = get_4h_candles(symbol, limit)
    
    df['MA_5'] = ta.sma(df['close'], length=5)
    df['MA_20'] = ta.sma(df['close'], length=20)
    df['MA_60'] = ta.sma(df['close'], length=60)
    df['MA_120'] = ta.sma(df['close'], length=120)
    df['MA_200'] = ta.sma(df['close'], length=200)
    
    # 필요한 열만 선택
    result_df = df[['timestamp', 'close', 'MA_5', 'MA_20', 'MA_60', 'MA_120', 'MA_200']]
    
    # 결과를 JSON 형식으로 변환
    result_json = result_df.to_json(orient='records')
    
    return result_json


"""
----------------------------------------------------
주어진 DataFrame에 대해 MACD를 계산합니다.
"""
def calculate_macd(symbol, limit):
    df = get_4h_candles(symbol, limit)
    
    # MACD 계산
    macd = ta.macd(df['close'], fast=12, slow=26, signal=9)
    df['MACD'] = macd['MACD_12_26_9']
    df['Signal_Line'] = macd['MACDs_12_26_9']
    df['MACD_Histogram'] = macd['MACDh_12_26_9']

    # 골든크로스와 데드크로스 체크
    df['Cross'] = df.apply(lambda row: 'Golden Cross' if row['MACD'] > row['Signal_Line'] else ('Dead Cross' if row['MACD'] < row['Signal_Line'] else 'No Cross'), axis=1)
    
    result_df = df[['timestamp', 'close', 'MACD', 'Signal_Line', 'MACD_Histogram', 'Cross']]
    result = result_df.to_json(orient='records')
    return result


"""
----------------------------------------------------
주어진 DataFrame에 대해 볼린저 밴드를 계산합니다.
"""
def calculate_bollinger_bands(symbol, limit):
    df = get_4h_candles(symbol, limit)
    
    # 볼린저 밴드 계산
    bollinger = ta.bbands(df['close'], length=20, std=2)
    df['Upper_Band'] = bollinger['BBU_20_2.0']
    df['Middle_Band'] = bollinger['BBM_20_2.0']
    df['Lower_Band'] = bollinger['BBL_20_2.0']

    result_df = df[['timestamp', 'close', 'Upper_Band', 'Middle_Band', 'Lower_Band']]
    result = result_df.to_json(orient='records')
    return result


"""
----------------------------------------------------
주어진 심볼에 대한 Top Trader 롱/숏 비율(포지션)을 가져와 JSON으로 반환하는 함수
"""
def get_top_trader_long_short_ratio(symbol, limit=100, period="4h"):
    try:
        long_short_ratio = um_futures_client.top_long_short_position_ratio(
            symbol=symbol,
            period=period
        )
        return json.dumps(long_short_ratio, indent=4)
    except Exception as e:
        print(f"Error fetching top trader long/short ratio: {e}")
        return None
    

"""
----------------------------------------------------
주어진 심볼에 대한 Funding Rate 정보를 가져와 JSON으로 반환하는 함수
"""
"""
----------------------------------------------------
주어진 심볼에 대한 최신 Funding Rate 정보를 가져와 JSON으로 반환하는 함수
"""
def get_latest_funding_rate(symbol):
    try:
        funding_rate_info = um_futures_client.funding_rate(
            symbol=symbol,
            limit=1  # 가장 최신의 하나만 가져오기 위해 limit를 1로 설정
        )
        if funding_rate_info:
            latest_funding_rate = funding_rate_info[0]  # 리스트의 첫 번째 요소가 최신 정보
            return json.dumps(latest_funding_rate, indent=4)
        else:
            return None
    except Exception as e:
        print(f"Error fetching funding rate info: {e}")
        return None