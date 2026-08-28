@echo off
REM ============================================
REM  START SARA - double-click this to run her
REM  Kills duplicates, starts every part of Sara
REM  Runs windowless (pythonw), no console flash
REM  Uses a LOCAL standalone Python (not tied to any agent)
REM ============================================
cd /d "%~dp0"

REM 1) Prefer Sara's own venv in this folder (created with: uv venv .venv-sara)
set PYTHONW=%~dp0.venv-sara\Scripts\pythonw.exe
if not exist "%PYTHONW%" (
    REM 2) Fall back to a pythonw on the system PATH
    set PYTHONW=pythonw
)

REM Launch the one-start script windowless
start "" "%PYTHONW%" "%~dp0start_sara.py"

echo Starting Sara...
echo She will be ready at http://127.0.0.1:8892
echo This window will close automatically.
timeout /t 3 >nul
