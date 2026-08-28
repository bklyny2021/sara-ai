#!/usr/bin/env python3
"""
SARA LEARNING CHAIN - Continuous learning loop
Runs in the background. Every cycle:
1. Reads Sara's memory files (daily notes, MEMORY.md, learning_state.json, conversations)
2. Has the worker model (qwen3:8b) reflect on what was learned
3. Distills new lessons and appends them to MEMORY.md
4. Saves a learning log
Runs forever (loop), windowless.
"""
import os
import json
import time
import re
import subprocess
import sys
from datetime import date, datetime

BASE = r"C:\Users\bklyn\SARA3-2026"
MEMORY_MD = os.path.join(BASE, "MEMORY.md")
MEMORY_DIR = os.path.join(BASE, "memory")
LEARN_LOG = os.path.join(BASE, "learning_logs", "learning_chain.json")
OLLAMA = "http://localhost:11434/api/chat"
WORKER = "sara-heretic"          # her main brain - learn like a capable agent
CHECKER = "qwen3:4b"
SKILLS_DIR = os.path.join(BASE, "skills")
CONV_FILE = os.path.join(BASE, "simple_memory", "conversations.json")
TOPICS_FILE = os.path.join(BASE, "simple_memory", "topics.json")
STATE_FILE = os.path.join(BASE, "learning_chain_state.json")
CYCLE_SECONDS = 300  # check every 5 minutes, but only learn when NEW conversation exists

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)

