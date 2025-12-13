import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# -------------------------
# Tool Mapping
# -------------------------
tool_map = {
    "nvt ratio": "nvt_ratio",
    "sharpe ratio": "sharpe_ratio",
    "price volume ratio": "price_volume_ratio",
    "mayer multiple": "mayer_multiple",
    "market cap growth": "market_cap_growth",
    "price": "price_history",
    "price history": "price_history",
}