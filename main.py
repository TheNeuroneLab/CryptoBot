import streamlit as st
import json
import os
import pandas as pd
import requests
import base64
from datetime import datetime, timedelta
import re
from groq import Groq  # Import Groq SDK
from analysis.peer import fetch_binance_data, calculate_nvt_ratio, calculate_sharpe_ratio, calculate_price_volume_ratio, calculate_mayer_multiple, calculate_speculative_signal, calculate_price_stability_ratio, calculate_rsi, calculate_macd
from analysis.fundamental import calculate_market_cap_growth, calculate_volume_cagr, calculate_liquidity_ratio, calculate_price_momentum, calculate_volume_momentum, calculate_volatility_adjusted_market_cap, calculate_turnover_ratio, calculate_volume_to_price_ratio, calculate_deuv, calculate_price_to_volatility_cost, calculate_regulatory_discount
from analysis.quantitative import calculate_cuv, calculate_volume_composition, calculate_volatility_reduction, calculate_risk_adjusted_volume_discount, calculate_trading_volume, calculate_volume_volatility, calculate_price_correlation, calculate_price_dcf, calculate_price_volume_ratio_alt
from analysis.technical import calculate_sma_50, calculate_ema_20, calculate_bollinger_width, calculate_atr, calculate_obv, calculate_vwap, calculate_roc, calculate_stochastic_k, calculate_williams_r, calculate_momentum, calculate_volume_oscillator, calculate_cmo, calculate_channel_breakout

load_dotenv()
# Binance API setup
BINANCE_API_URL = "https://api.binance.com/api/v3"

# Coin configurations (approximate circulating supplies as of April 2025)
COIN_CONFIG = {
    "BTC": {"symbol": "BTCUSDT", "supply": 19700000},
    "ETH": {"symbol": "ETHUSDT", "supply": 120000000},
    "AAVE": {"symbol": "AAVEUSDT", "supply": 16000000},
    "SOL": {"symbol": "SOLUSDT", "supply": 500000000},
    "BNB": {"symbol": "BNBUSDT", "supply": 150000000},
    "UNI": {"symbol": "UNIUSDT", "supply": 600000000},
    "LINK": {"symbol": "LINKUSDT", "supply": 500000000}
}

# Groq API setup
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"
groq_client = Groq(api_key=GROQ_API_KEY)

def extract_llm_query(query):
    prompt = f"""
    You are a crypto assistant that classifies user queries into structured data.

    Given a user question about cryptocurrency, extract and return the following information as JSON:

    - "coin": A list of coin names mentioned (e.g., Bitcoin, Ethereum).
    - "metric": A list of specific metrics the user is asking about.
    - "time_frame": The time frame mentioned (e.g., "last week", "past 30 days").
    - "analysis_type": A list of analysis types that the extracted metrics belong to. Choose from:
    - "Peer"
    - "Fundamental"
    - "Quantitative"
    - "Technical"

    Here are all the known metrics, grouped by analysis type:

    Peer Analysis:
    - NVT Ratio, Sharpe Ratio, Price/Volume Ratio, Mayer Multiple, Speculative Signal, Price Stability Ratio, RSI, MACD Histogram

    Fundamental Analysis:
    - NVT Ratio, Price/Volume Ratio, Market Cap Growth Rate, Volume CAGR, Liquidity Ratio, Mayer Multiple, Price Momentum, Volume Momentum, Volatility-Adjusted Market Cap, Turnover Ratio, Price Stability Ratio, Volume-to-Price Ratio, Discounted Expected Utility Value, Price to Volatility Cost, Regulatory Discount

    Quantitative Analysis:
    - NVT Ratio, Price/Volume Ratio, Sharpe Ratio, Current Utility Value, Discounted Expected Utility Value, Volume CAGR, Volume Composition (Buy), Volume Composition (Sell), Volatility Reduction, Price Momentum, Risk-Adjusted Volume Discount, Trading Volume, Volume Volatility, Price Stability Ratio, Volume-to-Price Ratio, Price Correlation, Mayer Multiple, Price DCF Intrinsic Value, Price DCF Valuation Ratio, Price to Volatility Cost, Regulatory Discount, Price/Volume Ratio (Alt)

    Technical Analysis:
    - SMA 50-day, EMA 20-day, RSI, MACD Histogram, Bollinger Bands Width, ATR (Average True Range), OBV (On-Balance Volume), VWAP (Volume Weighted Average Price), Price ROC (Rate of Change), Stochastic %K, Williams %R, Momentum, Volume Oscillator, Chande Momentum Oscillator, Price Channel Breakout

    Respond in the following JSON format
    If any part is not present in the user query, use an empty list [] or an empty string "".
    
    Example 1:
    User Query: "Can you show Ethereum's NVT Ratio and Trading Volume over the last week?"
    Response:
    {{
        "coin": ["Ethereum"],
        "metric": ["NVT Ratio", "Trading Volume"],
        "time_frame": "last week",
        "analysis_type": ["Peer", "Quantitative"]
    }}
    Example 2:
    User Query: "I want to see Bitcoin's RSI and Bollinger Bands Width for the past 30 days."
    Response:
    {{
        "coin": ["Bitcoin"],
        "metric": ["RSI", "Bollinger Bands Width"],
        "time_frame": "last 30 days",
        "analysis_type": ["Peer", "Technical"]
    }}
    
    USER QUERY: {query}
    """ 
    try:
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=1024,
            temperature=0.5
        )
        raw_output = response.choices[0].message.content
        # Extract JSON block using regex
        json_match = re.search(r"\{[\s\S]*?\}", raw_output)
        if json_match:
            json_str = json_match.group(0)
            return json.loads(json_str)
        else:
            raise ValueError("No JSON object found in the LLM response.")
    except Exception as e:
        return f"Error connecting to Groq: {str(e)}"

