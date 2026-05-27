import React, { useState, useRef, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Send, Bot, User, Loader2, Zap, RefreshCw } from 'lucide-react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

const SUGGESTED_PROMPTS = [
  'Track my order #101',
  'My package arrived damaged — help!',
  'How long do refunds take?',
  'Create a support ticket for a missing order',
];

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';
const SESSION_ID = `session-${Math.random().toString(36).slice(2)}`;

const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  const sendMessage = useCallback(async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || isLoading) return;

    const userMsg: Message = { role: 'user', content: trimmed, timestamp: new Date() };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);
    setError(null);

    try {
      const { data } = await axios.post(`${API_URL}/chat`, {
        message: trimmed,
        session_id: SESSION_ID,
      });

      const assistantMsg: Message = {
        role: 'assistant',
        content: data.response ?? 'No response received.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: unknown) {
      const msg =
        axios.isAxiosError(err) && err.response?.data?.detail
          ? err.response.data.detail
          : 'Failed to reach the support agent. Please try again.';
      setError(msg);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  }, [isLoading]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  };

  const clearChat = () => {
    setMessages([]);
    setError(null);
  };

  return (
    <div className="flex flex-col h-screen bg-zinc-950 text-zinc-100 font-sans">
      {/* Header */}
      <header className="flex-shrink-0 border-b border-zinc-800 px-6 py-4">
        <div className="max-w-3xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-900/40">
              <Bot size={22} />
            </div>
            <div>
              <h1 className="text-lg font-semibold tracking-tight">AI Support Agent</h1>
              <div className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                <span className="text-xs text-zinc-400">Online · Production Ready</span>
              </div>
            </div>
          </div>
          <button
            onClick={clearChat}
            className="flex items-center gap-1.5 text-xs text-zinc-500 hover:text-zinc-300 transition-colors px-3 py-1.5 rounded-lg hover:bg-zinc-800"
          >
            <RefreshCw size={13} />
            New chat
          </button>
        </div>
      </header>

      {/* Messages */}
      <main className="flex-1 overflow-y-auto" ref={scrollRef}>
        <div className="max-w-3xl mx-auto px-6 py-6 space-y-5">

          {/* Empty state */}
          {messages.length === 0 && (
            <div className="text-center py-16">
              <div className="w-16 h-16 bg-blue-600/10 border border-blue-600/20 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Zap size={28} className="text-blue-400" />
              </div>
              <h2 className="text-xl font-semibold mb-2">How can I help you today?</h2>
              <p className="text-zinc-500 text-sm mb-8">
                I can look up orders, answer FAQs, and create support tickets.
              </p>
              <div className="grid grid-cols-2 gap-3">
                {SUGGESTED_PROMPTS.map((prompt) => (
                  <button
                    key={prompt}
                    onClick={() => sendMessage(prompt)}
                    className="text-left text-sm bg-zinc-900 border border-zinc-800 hover:border-zinc-600 rounded-xl px-4 py-3 transition-colors"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Message list */}
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
            >
              {/* Avatar */}
              <div
                className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5 ${
                  msg.role === 'user' ? 'bg-zinc-700' : 'bg-blue-600'
                }`}
              >
                {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}
              </div>

              {/* Bubble */}
              <div
                className={`max-w-[78%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                  msg.role === 'user'
                    ? 'bg-blue-600 text-white rounded-tr-sm'
                    : 'bg-zinc-900 border border-zinc-800 text-zinc-100 rounded-tl-sm'
                }`}
              >
                <p className="whitespace-pre-wrap">{msg.content}</p>
                <p
                  className={`text-[10px] mt-1.5 ${
                    msg.role === 'user' ? 'text-blue-200' : 'text-zinc-600'
                  }`}
                >
                  {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </p>
              </div>
            </div>
          ))}

          {/* Typing indicator */}
          {isLoading && (
            <div className="flex gap-3">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center flex-shrink-0">
                <Bot size={16} />
              </div>
              <div className="bg-zinc-900 border border-zinc-800 rounded-2xl rounded-tl-sm px-4 py-3">
                <Loader2 size={16} className="animate-spin text-blue-400" />
              </div>
            </div>
          )}

          {/* Error banner */}
          {error && (
            <div className="bg-red-900/30 border border-red-700/50 text-red-300 text-sm px-4 py-3 rounded-xl">
              {error}
            </div>
          )}
        </div>
      </main>

      {/* Input area */}
      <footer className="flex-shrink-0 border-t border-zinc-800 px-6 py-4">
        <div className="max-w-3xl mx-auto">
          <div className="flex gap-3 items-center">
            <input
              ref={inputRef}
              type="text"
              className="flex-1 bg-zinc-900 border border-zinc-800 focus:border-blue-600 rounded-xl py-3 px-4 text-sm placeholder-zinc-600 focus:outline-none transition-colors"
              placeholder="Type your message… (Enter to send)"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isLoading}
              autoFocus
            />
            <button
              onClick={() => sendMessage(input)}
              disabled={isLoading || !input.trim()}
              className="w-11 h-11 bg-blue-600 hover:bg-blue-500 disabled:bg-zinc-800 disabled:text-zinc-600 rounded-xl flex items-center justify-center transition-colors flex-shrink-0"
              aria-label="Send message"
            >
              <Send size={18} />
            </button>
          </div>
          <p className="text-center text-[11px] text-zinc-700 mt-3">
            AI can make mistakes. Verify critical information independently.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default ChatPage;
