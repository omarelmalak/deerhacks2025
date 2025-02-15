import json

import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import cloudinary
import cloudinary.uploader
from PyPDF2 import PdfReader


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

    if not experiences:
        return jsonify({'error': 'No experiences provided'}), 400

    phase1_role = "Software Engineering Intern (Backend or Cloud)"
    phase1_companies = ["Shopify", "Stripe", "Twilio"]

    phase2_role = "Software Engineer (Backend/Cloud)"
    phase2_companies = ["AWS", "Microsoft", "Meta"]

    phase3_role = "Software Engineering Intern (Machine Learning or Cloud Infrastructure)"
    phase3_companies = ["Google Summer of Code", "Waymo", "DeepMind"]

    phase4_role = "Software Engineering Intern"
    phase4_companies = ["Google"]

    roadmap_json = f"""
    {{
      "roadmap": [
        {{
          "phase": "Phase 1: Short-Term (Next 3-6 Months)",
          "role": "{phase1_role}",
          "companies": {phase1_companies}
        }},
        {{
          "phase": "Phase 2: Mid-Term (6 Months - 1 Year)",
          "role": "{phase2_role}",
          "companies": {phase2_companies}
        }},
        {{
          "phase": "Phase 3: Pre-Target (1 Year - 1.5 Years)",
          "role": "{phase3_role}",
          "companies": {phase3_companies}
        }},
        {{
          "phase": "Phase 4: Target (1.5 - 2 Years)",
          "role": "{phase4_role}",
          "companies": {phase4_companies}
        }}
      ]
    }}
    """

    amazon_company = "Amazon"
    amazon_position = "Backend Developer Intern"
    amazon_dates = "May 2022 - August 2022"
    amazon_summary = "Built RESTful APIs using Node.js and optimized database queries with PostgreSQL."

    meta_company = "Meta"
    meta_position = "Software Engineering Intern"
    meta_dates = "June 2023 - September 2023"
    meta_summary = "Developed a social graph analysis tool using Python and GraphQL."

    cleaned_experiences_json = f"""
    {{
      "cleaned_experiences": [
        {{
          "company": "{amazon_company}",
          "position": "{amazon_position}",
          "dates": "{amazon_dates}",
          "summary": "{amazon_summary}"
        }},
        {{
          "company": "{meta_company}",
          "position": "{meta_position}",
          "dates": "{meta_dates}",
          "summary": "{meta_summary}"
        }}
      ]
    }}
    """


    prompt = f""" You are a career advisor. Below are professional experiences. First, clean and summarize these 
    experiences. Then, generate a career roadmap from my current position to the role of software engineer intern at 
    Google. This roadmap should be based on my previous experiences. Structure the roadmap into clear phases, 
    each showing a career step with company name and that stuff. Make it short and clear. "career_roadmap" should 
    contain the companies (OTHER THAN THE ONES I ALREADY HAVE) that I should aim to work at to land an internship at 
    google. The phases and timelines should start realistic. For example, can't expect me to get an Apple internship right away.


    Experiences:
    {experiences}

    Return ONLY the information in valid JSON format with ONLY keys: "cleaned_experiences" and "career_roadmap". Do 
    not put a "roadmap" key within "career_roadmap". Also do not put a "cleaned_experiences" key within "cleaned_experiences" This is what they keys should look like.
    
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
        'max_tokens': 3000,
        'temperature': 0.7
    }
    try:
        response = requests.post(COHERE_API_URL, json=payload, headers=headers)

        response_data = response.json()
        generated_text = response_data.get('generations', [{}])[0].get('text', '')


        parsed_response = json.loads(generated_text)
        cleaned_experiences = parsed_response.get('cleaned_experiences', [])
        career_roadmap = parsed_response.get('career_roadmap', [])

        return jsonify({
            'cleaned_experiences': cleaned_experiences,
            'career_roadmap': career_roadmap
        })
    except (json.JSONDecodeError, Exception) as e:
        return jsonify({'error': f'Parsing error: {str(e)}', 'raw_output': generated_text}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
