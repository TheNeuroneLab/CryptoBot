from analysis.peer import (
    fetch_binance_data, calculate_nvt_ratio, calculate_sharpe_ratio,
    calculate_price_volume_ratio, calculate_mayer_multiple
)
from analysis.fundamental import (
    calculate_market_cap_growth
)
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

# -----------------------------------------
# Shared Input Schema
# -----------------------------------------
class BinanceInput(BaseModel):
    symbol: str = Field(..., description="Cryptocurrency symbol (e.g., BTC, ETH)")
    start_date: str = Field(..., description="Start date in DD/MM/YYYY format")
    end_date: str = Field(..., description="End date in DD/MM/YYYY format")

# -----------------------------------------
# Tool Functions
# -----------------------------------------
def nvt_ratio_fn(symbol: str, start_date: str, end_date: str) -> float:
    df = fetch_binance_data(symbol, start_date, end_date)
    supply = 21000000  # Static for BTC; can be made dynamic
    return calculate_nvt_ratio(df, supply)

def sharpe_ratio_fn(symbol: str, start_date: str, end_date: str) -> float:
    df = fetch_binance_data(symbol, start_date, end_date)
    return calculate_sharpe_ratio(df)

def price_volume_ratio_fn(symbol: str, start_date: str, end_date: str) -> float:
    df = fetch_binance_data(symbol, start_date, end_date)
    return calculate_price_volume_ratio(df)

def mayer_multiple_fn(symbol: str, start_date: str, end_date: str) -> float:
    df = fetch_binance_data(symbol, start_date, end_date)
    return calculate_mayer_multiple(df)

def market_cap_growth_fn(symbol: str, start_date: str, end_date: str) -> float:
    df = fetch_binance_data(symbol, start_date, end_date)
    return calculate_market_cap_growth(df)

# -----------------------------------------
# Structured Tools
# -----------------------------------------
nvt_ratio = StructuredTool.from_function(
    func=nvt_ratio_fn,
    name="nvt_ratio",
    description=(
        "Calculate the Network Value to Transactions (NVT) ratio for a cryptocurrency "
        "between the given start and end dates. The NVT ratio is the market cap divided "
        "by transaction volume and is often used to assess whether a cryptocurrency is "
        "overvalued or undervalued relative to its transaction activity. "
        "Use when analyzing long-term valuation trends."
    ),
    args_schema=BinanceInput
)

sharpe_ratio = StructuredTool.from_function(
    func=sharpe_ratio_fn,
    name="sharpe_ratio",
    description=(
        "Calculate the Sharpe ratio for a cryptocurrency between the given start and end dates. "
        "The Sharpe ratio measures risk-adjusted returns by comparing the average return to the "
        "volatility. Use when you want to evaluate the performance of an asset compared to its risk."
    ),
    args_schema=BinanceInput
)

price_volume_ratio = StructuredTool.from_function(
    func=price_volume_ratio_fn,
    name="price_volume_ratio",
    description=(
        "Calculate the Price-to-Volume ratio for a cryptocurrency between the given start and end dates. "
        "This ratio compares the asset's price to its trading volume, helping identify liquidity trends "
        "and potential overbought/oversold conditions. Use when analyzing market activity strength."
    ),
    args_schema=BinanceInput
)

mayer_multiple = StructuredTool.from_function(
    func=mayer_multiple_fn,
    name="mayer_multiple",
    description=(
        "Calculate the Mayer Multiple for a cryptocurrency between the given start and end dates. "
        "The Mayer Multiple is the current price divided by its 200-day moving average. "
        "It is often used to identify potential buying or selling points based on historical averages."
    ),
    args_schema=BinanceInput
)

market_cap_growth = StructuredTool.from_function(
    func=market_cap_growth_fn,
    name="market_cap_growth",
    description=(
        "Calculate the market capitalization growth rate for a cryptocurrency between the given start and end dates. "
        "Market cap growth shows how quickly the total value of the network is increasing or decreasing over time. "
        "Use when analyzing adoption trends or overall market expansion."
    ),
    args_schema=BinanceInput
)



# -----------------------------------------
# Export Tools List
# -----------------------------------------
tools = [
    nvt_ratio,
    sharpe_ratio,
    price_volume_ratio,
    mayer_multiple,
    market_cap_growth
]
