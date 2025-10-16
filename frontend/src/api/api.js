// src/api/api.js
import axios from "axios";

const API_URL = (process.env.REACT_APP_API_URL || "http://localhost:8000/api/v1").replace(/\/+$/, "");

const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add a request interceptor to attach token if present
api.interceptors.request.use(
  (config) => {
    try {
      const token = localStorage.getItem("access_token");
      if (token) {
        config.headers = config.headers || {};
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch (e) {
      // ignore
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Optionally add a response interceptor to format errors
api.interceptors.response.use(
  (res) => res,
  (error) => {
    // Convert axios/HTTP errors into consistent shape
    if (error.response) {
      // server returned response
      return Promise.reject({
        status: error.response.status,
        data: error.response.data,
        message: error.response.data?.detail || error.response.statusText,
      });
    }
    return Promise.reject({ message: error.message || "Network Error" });
  }
);

export default api;
