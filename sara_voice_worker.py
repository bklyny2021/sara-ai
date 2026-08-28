#!/usr/bin/env python3
"""SARA voice worker - runs Piper TTS in a SEPARATE PROCESS so a native
voice-engine crash can NEVER take down the main Sara web app."""
import os, sys, subprocess, tempfile, shutil, re

PIPER_VOICE = r"F:\SARA3-2026\voices\en_GB-alba-medium.onnx"
FFPLAY = shutil.which("ffplay") or r"C:\ProgramData\chocolatey\bin\ffplay.exe"

def clean(text):
    import re as _re
    text = text.replace("```", "")
    # Strip ALL urls: http/https, www, protocol-relative //..., and @url:`...` wrapped
    text = _re.sub(r'https?://\S+|www\.\S+', '', text)
    text = _re.sub(r'(?<![\w/])//[^\s`]+', '', text)
    text = _re.sub(r'@url:`[^`]*`', '', text)
    # Strip code fences and inline code
    text = _re.sub(r'```[\s\S]*?```', '', text)
    text = _re.sub(r'`[^`]*`', '', text)
    text = text.replace("*", "").replace("_", "").replace("`", "")
    # Strip emoji (TTS struggles with them)
    text = _re.sub(r'[\U0001F300-\U0001FAFF\u2600-\u27BF]', '', text)
    # Collapse extra whitespace
    text = _re.sub(r'\s+', ' ', text).strip()
    if len(text) > 500:
        text = text[:450] + "... message truncated"
    return text.strip()

def speak(text):
    if not os.path.exists(PIPER_VOICE):
        print("ERR voice-missing"); return 1
    if not FFPLAY or not os.path.exists(FFPLAY):
        print("ERR ffplay-missing"); return 1
    text = clean(text)
    if not text:
        print("ERR empty"); return 1
    try:
        with tempfile.TemporaryDirectory() as td:
            wav = os.path.join(td, "out.wav")
            mp3 = os.path.join(td, "out.mp3")
            from piper import PiperVoice
            import wave
            voice = PiperVoice.load(PIPER_VOICE)
            with wave.open(wav, "wb") as f:
                voice.synthesize_wav(text, f)
            r = subprocess.run(["ffmpeg","-y","-loglevel","error","-i",wav,
                                "-codec:a","libmp3lame","-b:a","192k",mp3],
                               capture_output=True, text=True, timeout=60)
            if r.returncode != 0 or not os.path.exists(mp3) or os.path.getsize(mp3)==0:
                print("ERR ffmpeg"); return 1
            p = subprocess.Popen([FFPLAY,"-nodisp","-autoexit","-loglevel","quiet",mp3],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                 creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            p.wait(timeout=120)
            print("OK"); return 0
    except SystemExit:
        # native exit from piper/espeak - still just this child
        print("ERR piper-exit"); return 3
    except Exception as e:
        print("ERR", str(e)[:100]); return 4

if __name__ == "__main__":
    text = sys.argv[1] if len(sys.argv) > 1 else ""
    sys.exit(speak(text))
