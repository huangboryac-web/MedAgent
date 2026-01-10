import type { FC } from "react";
import { Role, type Message } from "../types";
import { LuBot, LuUser } from "react-icons/lu";

interface Props {
  message: Message;
}

export const ChatMessage: FC<Props> = ({ message }) => {
  const isBot = message.role === Role.ASSISTANT;

  return (
    <div
      className={`group flex w-full ${
        isBot ? "justify-start" : "justify-end"
      } mb-6 animate-in fade-in slide-in-from-bottom-2 duration-300`}
    >
      <div
        className={`flex max-w-[85%] md:max-w-[75%] gap-4 ${
          isBot ? "flex-row" : "flex-row-reverse"
        }`}
      >
        <div
          className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full border shadow-sm ${
            isBot
              ? "bg-teal-50 border-teal-100 text-teal-600 dark:bg-teal-900/30 dark:border-teal-800 dark:text-teal-400"
              : "bg-blue-50 border-blue-100 text-blue-600 dark:bg-blue-900/30 dark:border-blue-800 dark:text-blue-400"
          }`}
        >
          {isBot ? <LuBot size={18} /> : <LuUser size={18} />}
        </div>

        <div
          className={`relative rounded-2xl px-5 py-3.5 shadow-sm text-[15px] leading-7 ${
            isBot
              ? "bg-white border border-gray-100 text-gray-800 dark:bg-gray-800 dark:border-gray-700 dark:text-gray-100 rounded-tl-none"
              : "bg-blue-600 text-white shadow-blue-500/20 rounded-tr-none"
          }`}
        >
          <div className="whitespace-pre-wrap">{message.content}</div>
        </div>
      </div>
    </div>
  );
};
