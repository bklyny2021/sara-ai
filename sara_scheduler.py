#!/usr/bin/env python3
"""SARA SCHEDULER - reminders, appointments, and timers.
Reminders: "remind me to X at 3pm"
Appointments: "set an appointment/meeting on Friday at 2pm"
Timers: "set a timer for 5 minutes"
All persisted to sara_schedule.json so they survive restarts. Runs a checker
that fires due items (says them aloud via the voice worker + logs them)."""
import os, json, re, time, threading, subprocess
from datetime import datetime, timedelta

SCHED_FILE = r"C:/Users/bklyn/SARA3-2026/sara_schedule.json"
LOCK = threading.Lock()

def _load():
    try:
        if os.path.exists(SCHED_FILE):
            with open(SCHED_FILE, encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {"reminders": [], "appointments": [], "timers": []}

def _save(data):
    try:
        with open(SCHED_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return True
    except Exception:
        return False

def _now_ts():
    return time.time()

def _parse_time(text):
    """Parse '5:30pm', '17:30', '3pm', 'in 5 minutes', 'in 2 hours', 'at 3'."""
    t = text.lower().strip()
    # "in N minutes/hours/seconds"
    m = re.search(r'in\s+(\d+)\s*(second|sec|minute|min|hour|hr)s?', t)
    if m:
        n = int(m.group(1)); unit = m.group(2)
        mult = {"second":1,"sec":1,"minute":60,"min":60,"hour":3600,"hr":3600}[unit]
        return _now_ts() + n * mult, "in %s %s" % (n, unit)
    # clock time like 5pm / 17:30 / 3pm
    m = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', t)
    if m:
        hour = int(m.group(1)); minute = int(m.group(2) or 0); ampm = m.group(3)
        if ampm == "pm" and hour != 12: hour += 12
        if ampm == "am" and hour == 12: hour = 0
        now = datetime.now()
        when = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if when < now: when = when + timedelta(days=1)
        return when.timestamp(), when.strftime("%I:%M %p").lstrip("0")
    return None, None

def add_reminder(text, when_ts, when_disp):
    with LOCK:
        d = _load()
        d["reminders"].append({
            "id": int(_now_ts()*1000), "text": text,
            "due": when_ts, "due_disp": when_disp,
            "created": datetime.now().isoformat(), "fired": False
        })
        _save(d)
    return len(d["reminders"]) - 1

def add_timer(label, seconds):
    with LOCK:
        d = _load()
        d["timers"].append({
            "id": int(_now_ts()*1000), "label": label or "Timer",
            "due": _now_ts() + seconds, "seconds": seconds,
            "created": datetime.now().isoformat(), "fired": False
        })
        _save(d)
    return len(d["timers"]) - 1

def _fire_aloud(text):
    # speak notification
    import subprocess
    worker = r"C:/Users/bklyn/SARA3-2026/sara_voice_worker.py"
    pythonw = r"C:\Users\bklyn\AppData\Local\hermes\hermes-agent\venv\Scripts\pythonw.exe"
    if not os.path.exists(pythonw):
        pythonw = os.path.join(os.path.dirname(__import__('sys').executable), "pythonw.exe")
    try:
        subprocess.Popen([pythonw, worker, text], creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    except Exception:
        pass

def check_due():
    """Fire any due reminders/timers. Runs on a background thread."""
    changed = False
    with LOCK:
        d = _load()
        now = _now_ts()
        fired_msgs = []
        for item in d["reminders"]:
            if not item["fired"] and now >= item["due"]:
                item["fired"] = True
                fired_msgs.append("Reminder: " + item["text"])
                changed = True
        for item in d["timers"]:
            if not item["fired"] and now >= item["due"]:
                item["fired"] = True
                fired_msgs.append("Timer done: " + item["label"])
                changed = True
        for item in d["appointments"]:
            if not item.get("fired") and now >= item["due"]:
                item["fired"] = True
                fired_msgs.append("Appointment: " + item["text"])
                changed = True
        if changed:
            _save(d)
    for m in fired_msgs:
        _fire_aloud(m)
    return fired_msgs

def _fire_aloud(text):
    # speak notification
    import subprocess
    worker = r"C:/Users/bklyn/SARA3-2026/sara_voice_worker.py"
    pythonw = r"C:\Users\bklyn\AppData\Local\hermes\hermes-agent\venv\Scripts\pythonw.exe"
    if not os.path.exists(pythonw):
        pythonw = os.path.join(os.path.dirname(__import__('sys').executable), "pythonw.exe")
    try:
        subprocess.Popen([pythonw, worker, text], creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    except Exception:
        pass

def list_items():
    d = _load()
    out = []
    for r in d["reminders"]:
        out.append("🔔 Reminder: %s (%s, %s)" % ("⏰" if r["fired"] else "", r["text"], r["due_disp"]))
    for a in d["appointments"]:
        out.append("📅 Appointment: %s (%s)" % (a["text"], a["due_disp"]))
    for t in d["timers"]:
        out.append("⏳ Timer: %s" % t["label"])
    return "\n".join(out) if out else "No reminders, appointments, or timers set."

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "list":
        print(list_items())
