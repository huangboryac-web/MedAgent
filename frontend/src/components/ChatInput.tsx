import { useState, type FormEvent, type FC } from "react";
import { LuSend, LuPaperclip } from "react-icons/lu";

interface Props {
  onSend: (msg: string) => void;
  disabled: boolean;
}

export const ChatInput: FC<Props> = ({ onSend, disabled }) => {
  const [input, setInput] = useState("");

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSend(input);
      setInput("");
    }
  };

  return (
    <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-t border-gray-200 dark:border-gray-800 p-4 pb-6">
      <form
        onSubmit={handleSubmit}
        className="mx-auto flex max-w-4xl items-center gap-3 rounded-xl border border-gray-200 bg-white p-2 shadow-lg dark:border-gray-700 dark:bg-gray-800 dark:shadow-none focus-within:ring-2 focus-within:ring-blue-500/50 transition-all"
      >
        <button
          type="button"
          disabled={disabled}
          className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition"
        >
          <LuPaperclip size={20} />
        </button>

        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a medical question..."
          disabled={disabled}
          className="flex-1 bg-transparent px-2 py-2 text-gray-900 placeholder-gray-400 focus:outline-none dark:text-white dark:placeholder-gray-500"
        />

        <button
          type="submit"
          disabled={disabled || !input.trim()}
          className={`flex h-10 w-10 items-center justify-center rounded-lg transition-all duration-200 ${
            input.trim() && !disabled
              ? "bg-blue-600 text-white shadow-md hover:bg-blue-700"
              : "bg-gray-100 text-gray-400 dark:bg-gray-700 dark:text-gray-500 cursor-not-allowed"
          }`}
        >
          <LuSend size={18} className={input.trim() ? "ml-0.5" : ""} />
        </button>
      </form>
    </div>
  );
};
