"use client";
import { motion, useScroll, useTransform, useMotionTemplate } from 'framer-motion';
import { useRef, useState, useEffect } from 'react';

interface Experience {
    id: number;
    company: string;
    position: string;
    logo: string;
    description: string;
    start_date: string;
    end_date: string;
    summary: string;
    in_resume: boolean;
}

const mockExperiences: Experience[] = [
    {
        id: 1,
        company: "TechCorp",
        position: "Software Engineer",
        logo: "https://example.com/logo1.png",
        description: "Developing innovative software solutions for the financial sector.",
        start_date: "2021-01-01",
        end_date: "2022-12-31",
        summary: "Led the development of key features in the company's core product, improving system performance by 25%.",
        in_resume: true,
    },
    {
        id: 2,
        company: "InnovateX",
        position: "Frontend Developer",
        logo: "https://example.com/logo2.png",
        description: "Building user-friendly web applications with modern JavaScript frameworks.",
        start_date: "2020-06-01",
        end_date: "2021-12-31",
        summary: "Worked closely with UX/UI designers to create seamless user interfaces, increasing user engagement by 30%.",
        in_resume: true,
    },
    {
        id: 3,
        company: "DevSolutions",
        position: "Junior Backend Developer",
        logo: "https://example.com/logo3.png",
        description: "Collaborated on backend services for various e-commerce platforms.",
        start_date: "2019-03-01",
        end_date: "2020-05-31",
        summary: "Helped optimize database queries and APIs, which resulted in a 20% reduction in response times.",
        in_resume: false,
    },
    {
        id: 4,
        company: "CreativeLabs",
        position: "Intern - Full Stack Developer",
        logo: "https://example.com/logo4.png",
        description: "Assisted in both frontend and backend tasks for a variety of projects.",
        start_date: "2018-06-01",
        end_date: "2018-08-31",
        summary: "Contributed to the development of an internal tool that streamlined communication between teams.",
        in_resume: true,
    },
    {
        id: 5,
        company: "CreativeLabs",
        position: "Intern - Full Stack Developer",
        logo: "https://example.com/logo4.png",
        description: "Assisted in both frontend and backend tasks for a variety of projects.",
        start_date: "2018-06-01",
        end_date: "2018-08-31",
        summary: "Contributed to the development of an internal tool that streamlined communication between teams.",
        in_resume: true,
    },
    {
        id: 6,
        company: "CreativeLabs",
        position: "Intern - Full Stack Developer",
        logo: "https://example.com/logo4.png",
        description: "Assisted in both frontend and backend tasks for a variety of projects.",
        start_date: "2018-06-01",
        end_date: "2018-08-31",
        summary: "Contributed to the development of an internal tool that streamlined communication between teams.",
        in_resume: true,
    },
];


export default function SmoothScroll() {
    const [firstName, setFirstName] = useState<string>("");
    const [lastName, setLastName] = useState<string>("");
    const [profilePicture, setProfilePicture] = useState<string>("");

    const getProfileInformation = async () => {
        try {
            const userid = localStorage.getItem('user_id');
            const response = await fetch(`http://localhost:5000/getprofile/${Number(userid)}`);
            const data = await response.json();

            const { first_name, last_name, profile_picture } = data;

            setFirstName(first_name);
            setLastName(last_name);
            setProfilePicture(profile_picture);
        } catch (error) {
            console.error("Error retrieving user LinkedIn information:", error);
        }
    };

    const getUserExperiences = async () => {
        try {
            const userid = localStorage.getItem('user_id');
            const response = await fetch(`http://localhost:5000/get-cleaned-experiences/${Number(userid)}`);
            const data = await response.json();

            console.log(data);
        } catch (error) {
            console.error("Error retrieving user experiences:", error);
        }
    }

    useEffect(() => {
        getProfileInformation();
        getUserExperiences();
    }, []);

    return (
        <div className="bg-gradient-to-b from-gray-900 to-black p-8 text-white">
            {firstName && lastName && profilePicture && (
                <div className="absolute top-8 right-8 flex items-center space-x-3 px-4 py-2 rounded-full bg-gradient-to-b from-gray-900 to-black text-white shadow-md hover:shadow-xl hover:bg-gradient-to-r from-orange-500 to-red-800 transition-all ease-in-out duration-300 transform hover:scale-105">
                    <img src={profilePicture} alt="Profile" className="w-12 h-12 rounded-full border-2 border-white" />
                    <div>
                        <p className="font-semibold text-lg">{firstName} {lastName}</p>
                    </div>
                </div>
            )}
            <Hero />
            <div className="h-screen"></div>
        </div>
    );
}

