from flask import Flask, request, jsonify, session, redirect
import requests
from flask_cors import CORS
from flask_session import Session  # NEW: For persistent sessions
import redis

from supabase import create_client, Client

# Supabase URL and API Key
SUPABASE_URL = 'https://voenczphlgojgihwbcwi.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZvZW5jenBobGdvamdpaHdiY3dpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk2MDM0NzgsImV4cCI6MjA1NTE3OTQ3OH0.WASlZSz_mSEyxlDZxDhUWZOdQp9JG0n7IHvE0Y8Mo6Y'

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# http://127.0.0.1:5000/linkedin-openid/callback
app = Flask(__name__)
print(Session)



app.config['SECRET_KEY'] = 'WPL_AP1.vFgMgRskVtKfk2hP.RcATFw=='
app.config['SESSION_TYPE'] = 'redis'  # Use Redis for session storage
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_REDIS'] = redis.StrictRedis(host='localhost', port=6379, db=0)
Session(app)  # Initialize Flask-Session

app.secret_key = 'WPL_AP1.vFgMgRskVtKfk2hP.RcATFw=='  # Keep this safe
CLIENT_ID = '778z82h4dtgrrz'
CLIENT_SECRET = 'WPL_AP1.vFgMgRskVtKfk2hP.RcATFw=='
REDIRECT_URI = 'http%3A%2F%2F127.0.0.1%3A5000%2Flinkedin-openid%2Fcallback'  # No spaces
BACKEND_REDIRECT_URI = 'http://127.0.0.1:5000/linkedin-openid/callback'  # Backend receives code
FRONTEND_REDIRECT_URI = 'http://localhost:3000/'  # Where the user will go after login

CORS(app, origins='http://localhost:3000', supports_credentials=True)  # Make sure frontend is allowed

@app.route('/linkedin-openid/callback')
def linkedin_callback():
    code = request.args.get('code')
    print(code)
    if not code:
        return jsonify({"error": "No authorization code provided"}), 400

    token_url = 'https://www.linkedin.com/oauth/v2/accessToken'
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': 'http://127.0.0.1:5000/linkedin-openid/callback',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    print(data)
    response = requests.post(token_url, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    if response.status_code == 200:
        access_token = response.json().get('access_token')
        session['access_token'] = access_token  # Store in session
        print(f"Stored access token in session: {session.get('access_token')}")  # Debug print

        # Now store access token in Supabase
        user_data = {
            "access_token": access_token
        }
        # Assuming your table is named "users" with columns id, created_at, access_token
        supabase.table("User").insert([user_data]).execute()

        # Redirect user to frontend after login
        return redirect(f"{FRONTEND_REDIRECT_URI}?success=true")
    else:
        return redirect(f"{FRONTEND_REDIRECT_URI}?error=failed_to_authenticate")

@app.route('/linkedin-openid/token')
def get_access_token():
    access_token = session.get('access_token')
    if not access_token:
        return jsonify({"error": "No access token found"}), 400
    return jsonify({"access_token": access_token})

@app.route('/linkedin-openid/profile')
def linkedin_profile():
    print("HERE")
    access_token = session.get('access_token')
    print(access_token)
    if not access_token:
        return jsonify({"error": "No access token found"}), 400

    # LinkedIn API URL to get the user's profile
    profile_url = 'https://api.linkedin.com/v2/me'

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    # Make the request to LinkedIn API to get the user profile
    response = requests.get(profile_url, headers=headers)

    if response.status_code == 200:
        profile_data = response.json()  # The user's profile data
        return jsonify(profile_data)    # Return the profile data as a response
    else:
        return jsonify({"error": "Failed to fetch profile data", "details": response.json()}), 500



if __name__ == '__main__':
    app.run(debug=True)


