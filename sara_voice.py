#!/usr/bin/env python3
"""
SARA VOICE - fully offline voice assistant.
Listens on the mic, detects wake word "SARA", converts speech to text
with faster-whisper (offline), processes through Sara's brain, and
speaks the response with Piper (offline).

Wake word: "SARA" (or "hey Sara")
"""
import os
import sys
import time
import threading
import subprocess
import tempfile
import wave
import io

# Offline STT
try:
    from faster_whisper import WhisperModel
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

# Audio capture
try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False

SARA_DIR = r"C:\Users\bklyn\SARA3-2026"
WAKE_WORDS = ["sara", "hey sara", "sarah", "hey sarah"]
RATE = 16000
CHUNK = 1024
FORMAT = 8  # pyaudio.paInt16
CHANNELS = 1

class SaraVoice:
    """Offline voice assistant with wake word detection"""

    def __init__(self):
        self.whisper = None
        self.audio = None
        self.listening = False
        self._load_models()

    def _load_models(self):
        """Load offline STT model"""
        if WHISPER_AVAILABLE:
            try:
                # small model - good balance of speed/accuracy, runs on CPU
                self.whisper = WhisperModel("small", device="cpu", compute_type="int8")
                print("✅ Whisper STT loaded (offline)")
            except Exception as e:
                print(f"⚠️ Whisper load failed: {e}")
                self.whisper = None
        if PYAUDIO_AVAILABLE:
            try:
                self.audio = pyaudio.PyAudio()
                print("✅ Microphone ready")
            except Exception as e:
                print(f"⚠️ PyAudio failed: {e}")
                self.audio = None

    def _record(self, duration=5):
        """Record audio from mic for a duration"""
        if not self.audio:
            return None
        stream = self.audio.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                                 input=True, frames_per_buffer=CHUNK)
        frames = []
        for _ in range(int(RATE / CHUNK * duration)):
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                frames.append(data)
            except:
                break
        stream.stop_stream()
        stream.close()
        return b"".join(frames)

    def _transcribe(self, audio_bytes):
        """Convert audio bytes to text using faster-whisper (offline)"""
        if not self.whisper or not audio_bytes:
            return ""
        try:
            # Write to temp wav
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                with wave.open(f, "wb") as wf:
                    wf.setnchannels(CHANNELS)
                    wf.setsampwidth(2)
                    wf.setframerate(RATE)
                    wf.writeframes(audio_bytes)
                tmp = f.name
            segments, _ = self.whisper.transcribe(tmp)
            text = " ".join(s.text for s in segments).strip()
            os.unlink(tmp)
            return text
        except Exception as e:
            print(f"Transcribe error: {e}")
            return ""

    def listen_for_wake(self, timeout=30):
        """Listen until wake word detected. Returns True if woken."""
        print("🎤 Listening for 'SARA'...")
        start = time.time()
        while time.time() - start < timeout:
            audio = self._record(duration=3)
            text = self._transcribe(audio).lower()
            if text:
                print(f"  heard: {text}")
                for w in WAKE_WORDS:
                    if w in text:
                        print("🔊 Wake word detected!")
                        return True
        return False

    def listen_for_command(self, duration=6):
        """Listen for a command after wake word"""
        print("🎤 Listening for command...")
        audio = self._record(duration=duration)
        text = self._transcribe(audio)
        print(f"  command: {text}")
        return text

    def speak(self, text):
        """Speak using Piper (offline)"""
        try:
            import sara_voice_output as voice
            v = voice.SaraVoiceOutput()
            return v.speak(text)
        except Exception as e:
            print(f"Speak error: {e}")
            return False

    def run(self):
        """Main loop - listen for wake word, then command, then respond"""
        if not self.whisper or not self.audio:
            print("❌ Voice not available (need faster-whisper + pyaudio)")
            return
        print("SARA Voice ready. Say 'SARA' to wake me.")
        while True:
            try:
                if self.listen_for_wake():
                    self.speak("Yes Boo?")
                    cmd = self.listen_for_command()
                    if cmd:
                        # Process through Sara's brain
                        try:
                            import sara_web_fixed as web
                            response = web.sara.ask_sara(cmd)
                            # Strip emoji for TTS
                            import re
                            clean = re.sub(r'[\U0001F300-\U0001FAFF\u2600-\u27BF]', '', response)
                            self.speak(clean)
                        except Exception as e:
                            print(f"Brain error: {e}")
                            self.speak("Sorry, I had trouble with that.")
            except KeyboardInterrupt:
                print("Stopping.")
                break
            except Exception as e:
                print(f"Loop error: {e}")
                time.sleep(1)

if __name__ == "__main__":
    v = SaraVoice()
    v.run()
