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
    df["volume"] = df["volume"].astype(float)
    return df

# 1. NVT Ratio
# Theory: EMH; low NVT suggests price reflects activity (Gandal et al., 2018).
def calculate_nvt_ratio(df):
    circulating_supply = 16000000  # Fixed for AAVE
    market_caps = df["close"] * circulating_supply
    volumes = df["volume"] * df["close"]
    nvt = market_caps / volumes
    return nvt.mean()

# 2. Price/Volume Ratio
# Theory: High ratio tests price efficiency relative to activity.
def calculate_price_volume_ratio(df):
    current_price = df["close"].iloc[-1]
    avg_volume = (df["volume"] * df["close"]).mean()
    return current_price / avg_volume if avg_volume != 0 else np.inf

# 3. Market Cap Growth Rate
# Theory: High CAGR reflects investor demand, a fundamental driver.
def calculate_market_cap_growth(df):
    circulating_supply = 16000000
    start_market_cap = df["close"].iloc[0] * circulating_supply
    end_market_cap = df["close"].iloc[-1] * circulating_supply
    years = 1
    cagr = (end_market_cap / start_market_cap)**(1 / years) - 1 if start_market_cap != 0 else np.inf
    return cagr

# 4. Volume CAGR
# Theory: Growth in volume signals market interest, supporting fundamentals.
def calculate_volume_cagr(df):
    start_volume = (df["volume"] * df["close"]).iloc[0]
    end_volume = (df["volume"] * df["close"]).iloc[-1]
    years = 1
    cagr = (end_volume / start_volume)**(1 / years) - 1 if start_volume != 0 else np.inf
    return cagr

# 5. Liquidity Ratio
# Theory: High liquidity indicates market depth, a fundamental strength.
def calculate_liquidity_ratio(df):
    circulating_supply = 16000000
    market_cap = df["close"].iloc[-1] * circulating_supply
    avg_daily_volume = (df["volume"] * df["close"]).mean()
    return avg_daily_volume / market_cap if market_cap != 0 else np.inf

# 6. Mayer Multiple
# Theory: EMH; high multiple (>2.4) suggests speculation (Greater Fool Theory).
def calculate_mayer_multiple(df):
    prices = df["close"]
    ma_200 = prices.rolling(window=200).mean().iloc[-1]
    current_price = prices.iloc[-1]
    return current_price / ma_200 if ma_200 != 0 else np.inf

# 7. Price Momentum
# Theory: High momentum reflects demand strength, a fundamental signal.
def calculate_price_momentum(df):
    price_change = (df["close"].iloc[-1] - df["close"].iloc[0]) / df["close"].iloc[0]
    return price_change

