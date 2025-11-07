import axios from "axios";
import { logout } from "../utils/auth"; // you need to create a logout helper

const BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const instance = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Inject Authorization header automatically
instance.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 responses globally
instance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      logout(); // remove token & redirect
      window.location.href = "/"; // force redirect to login
    }
    return Promise.reject(error);
  }
);

export default instance;
