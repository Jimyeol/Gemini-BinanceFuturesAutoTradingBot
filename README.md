## Gemini-BinanceFuturesAutoTradingBot

This repository is an automated trading bot utilizing Gemini, Binance Futures, Pandas, and other tools. It analyzes both quantitative and qualitative data and delegates buy/sell decisions to AI. The code references YouTuber "Jocoding" project.

### Important Disclaimer
_The trading bot described here does not guarantee profits and is intended solely for informational and advisory purposes. Trading cryptocurrencies involves substantial risk and can result in significant financial losses. 
By using this trading bot, you acknowledge that you are solely responsible for your own investment decisions and actions. The creators and maintainers of this bot are not liable for any losses or damages incurred as a result of using this bot. It is strongly recommended that you conduct your own research and consult with a professional financial advisor before making any trading decisions.
Cryptocurrency markets are highly volatile and unpredictable. The advice and data provided by this bot are based on past market trends and technical analysis, which do not always predict future performance. Always be cautious and aware of the risks involved in trading.
By proceeding with the use of this bot, you agree to these terms and understand the inherent risks associated with cryptocurrency trading._

### Flow summary
1. Retrieve Candle Stick data (1h, 4h, 1d, 1w) from the Binance Futures API and use pandas to save various technical indicators as JSON.
2. Provide Gemini with trading principles and considerations, along with my current information (position) and market data JSON, to analyze market trends.
3. Based on the advice received from Gemini, execute trades directly using the Binance Futures API.
4. Receive position execution information via Telegram.

### Additional Details
1. **Data Retrieval**:
   - Use the Binance Futures API to get Candle Stick data for different time frames (1h, 4h, 1d, 1w).
   - Utilize pandas to process this data and compute various technical indicators such as RSI, MACD, Bollinger Bands, Moving Averages, etc.
   - Save these indicators in JSON format for further analysis.

2. **Market Analysis with Gemini**:
   - Provide Gemini with a set of trading principles and important considerations.
   - Include current position information and market data in JSON format when requesting market trend analysis from Gemini.
   - Ensure that the data provided to Gemini is comprehensive and up-to-date to get the most accurate advice.

3. **Trade Execution**:
   - Based on the advice received from Gemini, make trading decisions and execute trades using the Binance Futures API.
   - Implement error handling and logging to ensure that all trade executions are recorded and any issues are promptly addressed.

4. **Telegram Notifications**:
   - After executing trades based on Gemini's advice, send a message to a Telegram bot with details about the position execution.
   - Ensure that the Telegram notifications include important details such as entry price, exit price, stop loss, leverage, and any other relevant information.

5. **Automation and Scheduling**:
   - Automate the process to run at specific intervals (e.g., every 4 hours) using a task scheduler such as cron for Linux or Task Scheduler for Windows.
   - Ensure that the environment is set up correctly so that scripts can run autonomously without manual intervention.

### Information Provided to AI for Trading
To facilitate trading decisions, the following data is provided to the AI:
 - #### Data Market
   * **Data 1: Current Investment State**
     - Information about the current investment portfolio, including open positions, asset summary, and other relevant details.
   * **Data 2: Market Analysis**
     - Technical indicators derived from market data such as RSI, MACD, Bollinger Bands, Moving Averages, Stochastic Oscillator, and trend signals.
   * **Data 3: Fear and Greed Index**
     - A measure of market sentiment that indicates whether the market is currently in a state of fear or greed.

- #### Considerations
  * Considerations are provided to Gemini to ensure that the AI understands the trading principles and important factors to consider when analyzing the market. This helps Gemini provide more tailored and relevant advice based on the current market conditions and investment strategy.

- #### Instruction Workflow
  * The workflow for providing instructions to the AI involves several steps to ensure accurate and relevant market analysis.

- #### Example JSON
  * JSON data provided to Gemini for market analysis.


### Advice json.
Here is an example of the JSON advice received from Gemini, which guides the trading decisions:
```json
{
    "position": "Long",
    "risk_awareness": "Although leverage involves considerable risk, it also presents an opportunity for significant returns. Please proceed cautiously while considering the possibility of potential profits.",
    "probability_of_rise": {
        "percentage": 75,
        "reasons": [
            "The Fear and Greed Index is in the Greed zone, demonstrating bullish sentiment.",
            "The RSI on the 4-hour chart is above 50, indicating bullish momentum.",
            "The price has recently broken above the 50-day moving average, signaling an uptrend.",
            "Volume analysis reveals increasing buying activity, bolstering the bullish signal."
        ]
    },
    "probability_of_fall": {
        "percentage": 25,
        "reasons": [
            "The current price is approaching the upper Bollinger Band on the daily chart, which may act as a resistance level.",
            "There might be potential for profit-taking by traders at this level.",
            "Upcoming economic releases could introduce uncertainty into the market, potentially impacting sentiment."
        ]
    },
    "order": {
        "recommended_action": "Long",
        "investment_percentage": 75,
        "leverage": 4,
        "symbol": "BTCUSDT",
        "side": "BUY",
        "timeInForce": "GTC",
        "entryPrice": 65000.1,
        "entryPriceReason": "The current price of 65000.10 is chosen as the entry point as it aligns with a recent breakout above the 50-day moving average, signaling a bullish trend. Additionally, the RSI on the 4-hour chart is above 50, supporting the bullish momentum.",
        "exitPrice": 68000,
        "exitPriceReason": "The target exit price is set at 68000, which is near the upper Bollinger Band on the daily chart, indicating a strategic profit-taking zone.",
        "stoploss": 64000,
        "stopLossReason": "The stop-loss is set at 64000, just below the 50-day moving average and the lower Bollinger Band on the 4-hour chart, offering a buffer against a potential short-term pullback.",
        "positionSide": "LONG"
    },
    "hold_order": {},
    "timestamp": 1689607454
}
```


### Test
~~Gemini Token's limited quantity prevents backtesting, so we're conducting live tests. This log will record entries, take-profits, and stop-losses. We're starting the test with high expectations for good profits. `This program runs every 4 hours and aims to generate profits safely.`~~
~~- _2024. 07. 19_ - **63.39 USDT** Start~~

Restarting with a focus on scalping. The previous prompt was too patient and didn't enter trades frequently enough. Replacing it with a more active scalping bot.
- _2024. 07. 23_ - **44.96 USDT** Start