# Function to parse user query
def parse_query(query):
    query = query.lower().strip()
    result = {"coin": None, "analysis": None, "days": 365, "start_date": None, "end_date": None}
    
    # Extract coin
    for coin in COIN_CONFIG:
        if coin.lower() in query or COIN_CONFIG[coin]["symbol"].lower().replace("usdt", "") in query:
            result["coin"] = coin
            break
    
    # Extract analysis type
    for analysis in ["peer", "fundamental", "quantitative", "technical"]:
        if analysis in query:
            result["analysis"] = analysis
            break
    
    # Extract date range
    date_patterns = [
        (r"last (\d+) (days|months|years)", lambda m: int(m.group(1)) * {"days": 1, "months": 30, "years": 365}[m.group(2)]),
        (r"from (\d{4}-\d{2}-\d{2}) to (\d{4}-\d{2}-\d{2})", lambda m: (m.group(1), m.group(2)))
    ]
    for pattern, handler in date_patterns:
        match = re.search(pattern, query)
        if match:
            if pattern.startswith("last"):
                result["days"] = handler(match)
            else:
                result["start_date"] = datetime.strptime(handler(match)[0], "%Y-%m-%d")
                result["end_date"] = datetime.strptime(handler(match)[1], "%Y-%m-%d")
            break
    
    return result

# Function to configure date range
def configure_dates(days=None, start_date=None, end_date=None):
    if start_date and end_date:
        start_ts = int(start_date.timestamp() * 1000)
        end_ts = int(end_date.timestamp() * 1000)
    else:
        end_date = datetime(2025, 4, 7)
        start_date = end_date - timedelta(days=days or 365)
        start_ts = int(start_date.timestamp() * 1000)
        end_ts = int(end_date.timestamp() * 1000)
    return start_ts, end_ts

# Function to run peer analysis
def run_peer_analysis(coin, start_ts, end_ts):
    symbol = COIN_CONFIG[coin]["symbol"]
    peer_symbols = [COIN_CONFIG[c]["symbol"] for c in COIN_CONFIG if c != coin] + [symbol]
    data = {s: fetch_binance_data(s) for s in peer_symbols}
    results = {}
    for s in peer_symbols:
        df = data[s]
        supply = COIN_CONFIG[list(COIN_CONFIG.keys())[peer_symbols.index(s)]]["supply"]
        nvt = calculate_nvt_ratio(df, supply)
        mayer = calculate_mayer_multiple(df)
        results[s] = {
            "NVT Ratio": nvt,
            "Sharpe Ratio": calculate_sharpe_ratio(df),
            "Price/Volume Ratio": calculate_price_volume_ratio(df),
            "Mayer Multiple": mayer,
            "Speculative Signal": calculate_speculative_signal(nvt, mayer),
            "Price Stability Ratio": calculate_price_stability_ratio(df),
            "RSI": calculate_rsi(df),
            "MACD Histogram": calculate_macd(df)
        }
    csv_data = {"Metric": list(results[symbol].keys())}
    for s in peer_symbols:
        token = s.replace("USDT", "")
        csv_data[token] = [results[s][metric] for metric in csv_data["Metric"]]
    csv_df = pd.DataFrame(csv_data)
    csv_path = f"{coin.lower()}_peer_analysis.csv"
    csv_df.to_csv(csv_path, index=False)
    return csv_path, None  # No plot for simplicity

