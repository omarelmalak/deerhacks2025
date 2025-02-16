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


cloudinary.config(
    cloud_name = "dnc2tvpnn",
    api_key = "858953854634624",
    api_secret = "TU9T5WejPg4qe4LUniIqXQuFTN8",
    secure=True
)


app = Flask(__name__)
CORS(app)

COHERE_API_KEY = 'mwsy5HzGiJGheLAxKNObW529C9deFV6RhbIF7RGU'
COHERE_API_URL = 'https://api.cohere.ai/v1/generate'

API_KEY = 'iBSdCFmG4HjCwYhtcNHUR913W3bBFVaw'
URL_ENDPOINT = 'https://api.apilayer.com/resume_parser/url'

SUPABASE_URL = 'https://voenczphlgojgihwbcwi.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZvZW5jenBobGdvamdpaHdiY3dpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk2MDM0NzgsImV4cCI6MjA1NTE3OTQ3OH0.WASlZSz_mSEyxlDZxDhUWZOdQp9JG0n7IHvE0Y8Mo6Y'
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


app.secret_key = 'WPL_AP1.vFgMgRskVtKfk2hP.RcATFw=='  # Keep this safe
CLIENT_ID = '778z82h4dtgrrz'
CLIENT_SECRET = 'WPL_AP1.vFgMgRskVtKfk2hP.RcATFw=='
REDIRECT_URI = 'http%3A%2F%2F127.0.0.1%3A5000%2Flinkedin-openid%2Fcallback'  # No spaces
BACKEND_REDIRECT_URI = 'http://127.0.0.1:5000/linkedin-openid/callback'  # Backend receives code
FRONTEND_REDIRECT_URI = 'http://localhost:3000/'  # Where the user will go after login

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
    print("HERE")
    print(data)
    response = requests.post(token_url, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    if response.status_code == 200:
        access_token = response.json().get('access_token')
        print("ACCESS TOKEN")
        print(access_token)

        # LinkedIn API URL to get the user's profile
        profile_url = 'https://api.linkedin.com/v2/userinfo'

        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        # Make the request to LinkedIn API to get the user profile
        response = requests.get(profile_url, headers=headers)

        if response.status_code == 200:
            profile_data = response.json()  # The user's profile data
            print("PROFILE DATA JSON OUTPUT:")
            print(profile_data)
        else:
            return jsonify({"error": "Failed to fetch profile data", "details": response.json()}), 500

        first_name = profile_data.get("given_name", "Unknown first name")
        last_name = profile_data.get("family_name", "Unknown last name")
        email = profile_data.get("email", "Unknown email")
        profile_picture = profile_data.get("picture", "https://upload.wikimedia.org/wikipedia/commons/a/ac/Default_pfp.jpg")

        # IF THE EMAIL EXISTS, WE NEED TO JUST QUERY THAT RECORD
        response = supabase.table("user").select("*").eq("email", email).execute()

        if response.data:
            user_id = response.data[0].get("id")
        else:
            # IF IT DOESN'T EXIST, CREATE IT
            user_data = {
                "current_access_token": access_token,
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "profile_picture": profile_picture
            }
            # Assuming your table is named "users" with columns id, created_at, access_token
            supabase.table("user").insert([user_data]).execute()
            response = supabase.table("user").select("*").eq("email", email).execute()
            user_id = response.data[0].get("id")

        # Redirect user to frontend after login
        return redirect(f"{FRONTEND_REDIRECT_URI}?success={user_id}")
    else:
        return redirect(f"{FRONTEND_REDIRECT_URI}?error=failed_to_authenticate")

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
            return jsonify({'error': 'Could not extract text from the resume'}), 400


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
                raise json.JSONDecodeError("Invalid JSON format", generated_text, 0)
        except json.JSONDecodeError:
            parsed_resume = generated_text



        return jsonify({'experiences': parsed_resume})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/generate-roadmap', methods=['POST'])
def generate_roadmap():
    data = request.json
    experiences = data.get('experiences', [])

    user_goal_company = data.get('desiredCompany')
    user_goal_role = data.get('desiredRole')

    user_id = data.get('user_id')

    if not experiences:
        return jsonify({'error': 'No experiences provided'}), 400

    phase1_role = "Software Engineering Intern (Backend or Cloud)"
    phase1_companies = ["Shopify", "Stripe", "Twilio"]
    phase1_rationales = ["You should work at Shopify because ..... ", "Stripe will help elevate you by....", "Twilio is a good fit because...."]

    phase2_role = "Software Engineer (Backend/Cloud)"
    phase2_companies = ["AWS", "Microsoft", "Meta"]
    phase2_rationales = ["You should work at AWS because ..... ", "Microsoft will help elevate you by....", "Meta is a good fit because...."]


    phase3_role = "Software Engineering Intern (Machine Learning or Cloud Infrastructure)"
    phase3_companies = ["Google Summer of Code", "Waymo", "DeepMind"]
    phase3_rationales = ["You should work at Google Summer of Code because ..... ", "Waymo will help elevate you by....", "DeepMind is a good fit because...."]


    phase4_role = "Software Engineering Intern"
    phase4_companies = ["Google"]
    phase4_rationales = ["This is the end goal!"]


    roadmap_json = f"""
    {{
      "roadmap": [
        {{
          "start_date": "October 2023",
          "end_date": "January 2025",
          "position": "{phase1_role}",
          "companies": {phase1_companies},
          "company_rationale": {phase1_rationales}
        }},
        {{
          "start_date": "February 2025",
          "end_date": "October 2026",
          "position": "{phase2_role}",
          "companies": {phase2_companies},
          "company_rationale": {phase2_rationales}
        }},
        {{
          "start_date": "November 2026"
          "end_date": "January 2028",
          "position": "{phase3_role}",
          "companies": {phase3_companies},
          "company_rationale": {phase3_rationales}
        }},
        {{
          "start_date": "February 2028",
          "position": "{phase4_role}",
          "companies": {phase4_companies},
          "company_rationale": {phase4_rationales}
        }}
      ]
    }}
    """

    amazon_company = "Amazon"
    amazon_position = "Backend Developer Intern"
    amazon_start_date = "May 2022"
    amazon_end_date = "August 2022"
    amazon_summary = "Built RESTful APIs using Node.js and optimized database queries with PostgreSQL."

    meta_company = "Meta"
    meta_position = "Software Engineering Intern"
    meta_start_date = "June 2023"
    meta_end_date = "September 2023"
    meta_summary = "Developed a social graph analysis tool using Python and GraphQL."

    cleaned_experiences_json = f"""
    {{
      "cleaned_experiences": [
        {{
          "company": "{amazon_company}",
          "position": "{amazon_position}",
          "start_date": "{amazon_start_date}",
          "end_date": "{amazon_end_date}"
          "summary": "{amazon_summary}"
        }},
        {{
          "company": "{meta_company}",
          "position": "{meta_position}",
          "start_date": "{meta_start_date}",
          "end_date": "{meta_end_date}"
          "summary": "{meta_summary}"
        }}
      ]
    }}
    """

    # user_goal_company = "Google"
    # user_goal_role = "Chief Technical Officer"


    prompt = f""" You are a career advisor. Below are professional experiences. First, clean and summarize these 
    experiences. Then, generate a career roadmap from my current position to the role of {user_goal_role} at 
    {user_goal_company}. This roadmap should be based on my previous experiences. Structure the roadmap into clear 
    phases, each showing a career step with company name and that stuff. Make it short and clear. "career_roadmap" 
    should contain the companies (OTHER THAN THE ONES I ALREADY HAVE) that I should aim to work at to land an 
    {user_goal_role} at {user_goal_company}. The phases and timelines should start realistic. The timeline (start and end dates) should 
    be different depending on the goal role and company. For example, you can't expect me to get an Apple internship 
    right away if I have 0 internship experience. You also can't expect me to get a CTO Position within 3 years if I 
    have 0 previous experience. However, my career should only go up (i.e. I should not go from intern to full time and back
    to intern) The final entry should just have a start date and the end date should be "present" 
    because that should be the final goal.


    Experiences:
    {experiences}

    Return ONLY the information in valid JSON format with ONLY keys: "cleaned_experiences" and "career_roadmap". Do 
    not put a "roadmap" key within "career_roadmap". Also do not put a "cleaned_experiences" key within 
    "cleaned_experiences" This is an example of what the keys should look like. However, the actual content is 
    different based on what I just told you
    
    "cleaned_experiences": {cleaned_experiences_json},
    "career_roadmap" {roadmap_json}
    

    """

    headers = {
        'Authorization': f'Bearer {COHERE_API_KEY}',
        'Content-Type': 'application/json'
    }

    payload = {
        'model': 'command-xlarge-nightly',
        'prompt': prompt,
        'max_tokens': 4000,
        'temperature': 0.7
    }
    try:
        response = requests.post(COHERE_API_URL, json=payload, headers=headers)

        response_data = response.json()
        generated_text = response_data.get('generations', [{}])[0].get('text', '')


        parsed_response = json.loads(generated_text)
        cleaned_experiences = parsed_response.get('cleaned_experiences', [])
        career_roadmap = parsed_response.get('career_roadmap', [])


        json_data = jsonify({'cleaned_experiences': cleaned_experiences, 'career_roadmap': career_roadmap})

        as_dict = json_data.get_json()


        print("here")
        for cleaned_experience in as_dict["cleaned_experiences"]:
            print("here now")
            position = cleaned_experience.get("position", "Unknown Position")
            print(position)
            start_date = cleaned_experience.get("start_date", "Unknown Start Date")
            print(start_date)
            end_date = cleaned_experience.get("end_date", "Present")  # Set None if missing
            print(end_date)

            # Process company-rationale mapping safely
            company = cleaned_experience.get("company", "Unknown Company")
            print(company)
            summary = cleaned_experience.get("summary", "Empty Summary")
            print(summary)

            experience_data = {
                "company": company,
                "position": position,
                "start_date": start_date,
                "end_date": end_date,  # Set to NULL if not available
                "summary": summary,  # Store rationale as summary
                "in_resume": True  # Set to True for all
            }

            print(experience_data)

            response = supabase.table("experience").insert([experience_data]).execute()




        print("here")
        for roadmap in as_dict["career_roadmap"]:
            id = uuid.uuid4()
            print("here now")
            position = roadmap.get("position", "Unknown Position")
            print(position)
            start_date = roadmap.get("start_date", "Unknown Start Date")
            print(start_date)
            end_date = roadmap.get("end_date", "Present")  # Set None if missing
            print(end_date)

            # Process company-rationale mapping safely
            companies = roadmap.get("companies", [])
            print(companies)
            rationales = roadmap.get("company_rationale", [])
            print(rationales)

            for i in range(len(companies)):
                print(companies[i])
                print(rationales[i])
                experience_data = {
                    "company": companies[i],
                    "position": position,
                    "start_date": start_date,
                    "end_date": end_date,  # Set to NULL if not available
                    "summary": rationales[i],  # Store rationale as summary
                    "in_resume": False,
                    "roadmap_id": id 
                }

                response = supabase.table("experience").select("*").execute()

                print(experience_data)

                response = supabase.table("experience").insert([experience_data]).execute()

                response = (
                    supabase.table("user")
                    .update({
                        "roadmap_ids": supabase.sql("array_append(roadmap_ids, %s)", id)
                    })
                    .eq("id", user_id)
                    .execute()
                )



        return json_data
    except (json.JSONDecodeError, Exception) as e:
        return jsonify({'error': f'Parsing error: {str(e)}', 'raw_output': generated_text}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
