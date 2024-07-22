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

def escape_markdown(text):
    escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    return text

def send_message_position(advice_json):
    # 포맷에 맞게 JSON 데이터에서 값을 가져옵니다.
    position = escape_markdown(advice_json.get("position", "N/A"))
    risk_awareness = escape_markdown(advice_json.get("risk_awareness", "N/A"))
    probability_of_rise = escape_markdown(str(advice_json.get("probability_of_rise", {}).get("percentage", "N/A")))
    reasons_rise = escape_markdown(" ".join(advice_json.get("probability_of_rise", {}).get("reasons", [])))
    probability_of_fall = escape_markdown(str(advice_json.get("probability_of_fall", {}).get("percentage", "N/A")))
    reasons_fall = escape_markdown(" ".join(advice_json.get("probability_of_fall", {}).get("reasons", [])))
    
    # 기본 메시지 포맷
    message = (
        "----------------------------------------------------\n"
        f"*포지션*: {position}\n\n"
        f"*위험인식*: {risk_awareness}\n\n"
        f"*올라갈 확률*: {probability_of_rise}%\n"
        f"*이유*: {reasons_rise}\n\n"
        f"*떨어질 확률*: {probability_of_fall}%\n"
        f"*이유*: {reasons_fall}\n"
    )
    
    # order가 비어 있지 않은 경우에만 추가 메시지 포맷 설정
    order = advice_json.get("order", None)
    if order:
        investment_percentage = escape_markdown(str(order.get("investment_percentage", "N/A")))
        leverage = escape_markdown(str(order.get("leverage", "N/A")))
        entry_price = escape_markdown(str(order.get("entryPrice", "N/A")))
        entry_price_reason = escape_markdown(order.get("entryPriceReason", "N/A"))
        exit_price = escape_markdown(str(order.get("exitPrice", "N/A")))
        exit_price_reason = escape_markdown(order.get("exitPriceReason", "N/A"))
        stoploss = escape_markdown(str(order.get("stoploss", "N/A")))
        stop_loss_reason = escape_markdown(order.get("stopLossReason", "N/A"))
        
        message += (
            "\n\n"
            f"*진입비율*: {investment_percentage}%\n"
            f"*레버리지*: {leverage}배율\n"
            f"*진입가격*: {entry_price}\n"
            f" - {entry_price_reason}\n"
            f"*익절가격*: {exit_price}\n"
            f" - {exit_price_reason}\n"
            f"*스탑로스*: {stoploss}\n"
            f" - {stop_loss_reason}\n"
        )
    
    message += "----------------------------------------------------\n"
    
    # 메시지 전송
    asyncio.run(send_telegram_message(message))