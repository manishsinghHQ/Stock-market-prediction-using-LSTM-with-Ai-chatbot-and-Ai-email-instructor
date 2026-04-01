import requests
from django.conf import settings

def local_ai_reply(message):
    """
    Send user message to OpenRouter AI and return assistant reply.
    Falls back to free model if primary fails.
    """
    models_to_try = [
        getattr(settings, "OPENROUTER_MODEL", "arcee-ai/trinity-large-preview:free"),
        "arcee-ai/trinity-large-preview:free"  # fallback
    ]

    url = getattr(settings, "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1/chat/completions")
    api_key = getattr(settings, "OPENROUTER_API_KEY", None)

    if not api_key:
        return "Error: OPENROUTER_API_KEY is missing!"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    last_error = None

    for model in models_to_try:
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": message}]
        }
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            data = response.json()
            
            if "choices" in data and len(data["choices"]) > 0:
                choice = data["choices"][0]
                return choice.get("message", {}).get("content") or choice.get("text") or "AI Error: Empty response"
            else:
                last_error = data

        except Exception as e:
            last_error = str(e)

    return f"AI request failed. Last error: {last_error}"
