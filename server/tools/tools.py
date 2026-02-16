import re
import math
import pandas as pd
import json
from analysis.peer import (
    fetch_binance_data, calculate_nvt_ratio, calculate_sharpe_ratio,
    calculate_price_volume_ratio, calculate_mayer_multiple
)
from analysis.fundamental import (
    calculate_market_cap_growth
)
from langchain.tools import tool

def parse_metric_input(input_str: str):
    """
    Parse string: "symbol=XRPUSDT, interval=1m, startTime=2024-01-01, endTime=2024-01-31"
    Return: (symbol, interval, startTime, endTime)
    """
    pattern = r'symbol=([^,]+)(?:, interval=([^,]*))?(?:, startTime=([^,]*))?(?:, endTime=([^,]*))?'
    match = re.match(pattern, input_str.strip())

    if not match:
        return None  # Invalid input format

    return (
        match.group(1),  # symbol (string, required)
        match.group(2) or "1d",  # interval (default = 1d)
        match.group(3) or "",    # startTime (timestamp string)
        match.group(4) or ""     # endTime (timestamp string)
    )

@tool("nvt_ratio")
def nvt_ratio(input_str: str) -> str:
    """Calculate the NVT ratio."""
    parsed = parse_metric_input(input_str)
    if parsed is None:
        return "Invalid input format."
    symbol, interval, startTime, endTime = parsed
    try:
        df = fetch_binance_data(symbol, interval, startTime, endTime)
        supply = 21000000  # Static for BTC
        value = calculate_nvt_ratio(df, supply)
        return str(value)
    except Exception as e:
        return f"Error in nvt_ratio: {str(e)}"

@tool("sharpe_ratio")
def sharpe_ratio(input_str: str) -> str:
    """Calculate the Sharpe ratio."""
    parsed = parse_metric_input(input_str)
    if parsed is None:
        return "Invalid input format."
    symbol, interval, startTime, endTime = parsed
    try:
        df = fetch_binance_data(symbol, interval, startTime, endTime)
        value = calculate_sharpe_ratio(df)
        return str(value)
    except Exception as e:
        return f"Error in sharpe_ratio: {str(e)}"

@tool("price_volume_ratio")
def price_volume_ratio(input_str: str) -> str:
    """Calculate the Price-to-Volume ratio."""
    parsed = parse_metric_input(input_str)
    if parsed is None:
        return "Invalid input format."
    symbol, interval, startTime, endTime = parsed
    try:
        df = fetch_binance_data(symbol, interval, startTime, endTime)
        value = calculate_price_volume_ratio(df)
        return str(value)
    except Exception as e:
        return f"Error in price_volume_ratio: {str(e)}"

@tool("mayer_multiple")
def mayer_multiple(input_str: str) -> str:
    """Calculate the Mayer Multiple."""
    parsed = parse_metric_input(input_str)
    if parsed is None:
        return "Invalid input format."
    symbol, interval, startTime, endTime = parsed
    try:
        df = fetch_binance_data(symbol, interval, startTime, endTime)
        value = calculate_mayer_multiple(df)
        return str(value)
    except Exception as e:
        return f"Error in mayer_multiple: {str(e)}"

@tool("market_cap_growth")
def market_cap_growth(input_str: str) -> str:
    """Calculate the Market Cap Growth."""
    parsed = parse_metric_input(input_str)
    if parsed is None:
        return "Invalid input format."
    symbol, interval, startTime, endTime = parsed
    try:
        df = fetch_binance_data(symbol, interval, startTime, endTime)
        value = calculate_market_cap_growth(df)
        return str(value)
    except Exception as e:
        return f"Error in market_cap_growth: {str(e)}"

@tool("price_history")
def price_history(input_str: str) -> str:
    """Get the price history for the symbol in the given range."""
    parsed = parse_metric_input(input_str)
    if parsed is None:
        return "Invalid input format."
    symbol, interval, startTime, endTime = parsed
    try:
        df = fetch_binance_data(symbol, interval, startTime, endTime)
        print(f"DataFrame columns: {list(df.columns)}")
        if df.empty:
            return "No data returned for the given range."
        if 'timestamp' not in df.columns or 'close' not in df.columns:
            return f"Expected columns 'timestamp' and 'close', got {list(df.columns)}"
        # Convert timestamp to YYYY-MM-DD
        df['date'] = pd.to_datetime(df['timestamp'], unit='ms').dt.strftime('%Y-%m-%d')
        # Create structured output
        result = {
            "symbol": symbol,
            "interval": interval,
            "start_date": startTime,
            "end_date": endTime,
            "data": df[['date', 'close']].to_dict(orient='records'),
            "summary": {
                "average_price": float(df['close'].mean()),
                "min_price": float(df['close'].min()),
                "max_price": float(df['close'].max()),
                "count": len(df)
            }
        }
        return json.dumps(result, indent=2)  # Serialize to JSON string
    except Exception as e:
        return f"Error in price_history: {str(e)}"

# -----------------------------
# Export Tools List
# -----------------------------
tools = [
    nvt_ratio,
    sharpe_ratio,
    price_volume_ratio,
    mayer_multiple,
    market_cap_growth,
    price_history,
]