const SECTION_HEIGHT = 1500;

const Hero = () => {
    return (
        <div className="relative w-full" style={{ height: `calc(${SECTION_HEIGHT}px + 100vh)` }}>
            <CenterCard />
            <ParallaxCards />
            <div className="absolute bottom-0 left-0 right-0 h-96 bg-gradient-to-b from-zinc-950/0 to-zinc-950"></div>
        </div>
    );
}

const CenterCard = () => {
    const { scrollY } = useScroll();

    const opacity = useTransform(scrollY, [SECTION_HEIGHT, SECTION_HEIGHT + 500], [1, 0]);
    const backgroundSize = useTransform(scrollY, [0, SECTION_HEIGHT + 500], ["170%", "100%"]);

    return (
        <motion.div
            className="sticky top-0 h-screen w-full flex justify-center items-center"
            style={{
                opacity,
                backgroundSize,
            }}
        >
            <div className="bg-white p-6 rounded-2xl shadow-2xl flex flex-col items-center w-5/12">
                <img
                    src={"https://randomuser.me/api/portraits/men/32.jpg"} // Replace with actual user image
                    alt="Profile"
                    className="w-24 h-24 rounded-full border-4 border-gray-300 mb-4"
                />
                <h2 className="text-2xl font-bold text-gray-800">Omar E</h2>
                <p className="text-sm text-gray-500">Software Developer at XYZ</p>
                <p className="text-xs text-gray-400 italic">Joined in 2023</p>
                <p className="text-gray-700 mt-4 text-center">Passionate about technology, innovation, and helping others achieve their best work.</p>
            </div>
        </motion.div>
    );
}

const ParallaxCards = () => {
    return (
        <div className="relative mx-auto max-w-10xl px-4 pt-[200px] flex gap-16 justify-between">
            {mockExperiences.map((experience, index) => {
                // Generate random start and end values for the parallax effect
                const randomStart = Math.floor(Math.random() * 400) - 200; // Random number between -200 and 200
                const randomEnd = Math.floor(Math.random() * 500) - 200; // Random number between -200 and 500

                return (
                    <ParallaxCard
                        key={experience.id}
                        start={randomStart}
                        end={randomEnd}
                        alt={`Card ${index + 1}`}
                        className={`w-full md:w-1/3 lg:w-1/4`} // Responsive width: full on small screens, 1/3 on medium, and 1/4 on large
                        experience={experience}
                    />
                );
            })}
        </div>
    );
}


const ParallaxCard = ({
    className,
    alt,
    start,
    end,
    experience
}: {
    className?: string;
    alt: string;
    start: number;
    end: number;
    experience: Experience
}) => {
    const ref = useRef(null);
    const { scrollYProgress } = useScroll({
        target: ref,
        offset: [`${start}px end`, `end ${end * -1}px`]
    });

    const opacity = useTransform(scrollYProgress, [0.75, 1], [1, 0]);
    const y = useTransform(scrollYProgress, [0, 1], [start, end]);
    const scale = useTransform(scrollYProgress, [0.75, 1], [1, 0.85]);
    const transform = useMotionTemplate`translateY(${y}px) scale(${scale})`;

    return (
        <motion.div
            className={`${className} bg-white p-6 rounded-2xl shadow-2xl flex flex-col items-center max-w-[15vw]`}
            style={{ opacity, transform }}
            ref={ref}
        >
            <div className="h-14 bg-green-500 mb-4 rounded-full object-contain"></div>
            <h3 className="text-xl font-bold text-gray-800">{experience.position}</h3>
            <p className="text-sm text-gray-500">{experience.company}</p>
            <p className="text-xs text-gray-400 italic">{experience.start_date} - {experience.end_date}</p>
            <p className="text-gray-600 text-sm mt-2 text-center">
                {experience.summary}
            </p>
        </motion.div>
    );
}


