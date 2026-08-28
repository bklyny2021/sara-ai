#!/usr/bin/env python3
"""SARA WATCHOWL - Sara's own background heartbeat.
Runs silently (no console window - launch with pythonw.exe), checks every 2 min:
- due reminders/appointments/timers (fires them aloud)
- logs a heartbeat tick to a status file (no flashing windows)
- does NOT spin up any model/GPU while idle
Launched as part of Sara (sara_web_fixed), not as a separate tool."""
import os, sys, time, json, subprocess, threading
from datetime import datetime

BASE = r"C:/Users/bklyn/SARA3-2026"
# Ensure the Sara folder is on the path so 'import sara_scheduler' works
# even when this script is launched as a subprocess from a different cwd.
if BASE not in sys.path:
    sys.path.insert(0, BASE)
STATUS_FILE = os.path.join(BASE, "watchowl_status.json")
INTERVAL = 120  # seconds

def _log(msg):
    try:
        with open(os.path.join(BASE, "watchowl.log"), "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")
    except Exception:
        pass

def _speak(text):
    """Say something via Sara's voice worker - windowless."""
    try:
        worker = os.path.join(BASE, "sara_voice_worker.py")
        pythonw = r"C:\Users\bklyn\AppData\Local\hermes\hermes-agent\venv\Scripts\pythonw.exe"
        if not os.path.exists(pythonw):
            pythonw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
        subprocess.Popen([pythonw, worker, text],
                         creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    except Exception:
        pass

def tick():
    """One heartbeat pass."""
    try:
        # 1) Fire any due reminders/appointments/timers
        due = []
        try:
            import sara_scheduler as sched
            due = sched.check_due()
        except Exception as e:
            _log(f"scheduler error: {e}")
        for m in due:
            _speak(m)
            _log(f"FIRED: {m}")

        # 2) Write a quiet status file (no window, no model)
        try:
            st = {"last_tick": datetime.now().isoformat(), "due_fired": due}
            with open(STATUS_FILE, "w", encoding="utf-8") as f:
                json.dump(st, f)
        except Exception:
            pass
    except Exception as e:
        _log(f"tick error: {e}")

def main():
    # Duplicate-kill: only ONE WatchOwl runs. Kill any other watchowl process.
    _kill_dups()
    _log("WatchOwl started (silent heartbeat)")
    # Run one pass immediately, then loop
    tick()
    while True:
        time.sleep(INTERVAL)
        tick()

def _kill_dups():
    import os as _os, subprocess as _sp
    me = _os.getpid()
    try:
        out = _sp.run(["powershell", "-NoProfile", "-Command",
                       "Get-CimInstance Win32_Process | Where-Object { $_.Name -like '*pythonw*' -or $_.Name -like '*python*' } | Select-Object ProcessId,Name,CommandLine | ConvertTo-Json -Compress"],
                      capture_output=True, text=True, timeout=12)
        import json as _json
        try:
            procs = _json.loads(out.stdout or "[]")
            if isinstance(procs, dict):
                procs = [procs]
            for p in procs or []:
                pid = p.get("ProcessId")
                cmd = (p.get("CommandLine") or "")
                if pid and pid != me and "sara_watchowl" in cmd:
                    _sp.run(["taskkill", "/PID", str(pid), "/F"], capture_output=True, text=True, timeout=8)
                    _log(f"Killed duplicate WatchOwl PID {pid}")
        except Exception:
            pass
    except Exception:
        pass

if __name__ == "__main__":
    # Launch windowless if called with console; if already under pythonw, run directly.
    main()
