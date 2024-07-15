import os
from dotenv import load_dotenv
load_dotenv()
import binance_api
import json
import alternative
import util
import google.generativeai as genai
import os
import typing_extensions as typing

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
# img = PIL.Image.open('path/to/image.png')

def get_instructions(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            instructions = file.read()
        return instructions
    except FileNotFoundError:
        print("File not found.")
    except Exception as e:
        print("An error occurred while reading the file:", e)
        

class ProbabilityDetails(typing.TypedDict):
    percentage: int
    reasons: typing.List[str]

class Result(typing.TypedDict):
    recommended_action: str
    investment_percentage: int
    leverage: int
    risk_awareness: str
    probability_of_rise: ProbabilityDetails
    probability_of_fall: ProbabilityDetails
      
      
# orderbook_json = json.loads(binance_api.get_order_book("BTCUSDT", 5))
# util.save_json_to_file("orderbook_json", orderbook_json)
      
model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  # safety_settings = Adjust safety settings
  # See https://ai.google.dev/gemini-api/docs/safety-settings
  generation_config={"response_mime_type": "application/json",
                            "response_schema": Result},
  system_instruction=get_instructions("instructions.md"),
)


open_order = json.loads(binance_api.get_open_orders())
asset = json.loads(binance_api.get_asset_summary())
current_position = json.loads(binance_api.get_position_summary())
btc_price = json.loads(binance_api.get_coin_price("BTCUSDT"))


# Combine all results into a single JSON object
my_data = {
    "symbol": "BTCUSDT",
    "current_price": btc_price,
    "asset": asset,
    "current_position": current_position,
    "open_order": open_order,
}
#util.save_json_to_file("my_data", my_data)

candle_json = binance_api.get_candles_to_join("BTCUSDT", ['1h', '4h', '1d', '1w'], 1500)

# #topTraderLongShortRatio = binance_api.get_top_trader_long_short_ratio("BTCUSDT", "100", "4h")
# # util.save_json_to_file("get_top_trader_long_short_ratio", topTraderLongShortRatio)

rsi_json = binance_api.get_rsi_data(candle_json, 1)
ma_json = binance_api.get_moving_averages_data(candle_json, 1)
macd_json = binance_api.get_macd_data(candle_json, 1)
bb_json = binance_api.get_bollinger_bands_data(candle_json, 1)
fundingRate = binance_api.get_latest_funding_rate("BTCUSDT")
trend_json = binance_api.get_supertrend_signals(candle_json, 1)
stoch_oscil_json = binance_api.get_stochastic_oscillator_data(candle_json, 1)

# Combine all results into a single JSON object
indicator = {
    "rsi": json.loads(rsi_json),
    "moving_averages": json.loads(ma_json),
    "macd": json.loads(macd_json),
    "bollinger_bands": json.loads(bb_json),
    "stoch_oscil": json.loads(stoch_oscil_json),
    "funding_rate": json.loads(fundingRate),
    "trend_signals": json.loads(trend_json)
}

#util.save_json_to_file("indicator", indicator)


def analyze_data_with_gpt4(my_data, indicator, fear_greed_index):
    # 메시지 형식을 JSON 문자열로 변환
    message = [
        {"role": "user", "content": my_data},
        {"role": "user", "content": indicator},
        {"role": "user", "content": fear_greed_index}
    ]
    message_json = json.dumps(message)
    
    return model.generate_content(message_json)

      
advice = analyze_data_with_gpt4(my_data, indicator, alternative.get_fear_and_greed_index(limit=30))
util.save_json_to_file("advice", json.loads(advice.text))

