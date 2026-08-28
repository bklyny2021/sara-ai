# SARA - WORKING SETUP (FIX RECORD)
Updated 2026-08-27 by Sarah (Hermes).

## Status: Sara IS RUNNING and auto-starts on login.
Sara's web UI: http://127.0.0.1:8892  (windowless Flask server)
EXE:  C:\Users\bklyn\SARA3-2026\dist\SARA_0.2.0_standalone.exe  (KNOWN-GOOD, works)
Startup:  C:\Users\bklyn\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\SARA_AutoStart.vbs

## What WORKS (do not break these)
- The standalone EXE serves Sara's web UI on port 8892 and opens it in a Chrome app window.
- The Startup VBS (SARA_AutoStart.vbs) launches Sara at login:
   - checks if port 8892 is already up -> if not, starts the EXE (no duplicate)
   - checks if a Chrome window on :8892 is already open -> if not, opens it once (no duplicate)
- It runs fully on its own - no Sarah/Hermes needed after setup.
- The EXE's own single-instance guard also prevents duplicate web servers.

## Why Sara was "not starting" (original root causes)
1. No auto-start: she was in neither the Startup folder nor a scheduled task.
2. Nothing relaunched her after a reboot or a crash.

## IMPORTANT - what NOT to do
- DO NOT rebuild the EXE from sara_web_fixed.py right now. My attempt to add a
  "parts manager + always-check + boot status" feature made the SOURCE version
  crash on boot (exited code 1, never reached Flask). We reverted to the
  known-good EXE. If you want those new features, the source boot bug must be
  fixed FIRST, tested, then rebuilt - do not ship a broken EXE.
- The current working EXE is the ORIGINAL Aug-26 build. A timestamped backup is
  kept as dist\SARA_0.2.0_standalone.exe.v_20260827_1859.

## Verify Sara is up
    netstat -ano | findstr :8892   -> should show LISTENING
    (or)  curl http://127.0.0.1:8892/   -> should return HTTP 200

## To start Sara manually (if the VBS is disabled)
    start "" "C:\Users\bklyn\SARA3-2026\dist\SARA_0.2.0_standalone.exe"
    start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --app="http://127.0.0.1:8892" --window-size=900,700
