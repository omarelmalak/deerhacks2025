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

SUPABASE_URL = 'https://voenczphlgojgihwbcwi.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZvZW5jenBobGdvamdpaHdiY3dpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk2MDM0NzgsImV4cCI6MjA1NTE3OTQ3OH0.WASlZSz_mSEyxlDZxDhUWZOdQp9JG0n7IHvE0Y8Mo6Y'
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


app.secret_key = 'WPL_AP1.vFgMgRskVtKfk2hP.RcATFw=='  # Keep this safe
CLIENT_ID = '778z82h4dtgrrz'
CLIENT_SECRET = 'WPL_AP1.vFgMgRskVtKfk2hP.RcATFw=='
REDIRECT_URI = 'http%3A%2F%2F127.0.0.1%3A5000%2Flinkedin-openid%2Fcallback'  # No spaces
BACKEND_REDIRECT_URI = 'http://127.0.0.1:5000/linkedin-openid/callback'  # Backend receives code
FRONTEND_REDIRECT_URI = 'http://localhost:3000/resumeupload'  # Where the user will go after login

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
    phase1_rationales = ["You should work at Shopify because ..... ", "Stripe will help elevate you by....",
                         "Twilio is a good fit because...."]
    phase1_company_logos = [
        "https://www.google.com/imgres?q=wikipedia%20shopify%20logo&imgurl=https%3A%2F%2Fupload.wikimedia.org%2Fwikipedia%2Fcommons%2Fthumb%2F0%2F0e%2FShopify_logo_2018.svg%2F290px-Shopify_logo_2018.svg.png&imgrefurl=https%3A%2F%2Fen.wikipedia.org%2Fwiki%2FShopify&docid=s1x6v2b8kCY-OM&tbnid=qfwIbjySppw6nM&vet=12ahUKEwj0tOeizseLAxU66skDHS54JsQQM3oECDgQAA..i&w=290&h=91&hcb=2&ved=2ahUKEwj0tOeizseLAxU66skDHS54JsQQM3oECDgQAA",
        "data:image/png;base64,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",
        "data:image/png;base64,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"]

    phase2_role = "Software Engineer (Backend/Cloud)"
    phase2_companies = ["AWS", "Microsoft", "Meta"]
    phase2_rationales = ["You should work at AWS because ..... ", "Microsoft will help elevate you by....",
                         "Meta is a good fit because...."]
    phase2_company_logos = [
        "https://www.google.com/imgres?q=wikipedia%20logo%20aws&imgurl=https%3A%2F%2Fupload.wikimedia.org%2Fwikipedia%2Fcommons%2F9%2F93%2FAmazon_Web_Services_Logo.svg&imgrefurl=https%3A%2F%2Fen.wikipedia.org%2Fwiki%2FAmazon_Web_Services&docid=JSgXJbxN-7t0-M&tbnid=FB3B89WhUh9TUM&vet=12ahUKEwiXnN65zseLAxUfMdAFHS8hAjEQM3oECBwQAA..i&w=800&h=479&hcb=2&ved=2ahUKEwiXnN65zseLAxUfMdAFHS8hAjEQM3oECBwQAA",
        "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAOEAAADhCAMAAAAJbSJIAAAAclBMVEXz8/PzUyWBvAYFpvD/ugjz9PX19PXz+fr39fr69vPy9fp5uAAAofD/tgDz3Nji6tfzRADzTBfzmYew0oB/xfH70IDX5/P16tfz5eLo7eHzPADzlICs0Hfh6/N3wvH7znj07eEAnvDzvbPL3q6u1/L43q6vy/leAAABd0lEQVR4nO3cR1IDQRREwcb0SEgj770B7n9FNmhEBL1g8zUs8l2gIi9QKUmSpHs5vPtWFV4uANMwunUD3IyiS7+Jebgdx7bddb63uvt+dKOqIBw/xTaZNsLZc3CEhISEhISEhISEhISEhISEhISEhISEhISEhISEhISEhISEhISEhISEhISEhISEhISEhISEhISEhISEhISEhISEhISEhISEhISEhISEhISEhISEjxVuJ7GNfwj7LQjTejcN7noTVu+z4PabgjB1wmumqm50JaAkSX/oLbxmKveiK/zqp8NxHtvx40bMn6dFbKdzgbi81MEdb8LeaRDdqiSsX2Kr541wMXiNjZCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkPCxwuj/0kvb/6V5Gd2hmTqvokulm90HluNrFyhJ0j/rC6N0RI28dGy3AAAAAElFTkSuQmCC",
        "data:image/png;base64,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"]

    phase3_role = "Software Engineering Intern (Machine Learning or Cloud Infrastructure)"
    phase3_companies = ["Google Summer of Code", "Waymo", "DeepMind"]
    phase3_rationales = ["You should work at Google Summer of Code because ..... ",
                         "Waymo will help elevate you by....", "DeepMind is a good fit because...."]
    phase3_company_logos = [
        "data:image/png;base64,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",
        "data:image/png;base64,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",
        "data:image/png;base64,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"]

    phase4_role = "Software Engineering Intern"
    phase4_companies = ["Google"]
    phase4_rationales = ["This is the end goal!"]
    phase4_company_logos = [
        "data:image/png;base64,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"]

    roadmap_json = f"""
            {{
              "roadmap": [
                {{
                  "start_date": "October 2023",
                  "end_date": "January 2025",
                  "position": "{phase1_role}",
                  "companies": {phase1_companies},
                  "company_rationale": {phase1_rationales},
                  "company_logos": {phase1_company_logos}
                }},
                {{
                  "start_date": "February 2025",
                  "end_date": "October 2026",
                  "position": "{phase2_role}",
                  "companies": {phase2_companies},
                  "company_rationale": {phase2_rationales},
                  "company_logos": {phase2_company_logos}
                }},
                {{
                  "start_date": "November 2026"
                  "end_date": "January 2028",
                  "position": "{phase3_role}",
                  "companies": {phase3_companies},
                  "company_rationale": {phase3_rationales},
                  "company_logos": {phase3_company_logos}
                }},
                {{
                  "start_date": "February 2028",
                  "position": "{phase4_role}",
                  "companies": {phase4_companies},
                  "company_rationale": {phase4_rationales},
                  "company_logos": {phase4_company_logos}
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
    because that should be the final goal. All company logo URLS should come be wikipedia URLs.


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

        print("res")
        roadmap_response = supabase.table('roadmap').insert({
            'user_id': user_id
        }).execute()

        # Get newly created roadmap_id
        roadmap_id = roadmap_response.data[0]['id']
        print(f"New roadmap created for user {user_id} with ID: {roadmap_id}")

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
                "in_resume": True,  # Set to True for all
                "roadmap_id": roadmap_id
            }

            print(experience_data)

            response = supabase.table("experience").insert([experience_data]).execute()


        print("\n\nCAREER ROAD_MAP")
        print(career_roadmap)
        print("\n\n")


        print("here")
        for roadmap in as_dict["career_roadmap"]:
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
                    "roadmap_id": roadmap_id
                }




                response = supabase.table("experience").select("*").execute()

                print(experience_data)
                response = supabase.table("experience").insert([experience_data]).execute()
                print("response for experience", response)
                # response = supabase.table("roadmap").insert([])




        return json_data
    except (json.JSONDecodeError, Exception) as e:
        return jsonify({'error': f'Parsing error: {str(e)}', 'raw_output': generated_text}), 500

@app.route('/get-roadmaps/<user_id>', methods=['GET'])
def get_user_roadmaps(user_id):
    """Get all roadmaps for a specific user."""
    try:
        # Step 1: Query roadmaps linked to the user
        response = (
            supabase.table('roadmap')
            .select('*')
            .eq('user_id', user_id)
            .execute()
        )

        if not response.data:
            return jsonify({"message": "No roadmaps found for this user."}), 404

        roadmaps = response.data

        return jsonify({
            "user_id": user_id,
            "roadmaps": roadmaps
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/get-experiences/<roadmap_id>', methods=['GET'])
def get_roadmap_experiences(roadmap_id):
    """Get all experiences for a specific roadmap."""
    try:
        response = (
            supabase.table('experience')
            .select('*')
            .eq('roadmap_id', roadmap_id)
            .execute()
        )

        if not response.data:
            return jsonify({"message": "No experiences found for this roadmap."}), 404

        experiences = response.data

        return jsonify({
            "roadmap_id": roadmap_id,
            "experiences": experiences
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/getprofile/<id>', methods=['GET'])
def get_profile_information(id):
    # Fetch user profile from Supabase based on the provided id
    user_response = supabase.table("user").select("*").eq("id", id).execute()

    # Check if user exists
    if user_response.data:
        user = user_response.data[0]  # Get the first user (since .eq() returns a list)
        return jsonify(user), 200  # Return user data as JSON with a 200 OK status
    else:
        return jsonify({"error": "User not found"}), 404





@app.route('/generate-cleaned-experiences', methods=['POST'])
def generate_cleaned_experiences():
    data = request.json
    experiences = data.get('experiences', [])
    user_id = data.get('user_id')

    if not experiences:
        return jsonify({'error': 'No experiences provided'}), 400

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

    prompt = f""" You are a career assistant. Clean and summarize the following professional experiences. Any 
    projects should have "Project" for its company. Return ONLY the information with the following JSON format: 
    "cleaned_experiences": {cleaned_experiences_json}

    Experiences:
    {experiences}
    """

    headers = {
        'Authorization': f'Bearer {COHERE_API_KEY}',
        'Content-Type': 'application/json'
    }

    payload = {
        'model': 'command-xlarge-nightly',
        'prompt': prompt,
        'max_tokens': 2000,
        'temperature': 0.3
    }

    try:
        response = requests.post(COHERE_API_URL, json=payload, headers=headers)
        response_data = response.json()
        generated_text = response_data.get('generations', [{}])[0].get('text', '')
        parsed_response = json.loads(generated_text)

        cleaned_experiences = parsed_response.get('cleaned_experiences', [])



        # Store experiences in Supabase
        for exp in cleaned_experiences:
            experience_data = {
                "company": exp.get("company", "Unknown Company"),
                "position": exp.get("position", "Unknown Position"),
                "start_date": exp.get("start_date", ""),
                "end_date": exp.get("end_date", "Present"),
                "summary": exp.get("summary", ""),
                "in_resume": True,
                "user_id": user_id
            }
            supabase.table("experience").insert([experience_data]).execute()

        return jsonify({"cleaned_experiences": cleaned_experiences}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500




@app.route('/generate-roadmapp', methods=['POST'])
def generate_roadmapp():
    data = request.json
    experiences = data.get('experiences', [])
    user_goal_company = data.get('desiredCompany')
    user_goal_role = data.get('desiredRole')
    user_id = data.get('user_id')

    print("user_id", user_id)

    # if not user_goal_company or not user_goal_role:
    #     return jsonify({'error': 'Goal company and role required'}), 400

    phase1_role = "Software Engineering Intern (Backend or Cloud)"
    phase1_companies = ["Shopify", "Stripe", "Twilio"]
    phase1_rationales = ["You should work at Shopify because ..... ", "Stripe will help elevate you by....",
                         "Twilio is a good fit because...."]
    phase1_company_logos = ["https://www.google.com/imgres?q=wikipedia%20shopify%20logo&imgurl=https%3A%2F%2Fupload"
                            ".wikimedia.org%2Fwikipedia%2Fcommons%2Fthumb%2F0%2F0e%2FShopify_logo_2018.svg%2F290px"
                            "-Shopify_logo_2018.svg.png&imgrefurl=https%3A%2F%2Fen.wikipedia.org%2Fwiki%2FShopify"
                            "&docid=s1x6v2b8kCY-OM&tbnid=qfwIbjySppw6nM&vet"
                            "=12ahUKEwj0tOeizseLAxU66skDHS54JsQQM3oECDgQAA..i&w=290&h=91&hcb=2&ved"
                            "=2ahUKEwj0tOeizseLAxU66skDHS54JsQQM3oECDgQAA",
                           "data:image/png;base64,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",
                           "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAZoAAAB7CAMAAAB6t7bCAAAAkFBMVEX"
                           "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"]

    phase2_role = "Software Engineer (Backend/Cloud)"
    phase2_companies = ["AWS", "Microsoft", "Meta"]
    phase2_rationales = ["You should work at AWS because ..... ", "Microsoft will help elevate you by....",
                         "Meta is a good fit because...."]
    phase2_company_logos = ["https://www.google.com/imgres?q=wikipedia%20logo%20aws&imgurl=https%3A%2F%2Fupload.wikimedia.org%2Fwikipedia%2Fcommons%2F9%2F93%2FAmazon_Web_Services_Logo.svg&imgrefurl=https%3A%2F%2Fen.wikipedia.org%2Fwiki%2FAmazon_Web_Services&docid=JSgXJbxN-7t0-M&tbnid=FB3B89WhUh9TUM&vet=12ahUKEwiXnN65zseLAxUfMdAFHS8hAjEQM3oECBwQAA..i&w=800&h=479&hcb=2&ved=2ahUKEwiXnN65zseLAxUfMdAFHS8hAjEQM3oECBwQAA",
                           "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAOEAAADhCAMAAAAJbSJIAAAAclBMVEXz8/PzUyWBvAYFpvD/ugjz9PX19PXz+fr39fr69vPy9fp5uAAAofD/tgDz3Nji6tfzRADzTBfzmYew0oB/xfH70IDX5/P16tfz5eLo7eHzPADzlICs0Hfh6/N3wvH7znj07eEAnvDzvbPL3q6u1/L43q6vy/leAAABd0lEQVR4nO3cR1IDQRREwcb0SEgj770B7n9FNmhEBL1g8zUs8l2gIi9QKUmSpHs5vPtWFV4uANMwunUD3IyiS7+Jebgdx7bddb63uvt+dKOqIBw/xTaZNsLZc3CEhISEhISEhISEhISEhISEhISEhISEhISEhISEhISEhISEhISEhISEhISEhISEhISEhISEhISEhISEhISEhISEhISEhISEhISEhISEhISEhISEjxVuJ7GNfwj7LQjTejcN7noTVu+z4PabgjB1wmumqm50JaAkSX/oLbxmKveiK/zqp8NxHtvx40bMn6dFbKdzgbi81MEdb8LeaRDdqiSsX2Kr541wMXiNjZCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkPCxwuj/0kvb/6V5Gd2hmTqvokulm90HluNrFyhJ0j/rC6N0RI28dGy3AAAAAElFTkSuQmCC",
                           "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAfUAAABlCAMAAABjh4rUAAAA81BMVEX"
                           "///8ZKDAAgfsAZOEAEx8XJi8AAA7v8PH4+fkIICoAa"
                           "+cADhsAgPunq60Abem6vsAAcu2fpKYAABUAfPsAefvJzM0RIisABxfX2tsAefMAGiQAdfBHUFYtOD8ADxwAd"
                           "/tvdnqEio0AAABjam4AWd4AYuHo6eoAWN6xtbcAAAuSl5rp9P93fYFSW2A9R03FyMkiMDhVofzT5v4"
                           "+lvzC3P6mzP1bY2fd3+ASiPuOsO+72f6Fuf2Pv/3x+P9OnfxwnuvM4v6wyPMxeOTa5/pgp"
                           "/xCmPxumupMieifvPFBfuVyr/yAqO0jceO3zPQ1euRelu2bxv1i"
                           "/m4aAAAWUklEQVR4nO2deVcay9PHh30bQVkGMhEEZRBBcQeMkmBIYmLM"
                           "/eX9v5qHYZGp6uruaiTxnsf7vefcPyL0DPOZ7lq6utuyGOpe3Xz7nI5E0k+fHz59v"
                           "+pyvgM1urr7cjkMh4eX57fXk6R5A//p76p786PZbHpeZCpvquah9"
                           "+NmYtJC8vqrXSzYdjgctm27UCwOv3z4U3f7nzahq4fD5gx4QD75f+65HbZ7WyzOiK9kF/bs2zVGjP/0V3T1"
                           "+RAjX5JvZr9zWkje2oUwIbtQeHwJ90R1V1DiBe35OhabfIO2aPIgYz7n/vRL28T1sGBT0Ofc79a/t8S+g1VrrN"
                           "+cr4rYpPv2qN8IQzvmfvig7q6jL3sy5jPuxeHFujeXiIcERVvrtjbTroMbjKXeGvXuj6aa"
                           "+dzCq7r7OEwO7oD7ut2dou7W12xsplxZaPDvUG+VgF726r5MV7qOvuzu36RN/C6qOvpCxY"
                           "+jte6Poh6KV9b9uVOFYq9EfWc/E9D+zl+4pETfDznMfTV/SLDd7umZT1UYruXUkdSdk/V"
                           "/8U5NbO8vUY8CM7X1Fy5J6ycbuj/Kk8H7eZEF3Q/hjYL/hUjqoXJu3V+ciIld/Y1R"
                           "/8Yw6UHsY7GJc51JD2Jfw6ejqTvVdX9yI0o096aofzLo6TPsh4JPR/Z026YNvV0w7+009VBmzWfWIpt7S9R"
                           "/GvV0EvsXoafbhaI9S8dS8bsdNrbtEuqxs/U41d03Tp3vyEmxPxYF5Oe"
                           "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"]

    phase3_role = "Software Engineering Intern (Machine Learning or Cloud Infrastructure)"
    phase3_companies = ["Google Summer of Code", "Waymo", "DeepMind"]
    phase3_rationales = ["You should work at Google Summer of Code because ..... ",
                         "Waymo will help elevate you by....", "DeepMind is a good fit because...."]
    phase3_company_logos = ["data:image/png;base64,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",
                           "data:image/png;base64,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",
                           "data:image/png;base64,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"]

    phase4_role = "Software Engineering Intern"
    phase4_companies = ["Google"]
    phase4_rationales = ["This is the end goal!"]
    phase4_company_logos = ["data:image/png;base64,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"]

    roadmap_json = f"""
        {{
          "roadmap": [
            {{
              "start_date": "October 2023",
              "end_date": "January 2025",
              "position": "{phase1_role}",
              "companies": {phase1_companies},
              "company_rationale": {phase1_rationales},
              "company_logos": {phase1_company_logos}
            }},
            {{
              "start_date": "February 2025",
              "end_date": "October 2026",
              "position": "{phase2_role}",
              "companies": {phase2_companies},
              "company_rationale": {phase2_rationales},
              "company_logos": {phase2_company_logos}
            }},
            {{
              "start_date": "November 2026"
              "end_date": "January 2028",
              "position": "{phase3_role}",
              "companies": {phase3_companies},
              "company_rationale": {phase3_rationales},
              "company_logos": {phase3_company_logos}
            }},
            {{
              "start_date": "February 2028",
              "position": "{phase4_role}",
              "companies": {phase4_companies},
              "company_rationale": {phase4_rationales},
              "company_logos": {phase4_company_logos}
            }}
          ]
        }}
        """

    prompt = f""" Generate a career roadmap from my current position to the role of {user_goal_role} at 
    {user_goal_company}. This roadmap should be based on my previous experiences. Structure the roadmap into clear 
    phases, each showing a career step with company name and that stuff. Make it short and clear. "career_roadmap" 
    should contain the companies (OTHER THAN THE ONES I ALREADY HAVE) that I should aim to work at to land an 
    {user_goal_role} at {user_goal_company}. The phases and timelines should start realistic and should start atleast 
    6 months from today. The timeline (start and end dates) should be different depending on the goal role and 
    company. For example, you can't expect me to get an Apple internship right away if I have 0 internship 
    experience. You also can't expect me to get a CTO Position within 3 years if I have 0 previous experience. 
    However, my career should only go up (i.e. I should not go from intern to full time and back to intern) The final 
    entry should just have a start date and the end date should be "present" because that should be the final goal. 
    Every logo you get should be a wikipedia URL.


    Return ONLY the information in valid JSON format with ONLY keys: "cleaned_experiences" and "career_roadmap". Do 
    not put a "roadmap" key within "career_roadmap". Also do not put a "cleaned_experiences" key within 
    "cleaned_experiences" This is an example of what the keys should look like. However, the actual content is 
    different based on what I just told you. 
    
    "cleaned_experiences": {experiences},
    "career_roadmap" {roadmap_json}
    """


    headers = {
        'Authorization': f'Bearer {COHERE_API_KEY}',
        'Content-Type': 'application/json'
    }

    payload = {
        'model': 'command-xlarge-nightly',
        'prompt': prompt,
        'max_tokens': 3500,
        'temperature': 0.5
    }

    try:
        response = requests.post(COHERE_API_URL, json=payload, headers=headers)
        response_data = response.json()
        generated_text = response_data.get('generations', [{}])[0].get('text', '')
        parsed_response = json.loads(generated_text)

        career_roadmap = parsed_response.get('career_roadmap', [])

        roadmap_response = supabase.table('roadmap').insert({
            'user_id': user_id
        }).execute()

        roadmap_id = roadmap_response.data[0]['id']

        for step in career_roadmap:
            for i, company in enumerate(step.get("companies", [])):
                experience_data = {
                    "company": company,
                    "position": step.get("position", "Unknown Position"),
                    "start_date": step.get("start_date", ""),
                    "end_date": step.get("end_date", "Present"),
                    "summary": step.get("company_rationale", [""])[i],
                    "in_resume": False,
                    "roadmap_id": roadmap_id
                }
                supabase.table("experience").insert([experience_data]).execute()

        return jsonify({"career_roadmap": career_roadmap}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
