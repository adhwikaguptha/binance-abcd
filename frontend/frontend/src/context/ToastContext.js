import React, { createContext, useContext, useState } from "react";

const ToastContext = createContext();

export const useToast = () => useContext(ToastContext);

export const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);

  const addToast = (message, type = "info", duration = 3000) => {
    const id = Date.now();
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, duration);
  };

  return (
    <ToastContext.Provider value={{ addToast }}>
      {children}
      <div style={toastContainerStyle}>
        {toasts.map((t) => (
          <div key={t.id} style={{ ...toastStyle, ...toastTypeStyle[t.type] }}>
            {t.message}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
};

// Toast container
const toastContainerStyle = {
  position: "fixed",
  top: "20px",
  right: "20px",
  display: "flex",
  flexDirection: "column",
  gap: "10px",
  zIndex: 9999,
};

// Toast base style
const toastStyle = {
  padding: "10px 20px",
  borderRadius: "6px",
  color: "#fff",
  minWidth: "200px",
  boxShadow: "0 2px 6px rgba(0,0,0,0.2)",
  fontFamily: "Inter, sans-serif",
};

// Colors by type
const toastTypeStyle = {
  success: { background: "#16a34a" },
  error: { background: "#dc2626" },
  info: { background: "#2563eb" },
};
