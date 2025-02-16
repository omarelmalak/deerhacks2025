"use client";
import {
  motion,
  useScroll,
  useTransform,
  useMotionTemplate,
} from "framer-motion";
import { useRef, useState, useEffect, FormEvent } from "react";
import { Poppins } from "next/font/google";
import axios from "axios";
import { redirect } from "next/navigation";

interface Experience {
  id: number;
  company: string;
  position: string;
  start_date: string;
  end_date: string;
  summary: string;
  in_resume: boolean;
  roadmap_id?: number;
  user_id?: number;
}

const poppins = Poppins({
  subsets: ["latin"],
  weight: ["400"],
});

// const mockExperiences: Experience[] = [
//     {
//         id: 1,
//         company: "TechCorp",
//         position: "Software Engineer",
//         logo: "https://example.com/logo1.png",
//         description: "Developing innovative software solutions for the financial sector.",
//         start_date: "2021-01-01",
//         end_date: "2022-12-31",
//         summary: "Led the development of key features in the company's core product, improving system performance by 25%.",
//         in_resume: true,
//     },
//     {
//         id: 2,
//         company: "InnovateX",
//         position: "Frontend Developer",
//         logo: "https://example.com/logo2.png",
//         description: "Building user-friendly web applications with modern JavaScript frameworks.",
//         start_date: "2020-06-01",
//         end_date: "2021-12-31",
//         summary: "Worked closely with UX/UI designers to create seamless user interfaces, increasing user engagement by 30%.",
//         in_resume: true,
//     },
//     {
//         id: 3,
//         company: "DevSolutions",
//         position: "Junior Backend Developer",
//         logo: "https://example.com/logo3.png",
//         description: "Collaborated on backend services for various e-commerce platforms.",
//         start_date: "2019-03-01",
//         end_date: "2020-05-31",
//         summary: "Helped optimize database queries and APIs, which resulted in a 20% reduction in response times.",
//         in_resume: false,
//     },
//     {
//         id: 4,
//         company: "CreativeLabs",
//         position: "Intern - Full Stack Developer",
//         logo: "https://example.com/logo4.png",
//         description: "Assisted in both frontend and backend tasks for a variety of projects.",
//         start_date: "2018-06-01",
//         end_date: "2018-08-31",
//         summary: "Contributed to the development of an internal tool that streamlined communication between teams.",
//         in_resume: true,
//     },
//     {
//         id: 5,
//         company: "CreativeLabs",
//         position: "Intern - Full Stack Developer",
//         logo: "https://example.com/logo4.png",
//         description: "Assisted in both frontend and backend tasks for a variety of projects.",
//         start_date: "2018-06-01",
//         end_date: "2018-08-31",
//         summary: "Contributed to the development of an internal tool that streamlined communication between teams.",
//         in_resume: true,
//     },
//     {
//         id: 6,
//         company: "CreativeLabs",
//         position: "Intern - Full Stack Developer",
//         logo: "https://example.com/logo4.png",
//         description: "Assisted in both frontend and backend tasks for a variety of projects.",
//         start_date: "2018-06-01",
//         end_date: "2018-08-31",
//         summary: "Contributed to the development of an internal tool that streamlined communication between teams.",
//         in_resume: true,
//     },
// ];

type Roadmap = {
  id: number;
  title: string;
  companies: string[]; // Companies as a list
  duration: string;
  user_id: number;
};

