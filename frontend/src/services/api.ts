import { API_BASE_URL } from "../constants";
import type { Message, ChatResponse, Session, StreamEvent } from "../types";

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
    sessionId: string,
    onChunk: (event: StreamEvent) => void // New callback parameter
  ): Promise<void> => {
    const res = await fetch(`${API_BASE_URL}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "text/event-stream",
      },
      body: JSON.stringify({ query, session_id: sessionId }),
    });

    if (!res.ok) throw new Error("Failed to send message");
    if (!res.body) throw new Error("ReadableStream not supported");

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      // Decode current chunk and append to buffer
      buffer += decoder.decode(value, { stream: true });

      // Split by double newline (SSE standard delimiter)
      const parts = buffer.split("\n\n");

      // Keep the last part in buffer (it might be incomplete)
      buffer = parts.pop() || "";

      for (const part of parts) {
        if (part.startsWith("data: ")) {
          const jsonStr = part.replace("data: ", "").trim();
          if (jsonStr) {
            try {
              const event: StreamEvent = JSON.parse(jsonStr);
              onChunk(event);
            } catch (e) {
              console.error("Failed to parse SSE JSON", e);
            }
          }
        }
      }
    }
  },

  deleteSession: async (
    sessionId: string
  ): Promise<{ status: string; message: string }> => {
    const res = await fetch(`${API_BASE_URL}/session/${sessionId}`, {
      method: "DELETE",
    });
    if (!res.ok) throw new Error("Failed to delete session");
    return res.json();
  },
};
