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
    model="openai/gpt-oss-120b",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.5,
    max_tokens=1024,
)