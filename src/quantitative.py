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

# 1. NVT Ratio (Market Cap / Transaction Volume)
# Theory: EMH; low NVT suggests price reflects transaction activity.
def calculate_nvt_ratio(df):
    circulating_supply = 16000000  # Fixed for AAVE
    market_caps = df["close"] * circulating_supply
    volumes = df["volume"] * df["close"]  # Quote volume in USDT
    nvt = market_caps / volumes
    return nvt.mean()

# 2. Price/Volume Ratio (Proxy for P/F or P/S)
# Theory: High ratio indicates low activity relative to price, testing efficiency.
def calculate_price_volume_ratio(df):
    current_price = df["close"].iloc[-1]
    avg_volume = (df["volume"] * df["close"]).mean()
    return current_price / avg_volume if avg_volume != 0 else np.inf

# 3. Sharpe Ratio for Staking Yield
# Theory: CAPM; high Sharpe indicates attractive risk-adjusted returns.
def calculate_sharpe_ratio_staking(df):
    returns = df["close"].pct_change().dropna()
    staking_apy = 0.06  # Assumed
    daily_staking_yield = staking_apy / 365
    total_returns = returns + daily_staking_yield
    risk_free_rate = 0.025 / 365
    excess_returns = total_returns - risk_free_rate
    sharpe = excess_returns.mean() / excess_returns.std() * np.sqrt(365) if excess_returns.std() != 0 else np.inf
    return sharpe

# 4. Current Utility Value (Market Cap / Volume)
# Theory: High ratio suggests price outpaces activity, testing overvaluation.
def calculate_cuv(df):
    circulating_supply = 16000000
    market_cap = df["close"].iloc[-1] * circulating_supply
    avg_volume = (df["volume"] * df["close"]).mean()
    return market_cap / avg_volume if avg_volume != 0 else np.inf

# 5. Discounted Expected Utility Value (DEUV)
# Theory: Asset Pricing; discounts future volume growth for intrinsic value.
def calculate_deuv(df, discount_rate=0.12, growth_rate=0.08, years=5):
    circulating_supply = 16000000
    market_cap = df["close"].iloc[-1] * circulating_supply
    current_volume = (df["volume"] * df["close"]).mean()
    future_volumes = [current_volume * (1 + growth_rate)**t for t in range(1, years + 1)]
    discounted_volume = sum([vol / (1 + discount_rate)**t for t, vol in enumerate(future_volumes, 1)])
    deuv = market_cap / discounted_volume if discounted_volume != 0 else np.inf
    return deuv

# 6. CAGR of Volume
# Theory: High growth signals market interest, supporting price fundamentals.
def calculate_volume_cagr(df):
    start_volume = (df["volume"] * df["close"]).iloc[0]
    end_volume = (df["volume"] * df["close"]).iloc[-1]
    years = 1
    cagr = (end_volume / start_volume)**(1 / years) - 1 if start_volume != 0 else np.inf
    return cagr

# 7. Volume Source Composition (Buy vs. Sell Proxy)
# Theory: Balanced volumes suggest stable market dynamics.
def calculate_volume_composition(df):
    # Proxy buy/sell using taker volumes (approximate)
    buy_volume = df["taker_buy_quote"].astype(float).sum()
    total_volume = (df["volume"] * df["close"]).sum()
    sell_volume = total_volume - buy_volume
    return {"buy_volume": buy_volume / total_volume, "sell_volume": sell_volume / total_volume} if total_volume != 0 else {"buy_volume": 0, "sell_volume": 0}

