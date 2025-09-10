import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))  # Ensure the current directory is in sys.path
import json
import datetime
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from pydantic.v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from tools.tools import tools
from prompt.prompts import extraction_prompt, natural_prompt, merge_prompt  # Import prompts from prompts.py

load_dotenv()

# -------------------------
# LLM Setup
# -------------------------
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0,
    max_tokens=1024,
)

llm_natural = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.2,
    max_tokens=512,
)

# Current date
current_date = datetime.date.today().strftime("%Y-%m-%d")  # 2025-09-01

# -------------------------
# Intent Extraction Model
# -------------------------
class QueryIntent(BaseModel):
    metrics: list[str] = Field(description="List of metrics or analysis types requested, e.g., ['nvt ratio', 'sharpe ratio', 'price history']")
    symbol: str = Field(description="The crypto symbol, e.g., 'BTC', 'ETH'")
    interval: str = Field(default="1d", description="Data interval, e.g., '1d', '1h'. Default to '1d' if not specified.")
    start_date: str = Field(default="", description="Start date in YYYY-MM-DD. Leave empty if not specified.")
    end_date: str = Field(default="", description="End date in YYYY-MM-DD. Leave empty if not specified.")

extraction_chain = extraction_prompt | llm | JsonOutputParser()
natural_chain = natural_prompt | llm_natural
merge_chain = merge_prompt | llm_natural

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

# -------------------------
# Main Query Function
# -------------------------
def run_query(user_input):
    print(f"\nProcessing query: {user_input}")
    try:
        # Step 1: Extract Intent
        intent_raw = extraction_chain.invoke({
            "query": user_input,
            "current_date": current_date,
            "supported_metrics": ", ".join(tool_map.keys())
        })
        intent = QueryIntent(**intent_raw)
        print(f"Extracted Intent: {intent.dict()}")

        if not intent.metrics or all(m.lower() == "unknown" for m in intent.metrics):
            return f"Sorry, no valid metrics found. Supported: {list(tool_map.keys())}"

        # Prepare shared parameters
        symbol = intent.symbol.upper()
        if not symbol.endswith("USDT"):
            symbol += "USDT"
        interval = intent.interval
        start_date = intent.start_date
        end_date = intent.end_date

        results = []

        for metric in intent.metrics:
            metric_lower = metric.lower().strip()
            tool_name = tool_map.get(metric_lower)
            if not tool_name:
                results.append({"metric": metric, "error": f"Unknown metric. Supported: {list(tool_map.keys())}"})
                continue
            
            print(f"Selected Tool for {metric}: {tool_name}")

            tool_instance = next((t for t in tools if t.name == tool_name), None)
            if not tool_instance:
                results.append({"metric": metric, "error": f"Tool not found: {tool_name}"})
                continue

            input_str = f"symbol={symbol}, interval={interval}, startTime={start_date}, endTime={end_date}"
            tool_output = tool_instance.invoke(input_str)

            # Parse tool output safely
            try:
                tool_output_json = json.loads(tool_output) if isinstance(tool_output, str) else tool_output
            except Exception:
                tool_output_json = {"raw": str(tool_output)}

            results.append({"metric": metric, "tool_result": tool_output_json})

        if not results:
            return "No valid responses generated."

        # Step 2: Generate natural language response
        if len(results) == 0:
            return "No valid metrics to process."
        elif len(results) == 1:
            natural_response = natural_chain.invoke({"json_data": results[0]}).content
            return natural_response
        else:
            merged_json = {"json_data": results}
            natural_response = natural_chain.invoke(merged_json).content
            return natural_response

    except Exception as e:
        print(f"Error: {str(e)}")
        return f"Error processing query: {str(e)}"

# -------------------------
# Run as script
# -------------------------
if __name__ == "__main__":
    test_query = "I want to know BTC price from July 1 to July 20 2024"
    user_input = input("Enter your query (or press Enter for default): ").strip()
    query = user_input if user_input else test_query
    response = run_query(query)
    print(f"\nFinal Response:\n{response}")
