import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getMyTeachingSkills, createExchange } from "../api/exchanges";
import { toast } from "react-toastify";

export default function RequestToLearnModal({ open, onClose, teacherSkillId }) {
  const queryClient = useQueryClient();
  const [form, setForm] = useState({
    offered_skill: "",
    learning_goals: "",
    availability: "",
    proposed_duration: "",
    notes: "",
  });

  const { data: mySkills, isLoading: loadingSkills } = useQuery({
    queryKey: ["myTeachingSkills"],
    queryFn: getMyTeachingSkills,
    enabled: open,
  });

  const mutation = useMutation({
    mutationFn: (payload) => createExchange(payload),
    onSuccess: () => {
      toast.success("Request sent successfully!");
      queryClient.invalidateQueries(["exchanges"]);
      onClose();
    },
    onError: () => toast.error("Failed to send request"),
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!form.offered_skill) return toast.error("Select a skill to offer");
    mutation.mutate({ ...form, user_skill: teacherSkillId });
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black/70 backdrop-blur-sm z-50">
      <div className="bg-gray-900 text-white p-6 rounded-2xl w-full max-w-lg border border-gray-700 shadow-xl">
        <h2 className="text-2xl font-semibold mb-4">Request to Learn</h2>

        {loadingSkills ? (
          <p className="text-gray-400">Loading your skills...</p>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-3">
            <div>
              <label className="block mb-1 text-sm">Your Skill to Offer</label>
              <select
                value={form.offered_skill}
                onChange={(e) =>
                  setForm({ ...form, offered_skill: e.target.value })
                }
                className="w-full bg-gray-800 border border-gray-700 rounded p-2 text-white"
              >
                <option value="">Select your skill</option>
                {mySkills?.results?.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.skill_name} ({s.proficiency_level})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block mb-1 text-sm">Learning Goals</label>
              <textarea
                rows="2"
                value={form.learning_goals}
                onChange={(e) =>
                  setForm({ ...form, learning_goals: e.target.value })
                }
                className="w-full bg-gray-800 border border-gray-700 rounded p-2 text-white"
              />
            </div>

            <div>
              <label className="block mb-1 text-sm">Availability</label>
              <input
                type="text"
                value={form.availability}
                onChange={(e) =>
                  setForm({ ...form, availability: e.target.value })
                }
                placeholder="e.g. Weekdays 9PM"
                className="w-full bg-gray-800 border border-gray-700 rounded p-2 text-white"
              />
            </div>

            <div>
              <label className="block mb-1 text-sm">Proposed Duration (hours)</label>
              <input
                type="number"
                value={form.proposed_duration}
                onChange={(e) =>
                  setForm({ ...form, proposed_duration: e.target.value })
                }
                className="w-full bg-gray-800 border border-gray-700 rounded p-2 text-white"
              />
            </div>

            <div>
              <label className="block mb-1 text-sm">Notes</label>
              <textarea
                rows="2"
                value={form.notes}
                onChange={(e) => setForm({ ...form, notes: e.target.value })}
                className="w-full bg-gray-800 border border-gray-700 rounded p-2 text-white"
              />
            </div>

            <div className="flex justify-end space-x-2 mt-4">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={mutation.isLoading}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded"
              >
                {mutation.isLoading ? "Sending..." : "Send Request"}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
