import os
from dotenv import load_dotenv
load_dotenv()
import json
from binance.um_futures import UMFutures
from binance.error import ClientError

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

