// src/api/auth.js
import api from "./api";

/**
 * registerUser:
 * - userData should be an object matching backend expected fields.
 * - returns server response (data) on success; throws structured error on failure.
 */
export const registerUser = async (userData) => {
  // Example endpoint: POST /auth/register/ or /accounts/register/
  // Set this to whatever your backend uses.
  const endpoint = "/accounts/auth/register/"; // change if your backend uses different path
  const response = await api.post(endpoint, userData);
  return response.data;
};


export const loginUser = async (credentials) => {
  const endpoint = "/accounts/auth/token/";
  const response = await api.post(endpoint, credentials);
  return response.data;
};
