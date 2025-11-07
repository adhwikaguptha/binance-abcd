import React, { useEffect, useState } from "react";
import { getRiskSettings, updateRiskSettings } from "../api/risk";

const container = { padding: "20px", color: "#e6eef8", fontFamily: "Inter, sans-serif" };
const inputStyle = { width: "100%", padding: "8px", borderRadius: "6px", marginBottom: "10px", background: "transparent", color: "#e6eef8", border: "1px solid rgba(255,255,255,0.03)" };
const btnStyle = { padding: "8px 14px", borderRadius: "6px", background: "#2563eb", color: "#fff", border: "none", cursor: "pointer", fontWeight: "600" };

const Risk = () => {
  const [risk, setRisk] = useState({ capital: "", risk_per_trade_pct: "", max_daily_loss_pct: "" });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRisk = async () => {
      try {
        const data = await getRiskSettings();
        setRisk(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchRisk();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await updateRiskSettings(risk);
      alert("Risk settings updated!");
    } catch (err) {
      console.error(err);
      alert("Error updating settings");
    }
  };

  if (loading) return <div style={container}>Loading risk settings...</div>;

  return (
    <div style={container}>
      <h2>Risk Settings</h2>
      <form onSubmit={handleSubmit}>
        <label>Capital</label>
        <input
          type="number"
          style={inputStyle}
          value={risk.capital}
          onChange={(e) => setRisk({ ...risk, capital: e.target.value })}
        />
        <label>Risk per Trade (%)</label>
        <input
          type="number"
          style={inputStyle}
          value={risk.risk_per_trade_pct}
          onChange={(e) => setRisk({ ...risk, risk_per_trade_pct: e.target.value })}
        />
        <label>Max Daily Loss (%)</label>
        <input
          type="number"
          style={inputStyle}
          value={risk.max_daily_loss_pct}
          onChange={(e) => setRisk({ ...risk, max_daily_loss_pct: e.target.value })}
        />
        <button type="submit" style={btnStyle}>Update</button>
      </form>
    </div>
  );
};

export default Risk;
