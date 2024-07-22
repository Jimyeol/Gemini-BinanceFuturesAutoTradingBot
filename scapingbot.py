import pandas as pd
import binance_api
import util
import json
import os
from dotenv import load_dotenv
load_dotenv()
import google.generativeai as genai
from datetime import datetime
import typing_extensions as typing
import schedule
import telegram_bot

genai.configure(api_key=os.getenv("GOOGLE_API_SCAL_KEY"))

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
    
model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  # safety_settings = Adjust safety settings
  # See https://ai.google.dev/gemini-api/docs/safety-settings
  generation_config={"response_mime_type": "application/json",
                            "response_schema": Result},
  system_instruction=util.get_instructions("scalping_prompt.md"),
)

def save_ema_json(ema_data, root_dir="scalping"):
    """
    EMA 데이터를 JSON 파일로 저장합니다.

    Args:
        ema_data (list): EMA 데이터 딕셔너리 리스트
        root_dir (str): JSON 파일을 저장할 루트 디렉토리 (기본값: 'scalping')
    """

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")  # 현재 시간 기준 타임스탬프 생성

    # 루트 디렉토리가 없으면 생성
    os.makedirs(root_dir, exist_ok=True)

    file_path = os.path.join(root_dir, f"ema_{timestamp}.json")

    # EMA 데이터 리스트를 JSON 형태로 변환하여 저장
    with open(file_path, "w") as f:
        json.dump(ema_data, f)


def get_ema(candles_df):
    df = pd.DataFrame(candles_df)
    df['close'] = df['close'].astype(float)
    
    df['EMA_10'] = df['close'].ewm(span=10, adjust=False).mean()
    df['EMA_20'] = df['close'].ewm(span=20, adjust=False).mean()
    df['EMA_50'] = df['close'].ewm(span=50, adjust=False).mean()
    
    result_df = df[['timestamp', 'close', 'EMA_10', 'EMA_20', 'EMA_50']]
    result = result_df.to_json(orient='records')
    return result
    

def analyze_data_with_gpt4(my_data, candle15, candle30):
    # 메시지 형식을 JSON 문자열로 변환
    message = [
        {"role": "user", "content": my_data},
        {"role": "user", "content": candle15},
        {"role": "user", "content": candle30}
    ]
    message_json = json.dumps(message)
    
    return model.generate_content(message_json)

def run_analysis():
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
        "open_order": open_order
    }

    candle15 = json.loads(get_ema(binance_api.get_candles("BTCUSDT", '15m', 100)))
    candle30 = json.loads(get_ema(binance_api.get_candles("BTCUSDT", '30m', 100)))

    advice = analyze_data_with_gpt4(my_data, candle15, candle30)
    util.save_json_to_file("scalping", json.loads(advice.text))
    binance_api.process_order(json.loads(advice.text))
    telegram_bot.send_message_position(json.loads(advice.text))
    
# 15분마다 job 함수 실행 예약
run_analysis()
schedule.every(15).minutes.do(run_analysis)

while True:
    schedule.run_pending()

    

