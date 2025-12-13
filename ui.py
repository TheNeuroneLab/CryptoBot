import os
import sys
import datetime
import asyncio
import streamlit as st
from dotenv import load_dotenv
import main

# Load environment
load_dotenv()
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(
    page_title="Biracle",
    page_icon="🌞",
    layout="wide"
)

# ---------------------------
# Session State Init
# ---------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []  # current conversation

if "history" not in st.session_state:
    st.session_state.history = []   # list of past conversations

if "active_chat" not in st.session_state:
    st.session_state.active_chat = None  # track selected past chat

# ---------------------------
# Dynamic Title
# ---------------------------
crypto_emojis = ["💹", "📈", "📉", "💰", "🪙", "⚡"]
today = datetime.date.today().strftime("%A, %B %d, %Y")

st.markdown(
    f"""
    <div style="text-align: center; padding: 1rem 0;">
        <h1 style="font-size: 2.2rem; margin-bottom: 0.3rem;">
            {crypto_emojis[datetime.datetime.now().second % len(crypto_emojis)]} 
            Crypto Analysis Agent
        </h1>
        <p style="color: gray; font-size: 1rem; margin-top: 0;">
            Your AI assistant for precise crypto insights — {today}
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------
# Sidebar
# ---------------------------
with st.sidebar:
    st.header("⚙️ Controls")

    # Start a new chat
    if st.button("🆕 New Chat", use_container_width=True):
        if st.session_state.messages:  # save only if not empty
            preview = st.session_state.messages[0]["content"][:30] + "..."
            st.session_state.history.append({
                "title": preview,
                "messages": st.session_state.messages.copy()
            })
        st.session_state.messages = []
        st.session_state.active_chat = None
        st.rerun()

    # Clear all chats
    if st.button("🗑️ Clear All", use_container_width=True):
        st.session_state.messages = []
        st.session_state.history = []
        st.session_state.active_chat = None
        st.rerun()

    # Show past chats
    if st.session_state.history:
        st.markdown("### 📜 Past Chats")
        for i, chat in enumerate(st.session_state.history):
            label = chat["title"]
            if st.button(label, key=f"chat_{i}", use_container_width=True):
                st.session_state.messages = chat["messages"].copy()
                st.session_state.active_chat = i
                st.rerun()

# ---------------------------
# Display Current Chat
# ---------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------------------------
# Streaming Function
# ---------------------------
async def stream_response(input_text: str, container):
    try:
        response = main.run_query(input_text)  # sync function
        chunks = response.split(" ")
        streamed_response = ""
        for chunk in chunks:
            streamed_response += chunk + " "
            container.markdown(streamed_response)
            await asyncio.sleep(0.03)  # typing effect
        return streamed_response.strip()
    except Exception as e:
        container.markdown(f"❌ Error: {str(e)}")
        return None

# ---------------------------
# Chat Input
# ---------------------------
if prompt := st.chat_input("Ask me about crypto..."):
    # Save user input
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate assistant response
    with st.chat_message("assistant"):
        placeholder = st.empty()
        response = asyncio.run(stream_response(prompt, placeholder))
        if response:
            st.session_state.messages.append({"role": "assistant", "content": response})
