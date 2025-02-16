"use client";

import { useState, useEffect } from "react";
import { Poppins } from "next/font/google";
import { Linkedin } from "lucide-react";


const poppins = Poppins({
  subsets: ["latin"],
  weight: ["400"],
});

const LandingPage = () => {
  const [showWelcome, setShowWelcome] = useState<boolean>(false);

  useEffect(() => {
    setTimeout(() => {
      setShowWelcome(true);
    }, 100);
  }, []);

  return (
    <div
      className={`flex flex-col items-center ${poppins.className} justify-center min-h-screen bg-gradient-to-b from-gray-900 to-black p-8 text-white`}
    >

      {/* Header Section */}
      <div className="text-center">
        <h1 className="text-4xl sm:text-6xl lg:text-7xl font-bold tracking-wide leading-tight">
          Your roadmap,
          <span
            className={`block bg-gradient-to-r from-orange-500 to-red-800 text-transparent bg-clip-text ${showWelcome ? "animate-pop-up" : "opacity-0"}`}
          >
            your way.
          </span>
        </h1>

        {/* Description */}
        <p className="mt-6 text-lg sm:text-xl text-neutral-400 max-w-xl mx-auto leading-relaxed">
          Login, upload your resume, and enter your destination. We'll guide you on your journey.
        </p>
      </div>

      {/* LinkedIn Login Button */}
      <a
        href="https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=778z82h4dtgrrz&redirect_uri=http%3A%2F%2F127.0.0.1%3A5000%2Flinkedin-openid%2Fcallback&scope=openid%20profile%20email"
        className="mt-10 flex items-center gap-3 px-6 py-3 bg-blue-700 hover:bg-blue-800 rounded-lg shadow-lg transition hover:shadow-blue-500/50 hover:scale-105 linkedin-btn text-lg font-medium"
      >
        <Linkedin size={28} /> Login with LinkedIn
      </a>

      {/* Animations & Styles */}
      <style jsx>{`
        .animate-pop-up {
          animation: popUp 1.5s ease-out forwards;
        }

        @keyframes popUp {
          0% {
            opacity: 0;
            transform: translateY(-30px);
          }
          100% {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .linkedin-btn {
          transition: all 0.3s ease-in-out;
        }

        .linkedin-btn:hover {
          box-shadow: 0px 0px 20px rgba(10, 102, 194, 0.9);
        }
      `}</style>
    </div>
  );
};

export default LandingPage;
