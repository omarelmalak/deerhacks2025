"use client";

import React, { useEffect, useRef, useState, useLayoutEffect, FC } from "react";
import { gsap } from "gsap";
import { Bungee, Inter } from "next/font/google";
import ScrollTrigger from "gsap/ScrollTrigger";
import {
  useRouter,
  useSearchParams,
  usePathname,
  useParams,
} from "next/navigation";
import axios from "axios";
import { useSwipeable } from "react-swipeable";

gsap.registerPlugin(ScrollTrigger);

const bungee = Bungee({
  subsets: ["latin"],
  weight: ["400"],
});

const inter = Inter({
  subsets: ["latin"],
  weight: ["400", "600"],
});

interface Experience {
  id: number;
  company: string;
  position: string;
  description: string;
  start_date: string;
  end_date: string;
  summary: string;
  in_resume: boolean;
  user_id: number;
  roadmap_id?: number;
}

interface TimelineItem {
  type: "normal" | "concept";
  start_date: string;
  end_date: string;
  experiences: Experience[];
  experience?: Experience;
}

function formatDateRange(start: string, end: string) {
  return end === "Present" ? start : `${start} - ${end}`;
}

function buildTimeline(experiences: Experience[]): TimelineItem[] {
  const normalExps = experiences.filter((exp) => exp.in_resume);
  const conceptExps = experiences.filter((exp) => !exp.in_resume);
  const conceptMap: Record<string, Experience[]> = {};
  for (const exp of conceptExps) {
    const key = `${exp.start_date}-${exp.end_date}`;
    if (!conceptMap[key]) conceptMap[key] = [];
    conceptMap[key].push(exp);
  }
  const normalItems: TimelineItem[] = normalExps.map((exp) => ({
    type: "normal",
    start_date: exp.start_date,
    end_date: exp.end_date,
    experiences: [],
    experience: exp,
  }));
  const conceptItems: TimelineItem[] = Object.values(conceptMap).map(
    (group) => ({
      type: "concept",
      start_date: group[0].start_date,
      end_date: group[0].end_date,
      experiences: group,
    })
  );
  const merged = [...normalItems, ...conceptItems];
  merged.sort((a, b) => {
    const dateA = new Date(a.start_date).getTime();
    const dateB = new Date(b.start_date).getTime();
    return dateA - dateB;
  });
  return merged;
}

const SwipeableConceptCarousel: FC<{ experiences: Experience[] }> = ({
  experiences,
}) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const handlers = useSwipeable({
    onSwipedLeft: () =>
      setCurrentIndex((prev) =>
        prev === experiences.length - 1 ? 0 : prev + 1
      ),
    onSwipedRight: () =>
      setCurrentIndex((prev) =>
        prev === 0 ? experiences.length - 1 : prev - 1
      ),
    preventScrollOnSwipe: true,
    trackMouse: true,
  });
  const currentExp = experiences[currentIndex];
  return (
    <div
      {...handlers}
      className="relative bg-gradient-to-br from-blue-50 via-blue-100 to-blue-200 p-6 rounded-2xl shadow-2xl w-5/12 flex flex-col items-center border border-blue-300 transform transition-transform duration-300 hover:scale-105 hover:shadow-yellow-300/60"
    >
      <div className="absolute top-2 left-2 bg-blue-500 text-white text-[10px] font-bold px-2 py-0.5 uppercase rounded-full">
        Upcoming ({currentIndex + 1}/{experiences.length})
      </div>
      {/* <img
        src={currentExp.logo}
        alt={currentExp.company}
        className="h-14 mb-4 object-contain opacity-95"
      /> */}
      <h3 className="text-xl font-bold text-gray-800">{currentExp.position}</h3>
      <p className="text-sm text-gray-500">{currentExp.company}</p>
      <p className="text-xs text-gray-400 italic">
        {formatDateRange(currentExp.start_date, currentExp.end_date)}
      </p>
      {currentExp.description && (
        <p className="text-gray-600 text-sm mt-2 text-center">
          {currentExp.description}
        </p>
      )}
      {currentExp.summary && (
        <p className="text-gray-700 mt-4 text-center">{currentExp.summary}</p>
      )}
      <div className="flex justify-center mt-4 space-x-2">
        {experiences.map((_, idx) => (
          <button
            key={idx}
            onClick={() => setCurrentIndex(idx)}
            className={`w-2 h-2 rounded-full ${
              currentIndex === idx ? "bg-blue-500" : "bg-gray-300"
            }`}
          />
        ))}
      </div>
      <div className="flex justify-between absolute inset-y-1/2 w-full px-2">
        <button
          onClick={() =>
            setCurrentIndex(
              currentIndex === 0 ? experiences.length - 1 : currentIndex - 1
            )
          }
          className="px-1 py-0.5 bg-gray-200 rounded-full hover:bg-gray-300 text-sm"
        >
          {"<"}
        </button>
        <button
          onClick={() =>
            setCurrentIndex(
              currentIndex === experiences.length - 1 ? 0 : currentIndex + 1
            )
          }
          className="px-1 py-0.5 bg-gray-200 rounded-full hover:bg-gray-300 text-sm"
        >
          {">"}
        </button>
      </div>
      <style jsx>{`
        div::before {
          content: "";
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: linear-gradient(
            45deg,
            rgba(255, 255, 255, 0.08) 25%,
            rgba(0, 0, 0, 0) 25%,
            rgba(0, 0, 0, 0) 50%,
            rgba(255, 255, 255, 0.08) 50%,
            rgba(255, 255, 255, 0.08) 75%,
            rgba(0, 0, 0, 0) 75%,
            rgba(0, 0, 0, 0) 100%
          );
          background-size: 6px 6px;
          border-radius: 1rem;
          pointer-events: none;
          z-index: 0;
        }
        div:hover {
          box-shadow: 0px 0px 25px rgba(255, 215, 0, 0.5);
        }
      `}</style>
    </div>
  );
};

