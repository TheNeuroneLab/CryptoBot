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

# LLM Setup (for intent extraction)
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0,
    max_tokens=1024,
)

# LLM for natural language compilation
llm_natural = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.2,  # Slightly higher for natural phrasing
    max_tokens=512,
)

# Current date
current_date = datetime.date.today().strftime("%Y-%m-%d")  # 2025-09-01

# Step 1: Structured Intent Extraction
class QueryIntent(BaseModel):
    metrics: list[str] = Field(description="List of metrics or analysis types requested, e.g., ['nvt ratio', 'sharpe ratio', 'price history']")
    symbol: str = Field(description="The crypto symbol, e.g., 'BTC', 'ETH'")
    interval: str = Field(default="1d", description="Data interval, e.g., '1d', '1h'. Default to '1d' if not specified.")
    start_date: str = Field(default="", description="Start date in YYYY-MM-DD. Leave empty if not specified.")
    end_date: str = Field(default="", description="End date in YYYY-MM-DD. Leave empty if not specified.")

extraction_chain = extraction_prompt | llm | JsonOutputParser()

# Step 2: Natural Language Compilation
natural_chain = natural_prompt | llm_natural

# Step 3: Merge Chain
merge_chain = merge_prompt | llm_natural

# Step 4: Tool Mapping
tool_map = {
    "nvt ratio": "nvt_ratio",
    "sharpe ratio": "sharpe_ratio",
    "price volume ratio": "price_volume_ratio",
    "mayer multiple": "mayer_multiple",
    "market cap growth": "market_cap_growth",
    "price": "price_history",
    "price history": "price_history",
}

def run_query(user_input):
    print(f"\nProcessing query: {user_input}")
    
    try:
        # Step 1: Extract intent
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
        
        natural_responses = []
        
        for metric in intent.metrics:
            metric_lower = metric.lower()
            
            # Step 2: Select tool
            tool_name = next((v for k, v in tool_map.items() if k in metric_lower), None)
            if not tool_name:
                natural_responses.append(f"Unknown metric: {metric}. Supported: {list(tool_map.keys())}")
                continue
            
            print(f"Selected Tool for {metric}: {tool_name}")
            
            # Step 3: Format input
            input_str = f"symbol={symbol}, interval={interval}, startTime={start_date}, endTime={end_date}"
            print(f"Formatted Input for {metric}: {input_str}")
            
            # Step 4: Call the tool
            tool = next((t for t in tools if t.name == tool_name), None)
            if not tool:
                natural_responses.append(f"Tool not found: {tool_name}")
                continue
            
            result = tool.invoke(input_str)
            # Pretty-print JSON result for debugging
            try:
                result_json = json.loads(result)
                print(f"\nJSON Result for {metric}:\n{json.dumps(result_json, indent=2)}")
            except json.JSONDecodeError:
                print(f"\nJSON Result for {metric}: {result}")
                natural_responses.append(f"Error processing {metric}: Invalid tool output")
                continue
            
            # Step 5: Compile natural language response
            natural_response = natural_chain.invoke({"json_data": result}).content
            print(f"\nNatural Language Response for {metric}:\n{natural_response}")
            natural_responses.append(natural_response)
        
        # Step 6: Merge responses if multiple
        if len(natural_responses) == 0:
            return "No valid responses generated."
        elif len(natural_responses) == 1:
            return natural_responses[0]
        else:
            merged_input = {
                "responses": "\n\n".join([f"Response {i+1}: {resp}" for i, resp in enumerate(natural_responses)]),
                "query": user_input
            }
            merged_response = merge_chain.invoke(merged_input).content
            print(f"\nMerged Response:\n{merged_response}")
            return merged_response
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return f"Error processing query: {str(e)}"

if __name__ == "__main__":
    test_query = "I want to know BTC price from July 1 to July 20 2024"
    user_input = input("Enter your query (or press Enter for default): ").strip()
    query = user_input if user_input else test_query
    run_query(query)