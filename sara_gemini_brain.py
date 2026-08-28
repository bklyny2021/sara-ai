#!/usr/bin/env python3
"""
SARA GEMINI BRAIN - uses Gemini as Sara's primary brain (online).
Falls back to the local swarm when offline.
Gemini is far more capable than the small local models.
"""
import os
import json
import requests

# Read API key from .env
def _get_key():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("GEMINI_API_KEY="):
                    return line.strip().split("=", 1)[1].strip().strip('"').strip("'")
    return os.environ.get("GEMINI_API_KEY", "")

MODEL = "gemini-3.6-flash"
KEY = _get_key()

def gemini_chat(prompt, system=None, temperature=0.7, max_tokens=500):
    """Call Gemini with a prompt. Returns text or None on failure."""
    if not KEY:
        return None
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={KEY}"
    parts = []
    if system:
        parts.append({"text": system})
    parts.append({"text": prompt})
    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens}
    }
    try:
        r = requests.post(url, json=payload, timeout=60)
        if r.status_code == 200:
            data = r.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        return None
    except Exception as e:
        print(f"Gemini error: {e}")
        return None

def gemini_available():
    """Check if Gemini is reachable"""
    return bool(KEY)

def gemini_process(task, context=""):
    """Process a task with Gemini. Returns (response, used_gemini)."""
    system = (
        "You are SARA, a warm, helpful AI assistant. Your user is Boo (Bryan), the admin. "
        "Be concise, direct, and genuinely helpful. Never give canned or scripted responses - "
        "always answer naturally from your own understanding.\n"
        f"Context about Boo:\n{context[:1500]}"
    )
    response = gemini_chat(task, system=system)
    if response:
        return response, True
    return None, False

if __name__ == "__main__":
    import sys
    task = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Say hello"
    resp, used = gemini_process(task)
    print(f"[Gemini: {'ONLINE' if used else 'OFFLINE'}]")
    print(resp or "(no response)")