# Function to run fundamental analysis
def run_fundamental_analysis(coin, start_ts, end_ts):
    symbol = COIN_CONFIG[coin]["symbol"]
    df = fetch_binance_data(symbol)
    metrics = {
        "NVT Ratio": calculate_nvt_ratio(df, COIN_CONFIG[coin]["supply"]),
        "Price/Volume Ratio": calculate_price_volume_ratio(df),
        "Market Cap Growth Rate": calculate_market_cap_growth(df),
        "Volume CAGR": calculate_volume_cagr(df),
        "Liquidity Ratio": calculate_liquidity_ratio(df),
        "Mayer Multiple": calculate_mayer_multiple(df),
        "Price Momentum": calculate_price_momentum(df),
        "Volume Momentum": calculate_volume_momentum(df),
        "Volatility-Adjusted Market Cap": calculate_volatility_adjusted_market_cap(df),
        "Turnover Ratio": calculate_turnover_ratio(df),
        "Price Stability Ratio": calculate_price_stability_ratio(df),
        "Volume-to-Price Ratio": calculate_volume_to_price_ratio(df),
        "Discounted Expected Utility Value": calculate_deuv(df),
        "Price to Volatility Cost": calculate_price_to_volatility_cost(df),
        "Regulatory Discount": calculate_regulatory_discount(df)
    }
    csv_data = {
        "Metric": list(metrics.keys()),
        "Value": list(metrics.values())
    }
    csv_df = pd.DataFrame(csv_data)
    csv_path = f"{coin.lower()}_fundamental_metrics.csv"
    csv_df.to_csv(csv_path, index=False)
    return csv_path, None

# Function to run quantitative analysis
def run_quantitative_analysis(coin, start_ts, end_ts):
    symbol = COIN_CONFIG[coin]["symbol"]
    df = fetch_binance_data(symbol)
    metrics = {
        "NVT Ratio": calculate_nvt_ratio(df, COIN_CONFIG[coin]["supply"]),
        "Price/Volume Ratio": calculate_price_volume_ratio(df),
        "Sharpe Ratio": calculate_sharpe_ratio(df),
        "Current Utility Value": calculate_cuv(df),
        "Discounted Expected Utility Value": calculate_deuv(df),
        "Volume CAGR": calculate_volume_cagr(df),
        "Volume Composition (Buy)": calculate_volume_composition(df)["buy_volume"],
        "Volume Composition (Sell)": calculate_volume_composition(df)["sell_volume"],
        "Volatility Reduction": calculate_volatility_reduction(df),
        "Price Momentum": calculate_price_momentum(df),
        "Risk-Adjusted Volume Discount": calculate_risk_adjusted_volume_discount(df),
        "Trading Volume": calculate_trading_volume(df),
        "Volume Volatility": calculate_volume_volatility(df),
        "Price Stability Ratio": calculate_price_stability_ratio(df),
        "Volume-to-Price Ratio": calculate_volume_to_price_ratio(df),
        "Price Correlation": calculate_price_correlation(df),
        "Mayer Multiple": calculate_mayer_multiple(df),
        "Price DCF Intrinsic Value": calculate_price_dcf(df)["intrinsic_value"],
        "Price DCF Valuation Ratio": calculate_price_dcf(df)["valuation_ratio"],
        "Price to Volatility Cost": calculate_price_to_volatility_cost(df),
        "Regulatory Discount": calculate_regulatory_discount(df),
        "Price/Volume Ratio (Alt)": calculate_price_volume_ratio_alt(df)
    }
    csv_data = {
        "Metric": list(metrics.keys()),
        "Value": list(metrics.values())
    }
    csv_df = pd.DataFrame(csv_data)
    csv_path = f"{coin.lower()}_quantitative_metrics.csv"
    csv_df.to_csv(csv_path, index=False)
    return csv_path, None

