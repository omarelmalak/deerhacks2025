"use client";

import React, { useEffect } from "react";
import { fetchAccessToken } from "../../../utils/linkedinUtils.js";

const LinkedInCallback: React.FC = () => {
    useEffect(() => {
        const urlParams = new URLSearchParams(window.location.search);
        const code = urlParams.get('code');  // Extract the code from the URL

        if (code) {
            fetchAccessToken(code);  // Send code to fetch access token
        }
    }, []);

    return (
        <div>
            <h1>LinkedIn Callback</h1>
            <p>Fetching your profile...</p>
        </div>
    );
};

export default LinkedInCallback;
