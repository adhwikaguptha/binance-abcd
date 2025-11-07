import React, { useState } from "react";
import { placeTrade } from "../api/trade";
import axios from "../api/fetcher";

const container = { padding: "20px", color: "#e6eef8", fontFamily: "Inter, sans-serif" };
const btn = {
  padding: "10px 14px",
  marginRight: "10px",
  marginBottom: "10px",
  borderRadius: "6px",
  border: "none",
  background: "#2563eb",
  color: "#fff",
  cursor: "pointer",
};

const BinanceTest = () => {
  const [status, setStatus] = useState("");
  const [tradeResult, setTradeResult] = useState(null);

  const handlePing = async () => {
    try {
      const res = await axios.get("/binance-test/ping");
      setStatus(res ? "✅ Binance ping successful!" : "❌ Ping failed");
    } catch (err) {
      console.error(err);
      setStatus("❌ Ping failed");
    }
  };

  const handleAccount = async () => {
    try {
      const res = await axios.get("/binance-test/account");
      setStatus("✅ Account info retrieved");
      console.log(res);
    } catch (err) {
      console.error(err);
      setStatus("❌ Failed to get account info");
    }
  };

  const handleManualTrade = async () => {
    try {
      const tradeData = {
        symbol: "BTCUSDT",
        side: "BUY",
        qty: 0.001,
        price: null, // market order
      };
      const res = await placeTrade(tradeData);
      setTradeResult(res);
      setStatus("✅ Trade placed (paper trading)");
    } catch (err) {
      console.error(err);
      setStatus("❌ Trade failed");
    }
  };

  return (
    <div style={container}>
      <h2>Binance Test</h2>
      <div>
        <button style={btn} onClick={handlePing}>Ping</button>
        <button style={btn} onClick={handleAccount}>Account Info</button>
      </div>
      {status && <p>{status}</p>}
      {tradeResult && <pre>{JSON.stringify(tradeResult, null, 2)}</pre>}
    </div>
  );
};

export default BinanceTest;
