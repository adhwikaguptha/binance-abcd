// src/api/orders.js
import axios from "./fetcher";

/**
 * Fetch logged-in user's orders
 */
export const getOrders = async () => {
  const res = await axios.get("/orders");
  return res.data;
};
