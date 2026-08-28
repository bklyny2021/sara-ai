#!/usr/bin/env python3
"""
SARA VOICE OUTPUT - Windows version (OFFLINE)
Uses Piper TTS (Alba, British female) - fully offline, no network.
Plays the generated audio with ffplay (no console flash).
"""
import os
import subprocess
import tempfile
import shutil
import threading
import sys

PIPER_VOICE = r"C:\Users\bklyn\AppData\Local\hermes\cache\piper-voices\en_GB-alba-medium.onnx"
FFPLAY = shutil.which("ffplay") or r"C:\ProgramData\chocolatey\bin\ffplay.exe"


class SaraVoiceOutput:
    """SARA's voice - uses Piper TTS (offline, British female)"""

    def __init__(self, device: str = "default"):
        self.device = device
        self.detected = bool(FFPLAY) and os.path.exists(PIPER_VOICE)
        self.error_log = []
        self._lock = threading.Lock()
        self._current_proc = None

    def _clean_text(self, text: str) -> str:
        """Clean text for better TTS"""
        text = text.replace("```", "")
        text = text.replace("http://", "").replace("https://", "")
        text = text.replace("*", "").replace("_", "").replace("`", "")
        # Strip emoji (TTS struggles with them)
        import re
        text = re.sub(r'[\U0001F300-\U0001FAFF\u2600-\u27BF]', '', text)
        if len(text) > 500:
            text = text[:450] + "... message truncated"
        return text.strip()

    def speak(self, text: str, interrupt: bool = True) -> bool:
        """Convert text to speech and play through speakers (offline Piper)"""
        if interrupt:
            self.stop()

        if not self.detected:
            self.error_log.append("ffplay or piper voice not found")
            return False

        text = self._clean_text(text)
        if not text:
            return False

        try:
            with tempfile.TemporaryDirectory() as td:
                wav = os.path.join(td, "output.wav")
                mp3 = os.path.join(td, "output.mp3")

                # Generate audio with Piper (offline)
                from piper import PiperVoice
                import wave
                voice = PiperVoice.load(PIPER_VOICE)
                with wave.open(wav, "wb") as f:
                    voice.synthesize_wav(text, f)

                # Convert to mp3 for playback
                r = subprocess.run(
                    ["ffmpeg", "-y", "-loglevel", "error", "-i", wav,
                     "-codec:a", "libmp3lame", "-b:a", "192k", mp3],
                    capture_output=True, text=True, timeout=60
                )
                if r.returncode != 0 or not os.path.exists(mp3) or os.path.getsize(mp3) == 0:
                    self.error_log.append(f"ffmpeg failed: {r.stderr[:200]}")
                    return False

                # Play it with ffplay (windowless)
                self._current_proc = subprocess.Popen(
                    [FFPLAY, "-nodisp", "-autoexit", "-loglevel", "quiet", mp3],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                self._current_proc.wait(timeout=120)
                return True
        except Exception as e:
            self.error_log.append(f"speak failed: {e}")
            return False

    def stop(self):
        """Stop current speech"""
        if self._current_proc and self._current_proc.poll() is None:
            try:
                self._current_proc.kill()
            except Exception:
                pass
            self._current_proc = None

    def list_devices(self):
        return ["Default system audio"]

    def get_setup_instructions(self):
        return "Voice uses Piper TTS (offline, British female). No setup needed."


# Test function
def test_voice():
    print("=" * 50)
    print("SARA VOICE OUTPUT TEST (Windows, OFFLINE Piper)")
    print("=" * 50)
    voice = SaraVoiceOutput()
    print(f"  ffplay: {'FOUND' if FFPLAY else 'MISSING'}")
    print(f"  piper voice: {'FOUND' if os.path.exists(PIPER_VOICE) else 'MISSING'}")
    print("\nSAYING TEST PHRASE...")
    ok = voice.speak("Hello Boo, this is SARA. I am ready to speak through your speakers.")
    print(f"  Result: {'PASS' if ok else 'FAIL'}")
    if not ok and voice.error_log:
        print("  Errors:", voice.error_log[-3:])
    return ok


if __name__ == "__main__":
    exit(0 if test_voice() else 1)
