export interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
}

export interface ChatResponse {
  response: string;
}

export interface ChatState {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
}

export interface Session {
  session_id: string;
  last_active: string;
}

export type Theme = "light" | "dark" | "system";

export type StreamEvent =
  | { type: "step"; node: string }
  | { type: "answer"; content: string }
  | { type: "error"; content: string };

export enum Role {
  USER = "user",
  ASSISTANT = "assistant",
}

export enum Themes {
  LIGHT = "light",
  DARK = "dark",
  SYSTEM = "system",
}
