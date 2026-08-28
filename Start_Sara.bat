@echo off
REM ============================================
REM  START SARA - double-click this to run her
REM  Kills duplicates, starts every part of Sara
REM  Runs windowless (pythonw), no console flash
REM ============================================
cd /d "%~dp0"

REM Use the same pythonw that runs her
set PYTHONW=C:\Users\bklyn\AppData\Local\hermes\hermes-agent\venv\Scripts\pythonw.exe
if not exist "%PYTHONW%" set PYTHONW=pythonw

REM Launch the one-start script windowless
start "" "%PYTHONW%" "%~dp0start_sara.py"

echo Starting Sara...
echo She will be ready at http://127.0.0.1:8892
echo This window will close automatically.
timeout /t 3 >nul
