import { useEffect, useRef } from "react";
import "./Composer.scss";

const MAX_HEIGHT = 200;

export default function Composer({ value, disabled, onChange, onSubmit }) {
  const taRef = useRef(null);

  const autosize = (el) => {
    if (!el) return;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, MAX_HEIGHT) + "px";
  };

  useEffect(() => {
    autosize(taRef.current);
  }, []); // set lần đầu
  useEffect(() => {
    autosize(taRef.current);
  }, [value]); // khi value đổi

  return (
    <form className="composer" onSubmit={onSubmit}>
      <label htmlFor="chat-input" className="sr-only">
        Enter your prompt
      </label>

      <div className="composer__box">
        <textarea
          ref={taRef}
          id="chat-input"
          className="composer__textarea"
          placeholder="Enter your prompt"
          rows={1}
          required
          value={value}
          onInput={(e) => autosize(e.target)}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) onSubmit(e);
          }}
        />

        <button
          type="submit"
          disabled={disabled || !value.trim()}
          className="composer__send"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            height="24px"
            viewBox="0 -960 960 960"
            width="24px"
            fill="#ffffffff"
          >
            <path d="m296-224-56-56 240-240 240 240-56 56-184-183-184 183Zm0-240-56-56 240-240 240 240-56 56-184-183-184 183Z" />
          </svg>
        </button>
      </div>
    </form>
  );
}
