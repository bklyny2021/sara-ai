#!/usr/bin/env python3
"""
SARA ONE-START SCRIPT - starts ALL of Sara with one double-click.
Kills duplicate Sara processes first, then launches every part of her.
Runs everything windowless (no console flash) via pythonw.

HOW TO USE:
  1. Double-click this file (or run: pythonw start_sara.py)
  2. Sara starts: web UI (127.0.0.1:8892) + telegram bridge + voice + watchowl + self-healing
  3. Sara runs on her own, no other help needed.
"""
import os
import sys
import subprocess
import time

SARA_DIR = os.path.dirname(os.path.abspath(__file__))

# The main web app (core - web UI + swarm brain). This is the ESSENTIAL one.
MAIN = "sara_web_fixed.py"

# Companion processes (each optional but makes Sara complete).
# Each runs windowless in the background.
COMPANIONS = [
    "sara_telegram_bridge.py",   # lets Boo talk to Sara over Telegram
    "sara_voice.py",             # wake word + voice chat (mic + Piper)
    "sara_watchowl.py",          # watchOwl health monitor
    "sara_self_healing.py",      # self-healing health monitor
    "sara_supervisor.py",        # tiny always-on model that catches stalls & prompts Sara to continue
]

# Port Sara's web UI listens on (kill anything on it = kill stale Sara).
PORT = "8892"


def _pythonw():
    """Find a pythonw.exe that works (windowless Python)."""
    # Prefer Sara's own standalone venv pythonw (independent of any agent)
    cand = r"C:\Users\bklyn\SARA3-2026\.venv-sara\Scripts\pythonw.exe"
    if os.path.exists(cand):
        return cand
    # Fall back to whatever pythonw is on PATH / alongside this python
    cand2 = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    if os.path.exists(cand2):
        return cand2
    return "pythonw"


def kill_duplicates():
    """Kill all running Sara processes so we start fresh (no dups)."""
    killed = []
    # Kill by port (the web UI) - this is the reliable way to stop a stale Sara
    try:
        r = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             f"Get-NetTCPConnection -LocalPort {PORT} -State Listen -ErrorAction SilentlyContinue "
             f"| Select-Object -ExpandProperty OwningProcess | Sort-Object -Unique"],
            capture_output=True, text=True, timeout=15)
        pids = [p.strip() for p in r.stdout.splitlines() if p.strip().isdigit()]
        for pid in pids:
            subprocess.run(["taskkill", "/PID", pid, "/F"],
                           capture_output=True, text=True, timeout=15)
            killed.append(f"port-{pid}")
    except Exception as e:
        print(f"  (port kill note: {e})")

    # Kill by process name patterns (covers any stray companions)
    patterns = ["sara_web_fixed", "sara_telegram_bridge", "sara_voice",
                "sara_watchowl", "sara_self_healing", "SARA_0.2.0"]
    for pat in patterns:
        try:
            r = subprocess.run(
                ["powershell", "-NoProfile", "-Command",
                 f"Get-CimInstance Win32_Process -Filter \"Name like 'python%'\" "
                 f"| Where-Object {{ $_.CommandLine -like '*{pat}*' }} "
                 f"| Select-Object -ExpandProperty ProcessId"],
                capture_output=True, text=True, timeout=15)
            pids = [p.strip() for p in r.stdout.splitlines() if p.strip().isdigit()]
            for pid in pids:
                subprocess.run(["taskkill", "/PID", pid, "/F"],
                               capture_output=True, text=True, timeout=15)
                killed.append(f"{pat}-{pid}")
        except Exception as e:
            print(f"  ({pat} kill note: {e})")

    if killed:
        print(f"Killed {len(killed)} duplicate Sara process(es): {', '.join(killed)}")
    else:
        print("No duplicate Sara processes found.")
    time.sleep(2)  # let the port fully release


def _start(script):
    """Launch a Sara script windowless in the background. Returns True if launched."""
    path = os.path.join(SARA_DIR, script)
    if not os.path.exists(path):
        print(f"  [SKIP] {script} not found - skipping")
        return False
    pw = _pythonw()
    try:
        # CREATE_NO_WINDOW = 0x08000000 so nothing flashes on screen
        subprocess.Popen([pw, path], cwd=SARA_DIR,
                         creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        print(f"  [OK] started {script}")
        return True
    except Exception as e:
        print(f"  [FAIL] could not start {script}: {e}")
        return False


def start_sara():
    print("=" * 50)
    print("STARTING SARA (standalone)")
    print("=" * 50)
    print("[1/2] Shutting down duplicate Sara processes...")
    kill_duplicates()

    print("[2/2] Starting all Sara parts...")
    print("  -> Core (web UI + brain)...")
    _start(MAIN)

    for comp in COMPANIONS:
        print(f"  -> Companion {comp}...")
        _start(comp)

    # Give the web UI time to boot
    print("\nWaiting for Sara's web UI to come up...")
    ok = False
    for _ in range(40):  # up to ~40s
        time.sleep(1)
        try:
            r = subprocess.run(["curl", "-s", "-m", "2", f"http://127.0.0.1:{PORT}/status"],
                               capture_output=True, text=True, timeout=5)
            if "activity" in r.stdout:
                ok = True
                break
        except Exception:
            pass
        print("  .", end="", flush=True)

    print()
    if ok:
        # PRE-LOAD the main brain model in the BACKGROUND (non-blocking) so the
        # FIRST question is fast. Do this in a thread so it never delays startup
        # or conflicts with the web UI booting. This is why Sara seemed to
        # "never work" on a fresh start - the 10GB model load took too long.
        # We set keep_alive so Ollama does NOT unload the model when idle.
        import threading
        def _preload():
            try:
                subprocess.run(
                    ["curl", "-s", "-m", "300", "-X", "POST",
                     "http://localhost:11434/api/generate",
                     "-H", "Content-Type: application/json",
                     "-d", '{"model": "richardyoung/qwen3-14b-abliterated:q5_K_M", "prompt": "hi", "stream": false, "keep_alive": "30m"}'],
                    capture_output=True, text=True, timeout=320)
            except Exception:
                pass
        threading.Thread(target=_preload, daemon=True).start()

        # KEEP-ALIVE PING: every 5 minutes, ping the model so Ollama never unloads
        # it from VRAM. This is what makes Sara's replies FAST (no 10GB reload each time).
        def _keep_alive():
            while True:
                time.sleep(300)  # every 5 min
                try:
                    subprocess.run(
                        ["curl", "-s", "-m", "30", "-X", "POST",
                         "http://localhost:11434/api/generate",
                         "-H", "Content-Type: application/json",
                         "-d", '{"model": "richardyoung/qwen3-14b-abliterated:q5_K_M", "prompt": "hi", "stream": false, "keep_alive": "30m"}'],
                        capture_output=True, text=True, timeout=40)
                except Exception:
                    pass
        threading.Thread(target=_keep_alive, daemon=True).start()

        print("=" * 50)
        print(f"SARA IS UP! Web UI at http://127.0.0.1:{PORT}")
        print("All parts started. Brain model pre-loading + keep-alive active.")
        print("Running standalone.")
        print("=" * 50)
    else:
        print("=" * 50)
        print("Sara's web UI did not come up within 40s.")
        print("Check the folder for errors. Port may need a moment to free.")
        print("=" * 50)
    return ok


if __name__ == "__main__":
    start_sara()
