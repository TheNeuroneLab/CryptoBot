import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import matplotlib.pyplot as plt

# Binance API setup
BINANCE_API_URL = "https://api.binance.com/api/v3"
AAVE_SYMBOL = "AAVEUSDT"
DAYS = 365
START_DATE = int((datetime(2024, 4, 7)).timestamp() * 1000)
END_DATE = int((datetime(2025, 4, 7)).timestamp() * 1000)

# Helper function for Binance API
def fetch_binance_data(endpoint, params={}):
    url = f"{BINANCE_API_URL}/{endpoint}"
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API request failed: {response.status_code}")

# Fetch historical data
def fetch_historical_data(symbol):
    params = {
        "symbol": symbol,
        "interval": "1d",
        "startTime": START_DATE,
        "endTime": END_DATE,
        "limit": 1000
    }
    klines = fetch_binance_data("klines", params)
    df = pd.DataFrame(klines, columns=[
        "timestamp", "open", "high", "low", "close", "volume",
        "close_time", "quote_volume", "trades", "taker_buy_base",
        "taker_buy_quote", "ignore"
    ])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df["close"] = df["close"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["volume"] = df["volume"].astype(float)
    return df

# 1. SMA 50-day
# Theory: Dow Theory; price above SMA signals bullish trend.
def calculate_sma_50(df):
    return df["close"].rolling(window=50).mean().iloc[-1]

# 2. EMA 20-day
# Theory: Faster trend signal than SMA (Murphy, 1999).
def calculate_ema_20(df):
    return df["close"].ewm(span=20, adjust=False).mean().iloc[-1]

# 3. RSI
# Theory: Behavioral Finance; overbought (>70) or oversold (<30).
def calculate_rsi(df, period=14):
    delta = df["close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1] if not rsi.isna().all() else np.nan

# 4. MACD
# Theory: Dow Theory; MACD crossover signals trend changes.
def calculate_macd(df):
    ema_12 = df["close"].ewm(span=12, adjust=False).mean()
    ema_26 = df["close"].ewm(span=26, adjust=False).mean()
    macd = ema_12 - ema_26
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd.iloc[-1] - signal.iloc[-1]  # MACD Histogram

# 5. Bollinger Bands Width
# Theory: High width indicates volatility, potential breakout.
def calculate_bollinger_width(df):
    sma_20 = df["close"].rolling(window=20).mean()
    std_20 = df["close"].rolling(window=20).std()
    upper = sma_20 + 2 * std_20
    lower = sma_20 - 2 * std_20
    return (upper.iloc[-1] - lower.iloc[-1]) / sma_20.iloc[-1]

# 6. ATR
# Theory: Measures volatility; high ATR signals strong trends.
def calculate_atr(df, period=14):
    tr = pd.DataFrame()
    tr["hl"] = df["high"] - df["low"]
    tr["hc"] = (df["high"] - df["close"].shift()).abs()
    tr["lc"] = (df["low"] - df["close"].shift()).abs()
    tr["true_range"] = tr[["hl", "hc", "lc"]].max(axis=1)
    return tr["true_range"].rolling(window=period).mean().iloc[-1]

# 7. OBV
# Theory: Dow Theory; volume confirms price trends.
def calculate_obv(df):
    direction = np.where(df["close"].diff() > 0, 1, -1)
    obv = (direction * df["volume"]).cumsum()
    return obv.iloc[-1]

# 8. VWAP
# Theory: Dynamic support/resistance level.
def calculate_vwap(df):
    typical_price = (df["high"] + df["low"] + df["close"]) / 3
    vwap = (typical_price * df["volume"]).cumsum() / df["volume"].cumsum()
    return vwap.iloc[-1]

# 9. Price ROC
# Theory: High ROC indicates strong momentum.
def calculate_roc(df, period=14):
    return ((df["close"].iloc[-1] - df["close"].iloc[-period]) / df["close"].iloc[-period]) * 100

# 10. Stochastic %K
# Theory: Behavioral Finance; overbought (>80) or oversold (<20).
def calculate_stochastic_k(df, period=14):
    lowest_low = df["low"].rolling(window=period).min()
    highest_high = df["high"].rolling(window=period).max()
    k = 100 * (df["close"] - lowest_low) / (highest_high - lowest_low)
    return k.iloc[-1]

# 11. Williams %R
# Theory: Similar to Stochastic, inverted scale.
def calculate_williams_r(df, period=14):
    highest_high = df["high"].rolling(window=period).max()
    lowest_low = df["low"].rolling(window=period).min()
    r = -100 * (highest_high - df["close"]) / (highest_high - lowest_low)
    return r.iloc[-1]

# 12. Momentum Indicator
# Theory: Raw momentum signal for trend strength.
def calculate_momentum(df, period=10):
    return df["close"].iloc[-1] - df["close"].iloc[-period]

# 13. Volume Oscillator
# Theory: Volume surges support price moves.
def calculate_volume_oscillator(df):
    short_ma = df["volume"].rolling(window=5).mean()
    long_ma = df["volume"].rolling(window=20).mean()
    return (short_ma.iloc[-1] - long_ma.iloc[-1]) / long_ma.iloc[-1] * 100

# 14. Chande Momentum Oscillator
# Theory: Pure momentum, less noise than RSI.
def calculate_cmo(df, period=14):
    delta = df["close"].diff()
    up_sum = delta.where(delta > 0, 0).rolling(window=period).sum()
    down_sum = (-delta.where(delta < 0, 0)).rolling(window=period).sum()
    cmo = 100 * (up_sum - down_sum) / (up_sum + down_sum)
    return cmo.iloc[-1] if not cmo.isna().all() else np.nan

# 15. Price Channel Breakout
# Theory: Breakouts signal trend starts (Murphy, 1999).
def calculate_channel_breakout(df):
    high_20 = df["high"].rolling(window=20).max().iloc[-1]
    low_20 = df["low"].rolling(window=20).min().iloc[-1]
    current_price = df["close"].iloc[-1]
    return 1 if current_price > high_20 else -1 if current_price < low_20 else 0  # 1 = breakout, -1 = breakdown, 0 = within

# Plotting function
def plot_metrics(df, metrics):
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    
    # Top: Price, SMA, EMA, VWAP
    ax1.plot(df["timestamp"], df["close"], label="Price", color="blue")
    sma_50 = df["close"].rolling(window=50).mean()
    ema_20 = df["close"].ewm(span=20, adjust=False).mean()
    typical_price = (df["high"] + df["low"] + df["close"]) / 3
    vwap = (typical_price * df["volume"]).cumsum() / df["volume"].cumsum()
    ax1.plot(df["timestamp"], sma_50, label="SMA 50", color="orange")
    ax1.plot(df["timestamp"], ema_20, label="EMA 20", color="green")
    ax1.plot(df["timestamp"], vwap, label="VWAP", color="purple")
    ax1.set_ylabel("Price (USDT)")
    ax1.legend()
    ax1.set_title("Aave Technical Analysis")
    
    # Middle: Volume, OBV, Bollinger Width
    ax2.plot(df["timestamp"], df["volume"], label="Volume", color="gray")
    obv = (np.where(df["close"].diff() > 0, 1, -1) * df["volume"]).cumsum()
    ax2b = ax2.twinx()
    ax2b.plot(df["timestamp"], obv, label="OBV", color="red")
    sma_20 = df["close"].rolling(window=20).mean()
    std_20 = df["close"].rolling(window=20).std()
    bollinger_width = (sma_20 + 2 * std_20 - (sma_20 - 2 * std_20)) / sma_20
    ax2b.plot(df["timestamp"], bollinger_width, label="Bollinger Width", color="cyan", linestyle="--")
    ax2.set_ylabel("Volume")
    ax2b.set_ylabel("OBV / Bollinger Width")
    ax2.legend(loc="upper left")
    ax2b.legend(loc="upper right")
    
    # Bottom: RSI, MACD, ATR
    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rsi = 100 - (100 / (1 + gain / loss))
    ax3.plot(df["timestamp"], rsi, label="RSI", color="blue")
    ema_12 = df["close"].ewm(span=12, adjust=False).mean()
    ema_26 = df["close"].ewm(span=26, adjust=False).mean()
    macd = ema_12 - ema_26
    signal = macd.ewm(span=9, adjust=False).mean()
    macd_hist = macd - signal
    ax3b = ax3.twinx()
    ax3b.plot(df["timestamp"], macd_hist, label="MACD Histogram", color="green")
    tr = pd.DataFrame()
    tr["hl"] = df["high"] - df["low"]
    tr["hc"] = (df["high"] - df["close"].shift()).abs()
    tr["lc"] = (df["low"] - df["close"].shift()).abs()
    tr["true_range"] = tr[["hl", "hc", "lc"]].max(axis=1)
    atr = tr["true_range"].rolling(window=14).mean()
    ax3b.plot(df["timestamp"], atr, label="ATR", color="orange", linestyle="--")
    ax3.set_ylabel("RSI")
    ax3b.set_ylabel("MACD / ATR")
    ax3.legend(loc="upper left")
    ax3b.legend(loc="upper right")
    
    plt.xlabel("Date")
    fig.tight_layout()
    plt.savefig("aave_technical_plot.png")
    plt.close()

# Main function
def main():
    try:
        df = fetch_historical_data(AAVE_SYMBOL)
        
        # Calculate metrics
        metrics = {
            "sma_50": calculate_sma_50(df),
            "ema_20": calculate_ema_20(df),
            "rsi": calculate_rsi(df),
            "macd": calculate_macd(df),
            "bollinger_width": calculate_bollinger_width(df),
            "atr": calculate_atr(df),
            "obv": calculate_obv(df),
            "vwap": calculate_vwap(df),
            "roc": calculate_roc(df),
            "stochastic_k": calculate_stochastic_k(df),
            "williams_r": calculate_williams_r(df),
            "momentum": calculate_momentum(df),
            "volume_oscillator": calculate_volume_oscillator(df),
            "cmo": calculate_cmo(df),
            "channel_breakout": calculate_channel_breakout(df)
        }
        
        # Prepare CSV data
        csv_data = {
            "Metric": [
                "SMA 50-day", "EMA 20-day", "RSI", "MACD Histogram",
                "Bollinger Bands Width", "ATR", "OBV", "VWAP",
                "Price ROC", "Stochastic %K", "Williams %R", "Momentum",
                "Volume Oscillator", "Chande Momentum Oscillator", "Price Channel Breakout"
            ],
            "Value": [
                metrics["sma_50"], metrics["ema_20"], metrics["rsi"],
                metrics["macd"], metrics["bollinger_width"], metrics["atr"],
                metrics["obv"], metrics["vwap"], metrics["roc"],
                metrics["stochastic_k"], metrics["williams_r"], metrics["momentum"],
                metrics["volume_oscillator"], metrics["cmo"], metrics["channel_breakout"]
            ]
        }
        csv_df = pd.DataFrame(csv_data)
        csv_df.to_csv("aave_technical_metrics.csv", index=False)
        print("Technical metrics saved to aave_technical_metrics.csv")
        
        # Plot metrics
        plot_metrics(df, metrics)
        print("Plot saved to aave_technical_plot.png")
        
        # Print metrics
        print("Aave Technical Analysis (April 7, 2024 – April 7, 2025)")
        for i, metric in enumerate(csv_data["Metric"]):
            value = csv_data["Value"][i]
            print(f"{metric}: {value:.2f}")
                
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()