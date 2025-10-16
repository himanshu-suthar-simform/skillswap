import React from "react";
import { useQuery } from "@tanstack/react-query";
import { getCurrentUser, getUserSkills } from "../api/user";
import useAuth from "../hooks/useAuth";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";

export default function Profile() {
  const { logout } = useAuth();
  const navigate = useNavigate();

  // Fetch user info
  const { data: userInfo, isLoading: userLoading } = useQuery({
    queryKey: ["currentUser"],
    queryFn: getCurrentUser,
    onError: (err) => {
      toast.error("Failed to fetch user info");
      if (err.status === 401) {
        logout();
        navigate("/login");
      }
    },
    staleTime: 5 * 60 * 1000,
  });

  // Fetch user skills
  const { data: skills, isLoading: skillsLoading } = useQuery({
    queryKey: ["userSkills"],
    queryFn: getUserSkills,
    onError: (err) => toast.error("Failed to fetch user skills"),
    enabled: !!userInfo,
  });

  if (userLoading) return <div className="p-8 text-white">Loading profile...</div>;

  return (
    <div className="min-h-screen bg-black text-white p-8">
      {/* Header */}
      <div className="max-w-4xl mx-auto">
        <div className="flex flex-col md:flex-row items-center md:items-start bg-gray-900 rounded-xl p-6 shadow-lg mb-8">
          {/* Profile picture */}
          <div className="w-32 h-32 rounded-full overflow-hidden border-2 border-gray-700 mb-4 md:mb-0 md:mr-6 flex-shrink-0">
            <img
              src={userInfo.profile?.profile_picture_url || "https://via.placeholder.com/150"}
              alt="Profile"
              className="w-full h-full object-cover"
            />
          </div>

          {/* User info */}
          <div className="flex-1">
            <h1 className="text-3xl font-bold">{userInfo.full_name}</h1>
            <p className="text-gray-400">{userInfo.username}</p>
            <p className="mt-2">{userInfo.profile?.bio}</p>

            <div className="mt-4 grid grid-cols-2 gap-4 text-sm text-gray-300">
              <div>
                <strong>Email:</strong> {userInfo.email}
              </div>
              <div>
                <strong>Phone:</strong> {userInfo.profile?.phone_number || "N/A"}
              </div>
              <div>
                <strong>Location:</strong> {userInfo.profile?.location || "N/A"}
              </div>
              <div>
                <strong>Language:</strong> {userInfo.profile?.language_preference || "N/A"}
              </div>
            </div>
          </div>
        </div>

        {/* Teaching Skills */}
        <div>
          <h2 className="text-2xl font-semibold mb-4">My Teaching Skills</h2>
          {skillsLoading ? (
            <p>Loading skills...</p>
          ) : skills?.results && skills.results.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
              {skills.results.map((skill) => (
                <div
                  key={skill.id}
                  className="bg-gray-900 rounded-xl p-4 shadow hover:shadow-lg transition cursor-pointer"
                >
                  <h3 className="font-semibold text-lg">{skill.skill_name}</h3>
                  <p className="text-sm text-gray-400 mb-2">{skill.category_name}</p>
                  <p className="text-sm">
                    <strong>Proficiency:</strong> {skill.proficiency_level}
                  </p>
                  <p className="text-sm">
                    <strong>Students:</strong> {skill.student_count}
                  </p>
                  <p className="text-sm">
                    <strong>Rating:</strong> {skill.rating}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <p>No skills found</p>
          )}
        </div>
      </div>
    </div>
  );
}
