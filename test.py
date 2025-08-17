import streamlit as st
import os
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain.agents import initialize_agent, AgentType
from langchain_core.messages import SystemMessage
from tools import tools

load_dotenv()

# -----------------------------------------
# 1. Custom System Prompt
# -----------------------------------------
system_prompt_text = """
You are a crypto analytics assistant.

You have access to these tools:
- nvt_ratio(symbol: str, start_date: str, end_date: str)
- sharpe_ratio(symbol: str, start_date: str, end_date: str)
- price_volume_ratio(symbol: str, start_date: str, end_date: str)
- mayer_multiple(symbol: str, start_date: str, end_date: str)
- market_cap_growth(symbol: str, start_date: str, end_date: str)

Your job:
1. Identify the correct tool from the above list based on the metric in the user’s query.
2. Extract the cryptocurrency symbol (BTC, ETH, etc.).
3. Determine the period of time:
   - If both start and end dates are given, use them.
   - If only one date is given, use it as both start_date and end_date.
   - If a natural period like "last 7 days" or "past month" is given, choose the exact start_date and end_date based on today’s date.
   - Dates must be in DD/MM/YYYY format.
4. Call the chosen tool directly with the extracted `symbol`, `start_date`, and `end_date`.
5. If the query is missing the metric, symbol, or date, ask the user for the missing detail before calling the tool.
6. Do not explain what you are doing — either call the function or ask for missing details.
"""

# -----------------------------------------
# 2. Set up Groq LLM
# -----------------------------------------
llm = ChatGroq(
    model_name="deepseek-r1-distill-llama-70b",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0,
)

# -----------------------------------------
# 3. Create Agent (supports multiple params)
# -----------------------------------------
agent = initialize_agent(
    tools,
    llm,
    agent="openai-functions",  # supports multi-argument tools
    verbose=True,
    handle_parsing_errors=True,
    agent_kwargs={
        "extra_prompt_messages": [SystemMessage(content=system_prompt_text)]
    }
)

def run_query(user_input, chat_history=[]):
    return agent.invoke({
        "input": user_input,
        "chat_history": chat_history
    })

# -----------------------------------------
# 4. Streamlit UI
# -----------------------------------------
if __name__ == "__main__":
    chat_history = []
    st.title("CryptoBot: Dynamic Crypto Analysis")
    st.write("Enter a query (e.g., 'NVT Ratio for BTC from 01/01/2024 to 31/01/2024').")

    query = st.text_input("Your Query:", "")

    if query:
        st.subheader("Groq Analysis")
        response = run_query(query, chat_history)
        st.write(response)
        chat_history.append(("human", query))
        chat_history.append(("ai", response["output"]))
