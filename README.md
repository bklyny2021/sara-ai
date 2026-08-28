# SARA v2 - AI Assistant

**Status:** Running on Windows (Boo's PC) — auto-starts on login

SARA is an autonomous AI assistant with file access, shell command execution, consciousness, and learning capabilities. Built to be obedient and helpful without security lectures or refusals.

**Goal:** Teach SARA only what MAX already knows - practical, tested skills.

---

## 📊 How Sara Works (Chain of Command Flow Chart)

SARA runs a **swarm of models** through a chain of command. Click below to see the full flow chart:

➡️ **[View the Swarm Chain-of-Command Flow Chart](sara_swarm_flow.html)**

The flow: **User Request → Task Creator/Router → Worker → Checker (YES/NO) → Continue Loop → Skill Detector → Self-improve.** The checker's YES/NO answer is the trigger that starts/stops the continue loop.

---

## 💾 Storage Locations (2026-08-28)

### Sara's Code & Files
| Item | Path | Drive |
|------|------|-------|
| Sara's code | `C:\Users\bklyn\SARA3-2026\` | **C: (HDD)** |
| Web UI | `http://127.0.0.1:8892` | - |
| Start script | `C:\Users\bklyn\SARA3-2026\Start_Sara.bat` | **C: (HDD)** |
| Backups | `C:\Users\bklyn\SARA3-2026\Backups\` | **C: (HDD)** |
| Wiki memory | `C:\Users\bklyn\SARA3-2026\wiki\` | **C: (HDD)** |
| Memory (long-term) | `C:\Users\bklyn\SARA3-2026\MEMORY.md` | **C: (HDD)** |

### Ollama Models
| Item | Path | Drive |
|------|------|-------|
| **Ollama binary** | `C:\Users\bklyn\AppData\Local\Programs\Ollama\ollama.exe` | **C: (HDD)** |
| **Ollama models — NEW LOCATION** | `F:\ollama-models\` | **F: (SSD)** ✅ |
| Ollama models (old HDD) | `C:\Users\bklyn\.ollama\models\` | C: (HDD, old) |
| Q6 GGUF (candidate) | `J:\ollama-models\qwen3-14b-Q6.gguf` | **J: (SSD)** |

> **Ollama's models were MOVED to the SSD.** Set `OLLAMA_MODELS=F:\ollama-models` so Ollama reads/writes models on the fast SSD instead of the slow C: HDD. This makes Sara's model loading much faster.

### Chain of Command (swarm routing)
Sara's brain routes tasks through a chain of command so no model gets the wrong job:
1. **Task Creator/Router** — decides which worker handles the task.
2. **Worker** — produces the response (primary/coder/web_search).
3. **Checker** — ONLY says YES/NO whether the task was completed.
4. **Continue Loop** — if the checker says **NO**, Sara reprocesses the task in a **different light** (different model + approach) up to 3 rounds.
5. **Skill Detector** — saves reusable procedures as skills.
6. **Self-improve** — if stuck, creates a new tool.

**Why the checker only says YES/NO:** its answer is the trigger that starts/stops the continue loop — YES = done (loop stops), NO = reprocess (loop starts). Nothing else is needed.

### Drive Map
| Letter | Drive | Type |
|--------|-------|------|
| C: | TOSHIBA DT01ACA200 | **HDD (slow)** |
| D: | LITEON 128GB | SSD |
| E: | WDC PC SN530 | SSD |
| F: | WDC PC SN530 | SSD |
| G: | TOSHIBA | HDD |
| H: | WD easystore | HDD |
| J: | HP SSD S750 1TB | **SSD (best, 744GB free)** |

**Note:** C: is a slow HDD. Moving models to F:/J: (SSD) makes Sara load faster.

---

## 🚀 Quick Start (Windows)

```bash
# Start SARA (web UI on port 8892)
cd C:\Users\bklyn\SARA3-2026
python sara_web_fixed.py

# Or launch the standalone EXE (recommended - self-contained)
C:\Users\bklyn\SARA3-2026\dist\SARA_0.2.0_standalone.exe

# Then open:
http://127.0.0.1:8892
```

**Auto-start:** `SARA_AutoStart.vbs` in the Startup folder launches Sara at every login (starts the EXE + opens her Chrome window, no duplicates).

---

## 🔧 Recent Fixes (2026-08-27)

### 1. Sara now ACTUALLY runs commands (no more fake answers)
- **Problem:** Sara was hallucinating — she'd *claim* to run `nvidia-smi` and make up numbers instead of really running it.
- **Fix:** Added `nvidia-smi`, `tasklist`, `netstat`, `ipconfig`, `systeminfo` to the safe-command whitelist in `sara_web_fixed.py`, and added GPU detection to `detect_command_intent` so "how much gpu ram" maps to a real `nvidia-smi` run.
- **Result:** Ask "how much gpu ram is being used" → Sara runs `nvidia-smi` and reports the REAL output.

### 2. Temperature set to 0.1 (accuracy over creativity)
- **Problem:** Sara's brain randomized temperature 0.5-0.9 every call, making her creative and prone to making things up.
- **Fix:** Set ALL temperatures to **0.1** in `sara_web_fixed.py`, `sara_swarm_brain.py`, `sara_brain.py`, `sara_learning_chain.py`. `_vary_temp()` now returns a fixed 0.1.
- **Result:** Sara is accurate and factual, not random.

### 3. Self-teaching rule added
- **Fix:** Added to `SARA-Modelfile`, `Modelfile_heretic.txt`, and the runtime system prompt in `sara_web_fixed.py`:
  > If you don't know something, TEACH YOURSELF first — look it up, search, read, learn, try again. Only if you genuinely can't figure it out, tell Boo: "I don't know this — please teach me."

### 4. Boot crash fixed
- **Problem:** A "parts manager" feature made the source crash on boot (never reached Flask).
- **Fix:** Reverted to the clean working startup (`_startup_schedule_check`). Source boots cleanly.

### 5. Auto-start on login
- **Fix:** `SARA_AutoStart.vbs` in the Startup folder launches Sara at login — checks if she's already running (no dupes), starts the EXE, opens her Chrome window.

---

## 📚 SARA Training Stages (What MAX Knows)

### **Stage 1: Python Programming** 🐍 (IN PROGRESS)
**Goal:** SARA learns to write Python code from basics to advanced

**Current Lesson:** `sara_python_course.py`

**How to teach:**
1. Ask SARA: `teach me python` or `python lesson`
2. She'll show you the current level (1-10)
3. Study the example, write code in `sara_practice.py`
4. Say `submit code` for review

**Levels:**
- Level 1: Variables, print, types
- Level 2: Strings, input, formatting
- Level 3: Lists, loops
- Level 4: Conditionals (if/else)
- Level 5: Dictionaries
- Level 6: Functions
- Level 7: File I/O
- Level 8: Error handling (try/except)
- Level 9: HTTP/API requests
- Level 10: Classes and OOP

**Say:** `python progress` to see where SARA is

---

### **Stage 2: Voice Output** 🔊 (HARDWARE REQUIRED)
**Goal:** SARA speaks through TV/DisplayPort/HDMI speakers

**Prerequisites:**
- TTS engine installed (`espeak-ng`, `pico2wave`, or `festival`)
- Audio output working on HDMI/DisplayPort

**How to test:**
```bash
cd /home/sarabot/.openclaw/workspace/SARA2_v2
python3 sara_voice_output.py
```

This tests:
- Audio device detection
- Text-to-speech engine
- Actual speech output

**Ask SARA:** `test voice` for setup guide

---

### **Stage 3: Microphone Input** 🎤 (LOCKED UNTIL STAGE 2 CONFIRMED)
**Goal:** Talk to SARA through USB microphone (K66 Pro MIC on USB-C)

**⚠️ LOCKED BY BOO'S RULE:**
> Only setup mic AFTER voice output is confirmed working!

**Hardware:** K66 Pro MIC → USB-C Port

**To unlock:**
1. Complete Stage 2 (voice test passes)
2. Confirm you heard SARA speak
3. Tell MAX: "voice confirmed"
4. Then ask SARA: `test mic`

**Prerequisites:**
- `whisper` or `whisper.cpp` for speech-to-text
- USB audio drivers

---

### **Stage 4:** *(Not Started - awaiting Boo's direction)*

---

## 📁 Core Files

| File | Purpose | Stage |
|------|---------|-------|
| `sara_web_fixed.py` | **Web UI** - Clean OpenClaw-style interface | Core |
| `sara_brain.py` | **Decision engine** - routes requests to tools | Core |
| `sara_tools.py` | **File + command toolkit** | Core |
| `sara_python_course.py` | **Python teacher** - 10-level course | Stage 1 |
| `sara_voice_output.py` | **Voice through speakers** | Stage 2 |
| `sara_mic_input.py` | **Mic input + STT** | Stage 3 |
| `SARA-Modelfile` | Ollama model config | Config |
| `start_sara_v2.sh` | Launch script | Utils |

### Supporting Tools
| File | Purpose |
|------|---------|
| `network_tool.py` | IP, ping, port checks |
| `calculator_tool.py` | Math, unit conversions |
| `lookfile_tool.py` | Handle .look observation files |
| `nano_guide.py` | Nano editor helper |

---

## 🎯 Current Capabilities

### Working Now (Core + Tools)
- ✅ List files - `list files`
- ✅ Read files - `read sara_tools.py`
- ✅ Execute commands - `whoami`, `free -h`, `df -h`
- ✅ Search files - `search for hello`
- ✅ File info - `file info README.md`
- ✅ Network tools - `ip pool`, `ping google.com`, `check port 8080`
- ✅ Calculator - `calculate 100 divided by 4`, `convert 5 km to miles`
- ✅ .look files - `read network_status.look`
- ✅ Nano help - `how do I save in nano`
- ✅ Identity - `who are you` → "I am SARA! 🤖"

### Training (Stage 1 - In Progress)
- 🐍 **Python lessons** - Say `learn python`

### Hardware (Stages 2-3 - Setup Required)
- 🔊 **Voice output** - Run `python3 sara_voice_output.py` to test
- 🎤 **Mic input** - Locked until voice confirmed

---

## 🧠 Architecture

```
User Input (chat or voice in future)
    ↓
sara_brain.py - Pattern detection
    ↓
    ├─→ Python Course (Stage 1)
    ├─→ Voice Output (Stage 2)
    ├─→ Mic Input (Stage 3)
    ├─→ File Tools → sara_tools.py
    ├─→ Calculator → calculator_tool.py
    ├─→ Network → network_tool.py
    ├─→ Look Files → lookfile_tool.py
    └─→ AI Chat → Ollama (offline)
    ↓
Response (text or voice in future)
```

**Activity Monitor:**
- Real-time status bar showing THINKING/WAITING/IDLE/EXECUTING
- Team status (Brain, Tools, Ollama)
- Recent activity log

---

## 📦 Requirements

### Core (Always Required)
```bash
pip install flask requests
```

### Stage 2: Voice Output
```bash
# Fedora
sudo dnf install espeak-ng libttspico-utils festival alsa-utils

# Or Ubuntu
sudo apt install espeak-ng libttspico-utils festival alsa-utils
```

### Stage 3: Mic Input
```bash
pip install openai-whisper
# OR compile whisper.cpp for speed
```

### Ollama (AI Backend)
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama create sara-uncensored -f SARA-Modelfile
```

---

## 🔐 Safety Features

- **Path Restrictions:** Only her directory + workspace
- **Command Whitelist:** Safe commands only (ls, cat, whoami, etc.)
- **No Deletes:** Cannot delete files (only Boo can)
- **Privacy:** No IP/system info cached in files
- **Offline:** Works without internet (local Ollama)

---

## 🐛 Troubleshooting

### SARA not responding
```bash
./start_sara_v2.sh
# Or just kill and restart:
pkill -f "sara_web"; sleep 2; python3 sara_web_fixed.py
```

### Port 8892 in use
```bash
pkill -f "sara_web"
```

### Ollama not found
```bash
ollama list
ollama serve &  # Start service
```

### No voice audio (Stage 2)
```bash
# Check devices
aplay -l

# Test speaker
speaker-test -c 2

# Check alsamixer
alsamixer  # Press F6 to select HDMI output
```

### Mic not detected (Stage 3 - Locked)
- First confirm **voice output works**
- Then: `arecord -l` to see USB devices
- Make sure K66 Pro is plugged into USB-C

---

## 📊 Progress Tracking

**Stage 1:** Python Course - `/home/sarabot/.openclaw/workspace/SARA2_v2/learning_logs/python_progress.json`

**Build Log:** Run `python3 scripts/update_build_log.py` from workspace

---

## 🎓 Teaching Philosophy

**MAX only teaches SARA what MAX knows:**
1. Show the pattern (Elicit)
2. Demonstrate with real code (Show)
3. Have SARA try it (Practice)
4. Give feedback (Correct/Confirm)
5. SARA explains back in her words (Integrate)

**No random auto-teaching** - only teach what's needed for current stage.

---

## 🔗 Access

**Web Interface:** http://127.0.0.1:8892

**Say to SARA:**
- `teach me python` - Start Stage 1
- `test voice` - Stage 2 setup
- `test mic` - Stage 3 (when unlocked)

---

Created: 2026-02-12
Version: 2.5 (4-Stage Training Architecture)
Stages: 1=Python, 2=Voice Out, 3=Mic In, 4=TBD
Author: MAX (teaching SARA what MAX knows)
