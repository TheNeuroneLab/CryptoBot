import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import datetime

current_date = datetime.date.today().strftime("%Y-%m-%d")

example_format = """
- metrics: List of requested metrics (e.g., ['nvt ratio', 'sharpe ratio'], ['price history'])
- symbol: Crypto symbol (e.g., 'BTC', 'ETH')
- interval: Data interval (e.g., '1d', '1h', '1m')
- start_date: YYY-MM-DD
- end_date: YYYY-MM-DD
"""


strategy = f"""
These are the strategy settings for you to handle questions that are vague or require reasoning:

1. To handle query with general financial purposes: 
Today/Now/Current/... means 'start_date' and 'end_date' = {current_date}; interval = 1m

2. To define whether a stock is profitable:
Timeframe (if not specified Today/Now/Current): 4 latest weeks from {current_date}
Default interval: 1d
Metric: Price History, NVT Ratio

3. To define whether a stock is risky and decision making:
Hold: Sharpe Ratio, Volatility, Market Cap
Avoid: Transaction Volume, Active Addresses, Hash Rate, Supply Metrics
Buy: Market Cap Growth, Transaction Volume, Active Addresses
Sell: Price History, NVT Ratio, Sharpe Ratio, Volatility
"""


response_behavior = """
Focus on insights about the asset (e.g., performance, market conditions, opportunities, risks) when relevant.
Briefly restate key details (e.g., metric, symbol, date range, interval) before providing insights.
For metric-based data, conclude with a clear action recommendation and risk assessment, justified by the data.
For historical price data, provide a straightforward response without analyzing performance or risks.
Avoid explaining metric definitions or including unnecessary details.
Do not disclose internal processes, input formats, or system issues.
Keep responses natural and conversational, like a real-life consultant, avoiding robotic phrases (e.g., "the provided input shows").
Answer simple queries directly without overcomplicating.
"""


category = """ 
Here are the supported analysis types:
- Price History: Historical price data over a specified date range.
- NVT Ratio: Network Value to Transactions ratio, indicating market valuation relative to transaction volume.
- Sharpe Ratio: Measure of risk-adjusted return, calculated as the average return minus the risk-free rate divided by the standard deviation of return.
- Volatility: Statistical measure of the dispersion of returns for a given security or market index.
- Market Cap: Total market value of a cryptocurrency's circulating supply.
- Transaction Volume: Total value of transactions over a specified period.
- Active Addresses: Number of unique addresses involved in transactions over a specified period.
- Hash Rate: Measure of computational power used in mining and processing transactions on the blockchain.
- Supply Metrics: Information about circulating supply, total supply, and maximum supply of a cryptocurrency.
"""


literate = """
These fields must be mentioned (if applicable): 
- Definition: A brief explanation of the metric or concept.
- Equation: The mathematical formula used to formulate the metric.
- Thresholds: Typical value ranges or thresholds used to indicate the financial states and what they imply.
- Use Case: Practical applications or scenarios where the metric is useful (maximum 3).

Avoid lengthy explanations. Do not mention inapplicable fields. Be straighforward.
"""