export default function SmoothScroll() {
  const [experiences, setExperiences] = useState<Experience[]>([]);
  const [inputValue, setInputValue] = useState<string>("");
  const [roadmaps, setRoadmaps] = useState<Roadmap[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [showUploadSuccess, setShowUploadSuccess] = useState<boolean>(false);


  const userId = localStorage.getItem("user_id");

  const getUserExperiences = async () => {
    try {
      const userid = localStorage.getItem("user_id");
      const response = await fetch(
        `http://localhost:5000/get-current-experiences/${parseInt(
          localStorage.getItem("user_id") || "0"
        )}`
      );
      const data = await response.json();

      setExperiences(data.current_experiences);
    } catch (error) {
      console.error("Error retrieving user experiences:", error);
    }
    
  };

  useEffect(() => {
    console.log("Updated experiences state:", experiences);
  }, [experiences]);

  useEffect(() => {
    getUserExperiences();
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value);
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);

    try {

      const response = await axios.post(
        "http://127.0.0.1:5000/generate-roadmap",
        {
          userPrompt: inputValue,
          user_id: parseInt(localStorage.getItem("user_id") || "0"),
        }
      );

      setRoadmaps(response.data.career_roadmap || []);
      setInputValue("");

    } catch (error) {
      console.error("Error generating roadmap:", error);
    }finally {
        setLoading(false);
        setShowUploadSuccess(true);
        redirect(`/roadmaps/${roadmaps[0]?.id}`);
    }
  };
  const fetchRoadmaps = async () => {
    try {
      const response = await axios.get(
        `http://127.0.0.1:5000/get-roadmaps/${userId}`
      );
      setRoadmaps(response.data?.roadmaps ?? []);
    } catch {
      console.error("Error generating roadmap:");
    }
  };

  useEffect(() => {
    fetchRoadmaps();
  }, []);

  return (
    <div
      className={`bg-gradient-to-b from-gray-900 to-black p-8 text-white ${poppins.className}`}
    >
      <Hero experiences={experiences} />
      <div className="h-screen"></div>

      {/* Text field and submit form */}
      <div className="mt-8">
        <form
          onSubmit={(e) => handleSubmit(e)}
          className="flex flex-col items-center"
        >
          <input
            type="text"
            value={inputValue}
            onChange={handleInputChange}
            className="p-4 w-3/4 md:w-1/2 text-lg rounded-lg bg-gray-800 border border-gray-600 focus:outline-none focus:ring-2 focus:ring-orange-500 text-white"
            placeholder="I want to work at Google as a Software Engineer"
          />
          <button
            type="submit"
            className="mt-4 px-6 py-3 text-lg font-bold text-white bg-gradient-to-r from-orange-500 to-red-800 rounded-lg hover:bg-gradient-to-l focus:ring-2 focus:ring-orange-500"
          >
            Submit
          </button>
          {loading && (
                <div className="mt-6 text-center">
                    <div className="spinner-border text-blue-500 animate-spin inline-block w-8 h-8 border-4 border-t-transparent border-solid rounded-full"></div>
                    <p className="mt-4 text-neutral-400">Generating roadmap...</p>
                </div>
            )}

        </form>
        <div className="flex overflow-x-auto space-x-6 p-4">
        {roadmaps.length > 0 ? (
          roadmaps.map((roadmap) => (
            <a href={`/roadmaps/${roadmap.id}`} key={roadmap.id}>
              <motion.div
                key={roadmap.id}
                whileHover={{ scale: 1.05 }}
                className="flex-shrink-0 w-80 bg-white border-2 border-red-300 rounded-xl shadow-xl p-5 text-center"
              >
                <h3 className="text-xl font-extrabold text-gray-800 mb-3">
                  {roadmap.title}
                </h3>
                <div className="mb-3">
                  <p className="text-gray-500 font-semibold">
                    Featured Companies:
                  </p>
                  {roadmap.companies.slice(0, 2).map((company, idx) => (
                    <p key={idx} className="text-gray-600 text-sm">
                      {company}
                    </p>
                  ))}
                  
                </div>
                {roadmap.duration && (
                  <div className="text-gray-500 text-sm font-medium mb-2">
                    Duration: {roadmap.duration}
                  </div>
                )}
              </motion.div>
            </a>
          ))
        ) : (
          <div className="text-center text-gray-400 font-medium">
            No roadmaps found.
          </div>
        )}
      </div>
      </div>
     
    </div>
  );
}

const SECTION_HEIGHT = 1500;

const Hero = ({ experiences }: { experiences: Experience[] }) => {
  return (
    <div
      className="relative w-full"
      style={{ height: `calc(${SECTION_HEIGHT}px + 100vh)` }}
    >
      <CenterCard />
      <ParallaxCards experiences={experiences} />
      <div className="absolute bottom-0 left-0 right-0 h-96 bg-gradient-to-b from-zinc-950/0 to-zinc-950"></div>
    </div>
  );
};

