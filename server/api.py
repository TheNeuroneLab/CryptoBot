
import os, sys, uuid, datetime
from typing import List, Optional, Literal, Dict
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load env & ensure we can import main.run_query
load_dotenv()
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import main  # contains run_query()

# ---------- Data Models ----------
class Message(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str
    ts: Optional[str] = None

class Chat(BaseModel):
    chat_id: str
    title: str
    created_at: str
    updated_at: str
    messages: List[Message] = []

class ChatRequest(BaseModel):
    message: str
    chat_id: Optional[str] = None
    # Optionally the client can send full messages history; we’ll prefer store
    messages: Optional[List[Message]] = None

class ChatResponse(BaseModel):
    chat_id: str
    reply: str

# ---------- In-memory Store ----------
class ChatStore:
    def __init__(self):
        self.chats: Dict[str, Chat] = {}

    def new_chat(self, title: str = "New Chat") -> Chat:
        chat_id = uuid.uuid4().hex
        now = datetime.datetime.utcnow().isoformat()
        chat = Chat(
            chat_id=chat_id,
            title=title,
            created_at=now,
            updated_at=now,
            messages=[],
        )
        self.chats[chat_id] = chat
        return chat

    def get(self, chat_id: str) -> Chat:
        chat = self.chats.get(chat_id)
        if not chat:
            raise KeyError("chat not found")
        return chat

    def add_message(self, chat_id: str, role: Literal["user","assistant","system"], content: str) -> Chat:
        chat = self.get(chat_id)
        ts = datetime.datetime.utcnow().isoformat()
        chat.messages.append(Message(role=role, content=content, ts=ts))
        chat.updated_at = ts
        # Set title from first user message
        if role == "user" and len(chat.messages) == 1:
            preview = content.strip().replace("\n", " ")
            chat.title = (preview[:30] + "…") if len(preview) > 30 else preview or "New Chat"
        self.chats[chat_id] = chat
        return chat

    def clear_all(self):
        self.chats.clear()

    def list_meta(self):
        # Return metadata only (no full messages)
        out = []
        for c in self.chats.values():
            out.append({
                "chat_id": c.chat_id,
                "title": c.title,
                "created_at": c.created_at,
                "updated_at": c.updated_at,
                "num_messages": len(c.messages),
            })
        # sort by updated time desc
        out.sort(key=lambda x: x["updated_at"], reverse=True)
        return out

store = ChatStore()

# ---------- FastAPI App ----------
app = FastAPI(title="Biracle API", version="1.0.0")

# CORS cho Vite dev & web client
app.add_middleware(
    CORSMiddleware,
    allow_origins= "http://localhost:5175",
        
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Helpers ----------
def call_llm_with_history(user_text: str, history_msgs: List[Message]) -> str:
    """
    Gọi main.run_query. Nếu main.run_query hỗ trợ 2 tham số (message, messages),
    dùng trực tiếp; nếu không, fallback nhét lịch sử vào prompt.
    """
    as_list = [{"role": m.role, "content": m.content} for m in history_msgs]
    try:
        # Thử signature (message, messages)
        return main.run_query(user_text, as_list)  # type: ignore
    except TypeError:
        # Fallback: inject history vào câu hỏi
        hist = "\n".join(f'{m["role"].capitalize()}: {m["content"]}' for m in as_list[:-1])  # bỏ message cuối nếu là user hiện tại
        composed = f"Conversation history:\n{hist}\n\nUser: {user_text}" if hist else user_text
        return main.run_query(composed)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------- Endpoints ----------
@app.get("/api/health")
def health():
    return {"ok": True, "service": "Biracle API"}

@app.post("/api/new_chat")
def new_chat():
    chat = store.new_chat()
    return {
        "chat_id": chat.chat_id,
        "title": chat.title,
        "created_at": chat.created_at,
        "updated_at": chat.updated_at,
    }

@app.get("/api/history")
def list_history():
    return {"chats": store.list_meta()}

@app.get("/api/history/{chat_id}")
def get_history(chat_id: str):
    try:
        chat = store.get(chat_id)
        return chat
    except KeyError:
        raise HTTPException(status_code=404, detail="chat not found")

@app.post("/api/clear_all")
def clear_all():
    store.clear_all()
    return {"ok": True}

@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    # 1) Lấy/khởi tạo chat
    if req.chat_id:
        try:
            chat = store.get(req.chat_id)
        except KeyError:
            # nếu client gửi chat_id không tồn tại → tạo chat mới
            chat = store.new_chat()
    else:
        chat = store.new_chat()

    # 2) Lưu user message
    store.add_message(chat.chat_id, "user", req.message)

    # 3) Lấy lịch sử để gửi vào model
    history = store.get(chat.chat_id).messages

    # 4) Gọi LLM
    reply = call_llm_with_history(req.message, history)

    # 5) Lưu assistant message
    store.add_message(chat.chat_id, "assistant", reply)

    return ChatResponse(chat_id=chat.chat_id, reply=reply)
