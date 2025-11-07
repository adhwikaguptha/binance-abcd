// src/api/signals.js
import api from "./fetcher";
import axios from "./fetcher";


/**
 * Signal-related API helpers.
 * These map to your backend endpoints as provided earlier.
 */

export const getAllSignals = async (params = {}) => {
  // params can include ?status=pending, ?active=true, pagination etc.
  const res = await api.get("/signals", { params });
  return res.data;
};

export const getPendingSignals = async () => {
  const res = await api.get("/signals/pending");
  return res.data;
};

export const getActiveSignals = async () => {
  const res = await api.get("/signals/active");
  return res.data;
};

export const approveSignal = async (id, payload = {}) => {
  // payload can include { reason?: string, execute?: boolean } depending on backend
  const res = await api.post(`/signals/${id}/approve`, payload);
  return res.data;
};

export const rejectSignal = async (id, payload = {}) => {
  const res = await api.post(`/signals/${id}/reject`, payload);
  return res.data;
};

// optional: fetch single signal detail if backend supports it
export const getSignal = async (id) => {
  const res = await api.get(`/signals/${id}`);
  return res.data;
};

export const updateActiveSignals = async () => {
  try {
    const res = await axios.post("/signals/update_active");
    return res.data;
  } catch (err) {
    console.error("Error updating active signals:", err);
    throw err;
  }
};