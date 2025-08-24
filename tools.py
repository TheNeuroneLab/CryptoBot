import re
import math
from analysis.peer import (
    fetch_binance_data, calculate_nvt_ratio, calculate_sharpe_ratio,
    calculate_price_volume_ratio, calculate_mayer_multiple
)
from analysis.fundamental import (
    calculate_market_cap_growth
)
from langchain.tools import tool

# -----------------------------
# Regex Parser
# -----------------------------
def parse_metric_input(input_str: str):
    """
    Parse string dạng:
    "symbol=XRPUSDT, interval=1m, startTime=2024-01-01, endTime=2024-01-31"

    Return:
        (symbol, interval, startTime, endTime)
    """
    pattern = r'symbol=([^,]+)(?:, interval=([^,]*))?(?:, startTime=([^,]*))?(?:, endTime=([^,]*))?'
    match = re.match(pattern, input_str.strip())

    if not match:
        return None  # Invalid input format

    return (
        match.group(1),  # symbol (string, bắt buộc)
        match.group(2) or "1d",  # interval (default = 1d)
        match.group(3) or "",    # startTime (timestamp string)
        match.group(4) or ""     # endTime (timestamp string)
    )

# -----------------------------
# Tool Functions (ReAct friendly)
# -----------------------------

@tool("nvt_ratio")
def nvt_ratio(input_str: str) -> str:
    """Calculate the NVT ratio."""
    symbol, interval, startTime, endTime = parse_metric_input(input_str)
    df = fetch_binance_data(symbol, interval, startTime, endTime)
    supply = 21000000  # Static for BTC
    value = calculate_nvt_ratio(df, supply)
    return value

@tool("sharpe_ratio")
def sharpe_ratio(input_str: str) -> str:
    """Calculate the Sharpe ratio."""
    symbol, interval, startTime, endTime = parse_metric_input(input_str)
    df = fetch_binance_data(symbol, interval, startTime, endTime)
    value = calculate_sharpe_ratio(df)
    return value

@tool("price_volume_ratio")
def price_volume_ratio(input_str: str) -> str:
    """Calculate the Price-to-Volume ratio."""
    symbol, interval, startTime, endTime = parse_metric_input(input_str)
    df = fetch_binance_data(symbol, interval, startTime, endTime)
    value = calculate_price_volume_ratio(df)
    return value

@tool("mayer_multiple")
def mayer_multiple(input_str: str) -> str:
    """Calculate the Mayer Multiple."""
    symbol, interval, startTime, endTime = parse_metric_input(input_str)
    df = fetch_binance_data(symbol, interval, startTime, endTime)
    value = calculate_mayer_multiple(df)
    return value

@tool("market_cap_growth")
def market_cap_growth(input_str: str) -> str:
    """Calculate the Market Cap Growth."""
    symbol, interval, startTime, endTime = parse_metric_input(input_str)
    df = fetch_binance_data(symbol, interval, startTime, endTime)
    value = calculate_market_cap_growth(df)
    return value

# -----------------------------
# Export Tools List
# -----------------------------
tools = [
    nvt_ratio,
    sharpe_ratio,
    price_volume_ratio,
    mayer_multiple,
    market_cap_growth,
]
