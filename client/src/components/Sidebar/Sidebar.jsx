import ChatListItem from "./ChatListItem";
import "./Sidebar.scss";
import cryptobot from "/cryptobot.png";
export default function Sidebar({
  history,
  activeId,
  busy,
  onNew,
  onClear,
  onOpen,
}) {
  return (
    <aside className="sidebar">
      <div className="sidebar__head">
        <img src={cryptobot} alt="cryptobot" />
        <div className="sidebar__actions">
          <button className="btn btn--new" onClick={onNew} disabled={busy}>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              height="24px"
              viewBox="0 -960 960 960"
              width="24px"
              fill="#ffffffff"
            >
              <path d="M200-120q-33 0-56.5-23.5T120-200v-560q0-33 23.5-56.5T200-840h357l-80 80H200v560h560v-278l80-80v358q0 33-23.5 56.5T760-120H200Zm280-360ZM360-360v-170l367-367q12-12 27-18t30-6q16 0 30.5 6t26.5 18l56 57q11 12 17 26.5t6 29.5q0 15-5.5 29.5T897-728L530-360H360Zm481-424-56-56 56 56ZM440-440h56l232-232-28-28-29-28-231 231v57Zm260-260-29-28 29 28 28 28-28-28Z" />
            </svg>{" "}
            New chat
          </button>
          <button className="btn btn--clear" onClick={onClear} disabled={busy}>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              height="24px"
              viewBox="0 -960 960 960"
              width="24px"
              fill="#ffffffff"
            >
              <path d="M280-120q-33 0-56.5-23.5T200-200v-520h-40v-80h200v-40h240v40h200v80h-40v520q0 33-23.5 56.5T680-120H280Zm400-600H280v520h400v-520ZM360-280h80v-360h-80v360Zm160 0h80v-360h-80v360ZM280-720v520-520Z" />
            </svg>{" "}
            Clear all
          </button>
        </div>
      </div>

      <div className="sidebar__list">
        {(!history || history.length === 0) && (
          <div className="sidebar__empty">No past chats</div>
        )}
        {history?.map((h) => (
          <ChatListItem
            key={h.chat_id}
            title={h.title || "Untitled"}
            time={h.updated_at}
            active={activeId === h.chat_id}
            onClick={() => onOpen(h.chat_id)}
          />
        ))}
      </div>
    </aside>
  );
}
