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
import telegram_bot
import schedule
import time
import datetime

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        

class ProbabilityDetails(typing.TypedDict):
    percentage: int
    reasons: typing.List[str]

class OrderDetails(typing.TypedDict):
    recommended_action: str
    investment_percentage: int
    leverage: int
    symbol: str
    side: str
    timeInForce: str
    entryPrice: float
    entryPriceReason: str
    exitPrice: float
    exitPriceReason: str
    stoploss: float
    stopLossReason: str
    positionSide: str

class HoldOrder(typing.TypedDict):
    type: str  # 'hold' or 'close'

class Result(typing.TypedDict):
    position: str
    risk_awareness: str
    probability_of_rise: ProbabilityDetails
    probability_of_fall: ProbabilityDetails
    order: OrderDetails
    hold_order: HoldOrder
      
      
# orderbook_json = json.loads(binance_api.get_order_book("BTCUSDT", 5))
# util.save_json_to_file("orderbook_json", orderbook_json)
      
model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  # safety_settings = Adjust safety settings
  # See https://ai.google.dev/gemini-api/docs/safety-settings
  generation_config={"response_mime_type": "application/json",
                            "response_schema": Result},
  system_instruction=util.get_instructions("instructions.md"),
)


open_order = json.loads(binance_api.get_open_orders())
asset = json.loads(binance_api.get_asset_summary())
current_position = json.loads(binance_api.get_position_summary())
btc_price = json.loads(binance_api.get_coin_price("BTCUSDT"))

# advice 폴더에서 최근 5개의 조언 파일 읽기
directory_path = "advice"
latest_files = util.get_latest_files(directory_path)
recent_advice = [util.read_json_file(os.path.join(directory_path, file)) for file in latest_files]

# Combine all results into a single JSON object
my_data = {
    "symbol": "BTCUSDT",
    "current_price": btc_price,
    "asset": asset,
    "current_position": current_position,
    "open_order": open_order,
    "recent_advice": recent_advice
}
#util.save_json_to_file("my_data", my_data)

candle_json = binance_api.get_candles_to_join("BTCUSDT", ['1h', '4h', '1d', '1w'], 1500)


rsi_json = binance_api.get_rsi_data(candle_json, 1)
ma_json = binance_api.get_moving_averages_data(candle_json, 1)
macd_json = binance_api.get_macd_data(candle_json, 1)
bb_json = binance_api.get_bollinger_bands_data(candle_json, 1)
fundingRate = binance_api.get_latest_funding_rate("BTCUSDT")
trend_json = binance_api.get_supertrend_signals(candle_json, 1)
stoch_oscil_json = binance_api.get_stochastic_oscillator_data(candle_json, 1)
topTraderLongShortRatio = binance_api.get_top_trader_long_short_ratio("BTCUSDT", ['1h', '4h', '1d', '1w'])

# Combine all results into a single JSON object
indicator = {
    "rsi": json.loads(rsi_json),
    "moving_averages": json.loads(ma_json),
    "macd": json.loads(macd_json),
    "bollinger_bands": json.loads(bb_json),
    "stoch_oscil": json.loads(stoch_oscil_json),
    "funding_rate": json.loads(fundingRate),
    "trend_signals": json.loads(trend_json),
    "topTraderLongShortRatio": json.loads(topTraderLongShortRatio)
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
binance_api.process_order(json.loads(advice.text))
telegram_bot.send_message_position(json.loads(advice.text))
    
# def run_analysis():
    
    
# 4시간마다 job 함수 실행 예약
# schedule.every(4).hours.do(run_analysis)

# while True:
#     schedule.run_pending()
#     time.sleep(60)  # 1분마다 실행