"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

const BACKEND_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

const SUGGESTIONS = [
  "Why is Devanshu right for this role?",
  "Tell me about the VSCode assistant at Planto.ai",
  "What's his oil spill detection project?",
  "What's his tech stack for RAG?",
  "Check availability and book a call",
  "What would he do differently in his projects?",
];

const INITIAL_MESSAGE: Message = {
  id: "0",
  role: "assistant",
  content: `👋 Hi! I'm Devanshu's AI representative.

I can tell you about his **background, skills, and projects** — all grounded in his actual resume and GitHub repos. I can also **check his calendar and book a meeting** directly.

What would you like to know?`,
  timestamp: new Date(),
};

export default function ChatWidget() {
  const [messages, setMessages] = useState<Message[]>([INITIAL_MESSAGE]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  const sendMessage = useCallback(
    async (text: string) => {
      if (!text.trim() || isLoading) return;

      const userMessage: Message = {
        id: Date.now().toString(),
        role: "user",
        content: text.trim(),
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setInput("");
      setIsLoading(true);

      const assistantId = (Date.now() + 1).toString();
      setMessages((prev) => [
        ...prev,
        { id: assistantId, role: "assistant", content: "", timestamp: new Date() },
      ]);

      try {
        const response = await fetch(`${BACKEND_URL}/rag-query`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query: text.trim(), stream: true }),
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();

        if (!reader) throw new Error("No response body");

        let fullContent = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split("\n").filter((l) => l.startsWith("data: "));

          for (const line of lines) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.token) {
                fullContent += data.token;
                setMessages((prev) =>
                  prev.map((m) =>
                    m.id === assistantId ? { ...m, content: fullContent } : m
                  )
                );
              }
              if (data.done || data.error) break;
            } catch {
              // Skip malformed SSE lines
            }
          }
        }

        // If no content received (backend offline), show fallback
        if (!fullContent) {
          throw new Error("Empty response");
        }
      } catch {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId
              ? {
                  ...m,
                  content:
                    "I'm having trouble connecting to the knowledge base right now. Please try again, or call the phone number to speak with me directly.",
                }
              : m
          )
        );
      } finally {
        setIsLoading(false);
        inputRef.current?.focus();
      }
    },
    [isLoading]
  );

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    // Auto-resize
    e.target.style.height = "auto";
    e.target.style.height = Math.min(e.target.scrollHeight, 120) + "px";
  };

  return (
    <div className="chat-container">
      {/* Header */}
      <div className="chat-header">
        <div className="chat-avatar">D</div>
        <div className="chat-avatar-info">
          <h3>Devanshu&apos;s AI Representative</h3>
          <p>
            <span className="status-dot" />
            Online · RAG-grounded · Real calendar booking
          </p>
        </div>
      </div>

      {/* Messages */}
      <div className="chat-messages" id="chat-messages">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`message ${msg.role === "user" ? "message-user" : ""}`}
          >
            <div
              className={`message-avatar ${
                msg.role === "assistant" ? "message-avatar-ai" : "message-avatar-user"
              }`}
            >
              {msg.role === "assistant" ? "D" : "U"}
            </div>
            <div
              className={`message-bubble ${
                msg.role === "assistant" ? "message-bubble-ai" : "message-bubble-user"
              }`}
            >
              {msg.role === "assistant" && msg.content === "" ? (
                <div className="typing-indicator">
                  <div className="typing-dot" />
                  <div className="typing-dot" />
                  <div className="typing-dot" />
                </div>
              ) : (
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {msg.content}
                </ReactMarkdown>
              )}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Suggestions */}
      {messages.length <= 2 && (
        <div className="chat-suggestions">
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              className="suggestion-chip"
              onClick={() => sendMessage(s)}
              disabled={isLoading}
              id={`suggestion-${s.toLowerCase().replace(/\s+/g, "-").slice(0, 30)}`}
            >
              {s}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <div className="chat-input-area">
        <textarea
          ref={inputRef}
          className="chat-input"
          value={input}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          placeholder="Ask about Devanshu's experience, projects, or book a meeting..."
          disabled={isLoading}
          rows={1}
          id="chat-input"
          aria-label="Chat input"
        />
        <button
          className="chat-send-btn"
          onClick={() => sendMessage(input)}
          disabled={isLoading || !input.trim()}
          id="chat-send-btn"
          aria-label="Send message"
        >
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="m22 2-7 20-4-9-9-4Z" />
            <path d="M22 2 11 13" />
          </svg>
        </button>
      </div>
    </div>
  );
}
