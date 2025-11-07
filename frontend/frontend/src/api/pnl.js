// src/api/pnl.js
import axios from "./fetcher";

export const getTodayPnL = async () => {
  const res = await axios.get("/pnl/today");
  return res.data;
};

export const getPnLSummary = async () => {
  const res = await axios.get("/pnl/summary");
  return res.data;
};
