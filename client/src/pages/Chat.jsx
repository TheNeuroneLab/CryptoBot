import { useEffect, useRef, useState } from "react";
import Sidebar from "../components/Sidebar/Sidebar";
// import Messages from "../components/Messages/Messages";
// import Composer from "../components/Composer/Composer";
import "./Chat.scss";
import Messages from "../components/Messages/Messages";
import Composer from "../components/Composer/Composer";

export default function ChatPage() {
  const [chatId, setChatId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [input, setInput] = useState("BTC price from July 1 to July 20 2024");
  const listRef = useRef(null);
  const didInit = useRef(false);

  useEffect(() => {
    if (didInit.current) return;   // remove twice mounts
    didInit.current = true;
    newChat();
  }, []);

  useEffect(() => {
    listRef.current?.lastElementChild?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function newChat() {
    setBusy(true);
    setError("");
    try {
      const res = await fetch("/api/new_chat", { method: "POST" });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setChatId(data.chat_id);
      setMessages([]);
      await refreshHistory();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  async function refreshHistory() {
    try {
      const res = await fetch("/api/history");
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setHistory(data.chats ?? []);
    } catch (e) {
      console.error(e);
    }
  }

  async function loadChat(id) {
    setBusy(true);
    setError("");
    try {
      const res = await fetch(`/api/history/${id}`);
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setChatId(data.chat_id);
      setMessages(data.messages || []);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  async function clearAll() {
    setBusy(true);
    setError("");
    try {
      const res = await fetch("/api/clear_all", { method: "POST" });
      if (!res.ok) throw new Error(await res.text());
      setHistory([]);
      await newChat();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  async function send(e) {
    e?.preventDefault?.();
    const text = input.trim();
    if (!text || loading || !chatId) return;

    setLoading(true);
    setError("");
    const optimistic = [
      ...messages,
      { role: "user", content: text, ts: new Date().toISOString() },
    ];
    setMessages(optimistic);
    setInput("");

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ chat_id: chatId, message: text }),
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      if (data.chat_id && data.chat_id !== chatId) setChatId(data.chat_id);

      setMessages([
        ...optimistic,
        {
          role: "assistant",
          content: data.reply ?? "",
          ts: new Date().toISOString(),
        },
      ]);
      refreshHistory();
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="chat">
      <Sidebar
        history={history}
        activeId={chatId}
        busy={busy}
        onNew={newChat}
        onClear={clearAll}
        onOpen={loadChat}
      />

      <main className="chat__main">
        <header className="chat__head">
          <h1>
            <span className="chat__head-gradient">Biracle </span>
          </h1>
        </header>

        {/* messages list container */}
        <section className="chat__messages">
          <Messages messages={messages} loading={loading} />
        </section>

        {/* input prompt */}
        <footer className="chat__composer">
          <Composer
            value={input}
            disabled={loading}
            onChange={setInput}
            onSubmit={send}
          />
          {error && <div className="chat__error">⚠ {error}</div>}
        </footer>
      </main>
    </div>
  );
}
