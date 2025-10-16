// src/routes/AppRouter.jsx
import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Register from "../pages/Register";
import Login from "../pages/Login";
import Dashboard from "../pages/Dashboard"; // create placeholder page
import Profile from "../pages/Profile";
import UserList from "../pages/UserList";
import UserProfile from "../pages/UserProfile";
import TeachingSkills from "../pages/TeachingSkills";
import TeachingSkillDetail from "../pages/TeachingSkillDetail";

export default function AppRouter() {
  return (
    <Routes>
      <Route path="/register" element={<Register />} />
      {/* placeholder dashboard - create later */}
      <Route path="/login" element={<Login />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/profile" element={<Profile />} />
      <Route path="/users" element={<UserList />} />
      <Route path="/users/:id" element={<UserProfile />} />
      <Route path="/teaching-skills" element={<TeachingSkills />} />
      <Route path="/teaching-skills/:id" element={<TeachingSkillDetail />} />
    </Routes>
  );
}
