import os
from dotenv import load_dotenv
load_dotenv()
import binance_api
import json
import alternative
import util
from openai import OpenAI

# Setup
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

asset_summary = json.loads(binance_api.get_asset_summary())
coin_price = json.loads(binance_api.get_coin_price("BTCUSDT"))
position_summary = json.loads(binance_api.get_position_summary())
    
my_data = {
    "asset_summary": asset_summary,
    "coin_price": coin_price,
    "position_summary": position_summary
}

mydata = json.dumps(my_data, indent=4)

candles_df = binance_api.get_4h_candles("BTCUSDT", 50)

#topTraderLongShortRatio = binance_api.get_top_trader_long_short_ratio("BTCUSDT", "100", "4h")
# util.save_json_to_file("get_top_trader_long_short_ratio", topTraderLongShortRatio)

rsi = binance_api.calculate_rsi(candles_df, 50)
ma = binance_api.calculate_moving_averages(candles_df, 50)
macd = binance_api.calculate_macd(candles_df, 50)
bb = binance_api.calculate_bollinger_bands(candles_df, 50)
fundingRate = binance_api.get_latest_funding_rate("BTCUSDT")
trend = binance_api.generate_signals(binance_api.get_4h_candles("BTCUSDT", 100))

# Combine all results into a single JSON object
market_data = {
    "rsi": json.loads(rsi),
    "moving_averages": json.loads(ma),
    "macd": json.loads(macd),
    "bollinger_bands": json.loads(bb),
    "funding_rate": json.loads(fundingRate),
    "trend_signals": json.loads(trend)
}

# Convert the combined data to a JSON string
market_data_json = json.dumps(market_data, indent=4)
fear_greed_index = json.dumps(alternative.get_fear_and_greed_index(limit=30), indent=4)

def get_instructions(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            instructions = file.read()
        return instructions
    except FileNotFoundError:
        print("File not found.")
    except Exception as e:
        print("An error occurred while reading the file:", e)
        
def analyze_data_with_gpt4(my_data, market_data, fear_greed_index):
    instructions_path = "instructions.md"
    try:
        instructions = get_instructions(instructions_path)
        if not instructions:
            print("No instructions found.")
            return None
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": my_data},
                {"role": "user", "content": market_data},
                {"role": "user", "content": fear_greed_index},
            ],
            response_format={"type":"json_object"}
        )
        advice = response.choices[0].message.content
        return advice
    except Exception as e:
        print(f"Error in analyzing data with GPT-4: {e}")
        return None


advice = analyze_data_with_gpt4(market_data_json, market_data_json, fear_greed_index)
util.save_json_to_file("advice", advice)






