import json
import requests
from flask import Blueprint, request, jsonify

roadmap_bp = Blueprint('roadmap_bp', __name__)
COHERE_API_URL = 'https://api.cohere.ai/v1/generate'

@roadmap_bp.route('/generate-roadmap', methods=['POST'])
def generate_roadmap():
    from app import supabase, COHERE_API_KEY, COHERE_API_URL
    from services import supabase_service

    data = request.json

    user_prompt = data.get('userPrompt')
    user_id = data.get('user_id')

    experiences = supabase_service.get_cleaned_experience(user_id)
    print(experiences)

    if not experiences:
        return jsonify({'error': 'No experiences provided'}), 400

    phase1_role = "Software Engineering Intern (Backend or Cloud)"
    phase1_companies = ["Shopify", "Stripe", "Twilio"]
    phase1_rationales = ["You should work at Shopify because ..... ", "Stripe will help elevate you by....",
                         "Twilio is a good fit because...."]

    phase2_role = "Software Engineer (Backend/Cloud)"
    phase2_companies = ["AWS", "Microsoft", "Meta"]
    phase2_rationales = ["You should work at AWS because ..... ", "Microsoft will help elevate you by....",
                         "Meta is a good fit because...."]

    phase3_role = "Software Engineering Intern (Machine Learning or Cloud Infrastructure)"
    phase3_companies = ["Google Summer of Code", "Waymo", "DeepMind"]
    phase3_rationales = ["You should work at Google Summer of Code because ..... ",
                         "Waymo will help elevate you by....", "DeepMind is a good fit because...."]

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
                 "company_rationale": {phase1_rationales},
               }},
               {{
                 "start_date": "February 2025",
                 "end_date": "October 2026",
                 "position": "{phase2_role}",
                 "companies": {phase2_companies},
                 "company_rationale": {phase2_rationales},
               }},
               {{
                 "start_date": "November 2026"
                 "end_date": "January 2028",
                 "position": "{phase3_role}",
                 "companies": {phase3_companies},
                 "company_rationale": {phase3_rationales},
               }},
               {{
                 "start_date": "February 2028",
                 "position": "{phase4_role}",
                 "companies": {phase4_companies},
                 "company_rationale": {phase4_rationales},
               }}
             ]
           }}
           """

    user_goal_role= "i want to work at google as a CTO"

    prompt = f""" Generate a clear and concise career roadmap to help me reach my goal role. This is what I am 
    looking for {user_prompt}. Use my experience history ("cleaned_experiences") as a foundation, and structure the 
    roadmap into distinct phases, each representing a career step with corresponding company names and role details. 
    Ensure the roadmap is realistic and achievable, with a timeline that starts at least six months from the present 
    and progresses upward in terms of responsibility and prestige. Be very realistic with the timelines. For example, 
    I cant get to CTO position in 5 years if i have little experience. Each phase should have a unique start and end 
    date, with the final entry having an open-ended "present" end date as the long-term goal. Account for my previous 
    experiences and provide a path that builds upon them coherently.



       Return ONLY the information in valid JSON format with ONLY the following keys. Do 
       not put a "roadmap" key within "career_roadmap". Also do not put a "cleaned_experiences" key within 
       "cleaned_experiences" This is an example of what the keys should look like. However, the actual content is 
       different based on what I just told you. 

       "cleaned_experiences": {experiences},
       "career_roadmap" {roadmap_json}
       "roadmap_title": "Senior Software Engineer at Google",
       "roadmap_companies": ["Amazon", "Meta"], (this should be a list of all companies along the way in the roadmap)
       "roadmap_duration": "4-6 years"
       """


    headers = {
        'Authorization': f'Bearer {COHERE_API_KEY}',
        'Content-Type': 'application/json'
    }
    payload = {
        'model': 'command-xlarge-nightly',
        'prompt': prompt,
        'max_tokens': 20000,
        'temperature': 0.7
    }

    print("entering try now")
    try:
        COHERE_API_URL = 'https://api.cohere.ai/v1/generate'

        headers = {
            "Authorization": f"Bearer {COHERE_API_KEY}",
            "Content-Type": "application/json"
        }

        print(prompt)
        response = requests.post(COHERE_API_URL, json=payload, headers=headers)


        print("done cohere", response)

        response_data = response.json()
        print("\n\n", response_data)
        generated_text = response_data.get('generations', [{}])[0].get('text', '')
        print("generated_text: ", generated_text)
        parsed_response = json.loads(generated_text)
        print("parsed_response ", parsed_response)
        cleaned_experiences = parsed_response.get('cleaned_experiences', [])
        print("cleaned_experiences ", cleaned_experiences)

        career_roadmap = parsed_response.get('career_roadmap', [])
        print("career_roadmap ", career_roadmap)
        roadmap_title = parsed_response.get('roadmap_title', "")
        print()
        roadmap_companies = parsed_response.get('roadmap_companies', [])
        roadmap_duration = parsed_response.get("roadmap_duration", "")


        print("got json stuff")

        json_data = jsonify({'cleaned_experiences': cleaned_experiences, 'career_roadmap': career_roadmap,
                             'duration': roadmap_duration, 'companies': roadmap_companies, "title": roadmap_title })

        as_dict = json_data.get_json()

        print("here")

        print("res")
        roadmap_response = supabase.table('roadmap').insert({
            'user_id': user_id, 'title': as_dict["title"], "duration": as_dict["duration"], "companies": as_dict["companies"]
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
                "roadmap_id": roadmap_id,
                "user_id": user_id
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
                print("user prompt", user_prompt)

        return json_data
    except (json.JSONDecodeError, Exception) as e:
        return jsonify({'error': f'Parsing error: {str(e)}', 'raw_output': generated_text}), 500

@roadmap_bp.route('/get-roadmaps/<user_id>', methods=['GET'])
def get_user_roadmaps(user_id):
    from app import supabase, COHERE_API_KEY, COHERE_API_URL
    try:
        response = supabase.table('roadmap').select('*').eq('user_id', user_id).execute()
        print(response)
        if not response.data:
            return jsonify({"message": "No roadmaps found"}), 404
        return jsonify({"user_id": user_id, "roadmaps": response.data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
