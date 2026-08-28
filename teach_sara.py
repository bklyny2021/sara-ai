#!/usr/bin/env python3
"""
Sarah -> Sara teaching bridge.
Usage: python teach_sara.py "lesson text here"
Sends the lesson to Sara's /teach endpoint, which verifies with qwen3:4b
and saves to her MEMORY.md if it passes.
"""
import sys
import json
import requests

SARA_URL = "http://127.0.0.1:8892/teach"

def teach(lesson, source="Sarah"):
    try:
        r = requests.post(SARA_URL, json={"lesson": lesson, "source": source}, timeout=120)
        return r.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python teach_sara.py \"lesson text\"")
        sys.exit(1)
    lesson = " ".join(sys.argv[1:])
    result = teach(lesson)
    print(json.dumps(result, indent=2))
