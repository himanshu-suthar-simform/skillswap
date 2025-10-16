// src/pages/ExchangeDetailModal.jsx
import React from "react";

export default function ExchangeDetailModal({ open, onClose, exchange }) {
  if (!open || !exchange) return null;

  console.log("Exchange:", exchange);


  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black/70 backdrop-blur-sm z-50">
      <div className="bg-gray-900 text-white p-6 rounded-2xl w-full max-w-lg border border-gray-700 shadow-xl">
        <h2 className="text-2xl font-semibold mb-4">Request Detail</h2>

        <p>
          <span className="font-medium">Learner:</span>{" "}
          {exchange.learner.full_name}
        </p>
        <p>
          <span className="font-medium">Skill to Learn:</span>{" "}
          {exchange.teacher_skill.skill_name}
        </p>
        <p>
          <span className="font-medium">Status:</span> {exchange.status_display}
        </p>
        {exchange.reason && (
          <p>
            <span className="font-medium">Reason:</span> {exchange.reason}
          </p>
        )}

        <div className="flex justify-end mt-4">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