# 8. Volume Momentum
# Theory: Volume growth indicates activity supporting price fundamentals.
def calculate_volume_momentum(df):
    early_volume = (df["volume"] * df["close"]).iloc[:len(df)//2].mean()
    late_volume = (df["volume"] * df["close"]).iloc[len(df)//2:].mean()
    return (late_volume - early_volume) / early_volume if early_volume != 0 else np.inf

# 9. Volatility-Adjusted Market Cap
# Theory: Asset Pricing; adjusts value for risk (Damodaran, 2012).
def calculate_volatility_adjusted_market_cap(df):
    circulating_supply = 16000000
    market_cap = df["close"].iloc[-1] * circulating_supply
    returns = df["close"].pct_change().dropna()
    volatility = returns.std() * np.sqrt(365)
    return market_cap / (1 + volatility) if volatility != 0 else market_cap

# 10. Turnover Ratio
# Theory: High turnover suggests active use or selling pressure.
def calculate_turnover_ratio(df):
    circulating_supply = 16000000
    total_volume = (df["volume"] * df["close"]).sum()
    return total_volume / circulating_supply if circulating_supply != 0 else np.inf

# 11. Price Stability Ratio
# Theory: High stability supports intrinsic value as a utility token.
def calculate_price_stability_ratio(df):
    returns = df["close"].pct_change().dropna()
    volatility = returns.std() * np.sqrt(365)
    avg_price = df["close"].mean()
    return avg_price / volatility if volatility != 0 else np.inf

# 12. Volume-to-Price Ratio
# Theory: High ratio indicates activity supports price fundamentals.
def calculate_volume_to_price_ratio(df):
    avg_volume = (df["volume"] * df["close"]).mean()
    current_price = df["close"].iloc[-1]
    return avg_volume / current_price if current_price != 0 else np.inf

# 13. Discounted Expected Utility Value (DEUV)
# Theory: Asset Pricing; discounts future activity for intrinsic value.
def calculate_deuv(df, discount_rate=0.12, growth_rate=0.08, years=5):
    circulating_supply = 16000000
    market_cap = df["close"].iloc[-1] * circulating_supply
    current_volume = (df["volume"] * df["close"]).mean()
    future_volumes = [current_volume * (1 + growth_rate)**t for t in range(1, years + 1)]
    discounted_volume = sum([vol / (1 + discount_rate)**t for t, vol in enumerate(future_volumes, 1)])
    deuv = market_cap / discounted_volume if discounted_volume != 0 else np.inf
    return deuv

# 14. Price to Volatility Cost
# Theory: High ratio suggests price exceeds risk cost, a fundamental metric.
def calculate_price_to_volatility_cost(df):
    current_price = df["close"].iloc[-1]
    returns = df["close"].pct_change().dropna()
    volatility = returns.std() * np.sqrt(365)
    volatility_cost = current_price * volatility
    return current_price / volatility_cost if volatility_cost != 0 else np.inf

# 15. Regulatory Discount
# Theory: External risk impacts fundamental value (per feedback).
def calculate_regulatory_discount(df):
    current_price = df["close"].iloc[-1]
    haircut = 0.20
    return current_price * (1 - haircut)

# Plotting function
def plot_metrics(df, metrics):
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    
    # Top: Price and Mayer Multiple
    ax1.plot(df["timestamp"], df["close"], label="Price", color="blue")
    ma_200 = df["close"].rolling(window=200).mean()
    ax1.plot(df["timestamp"], ma_200, label="200-day MA", color="orange")
    ax1.axhline(metrics["regulatory_discount"], color="red", linestyle="--", label="Regulatory Discount")
    ax1.set_ylabel("Price (USDT)")
    ax1.legend()
    ax1.set_title("Aave Fundamental Metrics")
    
    # Middle: Volume and NVT Ratio
    ax2.plot(df["timestamp"], df["volume"] * df["close"], label="Volume", color="green")
    circulating_supply = 16000000
    nvt = (df["close"] * circulating_supply) / (df["volume"] * df["close"])
    ax2b = ax2.twinx()
    ax2b.plot(df["timestamp"], nvt, label="NVT Ratio", color="purple")
    ax2.set_ylabel("Volume (USDT)")
    ax2b.set_ylabel("NVT Ratio")
    ax2.legend(loc="upper left")
    ax2b.legend(loc="upper right")
    
    # Bottom: Price Momentum and Volume Momentum
    price_momentum = df["close"].pct_change(30).dropna()  # 30-day momentum
    volume_momentum = (df["volume"] * df["close"]).pct_change(30).dropna()
    ax3.plot(df["timestamp"][30:], price_momentum, label="Price Momentum", color="cyan")
    ax3b = ax3.twinx()
    ax3b.plot(df["timestamp"][30:], volume_momentum, label="Volume Momentum", color="magenta")
    ax3.set_ylabel("Price Momentum")
    ax3b.set_ylabel("Volume Momentum")
    ax3.legend(loc="upper left")
    ax3b.legend(loc="upper right")
    
    plt.xlabel("Date")
    fig.tight_layout()
    plt.savefig("aave_fundamental_plot.png")
    plt.close()

# Main function
def main():
    try:
        df = fetch_historical_data(AAVE_SYMBOL)
        
        # Calculate metrics
        metrics = {
            "nvt_ratio": calculate_nvt_ratio(df),
            "price_volume_ratio": calculate_price_volume_ratio(df),
            "market_cap_growth": calculate_market_cap_growth(df),
            "volume_cagr": calculate_volume_cagr(df),
            "liquidity_ratio": calculate_liquidity_ratio(df),
            "mayer_multiple": calculate_mayer_multiple(df),
            "price_momentum": calculate_price_momentum(df),
            "volume_momentum": calculate_volume_momentum(df),
            "volatility_adjusted_market_cap": calculate_volatility_adjusted_market_cap(df),
            "turnover_ratio": calculate_turnover_ratio(df),
            "price_stability_ratio": calculate_price_stability_ratio(df),
            "volume_to_price_ratio": calculate_volume_to_price_ratio(df),
            "deuv": calculate_deuv(df),
            "price_to_volatility_cost": calculate_price_to_volatility_cost(df),
            "regulatory_discount": calculate_regulatory_discount(df)
        }
        
        # Prepare CSV data
        csv_data = {
            "Metric": [
                "NVT Ratio", "Price/Volume Ratio", "Market Cap Growth Rate", "Volume CAGR",
                "Liquidity Ratio", "Mayer Multiple", "Price Momentum", "Volume Momentum",
                "Volatility-Adjusted Market Cap", "Turnover Ratio", "Price Stability Ratio",
                "Volume-to-Price Ratio", "Discounted Expected Utility Value",
                "Price to Volatility Cost", "Regulatory Discount"
            ],
            "Value": [
                metrics["nvt_ratio"], metrics["price_volume_ratio"], metrics["market_cap_growth"],
                metrics["volume_cagr"], metrics["liquidity_ratio"], metrics["mayer_multiple"],
                metrics["price_momentum"], metrics["volume_momentum"],
                metrics["volatility_adjusted_market_cap"], metrics["turnover_ratio"],
                metrics["price_stability_ratio"], metrics["volume_to_price_ratio"],
                metrics["deuv"], metrics["price_to_volatility_cost"], metrics["regulatory_discount"]
            ]
        }
        csv_df = pd.DataFrame(csv_data)
        csv_df.to_csv("aave_fundamental_metrics.csv", index=False)
        print("Fundamental metrics saved to aave_fundamental_metrics.csv")
        
        # Plot metrics
        plot_metrics(df, metrics)
        print("Plot saved to aave_fundamental_plot.png")
        
        # Print metrics
        print("Aave Fundamental Analysis (April 7, 2024 – April 7, 2025)")
        for i, metric in enumerate(csv_data["Metric"]):
            value = csv_data["Value"][i]
            print(f"{metric}: {value:.2f}")
                
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()