import binance_api
import json

asset = json.loads(binance_api.get_asset_summary())
print("총 잔고: " + asset[0]["availableBalance"])

btc_price = json.loads(binance_api.get_coin_price("BTCUSDT"))
print("BTC Price: " + btc_price["price"])

current_position = json.loads(binance_api.get_position_summary())
print("symbol: " + current_position[0]["symbol"])
print("레버리지: " + current_position[0]["leverage"])
print("진입가격: " + current_position[0]["entryPrice"])
print("손익률: " + current_position[0]["unrealizedProfit"])
print("수량: " + current_position[0]["positionAmt"] + "BTC")