# 8. Price Volatility Reduction
# Theory: Lower volatility signals market confidence, supporting EMH.
def calculate_volatility_reduction(df):
    returns = df["close"].pct_change().dropna()
    early_vol = returns.iloc[:len(returns)//2].std() * np.sqrt(365)
    late_vol = returns.iloc[len(returns)//2:].std() * np.sqrt(365)
    reduction = (early_vol - late_vol) / early_vol if early_vol != 0 else 0
    return max(0, reduction)

# 9. Price Momentum
# Theory: High momentum suggests bullish fundamentals or speculation.
def calculate_price_momentum(df):
    price_change = (df["close"].iloc[-1] - df["close"].iloc[0]) / df["close"].iloc[0]
    return price_change

# 10. Risk-Adjusted Volume Discount
# Theory: CAPM; adjusts volume for market risk exposure.
def calculate_risk_adjusted_volume_discount(df, risk_free_rate=0.025):
    returns = df["close"].pct_change().dropna()
    volatility = returns.std() * np.sqrt(365)
    avg_volume = (df["volume"] * df["close"]).mean()
    beta = 1.4  # Assumed
    market_risk_premium = 0.06
    discount_rate = risk_free_rate + beta * market_risk_premium
    risk_adjusted_volume = avg_volume / (1 + discount_rate * volatility)
    return risk_adjusted_volume / avg_volume if avg_volume != 0 else 0

# 11. Trading Volume
# Theory: High volume reflects market activity, supporting price.
def calculate_trading_volume(df):
    return (df["volume"] * df["close"]).mean()

# 12. Volume Volatility
# Theory: High volatility suggests diverse trader behavior.
def calculate_volume_volatility(df):
    volumes = df["volume"] * df["close"]
    return volumes.std() / volumes.mean() if volumes.mean() != 0 else 0

# 13. Price Stability Ratio
# Theory: High ratio indicates stability, supporting staking-like behavior.
def calculate_price_stability_ratio(df):
    returns = df["close"].pct_change().dropna()
    volatility = returns.std() * np.sqrt(365)
    avg_price = df["close"].mean()
    return avg_price / volatility if volatility != 0 else np.inf

# 14. Volume-to-Price Ratio
# Theory: High ratio suggests activity supports price, testing efficiency.
def calculate_volume_to_price_ratio(df):
    avg_volume = (df["volume"] * df["close"]).mean()
    current_price = df["close"].iloc[-1]
    return avg_volume / current_price if current_price != 0 else np.inf

# 15. Price Correlation to Market
# Theory: Low correlation suggests unique fundamentals.
def calculate_price_correlation(df):
    # Proxy market with AAVE itself (single asset); ideally use BTC/ETH
    returns = df["close"].pct_change().dropna()
    market_returns = returns  # Self-correlation for demo
    return np.corrcoef(returns, market_returns)[0, 1]

# 16. Mayer Multiple
# Theory: EMH; high multiple (>2.4) suggests Greater Fool pricing.
def calculate_mayer_multiple(df):
    prices = df["close"]
    ma_200 = prices.rolling(window=200).mean().iloc[-1]
    current_price = prices.iloc[-1]
    return current_price / ma_200 if ma_200 != 0 else np.inf

# 17. Price-Based DCF
# Theory: EMH; projects price growth as fundamental value.
def calculate_price_dcf(df, discount_rate=0.15, growth_rate=0.10, years=5):
    current_price = df["close"].iloc[-1]
    future_prices = [current_price * (1 + growth_rate)**t for t in range(1, years + 1)]
    discounted_price = sum([p / (1 + discount_rate)**t for t, p in enumerate(future_prices, 1)])
    valuation_ratio = discounted_price / current_price if current_price != 0 else np.inf
    return {"intrinsic_value": discounted_price, "valuation_ratio": valuation_ratio}

# 18. Price to Volatility Cost
# Theory: CAPM; high ratio suggests price exceeds risk cost.
def calculate_price_to_volatility_cost(df):
    current_price = df["close"].iloc[-1]
    returns = df["close"].pct_change().dropna()
    volatility = returns.std() * np.sqrt(365)
    volatility_cost = current_price * volatility  # Opportunity cost
    return current_price / volatility_cost if volatility_cost != 0 else np.inf

# 19. Regulatory Discount
# Theory: External risk impacts valuation.
def calculate_regulatory_discount(df):
    current_price = df["close"].iloc[-1]
    haircut = 0.20
    return current_price * (1 - haircut)

# 20. Price/Volume Ratio (Additional for P/S Proxy)
# Theory: Complements P/F, testing activity efficiency.
def calculate_price_volume_ratio_alt(df):
    current_price = df["close"].iloc[-1]
    recent_volume = (df["volume"] * df["close"]).iloc[-30:].mean()  # Last 30 days
    return current_price / recent_volume if recent_volume != 0 else np.inf

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
    ax1.set_title("Aave Price and Mayer Multiple")
    
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
    
    # Bottom: Sharpe Ratio and Momentum
    returns = df["close"].pct_change().dropna()
    rolling_sharpe = (returns.rolling(30).mean() / returns.rolling(30).std()) * np.sqrt(365)
    ax3.plot(df["timestamp"][1:], rolling_sharpe, label="Rolling Sharpe Ratio", color="cyan")
    momentum = df["close"].pct_change(30).dropna()  # 30-day momentum
    ax3b = ax3.twinx()
    ax3b.plot(df["timestamp"][30:], momentum, label="Price Momentum", color="magenta")
    ax3.set_ylabel("Sharpe Ratio")
    ax3b.set_ylabel("Momentum")
    ax3.legend(loc="upper left")
    ax3b.legend(loc="upper right")
    
    plt.xlabel("Date")
    fig.tight_layout()
    plt.savefig("aave_metrics_plot.png")
    plt.close()

# Main function
def main():
    try:
        df = fetch_historical_data(AAVE_SYMBOL)
        
        # Calculate metrics
        metrics = {
            "nvt_ratio": calculate_nvt_ratio(df),
            "price_volume_ratio": calculate_price_volume_ratio(df),
            "sharpe_ratio": calculate_sharpe_ratio_staking(df),
            "cuv": calculate_cuv(df),
            "deuv": calculate_deuv(df),
            "volume_cagr": calculate_volume_cagr(df),
            "volume_composition": calculate_volume_composition(df),
            "volatility_reduction": calculate_volatility_reduction(df),
            "price_momentum": calculate_price_momentum(df),
            "risk_adjusted_volume_discount": calculate_risk_adjusted_volume_discount(df),
            "trading_volume": calculate_trading_volume(df),
            "volume_volatility": calculate_volume_volatility(df),
            "price_stability_ratio": calculate_price_stability_ratio(df),
            "volume_to_price_ratio": calculate_volume_to_price_ratio(df),
            "price_correlation": calculate_price_correlation(df),
            "mayer_multiple": calculate_mayer_multiple(df),
            "price_dcf": calculate_price_dcf(df),
            "price_to_volatility_cost": calculate_price_to_volatility_cost(df),
            "regulatory_discount": calculate_regulatory_discount(df),
            "price_volume_ratio_alt": calculate_price_volume_ratio_alt(df)
        }
        
        # Prepare CSV data
        csv_data = {
            "Metric": [
                "NVT Ratio", "Price/Volume Ratio", "Sharpe Ratio", "Current Utility Value",
                "Discounted Expected Utility Value", "Volume CAGR", "Volume Composition (Buy)",
                "Volume Composition (Sell)", "Volatility Reduction", "Price Momentum",
                "Risk-Adjusted Volume Discount", "Trading Volume", "Volume Volatility",
                "Price Stability Ratio", "Volume-to-Price Ratio", "Price Correlation",
                "Mayer Multiple", "Price DCF Intrinsic Value", "Price DCF Valuation Ratio",
                "Price to Volatility Cost", "Regulatory Discount", "Price/Volume Ratio (Alt)"
            ],
            "Value": [
                metrics["nvt_ratio"], metrics["price_volume_ratio"], metrics["sharpe_ratio"],
                metrics["cuv"], metrics["deuv"], metrics["volume_cagr"],
                metrics["volume_composition"]["buy_volume"], metrics["volume_composition"]["sell_volume"],
                metrics["volatility_reduction"], metrics["price_momentum"],
                metrics["risk_adjusted_volume_discount"], metrics["trading_volume"],
                metrics["volume_volatility"], metrics["price_stability_ratio"],
                metrics["volume_to_price_ratio"], metrics["price_correlation"],
                metrics["mayer_multiple"], metrics["price_dcf"]["intrinsic_value"],
                metrics["price_dcf"]["valuation_ratio"], metrics["price_to_volatility_cost"],
                metrics["regulatory_discount"], metrics["price_volume_ratio_alt"]
            ]
        }
        csv_df = pd.DataFrame(csv_data)
        csv_df.to_csv("aave_metrics.csv", index=False)
        print("Metrics saved to aave_metrics.csv")
        
        # Plot metrics
        plot_metrics(df, metrics)
        print("Plot saved to aave_metrics_plot.png")
        
        # Print metrics
        print("Aave Financial Valuation (April 7, 2024 – April 7, 2025)")
        for metric, value in zip(csv_data["Metric"], csv_data["Value"]):
            if isinstance(value, dict):
                print(f"{metric}: {value}")
            else:
                print(f"{metric}: {value:.2f}")
    except Exception as e:
        print(f"Error: {str(e)}")           

if __name__ == "__main__":
    main()