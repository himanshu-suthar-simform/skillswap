// src/pages/TeachingSkillDetail.jsx
import React from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { getTeachingSkillDetail } from "../api/skills";
import { toast } from "react-toastify";

export default function TeachingSkillDetail() {
  const { id } = useParams();
  const navigate = useNavigate();

  const {
    data: skill,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ["teachingSkillDetail", id],
    queryFn: () => getTeachingSkillDetail(id),
    onError: () => toast.error("Failed to load skill details"),
  });

  if (isLoading) {
    return <div className="text-white p-4">Loading skill details...</div>;
  }

  if (isError || !skill) {
    return <div className="text-red-400 p-4">Error loading skill details.</div>;
  }

  return (
    <div className="min-h-screen bg-black text-white p-6">
      <button
        onClick={() => navigate(-1)}
        className="mb-6 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded"
      >
        ← Back
      </button>

      <div className="max-w-3xl mx-auto bg-gray-900/70 p-6 rounded-2xl border border-gray-800 shadow-lg">
        <h1 className="text-3xl font-bold mb-2">{skill.skill_name}</h1>
        <p className="text-gray-400 mb-4">{skill.category_name}</p>

        <div className="mb-4">
          <p className="text-sm">
            <span className="font-medium text-gray-300">Teacher:</span>{" "}
            {skill.user?.full_name}
          </p>
          <p className="text-sm">
            <span className="font-medium text-gray-300">Proficiency:</span>{" "}
            {skill.proficiency_level}
          </p>
          <p className="text-sm">
            <span className="font-medium text-gray-300">Experience:</span>{" "}
            {skill.years_of_experience || "N/A"} years
          </p>
          <p className="text-sm">
            <span className="font-medium text-gray-300">Available:</span>{" "}
            {skill.is_available ? "Yes" : "No"}
          </p>
        </div>

        {skill.description && (
          <div className="mb-4">
            <h2 className="text-xl font-semibold mb-2">Description</h2>
            <p className="text-gray-300 leading-relaxed">{skill.description}</p>
          </div>
        )}

        {skill.milestones && skill.milestones.length > 0 && (
          <div className="mb-4">
            <h2 className="text-xl font-semibold mb-2">Milestones</h2>
            <ul className="list-disc list-inside space-y-2">
              {skill.milestones.map((m) => (
                <li key={m.id}>
                  {m.title} ({m.estimated_hours} hrs)
                  <p className="text-gray-400">{m.description}</p>
                </li>
              ))}
            </ul>
          </div>
        )}

        <div className="mb-4">
          <h2 className="text-xl font-semibold mb-2">Details</h2>
          <p>{skill.skill_details?.description || "No description"}</p>
          <p>Proficiency Level: {skill.proficiency_level}</p>
          <p>Experience: {skill.years_of_experience} years</p>
          <p>Certifications: {skill.certifications || "N/A"}</p>
          <p>Portfolio Links:</p>
          {skill.portfolio_links ? (
            Array.isArray(skill.portfolio_links) ? (
              skill.portfolio_links.map((link, idx) => (
                <p key={idx}>
                  <a
                    href={link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-400 underline"
                  >
                    {link}
                  </a>
                </p>
              ))
            ) : (
              <p>
                <a
                  href={skill.portfolio_links}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-400 underline"
                >
                  {skill.portfolio_links}
                </a>
              </p>
            )
          ) : (
            <p>N/A</p>
          )}
          <p>Prerequisites: {skill.prerequisites || "N/A"}</p>
          <p>Learning Outcomes: {skill.learning_outcomes || "N/A"}</p>
          <p>Teaching Methods: {skill.teaching_methods || "N/A"}</p>
        </div>

        <div className="mt-6">
          <button
            onClick={() => toast.info("Feature coming soon: Request to Learn")}
            className="w-full py-2 rounded bg-blue-600 hover:bg-blue-700 transition"
          >
            Request to Learn
          </button>
        </div>
      </div>
    </div>
  );
}
