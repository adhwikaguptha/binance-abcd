import axios from "axios";
import { BASE_URL } from "./config";

/**
 * Login user via OAuth2 token (Swagger route)
 * Note: Backend expects form-encoded data
 */
export const loginUser = async (username, password) => {
  const res = await axios.post(
    `${BASE_URL}/auth/token`,
    new URLSearchParams({ username, password }),
    {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    }
  );
  return res.data;
};

/**
 * Register new user
 * Sends username, email, and password as JSON
 */
export const registerUser = async (username, email, password) => {
  const res = await axios.post(
    `${BASE_URL}/auth/register`,
    {
      username: username,
      email: email,
      password: password,
    },
    {
      headers: { "Content-Type": "application/json" },
    }
  );
  return res.data;
};