const CenterCard = () => {
  const [firstName, setFirstName] = useState<string>("");
  const [lastName, setLastName] = useState<string>("");
  const [profilePicture, setProfilePicture] = useState<string>("");
  const [experiences, setExperiences] = useState<Experience[]>([]);
  const [index, setIndex] = useState(0);

  useEffect(() => {
    getProfileInformation();
    getUserExperiences();
  }, []);

  useEffect(() => {
    if (!experiences || experiences.length === 0) return;

    const interval = setInterval(() => {
      setIndex((prevIndex) => (prevIndex + 1) % experiences.length);
    }, 1500); // Change every 1.5 seconds

    return () => clearInterval(interval); // Cleanup on unmount
  }, [experiences]);

  const getProfileInformation = async () => {
    try {
      const userid = localStorage.getItem("user_id");
      const response = await fetch(
        `http://localhost:5000/getprofile/${Number(userid)}`
      );
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
      const userid = localStorage.getItem("user_id");
      const response = await fetch(
        `http://localhost:5000/get-current-experiences/${parseInt(
          localStorage.getItem("user_id") || "0"
        )}`
      );
      const data = await response.json();

      setExperiences(data.current_experiences);

      console.log("EXPERIENCES", experiences);
    } catch (error) {
      console.error("Error retrieving user experiences:", error);
    }
  };

  const { scrollY } = useScroll();

  const opacity = useTransform(
    scrollY,
    [SECTION_HEIGHT, SECTION_HEIGHT + 500],
    [1, 0]
  );
  const backgroundSize = useTransform(
    scrollY,
    [0, SECTION_HEIGHT + 500],
    ["170%", "100%"]
  );

  return (
    <motion.div
      className="sticky top-0 min-h-screen w-full flex justify-center items-center"
      style={{
        opacity,
        backgroundSize,
      }}
    >
      <div className="flex flex-col items-center text-center">

        <img
          src={profilePicture}
          alt="Profile"
          className="w-32 h-32 rounded-full border-4 border-gray-300 mb-4"
        />

        {/* Name with Large, Bold Styling */}
        <h2 className="text-4xl sm:text-6xl lg:text-7xl font-bold tracking-wide leading-tight">
          {firstName} {lastName}
        </h2>

        {/* Rotating Position with Smooth Transition */}
        <p className="text-4xl sm:text-6xl lg:text-7xl font-bold tracking-wide leading-tight mt-4">
          <motion.span
            key={index} // Forces animation on change
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.6, ease: "easeInOut" }}
            className="block bg-gradient-to-r from-orange-500 to-red-800 text-transparent bg-clip-text"
          >
            {experiences && experiences[index]?.position}
          </motion.span>
        </p>
      </div>
    </motion.div>
  );
};

const ParallaxCards = ({ experiences }: { experiences: Experience[] }) => {
  return (
    <div className="relative mx-auto max-w-10xl px-4 pt-[200px] flex gap-16 justify-between">
      {experiences &&
        experiences.map((experience, index) => {
          // Generate random start and end values for the parallax effect
          const randomStart = Math.floor(Math.random() * 400) - 200; // Random number between -200 and 200
          const randomEnd = Math.floor(Math.random() * 500) - 200; // Random number between -200 and 500

          return (
            <ParallaxCard
              key={experience.id}
              start={randomStart}
              end={randomEnd}
              alt={`Card ${index + 1}`}
              className={`w-full md:w-1/3 lg:w-1/4`}
              experience={experience}
            />
          );
        })}
    </div>
  );
};

const ParallaxCard = ({
  className,
  alt,
  start,
  end,
  experience,
}: {
  className?: string;
  alt: string;
  start: number;
  end: number;
  experience: Experience;
}) => {
  const ref = useRef(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: [`${start}px end`, `end ${end * -1}px`],
  });

  const opacity = useTransform(scrollYProgress, [0.75, 1], [1, 0]);
  const y = useTransform(scrollYProgress, [0, 1], [start, end]);
  const scale = useTransform(scrollYProgress, [0.75, 1], [1, 0.85]);
  const transform = useMotionTemplate`translateY(${y}px) scale(${scale})`;

  return (
    <motion.div
      className={`${className} bg-white p-6 rounded-2xl shadow-2xl flex flex-col items-center max-w-[17vw]`}
      style={{ opacity, transform }}
      ref={ref}
    >
      <div className="h-14 bg-green-500 mb-4 rounded-full object-contain"></div>
      <h3 className="text-xl font-bold text-gray-800 text-center">
        {experience.position}
      </h3>
      <p className="text-sm text-gray-500">{experience.company}</p>
      <p className="text-xs text-gray-400 italic">
        {experience.start_date} - {experience.end_date}
      </p>
      <p className="text-gray-600 text-sm mt-2 text-center">
        {experience.summary}
      </p>
    </motion.div>
  );
};
