import json
import requests
from flask import Blueprint, request, jsonify

from services.supabase_service import get_cleaned_experience

experiences_bp = Blueprint('experiences_bp', __name__)

@experiences_bp.route('/generate-cleaned-experiences', methods=['POST'])
def generate_cleaned_experiences():
    from app import supabase, COHERE_API_KEY, COHERE_API_URL

    data = request.json
    experiences = data.get('experiences', [])
    user_id = data.get('user_id', None)
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
                  "summary": "{amazon_summary}",
                }},
                {{
                  "company": "{meta_company}",
                  "position": "{meta_position}",
                  "start_date": "{meta_start_date}",
                  "end_date": "{meta_end_date}"
                  "summary": "{meta_summary}",

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
        'max_tokens': 8000,
        'temperature': 0.3
    }
    print("we here")
    try:
        response = requests.post("https://api.cohere.ai/v1/generate", json=payload, headers=headers)
        print(response)
        response_data = response.json()
        print(response_data)
        text = response_data.get('generations', [{}])[0].get('text', '')
        parsed = json.loads(text)
        cleaned_experiences = parsed.get('cleaned_experiences', [])

        for exp in cleaned_experiences:
            supabase.table("experience").insert([{
                "company": exp.get("company", ""),
                "position": exp.get("position", ""),
                "start_date": exp.get("start_date", ""),
                "end_date": exp.get("end_date", "Present"),
                "summary": exp.get("summary", ""),
                "in_resume": True,

                "user_id": user_id
            }]).execute()

        return jsonify({"cleaned_experiences": cleaned_experiences}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@experiences_bp.route('/get-experiences/<roadmap_id>', methods=['GET'])
def get_roadmap_experiences(roadmap_id):
    from app import supabase, COHERE_API_KEY, COHERE_API_URL

    try:
        response = supabase.table('experience').select('*').eq('roadmap_id', roadmap_id).execute()
        if not response.data:
            return jsonify({"message": "No experiences found."}), 404
        return jsonify({"roadmap_id": roadmap_id, "experiences": response.data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@experiences_bp.route('/get-current-experiences/<user_id>', methods=['GET'])
def get_current_experiences(user_id):
    from services import supabase_service
    try:
        response = supabase_service.get_cleaned_experience(user_id)

        if not response.data:
            return jsonify({"message": "No current experiences found."}), 404

        return jsonify({"user_id": user_id, "current_experiences": response.data}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


