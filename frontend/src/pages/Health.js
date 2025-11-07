import React, { useEffect, useState } from "react";
import axios from "../api/fetcher";

const container = { padding: "20px", color: "#e6eef8", fontFamily: "Inter, sans-serif" };

const Health = () => {
  const [status, setStatus] = useState("Checking...");

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await axios.get("/health/");
        setStatus(res?.status || "Healthy");
      } catch (err) {
        console.error(err);
        setStatus("❌ Service unavailable");
      }
    };
    checkHealth();
  }, []);

  return (
    <div style={container}>
      <h2>Health Check</h2>
      <p>Status: {status}</p>
    </div>
  );
};

export default Health;
