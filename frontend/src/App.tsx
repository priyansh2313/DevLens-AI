import { useEffect, useState } from "react";

type Source = {
  file: string;
  similarity: number;
};

type Message = {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
};

type BackendStatus = "checking" | "online" | "offline";

const API_BASE_URL = "http://localhost:8000";
const QUICK_PROMPTS = [
  "How does routing work?",
  "Where is auth configured?",
  "Explain dependency injection",
  "Show request lifecycle",
];

function App() {
  const [repoUrl, setRepoUrl] = useState("");
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [backendStatus, setBackendStatus] = useState<BackendStatus>("checking");

  useEffect(() => {
    let isMounted = true;

    const probeBackend = async () => {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 2500);

      try {
        const res = await fetch(`${API_BASE_URL}/health`, {
          signal: controller.signal,
          cache: "no-store",
        });
        if (!isMounted) return;
        setBackendStatus(res.ok ? "online" : "offline");
      } catch {
        if (!isMounted) return;
        setBackendStatus("offline");
      } finally {
        clearTimeout(timeoutId);
      }
    };

    probeBackend();
    const intervalId = setInterval(probeBackend, 15000);

    return () => {
      isMounted = false;
      clearInterval(intervalId);
    };
  }, []);

  const statusLabel: Record<BackendStatus, string> = {
    checking: "Health Check Running",
    online: "Backend Connected",
    offline: "Backend Unreachable",
  };

  const handleSend = async () => {
    const cleanQuery = query.trim();
    const cleanRepoUrl = repoUrl.trim();
    if (!cleanQuery || !cleanRepoUrl || loading) return;

    const userMessage: Message = { role: "user", content: cleanQuery };
    setMessages((prev) => [...prev, userMessage]);

    setLoading(true);

    try {
      const res = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          repo_url: cleanRepoUrl,
          query: cleanQuery,
        }),
      });

      if (!res.ok) {
        throw new Error(`Request failed with status ${res.status}`);
      }

      const data = await res.json();

      const botMessage: Message = {
        role: "assistant",
        content: data.answer ?? "No response from assistant.",
        sources: Array.isArray(data.sources) ? data.sources : [],
      };

      setBackendStatus("online");

      setMessages((prev) => [...prev, botMessage]);
      setQuery("");
    } catch (err) {
      console.error("Chat request failed", err);
      setBackendStatus("offline");
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "I could not reach the backend. Please confirm the API is running on http://localhost:8000.",
          sources: [],
        },
      ]);
    }

    setLoading(false);
  };

  const handleKeyDown: React.KeyboardEventHandler<HTMLInputElement> = (e) => {
    if (e.key === "Enter") {
      handleSend();
    }
  };

  const applyPrompt = (prompt: string) => {
    setQuery(prompt);
  };

  return (
    <div className="site-shell">
      <div className="bg-orb orb-a" />
      <div className="bg-orb orb-b" />
      <div className="bg-orb orb-c" />

      <main className="workspace">
        <header className="masthead reveal reveal-1">
          <div>
            <p className="eyebrow">Repository Intelligence Studio</p>
            <h1>DevLens AI</h1>
            <p className="masthead-copy">
              Premium AI workspace for source-grounded developer conversations.
            </p>
          </div>
          <div className={`status-pill ${backendStatus}`}>
            <span className="status-dot" />
            {statusLabel[backendStatus]}
          </div>
        </header>

        <div className="layout-grid">
          <aside className="control-rail reveal reveal-2">
            <section className="panel repo-panel">
              <label className="field-label" htmlFor="repo-url">
                Repository URL
              </label>
              <input
                id="repo-url"
                className="field-input"
                placeholder="https://github.com/owner/repository"
                value={repoUrl}
                onChange={(e) => setRepoUrl(e.target.value)}
              />
              <p className="field-hint">Point DevLens to the repository you already ingested.</p>
            </section>

            <section className="panel prompt-panel">
              <p className="panel-title">Quick Prompts</p>
              <div className="prompt-grid">
                {QUICK_PROMPTS.map((prompt) => (
                  <button
                    key={prompt}
                    className="prompt-chip"
                    onClick={() => applyPrompt(prompt)}
                    type="button"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </section>

            <section className="panel telemetry-panel">
              <p className="panel-title">Session Telemetry</p>
              <div className="metric-row">
                <span>Messages</span>
                <strong>{messages.length}</strong>
              </div>
              <div className="metric-row">
                <span>Assistant Replies</span>
                <strong>{messages.filter((m) => m.role === "assistant").length}</strong>
              </div>
              <div className="metric-row">
                <span>Connection</span>
                <strong>{backendStatus === "online" ? "Stable" : "Check API"}</strong>
              </div>
            </section>
          </aside>

          <section className="conversation-stage reveal reveal-3">
            <div className="stage-header">
              <h2>Ask questions about the codebase</h2>
              <p>Responses are generated from your indexed chunks and ranked by relevance.</p>
            </div>

            <div className="message-feed">
              {messages.length === 0 && (
                <div className="empty-state">
                  <p className="empty-title">Ready when you are.</p>
                  <p className="empty-subtitle">
                    Add repository URL, choose a quick prompt, and start exploring your code.
                  </p>
                </div>
              )}

              {messages.map((msg, i) => (
                <article
                  key={`${msg.role}-${i}`}
                  className={`message-row ${msg.role === "user" ? "is-user" : "is-assistant"}`}
                >
                  <div className="message-meta">{msg.role === "user" ? "You" : "DevLens"}</div>
                  <div className="message-bubble">{msg.content}</div>

                  {msg.sources && msg.sources.length > 0 && (
                    <div className="source-list">
                      {msg.sources.map((s, idx) => (
                        <div key={`${s.file}-${idx}`} className="source-chip">
                          <span className="source-file">{s.file}</span>
                          <span className="source-score">{s.similarity.toFixed(2)}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </article>
              ))}

              {loading && (
                <div className="loading-row" aria-label="Assistant is thinking">
                  <span className="loading-dot" />
                  <span className="loading-dot" />
                  <span className="loading-dot" />
                </div>
              )}
            </div>

            <div className="composer-row">
              <input
                className="composer-input"
                placeholder="Ask about architecture, dependencies, patterns, or execution flow"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={handleKeyDown}
              />
              <button onClick={handleSend} className="send-btn" disabled={loading}>
                {loading ? "Thinking" : "Send"}
              </button>
            </div>
          </section>
        </div>
      </main>

      <footer className="site-footer">Designed for high-context engineering teams.</footer>
    </div>
  );
}

export default App;