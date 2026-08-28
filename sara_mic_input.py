#!/usr/bin/env python3
"""
🎤 SARA MIC INPUT - Stage 3 of 4 (AFTER voice output confirmed!)
Listen to USB-C K66 Pro MIC and convert to text for SARA

⚠️  BOO'S INSTRUCTION: Only setup after voice output is confirmed working!
"""

import os
import subprocess
import shutil
from typing import Optional, Callable


STAGE_LOCKED = True  # Locked until voice output is confirmed


class SaraMicInput:
    """
    Handle voice input for SARA through USB microphone
    K66 Pro MIC on USB-C Port
    """
    
    def __init__(self, device: str = "default"):
        self.device = device
        self.recorder = None
        self.stt_engine = None  # Speech-to-text
        self.is_enabled = False  # Disabled until voice output confirmed
        
        # USB-C K66 Pro MIC specific settings
        self.mic_name = "K66 Pro MIC"
        self.usb_port = "USB-C"
        
        # Audio settings
        self.sample_rate = 16000  # Good for speech
        self.channels = 1  # Mono
        self.format = "wav"
        
        # State
        self.is_listening = False
        self.last_audio_file = None
    
    def enable(self, voice_confirmed: bool = False):
        """
        BOO'S RULE: Only enable after voice output confirmed working!
        
        Args:
            voice_confirmed: Must be True (Boo confirmed voice works)
        """
        if not voice_confirmed:
            return {
                "enabled": False,
                "reason": "🔒 LOCKED - Boo's rules: Enable microphone ONLY after voice output is confirmed working!",
                "action_required": "Test and confirm voice output works first (sara_voice_output.py)",
                "status": "STAGE_3_LOCKED"
            }
        
        self.is_enabled = True
        return self._detect_mic()
    
    def _detect_mic(self) -> dict:
        """Detect K66 Pro MIC on USB-C"""
        results = {
            "detected": False,
            "device": None,
            "usb_port": self.usb_port,
            "mic_name": self.mic_name,
            "recorders": {},
            "stt_engines": {},
            "errors": []
        }
        
        if not self.is_enabled:
            results["errors"].append("Microphone locked - Voice output not confirmed")
            return results
        
        # Check for audio recorders
        results["recorders"] = {
            "arecord": shutil.which("arecord"),  # ALSA recorder
            "parecord": shutil.which("parecord"),  # PulseAudio
            "ffmpeg": shutil.which("ffmpeg"),  # Can record too
            "sox": shutil.which("sox"),  # Swiss army knife
        }
        
        # Check for Speech-to-Text
        results["stt_engines"] = {
            "whisper": shutil.which("whisper"),  # OpenAI Whisper local
            "whisper_cpp": shutil.which("whisper-cpp"),
            "vosk": None,  # Python lib
            "pocketsphinx": shutil.which("pocketsphinx_continuous"),
        }
        
        # List USB audio devices
        try:
            result = subprocess.run(
                ["arecord", "-l"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'usb' in line.lower() or 'k66' in line.lower():
                        results["device"] = line.strip()
                        results["detected"] = True
                        break
        except Exception as e:
            results["errors"].append(f"Device listing failed: {e}")
        
        return results
    
    def test_mic(self) -> dict:
        """Test microphone recording"""
        if STAGE_LOCKED:
            return {
                "success": False,
                "locked": True,
                "message": "🔐 STAGE 3 LOCKED - Voice output must be confirmed first!",
                "instruction": "Run sara_voice_output.py and confirm working before enabling mic"
            }
        
        if not self.is_enabled:
            return {
                "success": False,
                "enabled": False,
                "message": "Microphone not enabled"
            }
        
        # Try 3 second test recording
        test_file = "/tmp/sara_mic_test.wav"
        
        try:
            if shutil.which("arecord"):
                subprocess.run([
                    "arecord", "-d", "3", "-f", "cd", "-t", "wav",
                    "-D", "sysdefault:CARD=Device", test_file
                ], timeout=5, check=True)
            elif shutil.which("parecord"):
                subprocess.run([
                    "parecord", "--duration=3", test_file
                ], timeout=5, check=True)
            
            # Check if file was created and has audio
            if os.path.exists(test_file):
                size = os.path.getsize(test_file)
                if size > 1000:  # At least 1KB
                    return {
                        "success": True,
                        "file": test_file,
                        "size": size,
                        "message": "✅ Microphone recording successful!"
                    }
            
            return {
                "success": False,
                "message": "Recording file empty or missing"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"❌ Recording failed: {e}"
            }
    
    def listen_once(self, duration: int = 5) -> dict:
        """
        Record audio for duration seconds and transcribe
        
        Args:
            duration: How long to listen (seconds)
        
        Returns:
            dict with 'text' (transcribed) and success status
        """
        if STAGE_LOCKED or not self.is_enabled:
            return {
                "success": False,
                "text": None,
                "error": "Microphone locked or not enabled"
            }
        
        audio_file = f"/tmp/sara_capture_{datetime.now().strftime('%H%M%S')}.wav"
        
        try:
            # Record
            self.is_listening = True
            
            if shutil.which("arecord"):
                subprocess.run([
                    "arecord", "-d", str(duration), "-f", "cd", "-t", "wav",
                    "-D", "sysdefault:CARD=Device", audio_file
                ], timeout=duration + 2, check=True)
            
            # Transcribe (STT)
            text = self._transcribe(audio_file)
            
            self.last_audio_file = audio_file
            self.is_listening = False
            
            return {
                "success": True,
                "text": text,
                "audio_file": audio_file,
                "duration": duration
            }
            
        except Exception as e:
            self.is_listening = False
            return {
                "success": False,
                "text": None,
                "error": str(e)
            }
    
    def _transcribe(self, audio_file: str) -> Optional[str]:
        """Convert audio to text using available STT engine"""
        # Try whisper if available (best quality)
        if shutil.which("whisper"):
            try:
                result = subprocess.run(
                    ["whisper", audio_file, "--model", "tiny", "--language", "en"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                # Parse output to get text
                for line in result.stdout.split('\n'):
                    if line.strip() and not line.startswith('['):
                        return line.strip()
            except:
                pass
        
        # Fallback: Use whisper Python lib if installed
        try:
            import whisper
            model = whisper.load_model("tiny")  # Fastest
            result = model.transcribe(audio_file)
            return result["text"]
        except:
            pass
        
        # Return placeholder if no STT available
        return "[STT not available - install whisper]"
    
    def start_continuous(self, callback: Callable[[str], None]):
        """
        Start continuous listening (hotword activation in future)
        
        Args:
            callback: Function to call with transcribed text
        """
        if STAGE_LOCKED or not self.is_enabled:
            print("❌ Cannot start - mic locked")
            return False
        
        print("🎤 Continuous listening started...")
        print("   (Say something, I'll transcribe and respond)")
        
        # For now, just listen once
        # In future: add hotword detection ("Hey SARA")
        result = self.listen_once(duration=5)
        
        if result["success"] and result["text"]:
            callback(result["text"])
        
        return True
    
    def get_setup_instructions(self) -> str:
        """Get instructions for setting up the K66 Pro MIC"""
        return """
🎤 K66 Pro MIC SETUP (USB-C Port)

⚠️  PREREQUISITE: Voice output MUST be confirmed working first!

Install USB audio support:
  sudo dnf install alsa-utils pulseaudio-utils

Install Speech-to-Text:
  pip3 install openai-whisper
  # OR download whisper.cpp for faster local

Find your mic:
  arecord -l
  # Look for "USB Audio" or "K66"

Test recording:
  arecord -d 5 -f cd test.wav
  aplay test.wav  # Hear yourself?

Configure default input:
  alsamixer  # Press F4 for capture, select USB mic

Troubleshooting:
  - Mic not detected? Check USB-C port, try another cable
  - No audio? Check alsamixer capture levels (should be 80%+)
  - Static/noise? Try 'arecord -f S16_LE' instead of 'cd'
        """


def check_stage_3_unlocked(voice_confirmed: bool = False) -> dict:
    """
    Check if Stage 3 (mic input) can be unlocked
    
    Args:
        voice_confirmed: Boo confirms voice output works
    
    Returns:
        Status dict
    """
    if not voice_confirmed:
        return {
            "unlocked": False,
            "stage": 3,
            "message": "🔐 STAGE 3 LOCKED",
            "reason": "Boo's instruction: Only unlock microphone after voice output is confirmed working",
            "required": "Run test on sara_voice_output.py and confirm 'Yes, I heard it'",
            "current_status": "Waiting for voice output confirmation"
        }
    
    # Unlock it!
    global STAGE_LOCKED
    STAGE_LOCKED = False
    
    return {
        "unlocked": True,
        "stage": 3,
        "message": "🔓 STAGE 3 UNLOCKED!",
        "action": "Microphone can now be enabled",
        "next_step": "Run sara_mic_input.py and test recording"
    }


if __name__ == "__main__":
    print("=" * 60)
    print("🎤 SARA MIC INPUT - Stage 3 (Voice Input)")
    print("=" * 60)
    print()
    
    mic = SaraMicInput()
    
    # Show lock status
    if STAGE_LOCKED:
        print("⚠️  STAGE 3 IS LOCKED")
        print()
        print("🔒 BOO'S RULE: Microphone only enabled after voice output confirmed!")
        print()
        print("STEPS TO UNLOCK:")
        print("  1. First, test voice output: python3 sara_voice_output.py")
        print("  2. Confirm you hear SARA speak")
        print("  3. Then run: python3 sara_mic_input.py --unlock")
        print()
        print("Setup instructions ready to view:")
        print("-" * 40)
        print(mic.get_setup_instructions())
    else:
        print("✅ Stage 3 unlocked - testing microphone...")
        results = mic.enable(voice_confirmed=True)
        print(results)
        test = mic.test_mic()
        print("\nTest results:", test)
