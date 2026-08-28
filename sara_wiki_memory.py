#!/usr/bin/env python3
r"""
SARA WIKI MEMORY - Obsidian-style, never forgets anything Boo says.
Captures every message, organizes into wiki pages, searchable, persistent.

Structure (Obsidian-compatible):
  C:\Users\bklyn\SARA3-2026\wiki\
    index.json          - topic index
    topics\<topic>.md   - wiki pages per topic (Obsidian markdown)
    log.json            - full message log (append-only)
"""
import os
import json
import re
import time
from datetime import datetime

WIKI_DIR = os.path.join("C:", os.sep, "Users", "bklyn", "SARA3-2026", "wiki")
TOPICS_DIR = os.path.join(WIKI_DIR, "topics")
INDEX_FILE = os.path.join(WIKI_DIR, "index.json")
LOG_FILE = os.path.join(WIKI_DIR, "log.json")

# Topic keywords for auto-categorization
TOPIC_KEYWORDS = {
    "projects": ["tech2go", "world war watch", "gods eye", "mission control", "memorywiki", "todo", "e-bike", "worldview", "project"],
    "home": ["home assistant", "frigate", "camera", "light", "hue", "tv", "ginza", "duckie", "hazel", "doorbell"],
    "network": ["router", "wifi", "ip", "network", "mac filter", "firewall", "port"],
    "devices": ["phone", "moto", "razr", "iphone", "samsung", "gpu", "pc", "laptop", "macbook"],
    "preferences": ["i like", "i prefer", "i want", "i need", "never", "always", "dont", "don't", "rule"],
    "personal": ["bryan", "boo", "asperger", "family", "denise", "work", "job", "neuro"],
    "models": ["qwen", "ollama", "model", "deepseek", "llama", "gpu", "vram", "context"],
    "sara": ["sara", "sarah", "voice", "piper", "wake word", "swarm", "brain"],
}

def ensure_dirs():
    os.makedirs(TOPICS_DIR, exist_ok=True)

def _load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return default
    return default

def _save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def classify_topic(text):
    """Classify a message into a topic based on keywords"""
    t = text.lower()
    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(k in t for k in keywords):
            return topic
    return "general"

def remember(user_text, sara_response=None):
    """Store a message in the wiki memory. Never forgets."""
    ensure_dirs()
    ts = datetime.now().isoformat()
    topic = classify_topic(user_text)
    
    # 1) Append to full log (append-only, never overwrite)
    log = _load_json(LOG_FILE, [])
    log.append({
        "timestamp": ts,
        "user": user_text,
        "sara": sara_response or "",
        "topic": topic
    })
    _save_json(LOG_FILE, log)
    
    # 2) Update topic page (Obsidian markdown)
    topic_file = os.path.join(TOPICS_DIR, f"{topic}.md")
    entry = f"\n## {ts}\n**Boo said:** {user_text}\n"
    if sara_response:
        entry += f"**Sara replied:** {sara_response[:300]}\n"
    with open(topic_file, "a", encoding="utf-8") as f:
        f.write(entry)
    
    # 3) Update index
    index = _load_json(INDEX_FILE, {})
    if topic not in index:
        index[topic] = {"count": 0, "created": ts}
    index[topic]["count"] = index[topic].get("count", 0) + 1
    index[topic]["last"] = ts
    _save_json(INDEX_FILE, index)
    
    return topic

def search(query, limit=5):
    """Search the wiki memory for a query"""
    log = _load_json(LOG_FILE, [])
    q = query.lower()
    results = []
    for entry in reversed(log):
        if q in entry.get("user", "").lower() or q in entry.get("sara", "").lower():
            results.append(entry)
            if len(results) >= limit:
                break
    return results

def get_topics():
    """List all topics and their counts"""
    return _load_json(INDEX_FILE, {})

def get_topic_content(topic):
    """Get the full wiki page for a topic"""
    topic_file = os.path.join(TOPICS_DIR, f"{topic}.md")
    if os.path.exists(topic_file):
        with open(topic_file, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def get_stats():
    """Get memory stats"""
    log = _load_json(LOG_FILE, [])
    return {
        "total_messages": len(log),
        "topics": get_topics()
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "stats":
        print(json.dumps(get_stats(), indent=2))
    elif len(sys.argv) > 2 and sys.argv[1] == "search":
        for r in search(" ".join(sys.argv[2:])):
            print(f"[{r['timestamp']}] {r['user']}")
    else:
        print("Usage: python sara_wiki_memory.py stats|search <query>")
