from analysis.peer import (
    fetch_binance_data, calculate_nvt_ratio, calculate_sharpe_ratio,
    calculate_price_volume_ratio, calculate_mayer_multiple
)
from analysis.fundamental import (
    calculate_market_cap_growth
)
from langchain.tools import tool


@tool
def nvt_ratio(symbol: str) -> float:
    """
    Name: NVT Ratio
    Description: Get the Network Value to Transactions Ratio (NVT) for a given cryptocurrency symbol (e.g., BTC, ETH).
    Formula: Market Cap / Transaction Volume.
    Common aliases: "network value to transactions ratio", "Bitcoin PE ratio".
    """
    df = fetch_binance_data(symbol)
    supply = 21000000  # Static for BTC, you might want to make dynamic for other coins
    return calculate_nvt_ratio(df, supply)


@tool
def sharpe_ratio(symbol: str) -> float:
    """
    Name: Sharpe Ratio
    Description: Get the Sharpe ratio for a cryptocurrency, measuring risk-adjusted returns.
    Common aliases: "risk reward ratio", "risk-adjusted return".
    """
    df = fetch_binance_data(symbol)
    return calculate_sharpe_ratio(df)


@tool
def price_volume_ratio(symbol: str) -> float:
    """
    Name: Price Volume Ratio
    Description: Get the price-to-volume ratio for a cryptocurrency.
    Common aliases: "price vs volume", "price volume analysis".
    """
    df = fetch_binance_data(symbol)
    return calculate_price_volume_ratio(df)


@tool
def mayer_multiple(symbol: str) -> float:
    """
    Name: Mayer Multiple
    Description: Get the Mayer Multiple (price divided by 200-day moving average) for a cryptocurrency.
    Common aliases: "200-day average multiple", "Mayer ratio".
    """
    df = fetch_binance_data(symbol)
    return calculate_mayer_multiple(df)


@tool
def market_cap_growth(symbol: str) -> float:
    """
    Name: Market Cap Growth
    Description: Get the market capitalization growth for a cryptocurrency.
    Common aliases: "market cap change", "cap growth rate".
    """
    df = fetch_binance_data(symbol)
    return calculate_market_cap_growth(df)


tools = [
    nvt_ratio,
    sharpe_ratio,
    price_volume_ratio,
    mayer_multiple,
    market_cap_growth
]
