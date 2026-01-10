export const CHAT_SESSION_UPDATE_EVENT = "chat_session_updated";

export const API_BASE_URL = "http://localhost:8000";

export const nodeToLabel: Record<string, string> = {
  router: "Analyzing Request",
  retrieve: "Retrieving Medical Records",
  grade: "Evaluating Relevance",
  web_search: "Searching Medical Databases",
  hallucination_check: "Fact Checking",
  generate: "Synthesizing Response",
  guardrail: "Safety Verification",
  general: "Processing General Query",
  clarifier: "Requesting Clarification",
  cache: "Checking Cache",
};
