import os
import json
import datetime
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from pydantic.v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from tools import tools

load_dotenv()

# LLM Setup (for intent extraction)
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0,
    max_tokens=1024,
)

# New LLM for natural language compilation
llm_natural = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.2,  # Slightly higher for natural phrasing
    max_tokens=512,
)

# Current date
current_date = datetime.date.today().strftime("%Y-%m-%d")  # 2025-08-31

# Step 1: Structured Intent Extraction
class QueryIntent(BaseModel):
    metric: str = Field(description="The metric or analysis type requested, e.g., 'price', 'nvt ratio', 'sharpe ratio', 'price history'")
    symbol: str = Field(description="The crypto symbol, e.g., 'BTC', 'ETH'")
    interval: str = Field(default="1d", description="Data interval, e.g., '1d', '1h'. Default to '1d' if not specified.")
    start_date: str = Field(default="", description="Start date in YYYY-MM-DD. Leave empty if not specified.")
    end_date: str = Field(default="", description="End date in YYYY-MM-DD. Leave empty if not specified.")

extraction_prompt = ChatPromptTemplate.from_template("""
You are an expert at extracting intent from crypto analysis queries.
Extract the following as JSON:
- metric: The main metric or analysis type (e.g., 'price' for price history, 'nvt ratio', 'sharpe ratio'). Be precise.
- symbol: The cryptocurrency symbol (e.g., 'BTC', 'ETH'). Do not append 'USDT' here.
- interval: Data interval if mentioned (e.g., '1d', '1h'), default '1d'.
- start_date: Parsed start date in YYYY-MM-DD (e.g., 'July 1 2024' -> '2024-07-01', '01/01/2024' -> '2024-01-01'). Use {current_date} for 'today' or 'now'. Leave empty if not specified.
- end_date: Parsed end date in YYYY-MM-DD, similar to start_date. Leave empty if not specified.

If the query doesn't match a known metric, set metric to 'unknown'.

Query: {query}
""")

extraction_chain = extraction_prompt | llm | JsonOutputParser()

# Step 2: Natural Language Compilation
natural_prompt = ChatPromptTemplate.from_template("""
You are a natural language compiler. You will receive data in JSON format from a cryptocurrency analysis tool. Convert the data into a clear, concise, and natural language response for the user. Focus on summarizing the key information (e.g., metric value, price trends, or summary statistics) in a way that is easy to understand. Include relevant details like symbol, date range, or interval if provided.

JSON Data:
{json_data}

Output a natural language response.
""")

natural_chain = natural_prompt | llm_natural

# Step 3: Tool Mapping
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
        intent_raw = extraction_chain.invoke({"query": user_input, "current_date": current_date})
        intent = QueryIntent(**intent_raw)
        print(f"Extracted Intent: {intent.dict()}")
        
        if intent.metric.lower() == "unknown":
            return "Sorry, I don't support that metric yet."
        
        # Step 2: Select tool
        metric_lower = intent.metric.lower()
        tool_name = next((v for k, v in tool_map.items() if k in metric_lower), None)
        if not tool_name:
            return f"Unknown metric: {intent.metric}. Supported: {list(tool_map.keys())}"
        
        print(f"Selected Tool: {tool_name}")
        
        # Step 3: Format input
        symbol = intent.symbol.upper()
        if not symbol.endswith("USDT"):
            symbol += "USDT"
        input_str = f"symbol={symbol}, interval={intent.interval}, startTime={intent.start_date}, endTime={intent.end_date}"
        print(f"Formatted Input: {input_str}")
        
        # Step 4: Call the tool
        tool = next((t for t in tools if t.name == tool_name), None)
        if not tool:
            return f"Tool not found: {tool_name}"
        
        result = tool.invoke(input_str)
        # Pretty-print JSON result for debugging
        try:
            result_json = json.loads(result)
            print(f"\nJSON Result:\n{json.dumps(result_json, indent=2)}")
        except json.JSONDecodeError:
            print(f"\nJSON Result: {result}")
            return result
        
        # Step 5: Compile natural language response
        natural_response = natural_chain.invoke({"json_data": result})
        print(f"\nNatural Language Response:\n{natural_response.content}")
        return natural_response.content
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return f"Error processing query: {str(e)}"

if __name__ == "__main__":
    test_query = "I want to know BTC price from July 1 to July 20 2024"
    user_input = input("Enter your query (or press Enter for default): ").strip()
    query = user_input if user_input else test_query
    run_query(query)