import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import json
import datetime
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from pydantic.v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from tools.tools import tools
from prompt.prompts import extraction_prompt, natural_prompt, leader_prompt, irrelevant_prompt, literate_prompt
from utils.llm_utils import llm
from tools.map import tool_map
load_dotenv()

# Current date
current_date = datetime.date.today().strftime("%Y-%m-%d")

# -------------------------
# Leader Chain
# -------------------------
class LeaderDecision(BaseModel):
    workflow: str = Field(description="The workflow to route to, e.g., 'crypto_metrics', 'irrelevant_question', 'financial_detection'")

leader_chain = leader_prompt | llm | JsonOutputParser()

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
natural_chain = natural_prompt | llm
irrelevant_chain = irrelevant_prompt | llm
literate_chain = literate_prompt | llm

# -------------------------
# Workflow Functions
# -------------------------
def crypto_metrics_workflow(user_input):
    """The original workflow for crypto metrics analysis."""
    print(f"\nRunning crypto_metrics workflow for query: {user_input}")
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
            print(f"result of {str(metric)}: {str(tool_output_json)}")
            
        if not results:
            return "No valid responses generated."

        # Step 2: Generate natural language response
        if len(results) == 0:
            return "No valid metrics to process."
        elif len(results) == 1:
            natural_response = natural_chain.invoke({
                "query": user_input,
                "json_data": results[0]
            }).content
            return natural_response
        else:
            merged_json = {"json_data": results}
            natural_response = natural_chain.invoke({
                "query": user_input,
                "json_data": merged_json["json_data"]
            }).content
            return natural_response


    except Exception as e:
        print(f"Error in crypto_metrics_workflow: {str(e)}")
        return f"Error processing query: {str(e)}"

def irrelevant_question_workflow(user_input):
    """Workflow for handling irrelevant questions using LLM."""
    print(f"\nRunning irrelevant_question workflow for query: {user_input}")
    try:
        response = irrelevant_chain.invoke({"query": user_input}).content
        return response
    except Exception as e:
        print(f"Error in irrelevant_question_workflow: {str(e)}")
        return f"Sorry, I couldn't process your request. Please ask about cryptocurrency metrics like NVT ratio or price history."

def literate_question_workflow(user_input):
    """Workflow for handling irrelevant questions using LLM."""
    print(f"\nRunning literate_question workflow for query: {user_input}")
    try:
        response = literate_chain.invoke({"query": user_input}).content
        return response
    except Exception as e:
        print(f"Error in literate_question_workflow: {str(e)}")
        return f"Sorry, I couldn't process your request. Please ask about cryptocurrency metrics like NVT ratio or price history."


def financial_detection_workflow(user_input):
    """Placeholder workflow for financial detection."""
    print(f"\nRunning financial_detection workflow for query: {user_input}")
    return "Financial intent detected in your query. For crypto-specific metrics, please rephrase. For general financial advice, consult a professional."

# -------------------------
# Workflow Control
# -------------------------
workflows = {
    "crypto_metrics": crypto_metrics_workflow,
    "irrelevant_question": irrelevant_question_workflow,
    "literate_question": literate_question_workflow,
    "financial_detection": financial_detection_workflow,
}

# -------------------------
# Main Query Function with Leader
# -------------------------
def run_query(user_input):
    print(f"\nProcessing query: {user_input}")
    try:
        # Step 0: Leader Decision
        decision_raw = leader_chain.invoke({"query": user_input})
        decision = LeaderDecision(**decision_raw)
        print(f"Leader Decision: {decision.workflow}")

        if decision.workflow not in workflows:
            return f"Unknown workflow selected: {decision.workflow}. Please check the leader prompt."

        # Route to the selected workflow
        selected_workflow = workflows[decision.workflow]
        return selected_workflow(user_input)

    except Exception as e:
        print(f"Error in run_query: {str(e)}")
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
