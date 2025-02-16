"use client";

import React, { useEffect, useRef } from "react";
import { gsap } from "gsap";
import { Bungee, Inter } from 'next/font/google';
import ScrollTrigger from "gsap/ScrollTrigger";
import { useRouter, useSearchParams } from 'next/navigation';


gsap.registerPlugin(ScrollTrigger);

const experiences = [
    {
        id: 1,
        company: "Google",
        position: "Software Engineer",
        logo: "https://upload.wikimedia.org/wikipedia/commons/4/4a/Logo_2013_Google.png",
        description: "Worked on scaling backend services and optimizing API performance.",
        year: "2023-2024",
    },
    {
        id: 2,
        company: "Meta",
        position: "Frontend Developer",
        logo: "https://upload.wikimedia.org/wikipedia/commons/0/05/Facebook_Logo_%282019%29.png",
        description: "Developed interactive UI components for Facebook's news feed.",
        year: "2022-2023",
    },
    {
        id: 3,
        company: "Shopify",
        position: "Intern - Full Stack",
        logo: "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5d/Shopify_logo_2018.svg/512px-Shopify_logo_2018.svg.png",
        description: "Built features for Shopify storefronts and improved checkout UX.",
        year: "2021-2022",
    },
    {
        id: 4,
        company: "Shopify",
        position: "Intern - Full Stack",
        logo: "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5d/Shopify_logo_2018.svg/512px-Shopify_logo_2018.svg.png",
        description: "Built features for Shopify storefronts and improved checkout UX.",
        year: "2021-2022",
    },
    {
        id: 5,
        company: "Shopify",
        position: "Intern - Full Stack",
        logo: "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5d/Shopify_logo_2018.svg/512px-Shopify_logo_2018.svg.png",
        description: "Built features for Shopify storefronts and improved checkout UX.",
        year: "2021-2022",
    },
];

const bungee = Bungee({
    subsets: ['latin'],
    weight: ['400']
});

const inter = Inter({
    subsets: ['latin'],
    weight: ['400', '600'],
});

export default function ExperienceTimeline() {
    const experienceRefs = useRef<(HTMLDivElement | null)[]>([]);
    const userCardRef = useRef<HTMLDivElement | null>(null);
    const lineRef = useRef<HTMLDivElement | null>(null);
    const router = useRouter();
    const searchParams = useSearchParams();

    const success = searchParams.get('success');

    if (success) {
        localStorage.setItem('user_id', success.toString());
    } else {
        localStorage.setItem('user_id', 'None')
    }

    useEffect(() => {


        gsap.fromTo(
            userCardRef.current,
            { opacity: 0, y: 50 },
            {
                opacity: 1,
                y: 0,
                duration: 1,
                ease: "power4.out",
                scrollTrigger: {
                    trigger: userCardRef.current,
                    start: "top 80%",
                    toggleActions: "play none none none",
                }
            }
        );


        gsap.fromTo(
            lineRef.current,
            { height: "0%" },
            {
                height: "100%",
                duration: 1,
                scrollTrigger: {
                    trigger: lineRef.current,
                    start: "top 80%",
                    end: "bottom top",
                    scrub: true,
                    markers: false,
                    toggleActions: "play none none none",
                }
            }
        );

        experienceRefs.current.forEach((expRef, index) => {
            gsap.fromTo(
                expRef,
                { opacity: 0, y: 50 },
                {
                    opacity: 1,
                    y: 0,
                    duration: 1,
                    stagger: 0.2,
                    ease: "power4.out",
                    scrollTrigger: {
                        trigger: expRef,
                        start: "top 80%",
                        toggleActions: "play none none none",
                        once: true,
                    }
                }
            );
        });
    }, []);

    return (
        <div className={`flex flex-col items-center p-8 bg-gradient-to-b from-gray-900 to-black min-h-screen ${bungee.className}`}>
            <div
                ref={userCardRef}
                className="bg-white p-6 rounded-2xl shadow-2xl max-w-1xl mb-12"
            >
                <div className="flex items-center justify-center space-x-8">
                    <div className="text-center">
                        <div className="flex justify-center">
                            <img
                                src="https://upload.wikimedia.org/wikipedia/commons/0/05/Facebook_Logo_%282019%29.png"
                                alt="User Photo"
                                className="h-24 w-24 rounded-full mb-4 object-cover border-4 border-gradient-to-b from-gray-900 to-black"
                            />
                        </div>
                        <h3 className="text-xl font-bold text-gray-800">John Doe</h3>
                        <p className="text-sm text-gray-500">Full Stack Developer</p>
                        <p className="text-xs text-gray-400 italic">2021 - Present</p>
                        <p className="text-black">LOCAL STORAGE CONTENT: {localStorage.getItem('user_id')}</p>
                    </div>
                </div>
            </div>

            <div className="relative w-full max-w-4xl">

                <div
                    ref={lineRef}
                    className="absolute left-1/2 w-1 bg-gradient-to-b from-gray-600 via-gray-500 to-gray-400 -translate-x-1/2"
                ></div>


                {experiences.map((exp, index) => (
                    <div
                        key={exp.id}
                        ref={(el) => { experienceRefs.current[index] = el; }}
                        className={`flex items-center justify-between w-full my-8 ${index % 2 === 0 ? "flex-row-reverse" : "flex-row"}`}
                    >

                        <div className="w-6 h-6 bg-white rounded-full absolute left-1/2 transform -translate-x-1/2"></div>

                        <div className="bg-white p-6 rounded-2xl shadow-2xl w-5/12 flex flex-col items-center transform transition-transform duration-300 hover:scale-105">
                            <img src={exp.logo} alt={exp.company} className="h-14 mb-4 object-contain" />
                            <h3 className="text-xl font-bold text-gray-800">{exp.position}</h3>
                            <p className="text-sm text-gray-500">{exp.company}</p>
                            <p className="text-xs text-gray-400 italic">{exp.year}</p>
                            <p className="text-gray-700 mt-4 text-center">{exp.description}</p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
