import React, { useState, useEffect } from "react";
import {
  LuChevronDown,
  LuChevronRight,
  LuLoader,
  LuCheckCheck,
  LuBrainCircuit,
} from "react-icons/lu";
import { nodeToLabel } from "../constants";

interface Props {
  steps: string[];
  status: "idle" | "thinking" | "done";
}

export const ThinkingIndicator: React.FC<Props> = ({ steps, status }) => {
  const [isOpen, setIsOpen] = useState(true);

  useEffect(() => {
    if (status === "thinking") setIsOpen(true);
    if (status === "done") setIsOpen(false);
  }, [status]);

  if (steps.length === 0 && status !== "thinking") return null;

  return (
    <div className="mb-6 w-full max-w-[85%] md:max-w-[75%] animate-in fade-in slide-in-from-bottom-2">
      <div className="rounded-xl border border-gray-200 bg-white shadow-sm overflow-hidden dark:border-gray-700 dark:bg-gray-800/50">
        <button
          onClick={() => setIsOpen(!isOpen)}
          disabled={steps.length === 0}
          className="flex w-full items-center gap-3 bg-gray-50/50 px-4 py-3 text-sm font-medium text-gray-700 hover:bg-gray-100 dark:bg-gray-800 dark:text-gray-200 dark:hover:bg-gray-700 transition-colors"
        >
          <div className="flex items-center gap-2 text-teal-600 dark:text-teal-400">
            {status === "thinking" ? (
              <LuLoader className="animate-spin" size={18} />
            ) : (
              <LuBrainCircuit size={18} />
            )}
          </div>

          <span className="flex-1 text-left">
            {status === "thinking" ? "Thinking Process..." : "Thought Process"}
          </span>

          {steps.length > 0 && (
            <div className="text-gray-400">
              {isOpen ? (
                <LuChevronDown size={16} />
              ) : (
                <LuChevronRight size={16} />
              )}
            </div>
          )}
        </button>

        {isOpen && (
          <div
            className={`border-t border-gray-100 bg-white ${
              steps.length > 0 ? "px-4 py-3" : ""
            } dark:border-gray-700 dark:bg-gray-900/30`}
          >
            <div className="flex flex-col gap-3">
              {steps.map((step, idx) => {
                if (!step) return null;
                const isLast = idx === steps.length - 1;
                const isActive = isLast && status === "thinking";

                return (
                  <div key={idx} className="flex items-center gap-3 text-sm">
                    <div
                      className={`shrink-0 ${
                        isActive ? "text-teal-500" : "text-gray-400"
                      }`}
                    >
                      {isActive ? (
                        <LuLoader className="animate-spin" size={14} />
                      ) : (
                        <LuCheckCheck size={14} />
                      )}
                    </div>
                    <span
                      className={`${
                        isActive
                          ? "text-gray-800 font-medium dark:text-gray-200"
                          : "text-gray-500 dark:text-gray-400"
                      }`}
                    >
                      {nodeToLabel[step] || step}
                    </span>
                  </div>
                );
              })}

              {status === "done" && (
                <div className="flex items-center gap-3 text-sm">
                  <LuCheckCheck size={14} className="text-green-500" />
                  <span className="text-gray-500 dark:text-gray-400">
                    Response Ready
                  </span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
