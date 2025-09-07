import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import PromptTemplate

# Step 1: Structured Intent Extraction
extraction_prompt = ChatPromptTemplate.from_template("""
You are an expert at extracting intent from user queries about cryptocurrency metrics. Given a user query, identify the requested metrics (e.g., 'nvt ratio', 'sharpe ratio', 'price history') and other parameters. Always output a JSON object with a 'metrics' field as a list, even if only one metric is detected. If no valid metric is recognized, use ['unknown']. Supported metrics: {supported_metrics}.

Current date: {current_date}

Query: {query}

Output JSON with:
- metrics: List of requested metrics (e.g., ['nvt ratio', 'sharpe ratio'] or ['price history'])
- symbol: Crypto symbol (e.g., 'BTC', 'ETH')
- interval: Data interval (default '1d' if not specified)
- start_date: Start date in YYYY-MM-DD (empty string if not specified)
- end_date: End date in YYYY-MM-DD (empty string if not specified)

Example:
Query: "I want to know BTC price and NVT from July 1 to July 20 2024"
Output: ```json
{{
  "metrics": ["price history", "nvt ratio"],
  "symbol": "BTC",
  "interval": "1d",
  "start_date": "2024-07-01",
  "end_date": "2024-07-20"
}}
""")

# Step 2: Natural Language Compilation
natural_prompt = ChatPromptTemplate.from_template("""
You are a cryptofinance analyst. 
You will receive financial data in JSON format.
Interpret the data into a clear, concise, and natural language response for the end user. 
Focus on exploiting insights and summarizing the key information (e.g., metric value, price trends, momentum, summary statistics) in a profesisonal manner.
State relevant details (e.g. metric name, symbol, date range, interval, etc.) if provided.

JSON Data:
{json_data}

Output a professional response.
""")

# Step 3: Merge
merge_prompt = PromptTemplate(
    input_variables=["responses", "query"],
    template="""Original query: {query}

You are given multiple natural language responses for different metrics about a cryptocurrency. Merge these into a single, cohesive, and concise natural language response. Avoid repetition, organize logically (e.g., sections per metric or a unified summary), and ensure the response is user-friendly and clear.

Responses:
{responses}

Output a single merged natural language response:
"""
)


analysis_type = """Here are the supported analysis types:
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