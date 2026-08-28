#!/usr/bin/env python3
"""SARA VOICE INPUT (Windows) - mirror of the Hermes desktop app's voice stack.
Records from the default microphone (sounddevice), transcribes with faster-whisper.
No Linux tools needed. Returns recognized text."""
import os, sys, tempfile, io, json

def record(duration=5.0, sample_rate=16000):
    """Record `duration` seconds from the default mic, return WAV bytes."""
    import sounddevice as sd
    import numpy as np
    import wave
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype="int16")
    sd.wait()
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        w.writeframes(audio.tobytes())
    return buf.getvalue()

def transcribe(wav_bytes):
    """Transcribe WAV bytes with faster-whisper (same engine Hermes uses)."""
    from faster_whisper import WhisperModel
    model = WhisperModel("small", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(wav_bytes, beam_size=1)
    text = " ".join(s.text.strip() for s in segments).strip()
    return text

def listen(duration=5.0):
    """Record + transcribe one phrase. Returns text or empty."""
    try:
        wav = record(duration)
        if not wav or len(wav) < 1000:
            return ""
        return transcribe(wav)
    except Exception as e:
        return f"[mic error: {e}]"

if __name__ == "__main__":
    d = float(sys.argv[1]) if len(sys.argv) > 1 else 5.0
    print(listen(duration=d))
