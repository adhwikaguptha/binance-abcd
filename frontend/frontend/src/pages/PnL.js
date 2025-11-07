import React, { useEffect, useState } from "react";
import { getTodayPnL, getPnLSummary } from "../api/pnl";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const container = { padding: "20px", color: "#e6eef8", fontFamily: "Inter, sans-serif" };
const card = {
  padding: "14px",
  borderRadius: "12px",
  marginBottom: "12px",
  background: "rgba(255,255,255,0.02)",
  border: "1px solid rgba(255,255,255,0.03)",
};

const PnL = () => {
  const [today, setToday] = useState(null);
  const [summary, setSummary] = useState(null);
  const [history, setHistory] = useState([]); // For chart
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPnL = async () => {
      try {
        const t = await getTodayPnL();
        const s = await getPnLSummary();
        setToday(t);
        setSummary(s);

        // Build mock history array if backend does not provide detailed daily data
        // Each item: { date: '2025-10-21', pnl: 1200 }
        const hist = s?.daily || []; 
        setHistory(hist);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchPnL();
  }, []);

  if (loading) return <div style={container}>Loading PnL...</div>;

  return (
    <div style={container}>
      <h2>Profit & Loss</h2>

      <div style={card}>
        <h4>Today</h4>
        <p>Realized: {today?.realized ?? 0}</p>
      </div>
    </div>
  );
};

export default PnL;
