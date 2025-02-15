"use client";

import React from "react";

const LinkedInLoginButton: React.FC = () => {
    const clientId = '778z82h4dtgrrz';
    const redirectUri = 'http%3A%2F%2F127.0.0.1%3A5000%2Flinkedin-openid%2Fcallback'; // URL-encoded redirect URI
    const scope = 'openid%20profile%20email';

    const linkedInUrl = `https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=778z82h4dtgrrz&redirect_uri=http%3A%2F%2F127.0.0.1%3A5000%2Flinkedin-openid%2Fcallback&scope=openid%20profile%20email`;

    const getProfile = async () => {
        const response = await fetch("http://127.0.0.1:5000/linkedin-openid/profile", {
            credentials: "include",
        })
        const data = response.json();
        console.log(data);
    }

    return (
        <div>
            <a href={linkedInUrl}>
                <button>Login with LinkedIn</button>
            </a>
            <button onClick={getProfile}>
                Click here to log info
            </button>
        </div>
    );
};

export default LinkedInLoginButton;
