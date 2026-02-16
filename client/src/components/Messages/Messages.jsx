import "./Messages.scss";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Component, useMemo, useState } from "react";

// Bắt http/https URL có thể là ảnh (đuôi ảnh hoặc có query presigned)
const IMG_URL_RE =
  /\bhttps?:\/\/[^\s)'"<>]+(?:\.(?:png|jpe?g|gif|webp|svg)\b|(?=\?[^)\s'"<>]*$)|(?=$))/gi;
// Bắt URL tương đối có đuôi ảnh (ví dụ: /charts/xxx.png)
const REL_IMG_RE = /(?:^|[\s(])\/[^\s)'"<>]+?\.(?:png|jpe?g|gif|webp|svg)\b/gi;

function extractImageUrls(text = "") {
  const urls = new Set();
  const add = (u) => {
    const cleaned = String(u).trim().replace(/^[\s(]+|[)\s,.]+$/g, "");
    if (cleaned) urls.add(cleaned);
  };
  (text.match(IMG_URL_RE) || []).forEach(add);
  (text.match(REL_IMG_RE) || []).forEach((m) => add(m.trim()));
  return Array.from(urls);
}

function ImagePreview({ url }) {
  const [state, setState] = useState("loading");
  return (
    <figure className={`msg-img ${state}`}>
      <img
        src={url}
        alt="preview"
        loading="lazy"
        onLoad={() => setState("ok")}
        onError={() => setState("err")}
        style={{ maxWidth: "100%", borderRadius: 8 }}
      />
      {state === "loading" && (
        <figcaption className="msg-img__cap">Loading image…</figcaption>
      )}
      {state === "err" && (
        <figcaption className="msg-img__cap err">
          Cannot load image:{" "}
          <a href={url} target="_blank" rel="noreferrer">
            {url}
          </a>
        </figcaption>
      )}
    </figure>
  );
}

// --- markdown normalize như cũ ---
const normalizeLLM = (raw = "") => {
  let s = String(raw ?? "");
  s = s.replace(/```(?:\w+)?\s*([\s\S]*?)```/gi, "$1");
  s = s.replace(/\r\n?/g, "\n").trim();

  const lines = s.split("\n");
  const minIndent = lines
    .filter((l) => l.trim().length)
    .reduce((min, l) => {
      const n = (l.match(/^[\t ]*/)?.[0] ?? "").replace(/\t/g, "    ").length;
      return Math.min(min, n);
    }, Infinity);
  if (minIndent !== Infinity && minIndent >= 4) {
    s = lines.map((l) => l.slice(minIndent)).join("\n");
  }
  s = s.replace(/^[ \t]+(?=\|)/gm, "");
  const bullets = s.match(/^\s*[-•]\s*\d{4}-\d{2}-\d{2}[:|]\s*[\d.,]+/gm);
  if (bullets && bullets.length >= 3) {
    const rows = bullets.map((l) => {
      const [d, p] = l.replace(/^\s*[-•]\s*/, "").split(/[:|]/);
      return `| ${d.trim()} | ${p.trim()} |`;
    });
    const table = [
      "| Date | Close (USD) |",
      "|------|--------------|",
      ...rows,
    ].join("\n");
    s = s.replace(bullets.join("\n"), table);
  }
  return s.trim();
};

class MDErrorBoundary extends Component {
  constructor(p) {
    super(p);
    this.state = { hasError: false };
  }
  static getDerivedStateFromError() {
    return { hasError: true };
  }
  render() {
    if (this.state.hasError) return this.props.fallback ?? null;
    return this.props.children;
  }
}

function SafeMarkdown({ text }) {
  const content = useMemo(() => normalizeLLM(text), [text]);
  return (
    <MDErrorBoundary
      fallback={<p className="message__text">{String(text ?? "")}</p>}
    >
      <div className="message__md">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={{
            table: (p) => <table className="md-table" {...p} />,
            thead: (p) => <thead className="md-thead" {...p} />,
            tbody: (p) => <tbody className="md-tbody" {...p} />,
            th: (p) => <th className="md-th" {...p} />,
            td: (p) => <td className="md-td" {...p} />,
            code({ inline, children, ...rest }) {
              return inline ? (
                <code className="md-code-inline" {...rest}>
                  {children}
                </code>
              ) : (
                <pre className="md-pre">
                  <code>{children}</code>
                </pre>
              );
            },
            a: (p) => (
              <a className="md-link" target="_blank" rel="noreferrer" {...p} />
            ),
            hr: (p) => <hr className="md-hr" {...p} />,
          }}
        >
          {content}
        </ReactMarkdown>
      </div>
    </MDErrorBoundary>
  );
}

// --- main component ---
export default function Messages({ messages, loading }) {
  return (
    <div className="messages">
      <div className="messages__list">
        {messages.map((m, i) => {
          const isUser = m.role === "user";
          const imgUrls = extractImageUrls(m.content || "");

          return (
            <div
              key={i}
              className={`message ${
                isUser ? "message--user" : "message--assistant"
              }`}
            >
              <img
                className="message__avatar"
                src={
                  isUser
                    ? "https://dummyimage.com/128x128/9B9B9B/ffffff&text=U"
                    : "https://dummyimage.com/128x128/9B9B9B/ffffff&text=B"
                }
                alt=""
              />
              <div className="message__bubble">
                <SafeMarkdown text={m.content} />
                {imgUrls.length > 0 && (
                  <div className="message__images">
                    {imgUrls.map((u) => (
                      <ImagePreview key={u} url={u} />
                    ))}
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {loading && <div className="messages__typing">Assistant is typing…</div>}
      </div>
    </div>
  );
}
