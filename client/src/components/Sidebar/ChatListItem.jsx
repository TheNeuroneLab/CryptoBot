export default function ChatListItem({ title, time, active, onClick }) {
  return (
    <button className={`chat-item ${active ? "is-active" : ""}`} onClick={onClick} title={title}>
      <div className="chat-item__title">{title}</div>
      <div className="chat-item__time">{new Date(time).toLocaleString()}</div>
    </button>
  );
}
