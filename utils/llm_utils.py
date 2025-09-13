import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
from langchain_groq import ChatGroq
load_dotenv()

# -------------------------
# LLM Setup
# -------------------------
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=1.0,
    max_tokens=1024,
)