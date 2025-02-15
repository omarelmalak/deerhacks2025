export const fetchAccessToken = async (code) => {
    // Send the authorization code to your backend to exchange it for an access token
    const response = await fetch('http://localhost:5000/linkedin/token', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code }),  // Send the code to the backend
    });

    const data = await response.json();

    if (data.access_token) {
        // Use the access token to fetch the LinkedIn profile
        const profileData = await fetchLinkedInProfile(data.access_token);
        console.log(profileData);
    } else {
        console.log('Error fetching access token');
    }
};

export const fetchLinkedInProfile = async (accessToken) => {
    const response = await fetch('https://api.linkedin.com/v2/me', {
        headers: {
            'Authorization': `Bearer ${accessToken}`,
        },
    });
    const data = await response.json();
    return data;
};
