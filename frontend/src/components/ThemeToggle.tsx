import { useState, useRef, useEffect, type FC } from "react";
import { useTheme } from "../context/ThemeContext";
import { LuSun, LuMoon, LuMonitor, LuChevronDown } from "react-icons/lu";

export const ThemeToggle: FC = () => {
  const { theme, setTheme } = useTheme();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const icons = {
    light: <LuSun size={16} />,
    dark: <LuMoon size={16} />,
    system: <LuMonitor size={16} />,
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex w-full items-center justify-between rounded-lg border border-gray-700 bg-gray-800/50 px-3 py-2.5 text-sm text-gray-300 transition hover:bg-gray-800 hover:text-white hover:border-gray-600"
      >
        <div className="flex items-center gap-3">
          {icons[theme]}
          <span className="capitalize font-medium">{theme} Mode</span>
        </div>
        <LuChevronDown
          size={14}
          className={`transition-transform duration-200 ${
            isOpen ? "rotate-180" : ""
          }`}
        />
      </button>

      {isOpen && (
        <div className="absolute bottom-full left-0 mb-2 w-full overflow-hidden rounded-lg border border-gray-700 bg-gray-900 shadow-xl animate-in fade-in slide-in-from-bottom-2">
          {(["light", "dark", "system"] as const).map((t) => (
            <button
              key={t}
              onClick={() => {
                setTheme(t);
                setIsOpen(false);
              }}
              className={`flex w-full items-center gap-3 px-3 py-2.5 text-sm transition ${
                theme === t
                  ? "bg-blue-600/10 text-blue-400 font-medium"
                  : "text-gray-400 hover:bg-gray-800 hover:text-gray-200"
              }`}
            >
              {icons[t]}
              <span className="capitalize">{t}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
};