const ConceptCard: FC<{ experience: Experience }> = ({ experience }) => (
  <div className="relative bg-gradient-to-br from-blue-50 via-blue-100 to-blue-200 p-6 rounded-2xl shadow-2xl w-5/12 flex flex-col items-center border border-blue-300 transform transition-transform duration-300 hover:scale-105 hover:shadow-yellow-300/60">
    <div className="absolute top-2 left-2 bg-blue-500 text-white text-[10px] font-bold px-2 py-0.5 uppercase rounded-full">
      Upcoming
    </div>
    {/* <img
      src={experience.logo}
      alt={experience.company}
      className="h-14 mb-4 object-contain opacity-95"
    /> */}
    <h3 className="text-xl font-bold text-gray-800">{experience.position}</h3>
    <p className="text-sm text-gray-500">{experience.company}</p>
    <p className="text-xs text-gray-400 italic">
      {formatDateRange(experience.start_date, experience.end_date)}
    </p>
    {experience.description && (
      <p className="text-gray-600 text-sm mt-2 text-center">
        {experience.description}
      </p>
    )}
    {experience.summary && (
      <p className="text-gray-700 mt-4 text-center">{experience.summary}</p>
    )}
    <style jsx>{`
      div::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(
          45deg,
          rgba(255, 255, 255, 0.08) 25%,
          rgba(0, 0, 0, 0) 25%,
          rgba(0, 0, 0, 0) 50%,
          rgba(255, 255, 255, 0.08) 50%,
          rgba(255, 255, 255, 0.08) 75%,
          rgba(0, 0, 0, 0) 75%,
          rgba(0, 0, 0, 0) 100%
        );
        background-size: 6px 6px;
        border-radius: 1rem;
        pointer-events: none;
        z-index: 0;
      }
      div:hover {
        box-shadow: 0px 0px 25px rgba(255, 215, 0, 0.5);
      }
    `}</style>
  </div>
);

const NormalCard: FC<{ experience: Experience }> = ({ experience }) => (
  <div className="bg-white p-6 rounded-2xl shadow-2xl w-5/12 flex flex-col items-center transform transition-transform duration-300 hover:scale-105">
    {/* <img
      src={experience.logo}
      alt={experience.company}
      className="h-14 mb-4 object-contain"
    /> */}
    <h3 className="text-xl font-bold text-gray-800">{experience.position}</h3>
    <p className="text-sm text-gray-500">{experience.company}</p>
    <p className="text-xs text-gray-400 italic">
      {formatDateRange(experience.start_date, experience.end_date)}
    </p>
    {experience.description && (
      <p className="text-gray-600 text-sm mt-2 text-center">
        {experience.description}
      </p>
    )}
    {experience.summary && (
      <p className="text-gray-700 mt-4 text-center">{experience.summary}</p>
    )}
  </div>
);

