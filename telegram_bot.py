import os
from dotenv import load_dotenv
load_dotenv()
import asyncio
from telegram import Bot

async def send_telegram_message(message):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    bot = Bot(token=token)
    await bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

def send_message_position(advice_json):
    # 포맷에 맞게 JSON 데이터에서 값을 가져옵니다.
    position = advice_json["position"]
    risk_awareness = advice_json["risk_awareness"]
    probability_of_rise = advice_json["probability_of_rise"]["percentage"]
    reasons_rise = " ".join(advice_json["probability_of_rise"]["reasons"])
    probability_of_fall = advice_json["probability_of_fall"]["percentage"]
    reasons_fall = " ".join(advice_json["probability_of_fall"]["reasons"])
    
    # 기본 메시지 포맷
    message = (
        f"----------------------------------------------------\n"
        f"*포지션*: {position}\n"
        "\n\n"
        f"*위험인식*: _{risk_awareness}_\n"
        "\n\n"
        f"*올라갈 확률*: {probability_of_rise}%\n"
        f"*이유*: _{reasons_rise}_\n"
        "\n\n"
        f"*떨어질 확률*: {probability_of_fall}%\n"
        f"*이유*: _{reasons_fall}_\n"
    )
    
    # order가 비어 있지 않은 경우에만 추가 메시지 포맷 설정
    if advice_json["order"]:
        order = advice_json["order"]
        investment_percentage = order["investment_percentage"]
        leverage = order["leverage"]
        entry_price = order["entryPrice"]
        entry_price_reason = order["entryPriceReason"]
        exit_price = order["exitPrice"]
        exit_price_reason = order["exitPriceReason"]
        stoploss = order["stoploss"]
        stop_loss_reason = order["stopLossReason"]
        
        message += (
            "\n\n"
            f"*진입비율*: {investment_percentage}%\n"
            f"*레버리지*: {leverage}배율\n"
            f"*진입가격*: {entry_price}\n"
            f" - _{entry_price_reason}_\n"
            f"*익절가격*: {exit_price}\n"
            f" - _{exit_price_reason}_\n"
            f"*스탑로스*: {stoploss}\n"
            f" - _{stop_loss_reason}_\n"
        )
        
    message += f"----------------------------------------------------\n"
    
    # 메시지 전송
    asyncio.run(send_telegram_message(message))
