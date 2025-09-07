import streamlit as st
import main  # Import the existing crypto analysis agent
import datetime
from streamlit.components.v1 import html
import asyncio
import time

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Custom CSS for ChatGPT-like styling using Tailwind CSS
def load_css():
    css = """
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <style>
        .chat-container {
            max-width: 800px;
            margin: auto;
            padding: 20px;
            height: calc(100vh - 150px);
            overflow-y: auto;
        }
        .stChatMessage {
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 10px;
        }
        .input-container {
            position: fixed;
            bottom: 0;
            width: 100%;
            max-width: 800px;
            margin: auto;
            padding: 10px;
            background-color: white;
            border-top: 1px solid #e5e7eb;
        }
    </style>
    """
    html(css, height=0)

# Load custom CSS
load_css()

# Streamlit app layout
st.set_page_config(page_title="Crypto Analysis Agent", layout="wide")
st.title("Crypto Analysis Agent")
st.write("Ask about crypto metrics like price, NVT ratio, Sharpe ratio, etc.")

# Sidebar for configuration and context
with st.sidebar:
    st.header("Crypto Analysis Agent")
    st.write("Query crypto metrics for symbols like BTC, ETH, etc.")
    st.write(f"Current date: {datetime.date.today().strftime('%Y-%m-%d')}")
    st.markdown("---")
    st.write("Example queries:")
    st.write("- BTC price from July 1 to July 20 2024")
    st.write("- ETH NVT ratio for last 30 days")
    st.write("- Sharpe ratio for BTC")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Async function to simulate streaming response from synchronous run_query
async def stream_response(input_text: str, placeholder):
    if not input_text.strip():
        placeholder.markdown("Error: Please enter a valid query.")
        return None

    try:
        # Call the synchronous run_query function
        response = main.run_query(input_text)
        
        # Simulate streaming by breaking response into chunks
        chunks = response.split(" ")
        streamed_response = ""
        for chunk in chunks:
            streamed_response += chunk + " "
            placeholder.markdown(streamed_response)
            await asyncio.sleep(0.05)  # Simulate streaming delay
        return streamed_response.strip()
    except Exception as e:
        placeholder.markdown(f"Error: {str(e)}")
        return None

# Chat input
if user_input := st.chat_input("Type your crypto query (e.g., BTC price from July 1 to July 20 2024)"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Stream assistant response
    with st.chat_message("assistant"):
        placeholder = st.empty()
        response = asyncio.run(stream_response(user_input, placeholder))
        if response:
            st.session_state.messages.append({"role": "assistant", "content": response})