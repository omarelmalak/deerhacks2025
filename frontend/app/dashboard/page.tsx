"use client";

import React, { useState, useEffect } from "react";
import axios from "axios";

const ResumeUpload: React.FC = () => {
    const [file, setFile] = useState<File | null>(null);
    const [cleanedExperiences, setCleanedExperiences] = useState<any[]>([]);
    const [roadmap, setRoadmap] = useState<any[]>([]);
    const [desiredRole, setDesiredRole] = useState<string>("");
    const [desiredCompany, setDesiredCompany] = useState<string>("");

    const linkedInUrl = `https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=778z82h4dtgrrz&redirect_uri=http%3A%2F%2F127.0.0.1%3A5000%2Flinkedin-openid%2Fcallback&scope=openid%20profile%20email`;

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files?.length) {
            setFile(e.target.files[0]);
        }
    };

    const handleFileUpload = async () => {
        if (!file) return alert("Please select a resume file to upload.");
        if (desiredRole === "" || desiredCompany === "") return alert("Please enter a desired role and company.");

        const formData = new FormData();
        formData.append("file", file);

        try {
            const res = await axios.post("http://127.0.0.1:5000/parse-resume", formData);
            handleGenerateRoadmap(res.data.experiences || []);
        } catch (error) {
            console.error("Error uploading file:", error);
        }
    };

    const handleGenerateRoadmap = async (experiences: any[]) => {
        try {
            const response = await axios.post("http://127.0.0.1:5000/generate-roadmap", { experiences, desiredRole, desiredCompany, user_id: localStorage.getItem("user_id") });
            console.log("API Response:", response.data);

            // Ensure correct data assignment
            const { cleaned_experiences, career_roadmap } = response.data;
            setCleanedExperiences(cleaned_experiences || []);
            setRoadmap(career_roadmap || []);
        } catch (error) {
            console.error("Error generating roadmap:", error);
        }
    };

    useEffect(() => {
        console.log("Cleaned Experiences:", cleanedExperiences);
        console.log("Career Roadmap:", roadmap);
    }, [cleanedExperiences, roadmap]);

    return (
        <div className="max-w-lg mx-auto p-4 border rounded-lg shadow">
            <h2 className="text-xl font-bold mb-4">Upload Your Resume</h2>
            <input type="file" onChange={handleFileChange} className="mb-4" />
            <button
                onClick={handleFileUpload}
                className="w-full px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
                Upload and Generate Roadmap
            </button>

            {cleanedExperiences.length > 0 && (
                <div className="mt-4 border rounded p-2">
                    <h3 className="font-bold mb-2">Cleaned Experiences:</h3>
                    <ul className="text-sm">
                        {cleanedExperiences.map((exp, index) => (
                            <li key={index} className="py-1">
                                <strong>{exp.position}</strong> at {exp.company} ({exp.start_date} to {exp.end_date}): {exp.summary}
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            {roadmap.length > 0 && (
                <div className="mt-4 border rounded p-2">
                    <h3 className="font-bold mb-2">Career Roadmap:</h3>
                    <ul className="text-sm">
                        {roadmap.map((phase, index) => (
                            <li key={index} className="py-2">
                                <strong>{phase.position} at {phase.companies?.join(", ") || "N/A"} </strong> ({phase.start_date} to {phase.end_date})
                            </li>
                        ))}
                    </ul>
                </div>
            )}
            <input
                type="text"
                placeholder="Desired Role"
                value={desiredRole}
                onChange={(e) => setDesiredRole(e.target.value)}
                className="w-full mb-2 p-2 border rounded"
            />
            <input
                type="text"
                placeholder="Desired Company"
                value={desiredCompany}
                onChange={(e) => setDesiredCompany(e.target.value)}
                className="w-full mb-4 p-2 border rounded"
            />

            <a href={linkedInUrl}>
                <button>Login with LinkedIn</button>
            </a>
        </div>
    );
};

export default ResumeUpload;
