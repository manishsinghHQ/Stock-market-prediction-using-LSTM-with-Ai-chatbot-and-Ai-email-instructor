import requests
import os

def local_ai_reply(message):
    API_KEY = os.getenv("OPENROUTER_API_KEY")   # from environment variable
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "HTTP-Referer": "http://localhost",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "nvidia/nemotron-nano-12b-v2-vl:free",
        "messages": [
            {"role": "user", "content": message}
        ]
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()

        if "choices" in data:
            return data["choices"][0]["message"]["content"]

        return "AI Error: " + str(data)

    except Exception as e:
        return f"Request error: {str(e)}"
