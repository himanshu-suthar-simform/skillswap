// src/pages/UserList.jsx
import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { getUsers } from "../api/user";
import { toast } from "react-toastify";
import { useNavigate } from "react-router-dom";

export default function UserList() {
  const [page, setPage] = useState(1);
  const navigate = useNavigate();

  // Fetch users with React Query v5 syntax (object form)
  const { data, isLoading, isError } = useQuery({
    queryKey: ["usersList", page],
    queryFn: () => getUsers(page),
    keepPreviousData: true,
    onError: () => toast.error("Failed to load users"),
  });

  if (isLoading) {
    return <div className="text-white p-4">Loading users...</div>;
  }

  if (isError) {
    return <div className="text-red-400 p-4">Error loading users.</div>;
  }

  const users = data?.results || [];

  return (
    <div className="min-h-screen bg-black text-white p-6">
      <h1 className="text-3xl font-bold mb-6">Available Users</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {users.map((user) => (
          <div
            key={user.id}
            className="bg-gray-900/60 backdrop-blur-sm border border-gray-800 rounded-xl p-4 shadow hover:shadow-lg transition"
          >
            <div className="flex items-center mb-4">
              <img
                src={user.profile_picture_url || "/default-avatar.png"}
                alt={user.full_name}
                className="w-16 h-16 rounded-full object-cover mr-4 border border-gray-700"
              />
              <div>
                <h2 className="text-lg font-semibold">{user.full_name}</h2>
                <p className="text-sm text-gray-400">@{user.username}</p>
              </div>
            </div>

            <p className="text-sm mb-2">
              <span className="font-medium">Location:</span>{" "}
              {user.profile?.location || "N/A"}
            </p>
            <p className="text-sm mb-4">
              <span className="font-medium">Available:</span>{" "}
              {user.profile?.is_available ? "Yes" : "No"}
            </p>

            <button
              onClick={() => navigate(`/users/${user.id}`)}
              className="w-full py-2 rounded bg-blue-600 hover:bg-blue-700 transition"
            >
              View Profile
            </button>
          </div>
        ))}
      </div>

      {/* Pagination */}
      <div className="flex justify-between items-center mt-6">
        <button
          onClick={() => setPage((prev) => Math.max(prev - 1, 1))}
          disabled={!data?.previous}
          className="px-4 py-2 rounded bg-gray-700 hover:bg-gray-600 disabled:opacity-50 transition"
        >
          Previous
        </button>
        <span>
          Page {page} of {data?.total_pages || 1}
        </span>
        <button
          onClick={() => setPage((prev) => prev + 1)}
          disabled={!data?.next}
          className="px-4 py-2 rounded bg-gray-700 hover:bg-gray-600 disabled:opacity-50 transition"
        >
          Next
        </button>
      </div>
    </div>
  );
}
