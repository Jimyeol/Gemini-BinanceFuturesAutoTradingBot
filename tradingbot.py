import binance_api
import json
import alternative

asset = json.loads(binance_api.get_asset_summary())
print("총 잔고: " + asset[0]["availableBalance"])

btc_price = json.loads(binance_api.get_coin_price("BTCUSDT"))
print("BTC Price: " + btc_price["price"])

current_position = json.loads(binance_api.get_position_summary())
print("심볼: " + current_position[0]["symbol"])
print("레버리지: " + current_position[0]["leverage"])
print("진입가격: " + current_position[0]["entryPrice"])
print("손익률: " + current_position[0]["unrealizedProfit"])
print("수량: " + current_position[0]["positionAmt"] + "BTC")

fear_greed_index = json.loads(alternative.get_fear_and_greed_index())
print("탐욕 값: " + fear_greed_index["data"][0]["value"])
print("탐욕 지수: " + fear_greed_index["data"][0]["value_classification"])