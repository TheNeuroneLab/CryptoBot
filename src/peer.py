import requests
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

# Binance API setup
BINANCE_API_URL = "https://api.binance.com/api/v3"
SYMBOLS = ["AAVEUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "UNIUSDT", "LINKUSDT"]
DAYS = 365
START_DATE = int((datetime(2024, 4, 7)).timestamp() * 1000)
END_DATE = int((datetime(2025, 4, 7)).timestamp() * 1000)

# Circulating supply (fixed, approximate as of April 2025)
SUPPLIES = {
    "AAVEUSDT": 16000000,  # Aave
    "ETHUSDT": 120000000,  # Ethereum
    "SOLUSDT": 500000000,  # Solana
    "BNBUSDT": 150000000,  # BNB
    "UNIUSDT": 600000000,  # Uniswap
    "LINKUSDT": 500000000  # Chainlink
}

# Fetch historical data
def fetch_binance_data(symbol):
    params = {
        "symbol": symbol,
        "interval": "1d",
        "startTime": START_DATE,
        "endTime": END_DATE,
        "limit": 1000
    }
    url = f"{BINANCE_API_URL}/klines"
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"API failed for {symbol}: {response.status_code}")
    klines = response.json()
    df = pd.DataFrame(klines, columns=[
        "timestamp", "open", "high", "low", "close", "volume",
        "close_time", "quote_volume", "trades", "taker_buy_base",
        "taker_buy_quote", "ignore"
    ])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df["close"] = df["close"].astype(float)
    df["volume"] = df["volume"].astype(float)
    return df

# Quantitative Metrics
def calculate_nvt_ratio(df, supply):
    market_caps = df["close"] * supply
    volumes = df["volume"] * df["close"]
    return (market_caps / volumes).mean()

def calculate_sharpe_ratio(df):
    returns = df["close"].pct_change().dropna()
    staking_apy = 0.05 / 365  # 5% annualized
    total_returns = returns + staking_apy
    risk_free_rate = 0.025 / 365
    excess_returns = total_returns - risk_free_rate
    return excess_returns.mean() / excess_returns.std() * np.sqrt(365) if excess_returns.std() != 0 else np.inf

# Fundamental Metrics
def calculate_price_volume_ratio(df):
    current_price = df["close"].iloc[-1]
    avg_volume = (df["volume"] * df["close"]).mean()
    return current_price / avg_volume if avg_volume != 0 else np.inf

def calculate_mayer_multiple(df):
    ma_200 = df["close"].rolling(window=200).mean().iloc[-1]
    current_price = df["close"].iloc[-1]
    return current_price / ma_200 if ma_200 != 0 else np.inf

# Qualitative Proxies
def calculate_speculative_signal(nvt, mayer):
    return 1 if nvt > 50 or mayer > 2.4 else 0

def calculate_price_stability_ratio(df):
    returns = df["close"].pct_change().dropna()
    volatility = returns.std() * np.sqrt(365)
    avg_price = df["close"].mean()
    return avg_price / volatility if volatility != 0 else np.inf

# Technical Metrics
def calculate_rsi(df, period=14):
    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1] if not rsi.isna().all() else np.nan

def calculate_macd(df):
    ema_12 = df["close"].ewm(span=12, adjust=False).mean()
    ema_26 = df["close"].ewm(span=26, adjust=False).mean()
    macd = ema_12 - ema_26
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd.iloc[-1] - signal.iloc[-1]

# Main function
def main():
    try:
        # Fetch data for all tokens
        data = {symbol: fetch_binance_data(symbol) for symbol in SYMBOLS}
        
        # Compute metrics
        results = {}
        for symbol in SYMBOLS:
            df = data[symbol]
            supply = SUPPLIES[symbol]
            nvt = calculate_nvt_ratio(df, supply)
            mayer = calculate_mayer_multiple(df)
            results[symbol] = {
                "NVT Ratio": nvt,
                "Sharpe Ratio": calculate_sharpe_ratio(df),
                "Price/Volume Ratio": calculate_price_volume_ratio(df),
                "Mayer Multiple": mayer,
                "Speculative Signal": calculate_speculative_signal(nvt, mayer),
                "Price Stability Ratio": calculate_price_stability_ratio(df),
                "RSI": calculate_rsi(df),
                "MACD Histogram": calculate_macd(df)
            }
        
        # Prepare CSV data
        csv_data = {"Metric": list(results["AAVEUSDT"].keys())}
        for symbol in SYMBOLS:
            token = symbol.replace("USDT", "")
            csv_data[token] = [results[symbol][metric] for metric in csv_data["Metric"]]
        csv_df = pd.DataFrame(csv_data)
        csv_df.to_csv("aave_peer_analysis.csv", index=False)
        print("Peer analysis saved to aave_peer_analysis.csv")
        
        # Plotting bar chart
        metrics_to_plot = ["NVT Ratio", "Sharpe Ratio", "Price/Volume Ratio", "Mayer Multiple", 
                          "Price Stability Ratio", "RSI", "MACD Histogram"]  # Exclude binary Speculative Signal
        fig, axes = plt.subplots(len(metrics_to_plot), 1, figsize=(12, 20), sharex=True)
        tokens = [symbol.replace("USDT", "") for symbol in SYMBOLS]
        
        for i, metric in enumerate(metrics_to_plot):
            values = [results[symbol][metric] for symbol in SYMBOLS]
            bars = axes[i].bar(tokens, values, color=['#1f77b4' if t != "AAVE" else '#ff7f0e' for t in tokens])
            axes[i].set_ylabel(metric)
            axes[i].set_title(f"{metric} Comparison")
            # Add value labels on top of bars
            for bar in bars:
                height = bar.get_height()
                axes[i].text(bar.get_x() + bar.get_width()/2, height, f"{height:.2f}", 
                            ha="center", va="bottom" if height >= 0 else "top")
        
        plt.xlabel("Tokens")
        fig.suptitle("Aave vs. Peers: Key Metrics Comparison", fontsize=16)
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        plt.savefig("aave_peer_analysis_plot.png")
        print("Bar chart saved to aave_peer_analysis_plot.png")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()