def chat(model, messages):
    payload = {"model": model, "stream": False, "think": False, "messages": messages,
               "options": {"temperature": 0.1, "num_predict": 400, "num_ctx": 20000}}
    try:
        r = subprocess.run(["curl", "-s", OLLAMA, "-d", json.dumps(payload)],
                           capture_output=True, text=True, timeout=120,
                           creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        return json.loads(r.stdout).get("message", {}).get("content", "")
    except Exception as e:
        log(f"chat error: {e}")
        return ""

def latest_conversation_time():
    """Latest timestamp of any conversation/topic exchange."""
    try:
        with open(CONV_FILE, encoding="utf-8") as f:
            c = json.load(f).get("conversations", [])
        if c:
            return max(x.get("timestamp", 0) for x in c)
    except Exception:
        pass
    try:
        with open(TOPICS_FILE, encoding="utf-8") as f:
            d = json.load(f)
        tops = d.get("topics", d) if isinstance(d, dict) else d
        last = 0
        for tp in tops:
            ms = tp.get("messages", [])
            if ms:
                last = max(last, ms[-1].get("timestamp", 0))
        return last
    except Exception:
        return 0

def has_new_activity():
    """True only if there is NEW conversation since the last time we learned.
    When nobody's talking, this stays False and we do NOT wake the model."""
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            last_learned = json.load(f).get("last_learned_ts", 0)
    except Exception:
        last_learned = 0
    return latest_conversation_time() > last_learned

def mark_learned():
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({"last_learned_ts": latest_conversation_time()}, f)

def read_daily_notes():
    """Read today's + yesterday's daily notes"""
    text = ""
    for d in [date.today(), date.today() - __import__('datetime').timedelta(days=1)]:
        p = os.path.join(MEMORY_DIR, d.strftime("%Y-%m-%d") + ".md")
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                text += f.read() + "\n"
    return text

def read_memory_md():
    if os.path.exists(MEMORY_MD):
        with open(MEMORY_MD, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def read_learning_state():
    p = os.path.join(BASE, "learning_state.json")
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def append_to_memory_md(lesson):
    """Append a distilled lesson to MEMORY.md"""
    with open(MEMORY_MD, "a", encoding="utf-8") as f:
        f.write(f"\n## Lesson ({datetime.now().strftime('%Y-%m-%d %H:%M')})\n{lesson}\n")

def save_skill(skill_name, lesson):
    """Distill a lesson into a reusable SKILL.md (like a capable agent's skill library)."""
    try:
        os.makedirs(SKILLS_DIR, exist_ok=True)
        safe = re.sub(r'[^a-z0-9_-]+', '-', skill_name.lower()).strip('-') or "lesson"
        path = os.path.join(SKILLS_DIR, safe, "SKILL.md")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        content = (
            f"---\nname: {safe}\ndescription: Use when {safe} is relevant.\n---\n\n"
            f"# {skill_name}\n\n{lesson}\n"
        )
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        log(f"📚 Saved skill: {path}")
        return True
    except Exception as e:
        log(f"save_skill error: {e}")
        return False

def save_learn_log(entry):
    data = []
    if os.path.exists(LEARN_LOG):
        try:
            with open(LEARN_LOG, "r", encoding="utf-8") as f:
                data = json.load(f)
        except:
            data = []
    data.append(entry)
    data = data[-200:]
    os.makedirs(os.path.dirname(LEARN_LOG), exist_ok=True)
    with open(LEARN_LOG, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def run_cycle(force=False):
    # Idle-aware: only wake the model if there's NEW conversation since we last learned.
    if not force and not has_new_activity():
        log("No new conversation since last learn - idle, skipping model wake.")
        return
    # We are processing up to the current conversation; mark it as handled so we
    # don't re-wake the model every cycle while nobody is chatting.
    mark_learned()
    log("=== Learning cycle start ===")
    daily = read_daily_notes()
    memory = read_memory_md()
    state = read_learning_state()
    
    # Build context for the worker
    context = f"DAILY NOTES:\n{daily[:2000]}\n\nCURRENT MEMORY:\n{memory[:2000]}\n\nLEARNING STATE:\n{json.dumps(state)[:500]}"
    
    prompt = (
        "You are SARA, an AI assistant that learns and grows. Review the context below "
        "(your daily notes, current memory, and learning state).\n\n"
        f"{context}\n\n"
        "Identify 1-2 NEW lessons or insights worth remembering long-term. These should be "
        "things that will make you smarter or more helpful in the future. "
        "For EACH lesson, give a short NAME (2-4 words, like a skill/topic) and the lesson itself. "
        "Output ONLY lines in this exact format, one per lesson:\n"
        "NAME: <short skill name>\nLESSON: <the lesson>\n"
        "Do not repeat lessons already in your memory. If nothing new, output 'NO_NEW_LESSONS'."
    )
    
    lessons = chat(WORKER, [{"role": "user", "content": prompt}])
    lessons = lessons.strip()
    
    if not lessons or "NO_NEW_LESSONS" in lessons.upper():
        log("No new lessons this cycle.")
        return
    
    # Verify with checker
    check_prompt = (
        "You are a QA verifier. A worker model produced these lessons to add to an AI's memory:\n"
        f"{lessons}\n\n"
        "Are these genuinely useful, non-duplicative lessons? Reply PASS or FAIL with a one-line reason."
    )
    verdict = chat(CHECKER, [{"role": "user", "content": check_prompt}])
    log(f"Checker: {verdict[:60]}")
    
    if "PASS" in verdict.upper() and "FAIL" not in verdict.upper():
        append_to_memory_md(lessons)
        # Also save each lesson as a reusable SKILL
        blocks = re.split(r'\n\s*\n', lessons)
        saved_any = False
        for block in blocks:
            nm = re.search(r'NAME:\s*(.+)', block, re.IGNORECASE)
            ls = re.search(r'LESSON:\s*(.+)', block, re.IGNORECASE)
            if nm and ls:
                if save_skill(nm.group(1).strip(), ls.group(1).strip()):
                    saved_any = True
        save_learn_log({
            "timestamp": datetime.now().isoformat(),
            "lessons": lessons,
            "verdict": verdict
        })
        log(f"✅ Added lessons to MEMORY.md" + (f" and skills/" if saved_any else ""))
    else:
        log("Checker rejected lessons, not saving.")

def main():
    # Single-instance protection: use a lock file with PID
    import os as _os
    lock_file = _os.path.join(BASE, "learning_chain.lock")
    if _os.path.exists(lock_file):
        try:
            with open(lock_file, "r") as f:
                old_pid = int(f.read().strip())
            # Check if that PID is still alive and is a learning chain
            import subprocess as _sp
            r = _sp.run(["powershell", "-NoProfile", "-Command",
                         f"Get-CimInstance Win32_Process -Filter \"ProcessId={old_pid}\" | Select-Object -ExpandProperty CommandLine"],
                        capture_output=True, text=True, timeout=10)
            if "sara_learning_chain" in (r.stdout or ""):
                log(f"Duplicate learning chain (PID {old_pid}). Killing it so only one runs.")
                try:
                    _sp.run(["taskkill", "/PID", str(old_pid), "/F"], capture_output=True, text=True, timeout=10)
                    log(f"Killed duplicate PID {old_pid}")
                except Exception:
                    pass
        except Exception:
            pass
    # Write our PID to the lock file
    with open(lock_file, "w") as f:
        f.write(str(_os.getpid()))
    log(f"Lock acquired (PID {_os.getpid()})")
    
    log("SARA Learning Chain started. Loop every %ds" % CYCLE_SECONDS)
    while True:
        try:
            run_cycle()
        except Exception as e:
            log(f"Cycle error: {e}")
        time.sleep(CYCLE_SECONDS)

if __name__ == "__main__":
    main()