export default function ExperienceTimeline() {
  const experienceRefs = useRef<HTMLDivElement[]>([]);
  const userCardRef = useRef<HTMLDivElement | null>(null);
  const lineRef = useRef<HTMLDivElement | null>(null);
  const [experiences, setExperiences] = useState<Experience[]>([]);
  const [roadmapExperiences, setRoadmapExperiences] = useState<Experience[]>(
    []
  );
  const [userRoadmaps, setUserRoadmaps] = useState([]);
  const [firstName, setFirstName] = useState<string>("");
  const [lastName, setLastName] = useState<string>("");
  const [profilePicture, setProfilePicture] = useState<string>("");
  const router = useRouter();
  const searchParams = useSearchParams();
  const success = searchParams.get("success");
  const timelineItems = buildTimeline(experiences);

  const pathname = usePathname();
  const segments = pathname.split("/").filter(Boolean);

  segments.splice(-1);

  const newPathname = "/" + segments.join("/");

  const { id } = useParams();
  const handleGetUserRoadmaps = async () => {
    try {
      const response = await axios.get(
        `http://127.0.0.1:5000/get-roadmaps/${success}`
      );
      setUserRoadmaps(response.data.roadmaps);
    } catch (error) {}
  };

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

  const handleGetRoadmapExperiences = async () => {
    try {
      const response = await axios.get(
        `http://127.0.0.1:5000/get-experiences/${id}`
      );
      const sortedExperiences: Experience[] = response.data.experiences.sort(
        (a: Experience, b: Experience) =>
          new Date(a.end_date).getTime() - new Date(b.end_date).getTime()
      );

      setRoadmapExperiences(sortedExperiences);
      setExperiences(sortedExperiences);

      console.log(roadmapExperiences);
    } catch (error) {}
  };

  if (success) {
    localStorage.setItem("user_id", success.toString());
  }

  useEffect(() => {
    if (success) {
      localStorage.setItem("user_id", success.toString());
    }
    handleGetRoadmapExperiences();
    getProfileInformation();

  }, []);

  useEffect(() => {
    console.log(experiences);

  }, [experiences]);

  useLayoutEffect(() => {
    gsap.registerPlugin(ScrollTrigger);
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
        },
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
        },
      }
    );
    const ctx = gsap.context(() => {
      experienceRefs.current.forEach((expRef) => {
        if (expRef) {
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
              },
            }
          );
        }
      });
    });
    return () => ctx.revert();
  }, [timelineItems]);

  return (
    <div
      className={`flex flex-col items-center p-8 bg-gradient-to-b from-gray-900 to-black min-h-screen ${bungee.className}`}
    >
      <div
        ref={userCardRef}
        className="bg-white p-6 rounded-2xl shadow-2xl max-w-1xl mb-12"
      >
        <div className="flex items-center justify-center space-x-8">
          <div className="text-center">
            <div className="flex justify-center">
              <img
                // src="https://upload.wikimedia.org/wikipedia/commons/0/05/Facebook_Logo_%282019%29.png"
                alt="User Photo"
                className="h-24 w-24 rounded-full mb-4 object-cover border-4 border-gradient-to-b from-gray-900 to-black"
              />
            </div>
            <h3 className="text-xl font-bold text-gray-800">{firstName} {lastName}</h3>
            <p className="text-sm text-gray-500">{experiences && experiences[0]?.position}</p>
            {/* <p className="text-xs text-gray-400 italic">2021 - Present</p> */}
            {/* <p className="text-black">
              LOCAL STORAGE CONTENT: {localStorage.getItem("user_id")}
            </p> */}
          </div>
        </div>
      </div>
      <div className="relative w-full max-w-4xl">
        <div
          ref={lineRef}
          className="absolute left-1/2 w-1 bg-gradient-to-b from-gray-600 via-gray-500 to-gray-400 -translate-x-1/2"
        />
        {timelineItems.map((item, index) => (
          <div
            key={index}
            ref={(el) => {
              if (el) experienceRefs.current[index] = el;
            }}
            className={`flex items-center justify-between w-full my-8 ${
              index % 2 === 0 ? "flex-row-reverse" : "flex-row"
            }`}
          >
            <div className="w-6 h-6 bg-white rounded-full absolute left-1/2 transform -translate-x-1/2" />
            {item.type === "normal" && item.experience ? (
              <NormalCard experience={item.experience} />
            ) : item.experiences.length > 1 ? (
              <SwipeableConceptCarousel experiences={item.experiences} />
            ) : (
              <ConceptCard experience={item.experiences[0]} />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
