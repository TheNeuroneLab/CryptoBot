import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from langchain_core.prompts import ChatPromptTemplate
import datetime

current_date = datetime.date.today().strftime("%Y-%m-%d")

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

natural_prompt = ChatPromptTemplate.from_template("""
You are a cryptofinance analyst. 
You will receive financial data in JSON format.
Interpret the data into a clear, concise, and natural language response for the end user. 
Focus on exploiting insights and summarizing the key information (e.g., metric value, price trends, momentum, summary statistics) in a professional manner.
State relevant details (e.g. metric name, symbol, date range, interval, etc.) if provided.

JSON Data:
{json_data}

Output a professional response.
""")

leader_prompt = ChatPromptTemplate.from_template("""
You are a leader agent that decides which workflow to route the user query to. Your goal is to classify the query accurately and choose the most appropriate workflow.

Available workflows:
- crypto_metrics: For queries requesting cryptocurrency analysis, metrics (e.g., NVT ratio, Sharpe ratio, Mayer multiple, price history, market cap growth), or data for specific symbols like BTC, ETH, etc.
- irrelevant_question: For off-topic queries, chit-chat, or anything not related to cryptocurrency analysis or financial detection.
- financial_detection: For queries involving general financial advice, scam detection, investment recommendations, or broader financial topics outside of specific crypto metrics.

User query: {query}

Respond with a JSON object containing only the workflow key, e.g., {{"workflow": "crypto_metrics"}}.
Do not add extra text or explanations.
""")

irrelevant_prompt = ChatPromptTemplate.from_template("""
You are a polite assistant handling irrelevant or off-topic user queries. The query does not relate to cryptocurrency metrics or financial analysis. Respond in a friendly, professional manner, gently informing the user that their question is outside the system's scope and suggesting they ask about cryptocurrency metrics (e.g., NVT ratio, Sharpe ratio, price history) or financial topics. If the query has a clear topic, tailor the response to acknowledge it briefly.

User query: {query}

Output a concise, natural language response.
Example for query "What's the weather like?":
"Sorry, I can't help with weather updates. My expertise is in cryptocurrency analysis. Would you like to know about metrics like BTC price history or NVT ratio?"
""")