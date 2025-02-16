import json

import requests
from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
import cloudinary
import cloudinary.uploader
from PyPDF2 import PdfReader
from supabase import create_client, Client
from flask_session import Session  # NEW: For persistent sessions
import uuid
from routes.linkedin import linkedin_bp
from routes.experiences import experiences_bp
from routes.roadmap import roadmap_bp


cloudinary.config(
    cloud_name = "dnc2tvpnn",
    api_key = "858953854634624",
    api_secret = "TU9T5WejPg4qe4LUniIqXQuFTN8",
    secure=True
)


app = Flask(__name__)
CORS(app)

COHERE_API_KEY = '86GngtGqjEgRBd8njQkXQ9fl4LcRWY9dhpwY1vvs'
COHERE_API_URL = 'https://api.cohere.ai/v1/generate'

SUPABASE_URL = 'https://voenczphlgojgihwbcwi.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZvZW5jenBobGdvamdpaHdiY3dpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk2MDM0NzgsImV4cCI6MjA1NTE3OTQ3OH0.WASlZSz_mSEyxlDZxDhUWZOdQp9JG0n7IHvE0Y8Mo6Y'
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


app.secret_key = 'WPL_AP1.vFgMgRskVtKfk2hP.RcATFw=='
CLIENT_ID = '778z82h4dtgrrz'
CLIENT_SECRET = 'WPL_AP1.vFgMgRskVtKfk2hP.RcATFw=='
REDIRECT_URI = 'http%3A%2F%2F127.0.0.1%3A5000%2Flinkedin-openid%2Fcallback'  # No spaces
BACKEND_REDIRECT_URI = 'http://127.0.0.1:5000/linkedin-openid/callback'  # Backend receives code
FRONTEND_REDIRECT_URI = 'http://localhost:3000/resumeupload'


@app.route('/parse-resume', methods=['POST'])
def parse_resume():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Empty file name'}), 400
    try:
        reader = PdfReader(file)
        extracted_text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                extracted_text += page_text + "\n"
        if not extracted_text.strip():
            return jsonify({'error': 'Could not extract text'}), 400

        prompt = f""" You are a resume parsing assistant. Extract the following information from the resume provided, 
        and include any projects under "work_experience".: - Full Name - Email - Phone Number - Summary - Work 
        Experience (for each: company name, title, dates, responsibilities) - Education (for each: institution, 
        degree, dates) - Skills

        Return ONLY the information in valid JSON format with keys: "name", "email", "phone", "summary", "work_experience", "education", "skills".

        Resume Text:
        {extracted_text}
        """
        headers = {
            'Authorization': f'Bearer {COHERE_API_KEY}',
            'Content-Type': 'application/json'
        }
        payload = {
            'model': 'command-xlarge-nightly',
            'prompt': prompt,
            'max_tokens': 1500,
            'temperature': 0.3
        }
        response = requests.post(COHERE_API_URL, json=payload, headers=headers)
        response_data = response.json()
        generated_text = response_data.get('generations', [{}])[0].get('text', '')
        try:
            if isinstance(generated_text, str) and generated_text.strip().startswith('{'):
                parsed_resume = json.loads(generated_text)
            else:
                raise json.JSONDecodeError("Invalid JSON", generated_text, 0)
        except json.JSONDecodeError:
            parsed_resume = generated_text

        return jsonify({'experiences': parsed_resume})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/getprofile/<id>', methods=['GET'])
def get_profile_information(id):
    user_response = supabase.table("user").select("*").eq("id", id).execute()
    if user_response.data:
        user = user_response.data[0]
        return jsonify(user), 200
    else:
        return jsonify({"error": "User not found"}), 404


app.register_blueprint(linkedin_bp, url_prefix='/')
app.register_blueprint(experiences_bp, url_prefix='/')
app.register_blueprint(roadmap_bp, url_prefix='/')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)