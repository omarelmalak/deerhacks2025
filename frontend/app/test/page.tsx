"use client";
import React, { useEffect, useRef } from 'react';
import { Poppins, Bungee } from "next/font/google";
import gsap from 'gsap';

const poppins = Poppins({
    subsets: ["latin"],
    weight: ["400"],
});

const bungee = Bungee({
    subsets: ['latin'],
    weight: ['400']
});

const FloatingCards: React.FC = () => {
    const cardRef = useRef<HTMLDivElement[]>([]);

    useEffect(() => {
        const cards = cardRef.current;

        const floatAnimation = () => {
            // Get the window dimensions for boundaries
            const maxX = window.innerWidth / 2;
            const maxY = window.innerHeight / 2;

            cards.forEach((card, index) => {
                gsap.set(card, { x: 0, y: 0, rotation: 0 }); // Set the initial state

                gsap.to(card, {
                    duration: Math.random() * 3 + 3, // Random duration for each card
                    x: Math.random() * maxX - maxX / 2, // Move horizontally within the screen width
                    y: Math.random() * maxY - maxY / 2, // Move vertically within the screen height
                    rotation: Math.random() * 20 - 10, // Slight rotation for subtle effect
                    ease: 'power1.inOut',
                    repeat: -1, // Loop the animation indefinitely
                    yoyo: true, // Cards move back and forth
                    delay: Math.random() * 2, // Stagger the start time of each card
                    onUpdate: () => {
                        // Optionally adjust each card's position on each update for interaction
                        gsap.to(card, {
                            x: "+=" + (Math.random() * 2 - 1) * 20, // Small random horizontal shift for interaction
                            y: "+=" + (Math.random() * 2 - 1) * 20, // Small random vertical shift for interaction
                            duration: 0.5, // Small update duration
                            ease: "power1.inOut"
                        });
                    }
                });
            });
        };

        // Wait until the component is mounted and cards are rendered
        const timeoutId = setTimeout(() => {
            floatAnimation(); // Start the animation after a short delay
        }, 100); // 100ms delay to ensure rendering

        // Optional: Resize listener to update limits when the window resizes
        const handleResize = () => {
            floatAnimation();
        };

        window.addEventListener('resize', handleResize);

        // Cleanup on component unmount
        return () => {
            clearTimeout(timeoutId); // Clear the timeout
            window.removeEventListener('resize', handleResize);
        };
    }, []);

    const cards = Array(6).fill(0); // Create an array of 6 cards to animate

    return (
        <div className={`relative h-screen bg-gradient-to-b from-gray-900 to-black ${poppins.className} flex flex-col justify-center items-center space-y-8`}>
            {/* Profile Section Above Cards */}
            <div className="bg-white p-6 rounded-2xl shadow-2xl flex flex-col items-center w-5/12">
                <img
                    src="https://randomuser.me/api/portraits/men/32.jpg" // Replace with actual user image
                    alt="Profile"
                    className="w-24 h-24 rounded-full border-4 border-gray-300 mb-4"
                />
                <h2 className="text-2xl font-bold text-gray-800">John Doe</h2>
                <p className="text-sm text-gray-500">Software Developer at XYZ</p>
                <p className="text-xs text-gray-400 italic">Joined in 2023</p>
                <p className="text-gray-700 mt-4 text-center">Passionate about technology, innovation, and helping others achieve their best work.</p>
            </div>

            {/* Floating Cards */}
            <div className="flex justify-center items-center space-x-4">
                {cards.map((_, index) => (
                    <div
                        key={index}
                        ref={(el) => (cardRef.current[index] = el as HTMLDivElement)}
                    >
                        <div className="bg-white p-6 rounded-2xl shadow-2xl flex flex-col items-center transform transition-transform duration-300 hover:scale-105">
                            <h3 className="font-bold text-xl">Card {index + 1}</h3>
                            <p className="text-sm text-gray-500">Company Name</p>
                            <p className="text-xs text-gray-400 italic">2025</p>
                            <p className="text-gray-700 mt-4 text-center">Some content for the card goes here!</p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default FloatingCards;
