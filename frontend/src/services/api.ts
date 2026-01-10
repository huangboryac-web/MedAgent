import { API_BASE_URL } from "../constants";
import type { Message, ChatResponse, Session } from "../types";

export const api = {
  createSession: async (): Promise<string> => {
    const res = await fetch(`${API_BASE_URL}/session`);
    if (!res.ok) throw new Error("Failed to create session");
    const data = await res.json();
    return data.session_id;
  },

  getSessions: async (): Promise<Session[]> => {
    const res = await fetch(`${API_BASE_URL}/sessions`);
    if (!res.ok) throw new Error("Failed to fetch sessions");
    return res.json();
  },

  getHistory: async (sessionId: string): Promise<Message[]> => {
    const res = await fetch(`${API_BASE_URL}/history/${sessionId}`);
    if (!res.ok) throw new Error("Failed to fetch history");
    return res.json();
  },

  sendMessage: async (
    query: string,
    sessionId: string
  ): Promise<ChatResponse> => {
    const res = await fetch(`${API_BASE_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, session_id: sessionId }),
    });
    if (!res.ok) throw new Error("Failed to send message");
    return res.json();
  },
};
