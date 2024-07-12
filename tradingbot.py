import binance_api
import json
import alternative
import util

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

rsi = binance_api.calculate_rsi("BTCUSDT", 100)
# util.save_json_to_file("calculate_rsi", rsi)

ma = binance_api.calculate_moving_averages("BTCUSDT", 1000)
# util.save_json_to_file("calculate_moving_averages", ma)

macd = binance_api.calculate_macd("BTCUSDT", 500)
# util.save_json_to_file("calculate_macd", macd)

bb = binance_api.calculate_bollinger_bands("BTCUSDT", 100)
# util.save_json_to_file("calculate_bollinger_bands", bb)

topTraderLongShortRatio = binance_api.get_top_trader_long_short_ratio("BTCUSDT", "100", "4h")
# util.save_json_to_file("get_top_trader_long_short_ratio", topTraderLongShortRatio)

fundingRate = binance_api.get_latest_funding_rate("BTCUSDT")
util.save_json_to_file("get_latest_funding_rate", fundingRate)







