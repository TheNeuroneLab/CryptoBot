import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import json
import datetime
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from pydantic.v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from tools.tools import tools
from prompt.prompts import extraction_prompt, natural_prompt, leader_prompt, irrelevant_prompt, literate_prompt, chart_decision_prompt
from utils.llm_utils import llm
from tools.map import tool_map
from utils.helper import run_plot_code_and_upload

load_dotenv()
current_date = datetime.date.today().strftime("%Y-%m-%d")

# -------------------------
# Leader Chain
# -------------------------
class LeaderDecision(BaseModel):
    workflow: str = Field(description="Workflow to route to, e.g., 'crypto_metrics', 'irrelevant_question'")

leader_chain = leader_prompt | llm | JsonOutputParser()

# -------------------------
# Intent Extraction Model
# -------------------------
class QueryIntent(BaseModel):
    metrics: list[str]
    symbol: str
    interval: str = "1d"
    start_date: str = ""
    end_date: str = ""
class ChartDecision(BaseModel):
    should_chart: bool = False
    chart_type: str = "line"
    x_field: str = "date"
    y_field: str = "close"

extraction_chain = extraction_prompt | llm | JsonOutputParser()
irrelevant_chain = irrelevant_prompt | llm
literate_chain = literate_prompt | llm
chart_decision_chain = chart_decision_prompt | llm

# -------------------------
# Chart Generation
# -------------------------
def handle_chart_generation(tool_result):
    """Check chart suitability, generate chart, return image_url."""
    if not isinstance(tool_result, dict) or "data" not in tool_result:
        print("⚠️ No valid data found for chart.")
        return None

    try:
        response = chart_decision_chain.invoke({
            "metric_json": json.dumps(tool_result, ensure_ascii=False)
        }).content.strip().lower()

        print("\n🤖 Chart decision raw:", response)

        decision = ChartDecision()

        # Parse logic giống extraction-style, không cần JSON
        if "no chart" in response:
            decision.should_chart = False
        else:
            decision.should_chart = True
            if "bar" in response:
                decision.chart_type = "bar"
            elif "line" in response:
                decision.chart_type = "line"

            # X-axis
            if "exchange" in response:
                decision.x_field = "exchange"
            elif "date" in response:
                decision.x_field = "date"

            # Y-axis
            if "volume" in response:
                decision.y_field = "volume"
            elif "close" in response:
                decision.y_field = "close"

        if decision.should_chart:
            print(f"✅ Chart approved → {decision.chart_type} chart")
            image_url = run_plot_code_and_upload(
                tool_result.get("data"),
                chart_type=decision.chart_type,
                x_field=decision.x_field,
                y_field=decision.y_field
            )
            print(f"📈 Chart URL: {image_url}")
            return image_url
        else:
            print("🚫 Chart not needed for this metric.")
            return None

    except Exception as e:
        print(f"⚠️ handle_chart_generation error: {e}")
        return None

# -------------------------
# Metrics Workflow (Chart Test Version)
# -------------------------
def crypto_metrics_workflow(user_input):
    """Modified metrics flow: stops after chart generation."""
    print(f"\nRunning crypto_metrics test flow for query: {user_input}")
    try:
        # Step 1: Extract intent
        intent_raw = extraction_chain.invoke({
            "query": user_input,
            "current_date": current_date,
            "supported_metrics": ", ".join(tool_map.keys())
        })
        intent = QueryIntent(**intent_raw)
        print(f"🎯 Extracted Intent: {intent.dict()}")

        if not intent.metrics or all(m.lower() == "unknown" for m in intent.metrics):
            print("⚠️ No valid metrics found.")
            return "No valid metrics found."

        symbol = intent.symbol.upper()
        if not symbol.endswith("USDT"):
            symbol += "USDT"

        results = []

        # Step 2: Run tools & generate charts
        for metric in intent.metrics:
            metric_lower = metric.lower().strip()
            tool_name = tool_map.get(metric_lower)
            if not tool_name:
                print(f"⚠️ Unknown metric: {metric}")
                continue

            tool_instance = next((t for t in tools if t.name == tool_name), None)
            if not tool_instance:
                print(f"⚠️ Tool not found: {tool_name}")
                continue

            input_str = f"symbol={symbol}, interval={intent.interval}, startTime={intent.start_date}, endTime={intent.end_date}"
            print(f"\n🔧 Running {tool_name} with: {input_str}")
            tool_output = tool_instance.invoke(input_str)

            try:
                tool_output_json = json.loads(tool_output) if isinstance(tool_output, str) else tool_output
            except Exception:
                tool_output_json = {"raw": str(tool_output)}

            print(f"📊 Tool output sample: {str(tool_output_json)[:250]}")

            # Step 3: Handle chart generation
            image_url = handle_chart_generation(tool_output_json)
            results.append({
                "metric": metric,
                "chart_url": image_url
            })

        print("\n=== ✅ Chart Test Results ===")
        for res in results:
            print(f"• {res['metric']}: {res['chart_url'] or 'no chart generated'}")
        print("=============================\n")

        lines = ["### Chart Test Results"]
        for r in results:
            metric = r.get("metric", "unknown")
            url = r.get("chart_url")
            if url:
                # UI của bạn sẽ tự bắt URL này và render <img>
                lines.append(f"- **{metric}**: {url}")
            else:
                lines.append(f"- **{metric}**: no chart generated")

        return "\n".join(lines)

    except Exception as e:
        print(f"Error in crypto_metrics_workflow: {e}")
        return f"Error processing query: {str(e)}"

# -------------------------
# Other Workflows (unchanged)
# -------------------------
def irrelevant_question_workflow(user_input):
    print(f"\nRunning irrelevant_question workflow for query: {user_input}")
    try:
        response = irrelevant_chain.invoke({"query": user_input}).content
        return response
    except Exception as e:
        print(f"Error in irrelevant_question_workflow: {str(e)}")
        return "Sorry, I couldn't process your request."

def literate_question_workflow(user_input):
    print(f"\nRunning literate_question workflow for query: {user_input}")
    try:
        response = literate_chain.invoke({"query": user_input}).content
        return response
    except Exception as e:
        print(f"Error in literate_question_workflow: {str(e)}")
        return "Sorry, I couldn't process your request."

def financial_detection_workflow(user_input):
    print(f"\nRunning financial_detection workflow for query: {user_input}")
    return "Financial intent detected in your query."

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
# Main Function
# -------------------------
def run_query(user_input):
    print(f"\nProcessing query: {user_input}")
    try:
        decision_raw = leader_chain.invoke({"query": user_input})
        decision = LeaderDecision(**decision_raw)
        print(f"🧭 Leader Decision: {decision.workflow}")

        if decision.workflow not in workflows:
            return f"Unknown workflow: {decision.workflow}"

        selected_workflow = workflows[decision.workflow]
        return selected_workflow(user_input)

    except Exception as e:
        print(f"Error in run_query: {str(e)}")
        return f"Error processing query: {str(e)}"

# -------------------------
# Run as Script
# -------------------------
if __name__ == "__main__":
    test_query = "Show me BTC price history from October 1 to October 17 2025"
    user_input = input("Enter your query (or press Enter for default): ").strip()
    query = user_input if user_input else test_query
    response = run_query(query)
    print(f"\nFinal Result:\n{response}")
