import { useState, useEffect, useCallback } from "react";
import { Role, type Message } from "../types";
import { api } from "../services/api";
import { CHAT_SESSION_UPDATE_EVENT } from "../constants";

export const useChat = (sessionId: string | undefined) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!sessionId) return;

    const loadHistory = async () => {
      setIsLoading(true);
      try {
        const history = await api.getHistory(sessionId);
        setMessages(history);
        setError(null);
      } catch (err) {
        setError("Failed to load chat history");
      } finally {
        setIsLoading(false);
      }
    };
    loadHistory();
  }, [sessionId]);

  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim() || !sessionId) return;

      const userMsg: Message = { role: Role.USER, content };
      setMessages((prev) => [...prev, userMsg]);
      setIsLoading(true);
      setError(null);

      try {
        const data = await api.sendMessage(content, sessionId);
        const botMsg: Message = {
          role: Role.ASSISTANT,
          content: data.response,
        };
        setMessages((prev) => [...prev, botMsg]);

        window.dispatchEvent(new Event(CHAT_SESSION_UPDATE_EVENT));
      } catch (err) {
        setError("Failed to send message");
      } finally {
        setIsLoading(false);
      }
    },
    [sessionId]
  );

  return { messages, isLoading, error, sendMessage };
};
