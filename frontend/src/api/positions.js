// src/api/positions.js
import axios from "./fetcher";

export const getPositions = async () => {
  const res = await axios.get("/positions");
  return res.data;
};
