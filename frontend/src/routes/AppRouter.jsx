// src/routes/AppRouter.jsx
import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Register from "../pages/Register";

export default function AppRouter() {
  return (
    <Routes>
      <Route path="/register" element={<Register />} />
      {/* placeholder dashboard - create later */}
      <Route path="/dashboard" element={<div className="p-8">Dashboard (protected view)</div>} />
      <Route path="/" element={<Navigate to="/register" replace />} />
    </Routes>
  );
}
