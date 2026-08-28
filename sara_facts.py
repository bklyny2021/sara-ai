#!/usr/bin/env python3
"""SARA LEARNED FACTS - remembers verified Q&A facts on the go.
When Sara learns something (e.g. from a web search), she saves the Q->A fact.
Next time the same question comes up, she recalls it instantly instead of re-searching."""
import os, json, re
from datetime import datetime

FACTS_FILE = r"C:/Users/bklyn/SARA3-2026/learning_state.json"  # reuse existing file

def _load():
    try:
        if os.path.exists(FACTS_FILE):
            with open(FACTS_FILE, encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def _save(data):
    try:
        with open(FACTS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return True
    except Exception:
        return False

def _normalize(q):
    q = q.lower()
    q = re.sub(r'[^a-z0-9 ]', '', q)
    return " ".join(q.split())

def learn(q, a):
    """Save a verified fact (question -> answer)."""
    try:
        data = _load()
        facts = data.get("learned_facts", {})
        key = _normalize(q)
        if not key:
            return False
        facts[key] = {
            "q": q,
            "a": a[:600],
            "learned": datetime.now().isoformat(),
            "asked": facts.get(key, {}).get("asked", 0) + 1
        }
        data["learned_facts"] = facts
        return _save(data)
    except Exception:
        return False

def recall(q):
    """Return a saved answer if this question was already learned."""
    try:
        data = _load()
        facts = data.get("learned_facts", {})
        key = _normalize(q)
        if key in facts:
            return facts[key]["a"]
        # partial match on significant words
        words = set(key.split())
        for k, v in facts.items():
            if len(words) >= 2 and words.issubset(set(k.split())):
                return v["a"]
    except Exception:
        pass
    return None

def recall_context(q):
    """Return a context snippet if a learned fact matches (for injection into prompts)."""
    a = recall(q)
    if a:
        return f"\n[KNOWN FACT] {a}"
    return ""
