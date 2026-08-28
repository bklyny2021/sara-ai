#!/usr/bin/env python3
"""SARA TASK TRACKER - remembers every task Boo asks, and can recall the last
thing he asked. Persists to sara_tasks.json so it survives restarts."""
import os, json, time

TASKS_FILE = r"C:/Users/bklyn/SARA3-2026/sara_tasks.json"

def _load():
    try:
        if os.path.exists(TASKS_FILE):
            with open(TASKS_FILE, encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {"tasks": []}

def _save(d):
    try:
        with open(TASKS_FILE, "w", encoding="utf-8") as f:
            json.dump(d, f, indent=2)
        return True
    except Exception:
        return False

def save_task(text):
    """Log a task Boo asked for (dedupe recent identical ones)."""
    d = _load()
    t = {
        "text": text,
        "ts": time.time(),
        "when": time.strftime("%Y-%m-%d %H:%M"),
    }
    # avoid piling exact duplicates right after each other
    if d["tasks"] and d["tasks"][-1]["text"] == text and time.time() - d["tasks"][-1]["ts"] < 60:
        return
    d["tasks"].append(t)
    _save(d)

def last_tasks(n=3):
    """Return the most recent n tasks."""
    d = _load()
    tasks = d["tasks"][-n:][::-1]
    if not tasks:
        return "You haven't asked me to do anything yet."
    return "\n".join(f"- {t['when']}: {t['text']}" for t in tasks)

def all_tasks():
    d = _load()
    tasks = d["tasks"][::-1]
    if not tasks:
        return "No tasks logged yet."
    return "\n".join(f"- {t['when']}: {t['text']}" for t in tasks)

if __name__ == "__main__":
    print(last_tasks())
