# SARA Swarm - AI Assistant

**Status:** Running on Windows (Boo's PC) — auto-starts on login

SARA Swarm is an autonomous AI assistant with a **swarm of models** (task router, checker, coder, web-search, skill detector) that routes each request to the right model. Built to be obedient and helpful without security lectures or refusals.

**Goal:** Teach SARA only what MAX already knows - practical, tested skills.

---

## ✨ What's New in this Build

- **Swarm chain of command** — tasks route to the right model (task router → worker → checker → skill detector).
- **Fast path for simple questions** — simple math/greetings/basics use a small fast model (~15s instead of ~90s).
- **Checker only says YES/NO** — its answer triggers the continue loop (reprocess in a different light if not done).
- **Skill detector** — saves reusable procedures as skills.
- **Models on SSD** — faster loading (set `OLLAMA_MODELS` to an SSD path).
- **Standalone startup** — `Start_Sara.bat` uses a local Python, independent of any agent.

---

## 📊 HOW SARA WORKS — Swarm Chain of Command (FIRST)

```
        ┌─────────────┐
        │ USER REQUEST │
        └──────┬──────┘
               ▼
   ┌───────────────────────┐
   │ 1. TASK CREATOR/ROUTER │  decides which worker handles it
   └───────────┬───────────┘
               ▼
        ┌──────────────┐
        │ 2. WORKER     │  coder / web_search / primary
        └──────┬───────┘
               ▼
   ┌──────────────────────┐
   │ 3. CHECKER (YES/NO)  │  "was the task completed?"
   └───────────┬──────────┘
               │
     ┌─────────┴─────────┐
     ▼                   ▼
  YES (done)         NO (continue)
     │                   │
     │            ┌──────▼───────┐
     │            │ 4. REPROCESS  │  different model + approach (3 rounds)
     │            │  DIFFERENTLY  │
     │            └──────┬───────┘
     │                   │ (loop back to 2)
     ▼                   ▼
  RETURN ANSWER    ┌──────────────────┐
                   │ 5. SKILL DETECTOR │  save reusable procedure
                   └────────┬─────────┘
                            ▼
                   ┌──────────────────┐
                   │ 6. SELF-IMPROVE   │  create new tool if stuck
                   └──────────────────┘
```

**Why the checker only says YES/NO:** its answer is the trigger that starts/stops the continue loop. **YES** = done (loop stops). **NO** = reprocess in a different light (loop starts).

Full interactive version: [sara_swarm_flow.html](sara_swarm_flow.html)

---

## 🖥️ Hardware / GPU Requirements

Sara's swarm runs models **locally** through Ollama. Model loading uses **VRAM (GPU memory)**, not just system RAM.

### Minimum GPU (recommended)
| Spec | Minimum | Recommended (Boo's setup) |
|------|---------|---------------------------|
| VRAM | **12 GB** | **14 GB** (across 1-2 GPUs) |
| GPU | Any NVIDIA (CUDA) | RTX 4060 Ti (8GB) + GTX 1660 Ti (6GB) |
| RAM | 24 GB | 32 GB |
| Storage | SSD strongly recommended | SSD (models load 5-10x faster than HDD) |
| CPU | 6+ cores | Ryzen 5 7600X (6-core/12-thread) |

### Why VRAM matters
Each swarm model uses a chunk of VRAM when loaded. Ollama loads/unloads models on demand:

| Model | VRAM when loaded |
|-------|------------------|
| Primary brain (Q5, 14B) | ~9.8 GB |
| Primary brain (Q6, 14B) | ~11.3 GB |
| Checker (qwen3:4b) | ~2.3 GB |
| Supervisor (gemma3:1b) | ~0.8 GB |
| Coder (qwen2.5-coder:7b) | ~7.5 GB |
| Web search (14B) | ~8.4 GB |

**Peak concurrent usage:** primary brain + supervisor = ~10.6 GB (Q5) or ~12.1 GB (Q6). Both fit in 14 GB VRAM.

> ⚠️ **Model loading speed depends on your drive.** On a slow HDD, loading an 11 GB model can take 5+ minutes. **Use an SSD** (or set `OLLAMA_MODELS` to an SSD path) for fast loads. If VRAM runs out, models spill to system RAM (slow) — keep at least 12 GB VRAM.

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

> ⚠️ **IMPORTANT:** Sara's code has **hardcoded paths** from Boo's machine (`C:\Users\bklyn\SARA3-2026\...`). Before running on YOUR machine, you must update these to your own paths.

### Installation

```bash
# 1. Clone the repo
git clone https://github.com/bklyny2021/sara-ai.git
cd sara-ai

# 2. Fix the hardcoded paths (replace bklyn with YOUR username)
#    The main files that reference C:\Users\bklyn\SARA3-2026 are:
#    - sara_web_fixed.py
#    - sara_swarm_brain.py
#    - sara_brain.py
#    - sara_supervisor.py
#    - sara_browser.py
#    - and the tools/ folder
#    Use find-and-replace: "C:/Users/bklyn/SARA3-2026" -> "C:/Users/YOURNAME/SARA3-2026"

# 3. Install dependencies
pip install flask requests wikipedia

# 4. Install Ollama and pull the models Sara needs:
#    - Primary brain: ollama pull richardyoung/qwen3-14b-abliterated:q5_K_M
#    - Checker:       ollama pull qwen3:4b
#    - Supervisor:    ollama pull gemma3:1b
#    - Coder:         ollama pull qwen2.5-coder:7b-instruct-q8_0
#    - Web search:    ollama pull huihui_ai/qwen2.5-abliterate:14b

# 5. Start Sara
python sara_web_fixed.py

# 6. Open her web UI
http://127.0.0.1:8892
```

**Or launch the standalone EXE (recommended - self-contained):**
```bash
C:\Users\bklyn\SARA3-2026\dist\SARA_0.2.0_standalone.exe
```

**Auto-start:** `SARA_AutoStart.vbs` in the Startup folder launches Sara at every login (starts the EXE + opens her Chrome window, no duplicates).

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
