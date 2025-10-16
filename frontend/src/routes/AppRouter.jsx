// src/routes/AppRouter.jsx
import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Register from "../pages/Register";
import Login from "../pages/Login";
import Dashboard from "../pages/Dashboard"; // create placeholder page
import Profile from "../pages/Profile";



export default function AppRouter() {
  return (
    <Routes>
      <Route path="/register" element={<Register />} />
      {/* placeholder dashboard - create later */}
      <Route path="/login" element={<Login />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/profile" element={<Profile />} />
    </Routes>
  );
}
