// src/api/risk.js
import axios from "./fetcher";

export const getRiskSettings = async () => {
  const res = await axios.get("/risk");
  return res.data;
};

export const setupRiskSettings = async (data) => {
  const res = await axios.post("/risk/setup", data);
  return res.data;
};

export const updateRiskSettings = async (data) => {
  const res = await axios.put("/risk/update", data);
  return res.data;
};
