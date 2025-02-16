"use client";

import { useCallback } from "react";
import { Engine } from "@tsparticles/engine"; // ✅ Correct Engine import
import { loadFull } from "@tsparticles/full"; // ✅ Use the correct tsparticles package
import Particles from "react-particles";

const ParticlesBackground: React.FC = () => {
    const particlesInit = useCallback(async (engine: Engine) => {
        await loadFull(engine);
    }, []);

    return (
        <Particles
            id="tsparticles"
            init={particlesInit}
            options={{
                fullScreen: { enable: true },
                particles: {
                    number: { value: 100 },
                    move: {
                        direction: "right",
                        speed: 0.3,
                    },
                    size: { value: 1 },
                    opacity: { value: 0.8 },
                    line_linked: { enable: false },
                },
            }}
        />
    );
};

export default ParticlesBackground;
