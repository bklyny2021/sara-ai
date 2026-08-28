#!/usr/bin/env python3
"""
SARA SUPERVISOR - a tiny always-running model that watches Sara and catches
when she stalls (says "One moment", "working on it", "let me check") but doesn't
actually finish the task.

IMPORTANT: This does NOT coach Sara. It does NOT tell her what to say or how to
answer. It ONLY prompts her with the task she was working on, so she doesn't
forget and continues it. Her words always come from her own models.

Uses a tiny model (gemma3:1b, ~815MB) so it runs always-on without slowing
Sara's main 14B brain.
"""
import os
import json
import time
import subprocess
import requests

SARA_URL = "http://127.0.0.1:8892"
SUPERVISOR_MODEL = "gemma3:1b"   # tiny, always-on
OLLAMA_URL = "http://localhost:11434/api/chat"

# Stall phrases that mean Sara said she'd do something but hasn't finished.
STALL_PHRASES = [
    'one moment', 'still searching', 'still working', 'working on it',
    'working on that', 'let me check', "i'll search", 'i will search',
    'let me look', 'one sec', 'give me a moment', 'searching for',
    'looking for', 'let me find', 'i will look', "i'll look",
    'checking that', 'let me get', 'i will get', "i'll get", 'one minute',
    'let me see', 'give me a second', 'just a moment', 'hold on'
]

# Track the last task Sara was asked, so we can remind her what she was doing.
_last_task = None
_last_stall_time = 0


def _ask_tiny(prompt):
    """Ask the tiny supervisor model a yes/no question. Returns True/False."""
    try:
        r = requests.post(OLLAMA_URL, json={
            "model": SUPERVISOR_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {"temperature": 0.0, "num_predict": 20}
        }, timeout=30)
        if r.status_code == 200:
            return r.json().get("message", {}).get("content", "").strip()
    except Exception as e:
        print(f"[SUPERVISOR] tiny model error: {e}")
    return ""


def _is_stall(text):
    """Check if a response is a stall (Sara said she'd do it but didn't finish)."""
    t = (text or "").lower()
    return any(p in t for p in STALL_PHRASES)


def _get_last_exchange():
    """Get the most recent user->Sara exchange from Sara's conversation log."""
    try:
        with open("C:/Users/bklyn/SARA3-2026/simple_memory/conversations.json",
                  encoding="utf-8") as f:
            data = json.load(f)
        convos = data.get("conversations", [])
        if convos:
            last = convos[-1]
            return last.get("user", ""), last.get("sara", "")
    except Exception:
        pass
    return None, None


def _prompt_sara_to_continue(task):
    """Prompt Sara with the task she was working on (no coaching, just a reminder).
    Sends it back through her own /ask endpoint so SHE decides how to answer."""
    try:
        reminder = (
            f"[CONTINUE] You were working on this task and haven't finished it yet: "
            f"'{task}'. Please continue and complete it now."
        )
        r = requests.post(f"{SARA_URL}/ask", json={"message": reminder}, timeout=180)
        if r.status_code == 200:
            print(f"[SUPERVISOR] Prompted Sara to continue: {task[:60]}...")
            return True
    except Exception as e:
        print(f"[SUPERVISOR] prompt error: {e}")
    return False


def run():
    """Main supervisor loop - watches Sara for stalls AND keeps her brain model
    loaded in VRAM (keep-alive) so her replies are fast."""
    global _last_task, _last_stall_time
    print("[SUPERVISOR] Starting. Watching Sara for stalls + keeping brain loaded...")

    # KEEP-ALIVE: every 2 minutes, ping the 14B brain model so Ollama never unloads
    # it from VRAM. This is what makes Sara's replies FAST (no 10GB reload each time).
    # CRITICAL: the timeout must be LONG (300s) because if the model unloaded, the ping
    # has to RELOAD it from the slow HDD (5+ min). A short timeout would fail the reload.
    # Runs in a thread so it never blocks the stall-watching loop.
    import threading
    def _keep_alive():
        while True:
            time.sleep(120)  # every 2 min - keeps the model warmer
            try:
                requests.post(OLLAMA_URL, json={
                    "model": "richardyoung/qwen3-14b-abliterated:q5_K_M",
                    "messages": [{"role": "user", "content": "hi"}],
                    "stream": False,
                    "options": {"num_predict": 1},
                    "keep_alive": "30m"
                }, timeout=360)  # long timeout so a slow HDD reload completes
                print("[SUPERVISOR] Keep-alive ping sent (brain stays loaded)", flush=True)
            except Exception as e:
                print(f"[SUPERVISOR] keep-alive error: {e}", flush=True)
    threading.Thread(target=_keep_alive, daemon=True).start()

    while True:
        try:
            user, sara = _get_last_exchange()
            if user and sara:
                # Track the task Sara was asked
                _last_task = user
                # If Sara's response is a stall, prompt her to continue
                if _is_stall(sara):
                    now = time.time()
                    # Don't spam - only prompt once per stall (cooldown 20s)
                    if now - _last_stall_time > 20:
                        print(f"[SUPERVISOR] Detected stall: '{sara[:60]}...'")
                        _prompt_sara_to_continue(_last_task)
                        _last_stall_time = now
        except Exception as e:
            print(f"[SUPERVISOR] loop error: {e}")
        time.sleep(5)  # check every 5 seconds


if __name__ == "__main__":
    run()
