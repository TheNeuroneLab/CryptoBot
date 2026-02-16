# Cryptocurrency Analysis Toolkit

This project provides a set of Python scripts to perform comprehensive financial and technical analysis on any cryptocurrency using historical data from the Binance API. The scripts are designed for the period from April 7, 2024, to April 7, 2025, but can be adjusted for other timeframes. AAVE (AAVEUSDT) is used as an example ticker in this demo, but you can analyze any coin by changing the ticker symbol in the scripts.

## Overview

The toolkit includes four scripts, each focusing on a different type of analysis:

1. **Fundamental Analysis** (`fundamental_analysis.py`): Computes 15 metrics like NVT Ratio, Mayer Multiple, and Price Momentum to assess intrinsic value and market efficiency.
2. **Peer Analysis** (`peer_analysis.py`): Compares a target coin to peers (e.g., ETH, SOL, BNB) across 8 metrics, including Sharpe Ratio and RSI, to contextualize performance.
3. **Financial Valuation** (`financial_valuation.py`): Calculates 20 metrics, such as DEUV and Price DCF, for a detailed financial valuation of the coin.
4. **Technical Analysis** (`technical_analysis.py`): Analyzes 15 technical indicators, like RSI, MACD, and Bollinger Bands, to identify trends and momentum.

Each script fetches data from Binance, processes it, saves results to a CSV file, and generates a visualization saved as a PNG file.

## Prerequisites

- **Python 3.8+**
- **Required Libraries**:
  - `requests`
  - `pandas`
  - `numpy`
  - `matplotlib`

Install dependencies using:
```bash
pip install requests pandas numpy matplotlib
```

- **Binance API Access**: No API key is required as the scripts use public endpoints, but be aware of Binance API rate limits (e.g., 1200 requests per minute).

## Setup

1. Clone or download this repository.
2. Ensure all scripts are in the same directory.
3. Modify the ticker symbol in each script if analyzing a coin other than AAVE:
   - In `fundamental_analysis.py`, `financial_valuation.py`, and `technical_analysis.py`, update `AAVE_SYMBOL = "AAVEUSDT"` to your desired ticker (e.g., `BTCUSDT`).
   - In `peer_analysis.py`, update `SYMBOLS = ["AAVEUSDT", ...]` and the `SUPPLIES` dictionary with appropriate tickers and circulating supplies.
4. Verify circulating supply values in scripts (e.g., `SUPPLIES` in `peer_analysis.py` or hardcoded values in others) using reliable sources like CoinMarketCap or blockchain explorers.
5. Adjust `START_DATE` and `END_DATE` in each script if you want a different analysis period:
   ```python
   START_DATE = int((datetime(YYYY, MM, DD)).timestamp() * 1000)
   END_DATE = int((datetime(YYYY, MM, DD)).timestamp() * 1000)
   ```

## Usage

Run each script individually from the command line:

```bash
python fundamental_analysis.py
python peer_analysis.py
python financial_valuation.py
python technical_analysis.py
```

### Outputs

Each script generates:
- A **CSV file** containing calculated metrics:
  - `aave_fundamental_metrics.csv`
  - `aave_peer_analysis.csv`
  - `aave_metrics.csv`
  - `aave_technical_metrics.csv`
- A **PNG plot** visualizing key metrics:
  - `aave_fundamental_plot.png`
  - `aave_peer_analysis_plot.png`
  - `aave_metrics_plot.png`
  - `aave_technical_plot.png`

**Note**: Replace "aave" in filenames with your ticker if modified. Running scripts overwrites existing files with the same names.

### Example

To analyze Bitcoin instead of AAVE:
1. In `fundamental_analysis.py`, change:
   ```python
   AAVE_SYMBOL = "AAVEUSDT"
   circulating_supply = 16000000
   ```
   to:
   ```python
   AAVE_SYMBOL = "BTCUSDT"
   circulating_supply = 19700000  # Approximate Bitcoin supply
   ```
2. Repeat for `financial_valuation.py` and `technical_analysis.py`.
3. For `peer_analysis.py`, update `SYMBOLS` and `SUPPLIES` accordingly.
4. Run the scripts:
   ```bash
   python fundamental_analysis.py
   ```

## Notes

- **Data Availability**: The scripts assume Binance provides complete data for the specified period. For dates after April 14, 2025, results will be limited to available data unless simulated data is used.
- **Rate Limits**: Binance API requests are minimal (one per coin per script), but frequent runs may hit limits. Add `time.sleep(1)` between API calls if needed.
- **Assumptions**: Metrics like staking yields (e.g., 6% APY), beta (1.4), or regulatory haircuts (20%) are placeholders. Update these based on coin-specific or market data.
- **Error Handling**: Scripts include try-except blocks to catch API failures or division-by-zero errors. Check console output for errors.
- **Customization**: To add new metrics, modify the respective script’s metric functions and update the `csv_data` dictionary in the `main()` function.
