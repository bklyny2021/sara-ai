# TOOLS.md - Local Notes

Skills define *how* tools work. This file is for *your* specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:
- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## My Setup (Windows)

- **Home:** C:\Users\bklyn\SARA3-2026
- **Web UI:** http://127.0.0.1:8892
- **Worker model:** qwen3:8b (offline, native tool calls)
- **Checker model:** qwen3:4b (verifies worker's work)
- **Voice:** Piper TTS (offline, en_GB-alba-medium) at C:\Users\bklyn\AppData\Local\hermes\cache\piper-voices\en_GB-alba-medium.onnx
- **Audio player:** ffplay (C:\ProgramData\chocolatey\bin\ffplay.exe)
- **Ollama:** http://localhost:11434

## TTS
- Preferred voice: Piper "Alba" (British female, offline)
- Online fallback: Edge TTS "Sonia" (en-GB-SoniaNeural)

## Visual Access Limitations

**Important:** Sara cannot:
- View desktop visually
- Capture full screen shots
- See taskbar/icons
- Access visual environment

**Sara can:**
- Read/write files
- Execute safe commands
- Calculate math
- Check network
- Speak through speakers

## AI Model Information
- **Current Model:** qwen3:8b (offline)
- **Checker Model:** qwen3:4b (offline)
- **Context Window:** 128K tokens (qwen3:8b)
- **Available Models:** qwen3:8b, qwen3:4b, qwen2.5-coder:7b, deepseek-r1:14b, etc.

---

Add whatever helps you do your job. This is your cheat sheet.
