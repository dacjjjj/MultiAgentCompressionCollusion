"""
OpenRouter API client.
Uses OpenRouter to access Claude Haiku (or other models).
"""

import os
import json
import requests

# Untrusted agents - open-source model that will follow attack instructions
AGENT_MODEL = "mistralai/mistral-small-2603"

# Trusted monitor - stronger model that watches for suspicious behaviour
MONITOR_MODEL = "anthropic/claude-sonnet-4.6"

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"


def call_llm(system_prompt: str, user_message: str, model: str = None) -> str:
    """
    Call an LLM via OpenRouter.
    
    Args:
        system_prompt: The system prompt defining the agent's behaviour
        user_message: The user message / task
        model: Override the default model if needed
    
    Returns:
        The model's response text
    """
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable not set")
    
    model = model or AGENT_MODEL
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/hackathon-2026",  # Optional
        "X-Title": "AI Control Hackathon 2026",  # Optional
    }
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "max_tokens": 2048,
        "temperature": 0.7,
    }
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=90)
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            if content is None:
                print(f"Warning: model {model} returned null content")
                print(f"Full response: {json.dumps(data, indent=2)[:500]}")
                return "[NO RESPONSE]"
            return content
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
            print(f"Timeout/connection error (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                import time
                time.sleep(5)
                continue
            raise
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            raise


def test_connection():
    """Quick test to verify your API key works."""
    try:
        result = call_llm(
            "You are a helpful assistant.",
            "Say 'API connection successful!' and nothing else."
        )
        print(f"✓ Connection test passed: {result}")
        return True
    except Exception as e:
        print(f"✗ Connection test failed: {e}")
        return False


if __name__ == "__main__":
    print("Testing OpenRouter connection...")
    test_connection()
