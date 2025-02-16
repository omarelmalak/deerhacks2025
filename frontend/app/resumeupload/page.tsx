"use client";

import { useState, useEffect } from "react";
import { Poppins } from "next/font/google";
import { CheckCircle, CloudUpload } from "lucide-react";
import { useRouter, useSearchParams } from 'next/navigation';
import axios from "axios";


const poppins = Poppins({
    subsets: ["latin"],
    weight: ["400"],
});

const ResumeUploadPage = () => {
    const [showUploadSuccess, setShowUploadSuccess] = useState<boolean>(false);
    const [loading, setLoading] = useState<boolean>(false);
    const [resume, setResume] = useState<File | null>(null);
    const [firstName, setFirstName] = useState<string>("");
    const [lastName, setLastName] = useState<string>("");
    const [profilePicture, setProfilePicture] = useState<string>("");

    const searchParams = useSearchParams();
    const success = searchParams.get('success');

    if (success) {
        localStorage.setItem('user_id', success.toString());
    } else {
        localStorage.setItem('user_id', 'None')
    }

    const getProfileInformation = async () => {
        try {
            const userid = localStorage.getItem('user_id');
            console.log(userid)
            const response = await fetch(`http://localhost:5000/getprofile/${Number(userid)}`);
            const data = await response.json();
            console.log(data);

            const { first_name, last_name, profile_picture } = data;

            setFirstName(first_name);
            setLastName(last_name);
            setProfilePicture(profile_picture);

        } catch (error) {
            console.error("Error retrieving user LinkedIn information:", error);
        }
    };

    // Call getProfileInformation on component mount
    useEffect(() => {
        getProfileInformation();
    }, []);

    const handleResumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setResume(e.target.files[0]);
            setLoading(true);

            // Simulate a delay to mimic a file upload
            setTimeout(() => {
                setLoading(false);
                setShowUploadSuccess(true);
            }, 3000); // Simulating a 3-second file upload process
        }
    };

    return (
        <div
            className={`flex flex-col items-center ${poppins.className} justify-center min-h-screen bg-gradient-to-b from-gray-900 to-black p-8 text-white`}
        >
            {/* Glowing Pill for User Info */}
            {firstName && lastName && profilePicture && (
                <div className="absolute top-8 right-8 flex items-center space-x-3 px-4 py-2 rounded-full bg-gradient-to-b from-gray-900 to-black text-white shadow-md hover:shadow-xl hover:bg-gradient-to-r from-orange-500 to-red-800 transition-all ease-in-out duration-300 transform hover:scale-105">
                    <img src={profilePicture} alt="Profile" className="w-12 h-12 rounded-full border-2 border-white" />
                    <div>
                        <p className="font-semibold text-lg">{firstName} {lastName}</p>
                    </div>
                </div>
            )}

            {/* Header Section */}
            <div className="text-center">
                <h1 className="text-4xl sm:text-6xl lg:text-7xl font-bold tracking-wide leading-tight">
                    Upload your resume
                </h1>

                {/* Description */}
                <p className="mt-6 text-lg sm:text-xl text-neutral-400 max-w-xl mx-auto leading-relaxed">
                    Choose your resume file to start your journey with us.
                </p>
            </div>

            <div className="mt-10 text-center">
                <label
                    htmlFor="resume-upload"
                    className="px-6 py-3 bg-green-700 hover:bg-green-800 rounded-lg shadow-lg cursor-pointer flex items-center gap-3 text-lg font-medium linkedin-btn"
                >
                    <CloudUpload size={28} /> Select Resume
                </label>
                <input
                    type="file"
                    id="resume-upload"
                    accept=".pdf,.doc,.docx"
                    onChange={handleResumeChange}
                    className="hidden"
                />
            </div>


            {/* Loading Animation */}
            {loading && (
                <div className="mt-6 text-center">
                    <div className="spinner-border text-blue-500 animate-spin inline-block w-8 h-8 border-4 border-t-transparent border-solid rounded-full"></div>
                    <p className="mt-4 text-neutral-400">Uploading your resume...</p>
                </div>
            )}

            {/* Success Message */}
            {showUploadSuccess && !loading && (
                <div className="mt-6 text-center flex flex-col justify-center items-center">
                    <CheckCircle size={40} color="green" />
                    <p className="mt-4 text-lg text-neutral-400">Resume uploaded successfully!</p>
                </div>
            )}

            {/* Animations & Styles */}
            <style jsx>{`
                .spinner-border {
                    border-top-color: transparent;
                    animation: spin 1s linear infinite;
                }

                @keyframes spin {
                    0% {
                        transform: rotate(0deg);
                    }
                    100% {
                        transform: rotate(360deg);
                    }
                }

                .glow {
                    animation: glow-animation 1.5s ease-in-out infinite alternate;
                }

                @keyframes glow-animation {
                    0% {
                        box-shadow: 0 0 10px rgba(255, 255, 255, 0.7), 0 0 20px rgba(255, 255, 255, 0.5);
                    }
                    100% {
                        box-shadow: 0 0 30px rgba(255, 255, 255, 1), 0 0 60px rgba(255, 255, 255, 0.7);
                    }
                }
                .linkedin-btn {
                    transition: all 0.3s ease-in-out;
                }
            
                .linkedin-btn:hover {
                    box-shadow: 0px 0px 20px rgba(34, 197, 94, 0.9); 
                    transform: scale(1.05);
                }
            `}</style>
        </div>
    );
};

export default ResumeUploadPage;
