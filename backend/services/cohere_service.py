import requests
import json
from config.settings import COHERE_API_KEY, COHERE_API_URL

def generate_from_cohere(prompt, max_tokens=3500, temperature=0.3):
    headers = {
        'Authorization': f'Bearer {COHERE_API_KEY}',
        'Content-Type': 'application/json'
    }
    payload = {
        'model': 'command-xlarge-nightly',
        'prompt': prompt,
        'max_tokens': max_tokens,
        'temperature': temperature
    }
    response = requests.post(COHERE_API_URL, json=payload, headers=headers)
    response_data = response.json()
    generated_text = response_data.get('generations', [{}])[0].get('text', '')
    try:
        return json.loads(generated_text)
    except json.JSONDecodeError:
        return {"error": "Failed to parse Cohere output"}
