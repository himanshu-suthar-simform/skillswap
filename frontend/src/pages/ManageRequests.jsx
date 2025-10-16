// src/pages/ManageRequests.jsx
import React from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getMyExchanges, updateExchangeStatus } from "../api/exchanges";
import { toast } from "react-toastify";

export default function ManageRequests() {
  const queryClient = useQueryClient();

  // Get current logged-in user from local storage
  const currentUser = JSON.parse(localStorage.getItem("user"));

  // Fetch all exchanges
  const {
    data: exchanges,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ["teacherExchanges"],
    queryFn: getMyExchanges,
  });

  // Mutation to update exchange status
  const mutation = useMutation({
    mutationFn: ({ id, status, reason }) =>
      updateExchangeStatus(id, { status, reason }),
    onSuccess: () => {
      toast.success("Status updated successfully!");
      queryClient.invalidateQueries(["teacherExchanges"]);
    },
    onError: () => toast.error("Failed to update status"),
  });

  if (isLoading)
    return <div className="text-white p-4">Loading requests...</div>;
  if (isError)
    return <div className="text-red-400 p-4">Error loading requests.</div>;

  // Filter requests where the logged-in user is the teacher
  const teacherRequests = exchanges.filter(
    (ex) =>
      ex.teacher_skill &&
      ex.teacher_skill.user_id === currentUser.id &&
      ["PENDING", "IN_PROGRESS"].includes(ex.status)
  );

  return (
    <div className="min-h-screen bg-black text-white p-6">
      <h1 className="text-3xl font-bold mb-6">Manage Requests</h1>

      {teacherRequests.length === 0 ? (
        <p className="text-gray-400">No pending requests at the moment.</p>
      ) : (
        <div className="space-y-4">
          {teacherRequests.map((req) => (
            <div
              key={req.id}
              className="bg-gray-900/70 p-4 rounded-xl border border-gray-700 shadow-lg hover:shadow-xl transition cursor-pointer"
              onClick={() => toast.info("Open detail modal / page here")}
            >
              <h2 className="text-xl font-semibold mb-1">
                {req.learner.full_name} wants to learn{" "}
                {req.teacher_skill.skill_name}
              </h2>
              <p className="text-gray-400 mb-2">Status: {req.status_display}</p>

              <div className="flex space-x-2 mt-3">
                {req.status === "PENDING" && (
                  <>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        mutation.mutate({ id: req.id, status: "IN_PROGRESS" });
                      }}
                      className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded"
                    >
                      Accept
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        mutation.mutate({
                          id: req.id,
                          status: "CANCELLED",
                          reason: "Rejected by teacher",
                        });
                      }}
                      className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded"
                    >
                      Reject
                    </button>
                  </>
                )}
                {req.status === "IN_PROGRESS" && (
                  <>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        mutation.mutate({ id: req.id, status: "COMPLETED" });
                      }}
                      className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded"
                    >
                      Mark Completed
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        mutation.mutate({
                          id: req.id,
                          status: "CANCELLED",
                          reason: "Cancelled by teacher",
                        });
                      }}
                      className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded"
                    >
                      Cancel
                    </button>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
