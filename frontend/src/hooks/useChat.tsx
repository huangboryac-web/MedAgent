import { useState, useCallback, useEffect } from "react";
import type { Message } from "../types";
import { api } from "../services/api";

export const useChat = (sessionId?: string) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const [thinkingSteps, setThinkingSteps] = useState<string[]>([]);
  const [isThinking, setIsThinking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isHistoryLoading, setIsHistoryLoading] = useState(false);

  useEffect(() => {
    if (!sessionId) return;

    const fetchHistory = async () => {
      setIsHistoryLoading(true);
      setError(null);
      setThinkingSteps([]);
      setIsThinking(false);

      try {
        const history = await api.getHistory(sessionId);
        setMessages(history);
      } catch (err) {
        console.error("Failed to load history:", err);
        setError("Failed to load chat history.");
      } finally {
        setIsHistoryLoading(false);
      }
    };

    fetchHistory();
  }, [sessionId]);

  const sendMessage = useCallback(
    async (query: string) => {
      if (!sessionId) return;

      const userMsg: Message = { role: "user", content: query };
      setMessages((prev) => [...prev, userMsg]);

      setIsLoading(true);
      setIsThinking(true);
      setThinkingSteps([]);
      setError(null);

      try {
        await api.sendMessage(query, sessionId, (event) => {
          if (event.type === "step") {
            setThinkingSteps((prev) => {
              if (prev[prev.length - 1] === event.node) return prev;
              return [...prev, event.node];
            });
          } else if (event.type === "answer") {
            setMessages((prev) => [
              ...prev,
              { role: "assistant", content: event.content },
            ]);
          } else if (event.type === "error") {
            throw new Error(event.content);
          }
        });
      } catch (err) {
        setError(err instanceof Error ? err.message : "An error occurred");
      } finally {
        setIsLoading(false);
        setIsThinking(false);
      }
    },
    [sessionId]
  );

  return {
    messages,
    isLoading: isLoading || isHistoryLoading,
    isThinking,
    thinkingSteps,
    sendMessage,
    error,
  };
};
