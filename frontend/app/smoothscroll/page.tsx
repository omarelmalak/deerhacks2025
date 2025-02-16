"use client";
import { motion, useScroll, useTransform, useMotionTemplate } from 'framer-motion';
import { useRef } from 'react';

export const SmoothScroll = () => {
    return <div className="bg-zinc-950">
        <Hero />
        <div className="h-screen"></div> {/* Empty space to make room for scrolling */}
    </div>
}

const SECTION_HEIGHT = 1500; // Adjust based on content height

const Hero = () => {
    return (
        <div
            className="relative w-full"
            style={{ height: `calc(${SECTION_HEIGHT}px + 100vh)` }}
        >
            <CenterImage />
            <ParallaxCards />
            <div className="absolute bottom-0 left-0 right-0 h-96 bg-gradient-to-b from-zinc-950/0 to-zinc-950"></div>
        </div>
    );
}

const CenterImage = () => {
    const { scrollY } = useScroll();

    const opacity = useTransform(scrollY, [SECTION_HEIGHT, SECTION_HEIGHT + 500], [1, 0]);
    const backgroundSize = useTransform(scrollY, [0, SECTION_HEIGHT + 500], ["170%", "100%"]);

    return (
        <motion.div
            className="sticky top-0 h-screen w-full"
            style={{
                opacity,
                backgroundSize,
                backgroundImage: 'url(https://source.unsplash.com/random/1920x1080)', // Random image
                backgroundPosition: 'center',
                backgroundRepeat: 'no-repeat',
                backgroundAttachment: 'fixed',
            }}
        >
        </motion.div>
    )
}

const ParallaxCards = () => {
    return (
        <div className="relative z-10 mx-auto max-w-5xl px-4 pt-[100px]">
            <ParallaxCard
                start={-200}
                end={200}
                className="w-1/3"
                offset={-100}
            />
            <ParallaxCard
                start={-300}
                end={300}
                className="w-1/3"
                offset={0}
            />
            <ParallaxCard
                start={-600}
                end={400}
                className="w-1/3"
                offset={100}
            />
        </div>
    )
}

const ParallaxCard = ({
    className,
    start,
    end,
    offset,
}: {
    className?: string;
    start: number;
    end: number;
    offset: number;
}) => {
    const ref = useRef(null);
    const { scrollYProgress } = useScroll({
        target: ref,
        offset: [`${start}px end`, `end ${end * -1}px`]
    });

    const opacity = useTransform(scrollYProgress, [0.75, 1], [1, 0]);
    const y = useTransform(scrollYProgress, [0, 1], [start + offset, end + offset]);
    const scale = useTransform(scrollYProgress, [0.75, 1], [1, 0.85]);
    const transform = useMotionTemplate`translateY(${y}px) scale(${scale})`;

    return (
        <motion.div
            ref={ref}
            className="flex justify-center items-center space-x-4"
            style={{ opacity, transform }}
        >
            <div className={className}>
                <div className="bg-white p-6 rounded-2xl shadow-2xl flex flex-col items-center transform transition-transform duration-300 hover:scale-105">
                    <h3 className="font-bold text-xl">Card</h3>
                    <p className="text-sm text-gray-500">Company Name</p>
                    <p className="text-xs text-gray-400 italic">2025</p>
                    <p className="text-gray-700 mt-4 text-center">Some content for the card goes here!</p>
                </div>
            </div>
        </motion.div>
    );
}
