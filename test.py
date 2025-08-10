import streamlit as st
import os

from langchain_groq import ChatGroq
from langchain.agents import initialize_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage
from langchain_core.messages import HumanMessage
from tools import tools
from dotenv import load_dotenv


load_dotenv()
# -----------------------------------------
# 3. Custom System Prompt
# -----------------------------------------

system_prompt_text = """
You are a crypto analytics assistant.
When the user asks for a crypto metric like:
- NVT Ratio
- Sharpe Ratio
- Price Volume Ratio
- Mayer Multiple
- Market Cap Growth

You MUST:
1. Identify the correct tool from the provided list.
2. Pass the cryptocurrency symbol (e.g., BTC, ETH) to that tool.
3. Return ONLY the output from the tool.

Do NOT guess results. If the metric or symbol is missing, ask the user.
"""

# -----------------------------------------
# 5. Set up Groq LLM
# -----------------------------------------

llm = ChatGroq(
    model_name="deepseek-r1-distill-llama-70b",
    api_key=os.getenv("GROQ_API_KEY"),  # replace with your real API key
    temperature=0,
)

# -----------------------------------------
# 6. Create Agent + Memory
# -----------------------------------------

agent = initialize_agent(
    tools,
    llm,
    agent="chat-conversational-react-description",  # Conversational + tool description based
    verbose=True,
    handle_parsing_errors=True,
    agent_kwargs={
        "extra_prompt_messages": [system_prompt_text]
    }
)

def run_query(user_input, chat_history=[]):
    return agent.invoke({
        "input": user_input,
        "chat_history": chat_history
    })

# -----------------------------------------
# 7. Streamlit UI
# -----------------------------------------

if __name__ == "__main__":
    chat_history = []
    st.title("CryptoBot: Dynamic Crypto Analysis")
    st.write("Enter a query (e.g., 'Performance peer analysis on BTC coin', 'Fundamental analysis for ETH last 6 months').")

    query = st.text_input("Your Query:", "")

    if query:
        st.subheader("Groq Analysis")
        response = run_query(query, chat_history)
        st.write(response)
        chat_history.append(("human", query))
        chat_history.append(("ai", response["output"]))
