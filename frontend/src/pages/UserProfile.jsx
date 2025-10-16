// src/pages/UserProfile.jsx
import React from "react";
import { useQuery } from "@tanstack/react-query";
import { getUserById } from "../api/user";
import { useParams, useNavigate } from "react-router-dom";
import { toast } from "react-toastify";

export default function UserProfile() {
  const { id } = useParams();
  const navigate = useNavigate();

  const {
    data: user,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ["user", id],
    queryFn: () => getUserById(id),
    onError: (err) => {
      toast.error("Failed to load user profile");
      navigate("/users");
    },
  });

  if (isLoading)
    return <div className="text-white p-4">Loading profile...</div>;
  if (isError || !user)
    return <div className="text-red-400 p-4">User not found.</div>;

  return (
    <div className="min-h-screen bg-black text-white p-6">
      <div className="max-w-3xl mx-auto bg-gray-900/60 backdrop-blur-sm border border-gray-800 rounded-xl p-6 shadow">
        <div className="flex items-center mb-6">
          <img
            src={user.profile_picture_url || "/default-avatar.png"}
            alt={user.full_name}
            className="w-20 h-20 rounded-full object-cover mr-4 border border-gray-700"
          />
          <div>
            <h1 className="text-2xl font-semibold">{user.full_name}</h1>
            <p className="text-sm text-gray-400">@{user.username}</p>
            <p className="text-sm text-gray-400">
              Joined: {new Date(user.date_joined).toLocaleDateString()}
            </p>
          </div>
        </div>

        <div className="mb-4">
          <h2 className="text-lg font-semibold mb-2">Profile Info</h2>
          <p>
            <span className="font-medium">Email:</span> {user.email}
          </p>
          <p>
            <span className="font-medium">Location:</span>{" "}
            {user.profile?.location || "N/A"}
          </p>
          <p>
            <span className="font-medium">Available:</span>{" "}
            {user.profile?.is_available ? "Yes" : "No"}
          </p>
          <p>
            <span className="font-medium">Bio:</span>{" "}
            {user.profile?.bio || "N/A"}
          </p>
        </div>

        <button
          onClick={() => navigate("/users")}
          className="mt-4 py-2 px-4 rounded bg-blue-600 hover:bg-blue-700 transition"
        >
          Back to Users
        </button>
      </div>
    </div>
  );
}