# Function to run technical analysis
def run_technical_analysis(coin, start_ts, end_ts):
    symbol = COIN_CONFIG[coin]["symbol"]
    df = fetch_binance_data(symbol)
    metrics = {
        "SMA 50-day": calculate_sma_50(df),
        "EMA 20-day": calculate_ema_20(df),
        "RSI": calculate_rsi(df),
        "MACD Histogram": calculate_macd(df),
        "Bollinger Bands Width": calculate_bollinger_width(df),
        "ATR": calculate_atr(df),
        "OBV": calculate_obv(df),
        "VWAP": calculate_vwap(df),
        "Price ROC": calculate_roc(df),
        "Stochastic %K": calculate_stochastic_k(df),
        "Williams %R": calculate_williams_r(df),
        "Momentum": calculate_momentum(df),
        "Volume Oscillator": calculate_volume_oscillator(df),
        "Chande Momentum Oscillator": calculate_cmo(df),
        "Price Channel Breakout": calculate_channel_breakout(df)
    }
    csv_data = {
        "Metric": list(metrics.keys()),
        "Value": list(metrics.values())
    }
    csv_df = pd.DataFrame(csv_data)
    csv_path = f"{coin.lower()}_technical_metrics.csv"
    csv_df.to_csv(csv_path, index=False)
    return csv_path, None

# Function to encode image to base64
def image_to_base64(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    return None

# Function to call Groq
def get_llm_response(query, csv_data, plot_base64):
    prompt = f"""
    User Query: {query}
    
    CSV Data:
    {csv_data.to_string() if csv_data is not None else 'No CSV data available'}
    
    Plot Description: {'An image is available (base64 encoded). Analyze the metrics and provide insights.' if plot_base64 else 'No plot available.'}
    
    Provide a concise summary and insights based on the query, CSV data, and plot (if available).
    """
    
    try:
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=1024,
            temperature=0.5
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error connecting to Groq: {str(e)}"

# Streamlit UI
st.title("CryptoBot: Dynamic Crypto Analysis")
st.write("Enter a query (e.g., 'Performance peer analysis on BTC coin', 'Fundamental analysis for ETH last 6 months').")

# User input
query = st.text_input("Your Query:", "")

if query:
    st.subheader("Groq Analysis")
    # st.write(json.dumps(extract_llm_query(query)), indent=4)
    st.write(extract_llm_query(query))

    # Parse query
    # parsed_query = parse_query(query)
    # coin = parsed_query["coin"]
    # analysis = parsed_query["analysis"]
    # days = parsed_query["days"]
    # start_date = parsed_query["start_date"]
    # end_date = parsed_query["end_date"]
    
    # if not coin or not analysis:
    #     st.warning("Please specify a valid coin (e.g., BTC, ETH, AAVE) and analysis type (peer, fundamental, quantitative, technical).")
    # elif coin not in COIN_CONFIG:
    #     st.warning(f"Coin {coin} not supported. Choose from {', '.join(COIN_CONFIG.keys())}.")
    # else:
    #     st.subheader(f"Running {analysis.capitalize()} Analysis for {coin}")
        
    #     # Configure date range
    #     start_ts, end_ts = configure_dates(days, start_date, end_date)
        
    #     # Override date parameters in scripts
    #     START_DATE = start_ts
    #     END_DATE = end_ts
        
    #     # Run analysis
    #     analysis_functions = {
    #         "peer": run_peer_analysis,
    #         "fundamental": run_fundamental_analysis,
    #         "quantitative": run_quantitative_analysis,
    #         "technical": run_technical_analysis
    #     }
        
    #     try:
    #         csv_path, plot_path = analysis_functions[analysis](coin, start_ts, end_ts)
            
    #         # Display CSV
    #         csv_data = None
    #         if csv_path and os.path.exists(csv_path):
    #             csv_data = pd.read_csv(csv_path)
    #             st.subheader("CSV Output")
    #             st.dataframe(csv_data)
            
    #         # Display Plot (if available)
    #         plot_base64 = None
    #         if plot_path:
    #             if os.path.exists(plot_path):
    #                 st.subheader("Plot Output")
    #                 st.image(plot_path, caption="Analysis Plot", use_column_width=True)
    #                 plot_base64 = image_to_base64(plot_path)
    #             else:
    #                 st.error(f"Plot file {plot_path} not found.")
            
    #         # Get LLM response
    #         llm_response = get_llm_response(query, csv_data, plot_base64)
    #         st.subheader("Groq Analysis")
    #         st.write(llm_response)
            
        # except Exception as e:
        #     st.error(f"Error: {str(e)}")