import requests
from flask import Blueprint, request, jsonify, redirect

linkedin_bp = Blueprint('linkedin_bp', __name__)

@linkedin_bp.route('/linkedin-openid/callback')
def linkedin_callback():
    from app import supabase, CLIENT_ID, CLIENT_SECRET, BACKEND_REDIRECT_URI, FRONTEND_REDIRECT_URI

    code = request.args.get('code')
    if not code:
        return jsonify({"error": "No authorization code"}), 400
    token_url = 'https://www.linkedin.com/oauth/v2/accessToken'
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': BACKEND_REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    response = requests.post(token_url, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    if response.status_code == 200:
        access_token = response.json().get('access_token')
        profile_url = 'https://api.linkedin.com/v2/userinfo'
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(profile_url, headers=headers)
        if response.status_code == 200:
            profile_data = response.json()
        else:
            return jsonify({"error": "Failed to fetch profile"}), 500

        first_name = profile_data.get("given_name", "Unknown")
        last_name = profile_data.get("family_name", "Unknown")
        email = profile_data.get("email", "Unknown email")
        profile_picture = profile_data.get("picture", "https://upload.wikimedia.org/wikipedia/commons/a/ac/Default_pfp.jpg")

        user_response = supabase.table("user").select("*").eq("email", email).execute()
        if user_response.data:
            user_id = user_response.data[0].get("id")
        else:
            new_user = {
                "current_access_token": access_token,
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "profile_picture": profile_picture
            }
            supabase.table("user").insert([new_user]).execute()
            response = supabase.table("user").select("*").eq("email", email).execute()
            user_id = response.data[0].get("id")

        return redirect(f"{FRONTEND_REDIRECT_URI}?success={user_id}")
    else:
        return redirect(f"{FRONTEND_REDIRECT_URI}?error=failed_to_authenticate")
