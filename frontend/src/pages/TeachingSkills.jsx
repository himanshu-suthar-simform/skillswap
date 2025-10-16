// src/pages/TeachingSkills.jsx
import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { getTeachingSkills } from "../api/skills";
import { toast } from "react-toastify";
import { useNavigate } from "react-router-dom";

export default function TeachingSkills() {
  const [page, setPage] = useState(1);
  const navigate = useNavigate();

  const { data, isLoading, isError } = useQuery({
    queryKey: ["teachingSkills", page],
    queryFn: () => getTeachingSkills(page),
    keepPreviousData: true,
    onError: () => toast.error("Failed to load teaching skills"),
  });

  if (isLoading) {
    return <div className="text-white p-4">Loading teaching skills...</div>;
  }

  if (isError) {
    return (
      <div className="text-red-400 p-4">Error loading teaching skills.</div>
    );
  }

  const skills = data?.results || [];

  return (
    <div className="min-h-screen bg-black text-white p-6">
      <h1 className="text-3xl font-bold mb-6">Teaching Skills</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {skills.map((skill) => (
          <div
            key={skill.id}
            className="bg-gray-900/60 backdrop-blur-sm border border-gray-800 rounded-xl p-4 shadow hover:shadow-lg transition"
          >
            <h2 className="text-xl font-semibold mb-1">{skill.skill_name}</h2>
            <p className="text-sm text-gray-400 mb-2">
              Category: {skill.category_name}
            </p>
            <p className="text-sm mb-1">
              <span className="font-medium">Teacher:</span> {skill?.user?.full_name}
            </p>
            <p className="text-sm mb-1">
              <span className="font-medium">Proficiency:</span>{" "}
              {skill.proficiency_level}
            </p>
            <p className="text-sm mb-3">
              <span className="font-medium">Rating:</span>{" "}
              {skill.rating || "N/A"}
            </p>

            <button
              onClick={() => navigate(`/teaching-skills/${skill.id}`)}
              className="w-full py-2 rounded bg-blue-600 hover:bg-blue-700 transition"
            >
              View Details
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
