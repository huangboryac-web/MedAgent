import { useEffect, useState, type FC } from "react";
import { Link, useParams, useNavigate, useLocation } from "react-router-dom";
import { ThemeToggle } from "./ThemeToggle";
import { api } from "../services/api";
import {
  LuMessageSquare,
  LuPlus,
  LuSettings,
  LuActivity,
  LuX,
  LuLoader,
  LuTrash2,
} from "react-icons/lu";
import type { Session } from "../types";
import { CHAT_SESSION_UPDATE_EVENT } from "../constants";

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ChatSidebar: FC<SidebarProps> = ({ isOpen, onClose }) => {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();

  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);

  const [deleteTarget, setDeleteTarget] = useState<string | null>(null);

  const fetchSessions = async (isBackground = false) => {
    if (!isBackground) setLoading(true);
    try {
      const data = await api.getSessions();
      setSessions(data);
    } catch (err) {
      console.error("Failed to load sessions", err);
    } finally {
      if (!isBackground) setLoading(false);
    }
  };

  useEffect(() => {
    fetchSessions();
  }, [location.pathname]);

  useEffect(() => {
    const handleUpdate = () => fetchSessions(true);
    window.addEventListener(CHAT_SESSION_UPDATE_EVENT, handleUpdate);
    return () =>
      window.removeEventListener(CHAT_SESSION_UPDATE_EVENT, handleUpdate);
  }, []);

  const handleNewChat = async () => {
    setCreating(true);
    try {
      const newId = await api.createSession();
      navigate(`/chat/${newId}`);
      if (window.innerWidth < 768) onClose();
    } catch (err) {
      console.error("Failed to create new chat", err);
    } finally {
      setCreating(false);
    }
  };

  const handleDeleteSession = async () => {
    if (!deleteTarget) return;

    try {
      await api.deleteSession(deleteTarget);
      if (sessionId === deleteTarget) {
        navigate("/");
      }
      fetchSessions(true);
    } catch (err) {
      console.error("Failed to delete session", err);
    } finally {
      setDeleteTarget(null);
    }
  };

  return (
    <>
      <div
        className={`fixed inset-0 z-20 bg-black/60 backdrop-blur-sm transition-opacity md:hidden ${
          isOpen ? "opacity-100 visible" : "opacity-0 invisible"
        }`}
        onClick={onClose}
      />

      <div
        className={`
          fixed inset-y-0 left-0 z-30 flex flex-col bg-slate-950 border-r border-slate-800 text-slate-300 transition-all duration-300 ease-in-out
          md:relative md:translate-x-0 
          ${
            isOpen
              ? "translate-x-0 w-72"
              : "-translate-x-full w-72 md:w-0 md:-translate-x-0"
          }
          ${isOpen ? "p-4" : "p-0 overflow-hidden"}
        `}
      >
        <div className="mb-2 flex justify-end md:hidden">
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-white transition"
          >
            <LuX size={24} />
          </button>
        </div>

        <div
          className={`flex flex-col h-full ${
            isOpen ? "opacity-100" : "opacity-0 md:opacity-0"
          } transition-opacity duration-300`}
        >
          <Link
            to="/"
            className="mb-8 flex items-center gap-3 px-2 text-xl font-bold text-white hover:opacity-90 transition-opacity"
          >
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-teal-500 to-blue-600 shadow-lg shadow-blue-500/20">
              <LuActivity size={24} className="text-white" />
            </div>
            MedAgent
          </Link>

          <button
            onClick={handleNewChat}
            disabled={creating}
            className="group mb-6 flex w-full items-center gap-3 rounded-lg bg-blue-600 px-4 py-3.5 text-sm font-semibold text-white shadow-md shadow-blue-900/20 transition-all hover:bg-blue-500 hover:shadow-lg active:scale-[0.98] disabled:opacity-70 disabled:cursor-wait"
          >
            {creating ? (
              <LuLoader size={20} className="animate-spin" />
            ) : (
              <LuPlus
                size={20}
                className="transition-transform group-hover:rotate-90"
              />
            )}
            New Consultation
          </button>

          <div className="flex-1 overflow-y-auto px-1 custom-scrollbar">
            <div className="mb-2 px-2 text-xs font-bold uppercase tracking-wider text-slate-500">
              Recent Sessions
            </div>

            {loading && sessions.length === 0 ? (
              <div className="flex justify-center py-4">
                <LuLoader className="animate-spin text-slate-600" />
              </div>
            ) : (
              <div className="space-y-1">
                {sessionId &&
                  !sessions.find((s) => s.session_id === sessionId) && (
                    <Link
                      to={`/chat/${sessionId}`}
                      className="flex w-full items-center gap-3 rounded-lg px-3 py-3 text-sm bg-slate-800 text-white border border-slate-700 shadow-sm transition-colors"
                    >
                      <LuMessageSquare
                        size={16}
                        className="text-blue-400 shrink-0"
                      />
                      <div className="flex flex-col overflow-hidden text-left">
                        <span className="truncate font-medium">
                          New Consultation
                        </span>
                        <span className="truncate text-[10px] text-slate-500 font-mono">
                          {sessionId.slice(0, 8)}...
                        </span>
                      </div>
                      <div className="ml-auto h-1.5 w-1.5 rounded-full bg-green-500 animate-pulse shadow-[0_0_8px_rgba(34,197,94,0.6)]"></div>
                    </Link>
                  )}

                {sessions.length > 0
                  ? sessions.map((session) => {
                      const isActive = session.session_id === sessionId;
                      return (
                        <Link
                          key={session.session_id}
                          to={`/chat/${session.session_id}`}
                          onClick={() => window.innerWidth < 768 && onClose()}
                          className={`flex w-full justify-between rounded-lg px-3 py-3 text-sm transition-colors ${
                            isActive
                              ? "bg-slate-800 text-white border border-slate-700 shadow-sm"
                              : "text-slate-400 hover:bg-slate-900 hover:text-slate-200"
                          }`}
                        >
                          <div className="flex  items-center gap-3">
                            <LuMessageSquare
                              size={16}
                              className={
                                isActive ? "text-blue-400" : "text-slate-600"
                              }
                            />
                            <div className="flex flex-col overflow-hidden text-left">
                              <span className="truncate font-medium">
                                {isActive
                                  ? "Current Session"
                                  : `Session ${session.session_id.slice(0, 4)}`}
                              </span>
                              <span className="truncate text-[10px] text-slate-600 font-mono">
                                {session.session_id.slice(0, 8)}
                              </span>
                            </div>
                          </div>
                          <button
                            onClick={(e) => {
                              e.preventDefault();
                              e.stopPropagation();
                              setDeleteTarget(session.session_id);
                            }}
                            className="p-1.5 hover:bg-red-900/30 hover:text-red-400 rounded-md transition-all"
                            title="Delete Session"
                          >
                            <LuTrash2 size={14} />
                          </button>
                        </Link>
                      );
                    })
                  : (!sessionId ||
                      sessions.find((s) => s.session_id === sessionId)) && (
                      <div className="px-2 py-4 text-center text-sm text-slate-600 border border-dashed border-slate-800 rounded-lg">
                        No past sessions
                      </div>
                    )}
              </div>
            )}
          </div>

          <div className="border-t border-slate-800 pt-4 space-y-3">
            <p className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-slate-400">
              <LuSettings size={18} />
              Settings
            </p>
            <ThemeToggle />
          </div>
        </div>
      </div>
      {deleteTarget && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
          <div
            className="absolute inset-0 bg-black/80 backdrop-blur-sm"
            onClick={() => setDeleteTarget(null)}
          />

          <div className="relative w-full max-w-sm overflow-hidden rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-2xl">
            <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-red-500/10 text-red-500">
              <LuTrash2 size={24} />
            </div>

            <h3 className="mb-2 text-lg font-bold text-white">
              Delete Consultation?
            </h3>
            <p className="mb-6 text-sm text-slate-400">
              This action cannot be undone. All messages in this session will be
              permanently removed.
            </p>

            <div className="flex gap-3">
              <button
                onClick={() => setDeleteTarget(null)}
                className="flex-1 rounded-lg bg-slate-800 px-4 py-2 text-sm font-semibold text-slate-300 transition hover:bg-slate-700"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteSession}
                className="flex-1 rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-red-500"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
