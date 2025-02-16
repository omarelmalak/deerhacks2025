"use client";
import React, { useEffect, useState } from "react";
import axios from "axios";
import { motion } from "framer-motion";

type Roadmap = {
  id: number;
  title: string;
  companies: string[]; // Companies as a list
  duration: string;
  user_id: number;
};

export default function RoadmapCards() {
  const userId = 3;
  const [roadmaps, setRoadmaps] = useState<Roadmap[]>([]);
  const [userPrompt, setUserPrompt] = useState("");
  const [error, setError] = useState<string | null>(null);

  const fetchRoadmaps = async () => {
    try {
      const response = await axios.get(`http://127.0.0.1:5000/get-roadmaps/${userId}`);
      setRoadmaps(response.data?.roadmaps ?? []);
    } catch {
      setError("Failed to load roadmaps. Please try again later.");
    }
  };

  const handleSubmit = async () => {
    try {
      const response = await axios.post("http://127.0.0.1:5000/generate-roadmap", {
        userPrompt,
        user_id: parseInt(localStorage.getItem("user_id") || "0"),
      });
      setRoadmaps(response.data.career_roadmap || []);
    } catch (error) {
      console.error("Error generating roadmap:", error);
    }
  };

  useEffect(() => {
    fetchRoadmaps();
  }, []);

  return (
    <div className="p-6">
      <div className="mb-6 flex space-x-4 items-center">
        <input
          type="text"
          value={userPrompt}
          onChange={(e) => setUserPrompt(e.target.value)}
          placeholder="Enter your career goal..."
          className="border p-3 rounded-lg w-full shadow-sm focus:outline-blue-500"
        />
        <button
          onClick={handleSubmit}
          className="bg-gradient-to-r from-red-500 to-orange-400 text-white px-6 py-2 rounded-full shadow-lg hover:scale-105 transition-transform"
        >
          Generate
        </button>
      </div>
      <div className="flex overflow-x-auto space-x-6 p-4">
        {roadmaps.length > 0 ? (
          roadmaps.map((roadmap) => (
            <motion.div
              key={roadmap.id}
              whileHover={{ scale: 1.05 }}
              className="flex-shrink-0 w-80 bg-white border-2 border-red-300 rounded-xl shadow-xl p-5 text-center"
            >
              <h3 className="text-xl font-extrabold text-gray-800 mb-3">
                {roadmap.title}
              </h3>
              <div className="mb-3">
                <p className="text-gray-500 font-semibold">Featured Companies:</p>
                {roadmap.companies.slice(0, 2).map((company, idx) => (
                  <p key={idx} className="text-gray-600 text-sm">{company}</p>
                ))}
              </div>
              {roadmap.duration && (
                <div className="text-gray-500 text-sm font-medium mb-2">
                  Duration: {roadmap.duration}
                </div>
              )}
            </motion.div>
          ))
        ) : (
          <div className="text-center text-gray-400 font-medium">
            No roadmaps found.
          </div>
        )}
      </div>
    </div>
  );
}
