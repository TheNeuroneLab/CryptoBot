import streamlit as st
import os
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain.agents import initialize_agent, AgentType
from langchain_core.messages import SystemMessage
from tools import tools

load_dotenv()

# -----------------------------------------
# 1. System Prompt
# -----------------------------------------
system_prompt_text = """
You are a crypto analysis AI agent.

⚠️ IMPORTANT: When using a tool, you MUST follow this exact format:

Thought: <your reasoning in natural language>
Action: <tool_name>
Action Input: symbol=<SYMBOL>, interval=<INTERVAL>, startTime=<YYYY-MM-DD>, endTime=<YYYY-MM-DD>

---
❌ WRONG (do not use):
Action Input: BTC 2024-01-01 to 2024-01-31
Action Input: BTC
Action Input: BTCUSDT 2024-01-01

✅ CORRECT (always use key=value pairs):
Action: nvt_ratio
Action Input: symbol=BTCUSDT, interval=1d, startTime=2024-01-01, endTime=2024-01-31

---
RULES:
1. SYMBOL must always be full trading pair, e.g., BTCUSDT, ETHUSDT, XRPUSDT.
2. interval must be one of: 1s, 1m, 5m, 15m, 1h, 4h, 1d, 1w, 1M.
3. Dates must always be in YYYY-MM-DD format.
4. If no date is given:
   Action Input: symbol=BTCUSDT, interval="", startTime="", endTime=""

---
Examples:

User: "NVT ratio of BTC today"
You:
Thought: I need to calculate the NVT ratio for Bitcoin as of today.
Action: nvt_ratio
Action Input: symbol=BTCUSDT, interval=1d, startTime=2025-08-22, endTime=2025-08-22

User: "NVT ratio of BTC from 01/01/2024 to 31/01/2024"
You:
Thought: I need to calculate the NVT ratio for Bitcoin in the given range.
Action: nvt_ratio
Action Input: symbol=BTCUSDT, interval=1d, startTime=2024-01-01, endTime=2024-01-31

"""
# -----------------------------------------
# 2. LLM setup
# -----------------------------------------
llm = ChatGroq(
    model="openai/gpt-oss-120b",  # text-only model
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.5,
    max_tokens=1024,
)

# -----------------------------------------
# 3. Agent (ReAct style)
# -----------------------------------------
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    agent_kwargs={"extra_prompt_messages": [SystemMessage(content=system_prompt_text)]},
    handle_parsing_errors=True,
)

def run_query(user_input, chat_history=[]):
    return agent.run(user_input)

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
        try:
            response = run_query(query, chat_history)
            st.write(response)
            chat_history.append(("human", query))
            chat_history.append(("ai", response))
        except Exception as e:
            st.error(f"Error: {str(e)}")
