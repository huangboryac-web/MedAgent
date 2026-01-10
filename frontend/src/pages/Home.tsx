import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../services/api";
import { LuLoader } from "react-icons/lu";

export const Home: React.FC = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const createAndRedirect = async () => {
      try {
        const id = await api.createSession();
        navigate(`/chat/${id}`, { replace: true });
      } catch (error) {
        console.error("Failed to create session", error);
      }
    };
    createAndRedirect();
  }, [navigate]);
  return (
    <div className="flex h-screen w-full items-center justify-center bg-gray-50 text-gray-600 dark:bg-gray-950 dark:text-gray-400">
      <div className="flex flex-col items-center gap-4">
        <LuLoader className="h-10 w-10 animate-spin text-blue-600" />
        <p className="font-medium animate-pulse">
          Initializing Secure Session...
        </p>
      </div>
    </div>
  );
};
