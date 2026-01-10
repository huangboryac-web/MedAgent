import React, { useRef, useEffect, useState } from "react";
import { useParams, Navigate } from "react-router-dom";
import { ChatSidebar } from "../components/Sidebar";
import { ChatMessage } from "../components/ChatMessage";
import { ChatInput } from "../components/ChatInput";
import { useChat } from "../hooks/useChat";
import { LuMenu } from "react-icons/lu";

export const ChatPage: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const { messages, isLoading, sendMessage, error } = useChat(sessionId);
  const scrollRef = useRef<HTMLDivElement>(null);

  const [isSidebarOpen, setIsSidebarOpen] = useState(
    () => window.innerWidth >= 768
  );

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, isLoading]);

  if (!sessionId) return <Navigate to="/" />;

  return (
    <div className="flex h-screen bg-gray-50 font-sans dark:bg-gray-950 transition-colors duration-200">
      <ChatSidebar
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
      />

      <div className="flex flex-1 flex-col relative min-w-0 transition-all duration-300">
        <header className="sticky top-0 z-10 flex h-16 items-center justify-between border-b border-gray-200 bg-white/80 px-4 backdrop-blur-md dark:border-gray-800 dark:bg-gray-900/80">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="rounded-lg p-2 text-gray-500 hover:bg-gray-100 hover:text-gray-700 dark:text-gray-400 dark:hover:bg-gray-800 dark:hover:text-gray-200"
            >
              <LuMenu size={24} />
            </button>

            <div className="flex flex-col">
              <h1 className="text-base font-semibold text-gray-800 dark:text-white">
                Medical Assistant
              </h1>
              <span className="text-[10px] font-medium uppercase tracking-wider text-green-600 dark:text-green-400">
                Online
              </span>
            </div>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto scroll-smooth">
          <div className="mx-auto max-w-3xl px-4 py-6 sm:px-6">
            {error && (
              <div className="mb-6 rounded-lg border border-red-200 bg-red-50 p-4 text-center text-sm text-red-600 dark:border-red-900/50 dark:bg-red-900/20 dark:text-red-400">
                {error}
              </div>
            )}

            {messages.length === 0 && !isLoading && (
              <div className="flex flex-col items-center justify-center mt-20 text-center">
                <div className="mb-4 rounded-full bg-blue-100 p-4 dark:bg-blue-900/30">
                  <span className="text-3xl">👋</span>
                </div>
                <h2 className="text-xl font-semibold text-gray-800 dark:text-white">
                  Hello, User
                </h2>
                <p className="mt-2 max-w-sm text-sm text-gray-500 dark:text-gray-400">
                  I can assist with guidelines, protocols, and medical queries.
                  How can I help today?
                </p>
              </div>
            )}

            {messages.map((msg, index) => (
              <ChatMessage key={index} message={msg} />
            ))}

            {isLoading && (
              <div className="flex justify-start mb-6 animate-pulse">
                <div className="flex items-center gap-2 rounded-2xl rounded-tl-none bg-gray-100 px-4 py-3 text-sm text-gray-500 dark:bg-gray-800 dark:text-gray-400">
                  <div className="h-2 w-2 rounded-full bg-gray-400 animate-bounce"></div>
                  <div className="h-2 w-2 rounded-full bg-gray-400 animate-bounce delay-75"></div>
                  <div className="h-2 w-2 rounded-full bg-gray-400 animate-bounce delay-150"></div>
                </div>
              </div>
            )}
            <div ref={scrollRef} />
          </div>
        </main>

        <ChatInput onSend={sendMessage} disabled={isLoading} />
      </div>
    </div>
  );
};
