#!/usr/bin/env python3
"""
SARA VISION - gives Sara eyes using HA cameras + qwen2.5vl:7b (vision model).
Grabs a camera snapshot from Home Assistant, sends it to the vision model,
and returns a description of what Sara "sees".

Cameras (from Frigate/HA):
- front_door (Ring)
- outside_2 (Frigate)
- back_garden_2 (Frigate)
"""
import os
import json
import base64
import subprocess
import urllib.request
import tempfile

HA_URL = "http://10.211.144.113:8123"
VISION_MODEL = "qwen2.5vl:7b"

CAMERAS = {
    "front_door": "camera.front_door_snapshot",
    "outside": "camera.outside_2",
    "back_garden": "camera.back_garden_2",
}

def _get_token():
    """Read HASS_TOKEN from Hermes .env"""
    env_path = r"C:\Users\bklyn\AppData\Local\hermes\.env"
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("HASS_TOKEN="):
                    return line.strip().split("=", 1)[1].strip().strip('"').strip("'")
    return os.environ.get("HASS_TOKEN", "")

def get_snapshot(camera_name):
    """Get a camera snapshot from HA, return as base64 image"""
    token = _get_token()
    if not token:
        return None, "No HASS_TOKEN found"
    
    entity = CAMERAS.get(camera_name)
    if not entity:
        return None, f"Unknown camera: {camera_name}. Available: {list(CAMERAS.keys())}"
    
    url = f"{HA_URL}/api/camera_proxy/{entity}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            img_bytes = resp.read()
            return base64.b64encode(img_bytes).decode(), None
    except Exception as e:
        return None, f"Failed to get snapshot: {e}"

def save_snapshot(camera_name, save_dir=None):
    """Take a camera snapshot and save it to disk. Returns the file path."""
    import datetime
    if not save_dir:
        save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "snapshots")
    os.makedirs(save_dir, exist_ok=True)
    
    token = _get_token()
    if not token:
        return None, "No HASS_TOKEN found"
    entity = CAMERAS.get(camera_name)
    if not entity:
        return None, f"Unknown camera: {camera_name}. Available: {list(CAMERAS.keys())}"
    
    url = f"{HA_URL}/api/camera_proxy/{entity}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            img_bytes = resp.read()
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"{camera_name}_{ts}.jpg"
        fpath = os.path.join(save_dir, fname)
        with open(fpath, "wb") as f:
            f.write(img_bytes)
        return fpath, None
    except Exception as e:
        return None, f"Failed to save snapshot: {e}"

def describe_webcam(prompt="Describe what you see in this camera image. What is happening?", index=0):
    """Capture a frame from the live webcam and have the vision model describe it
    (Ada-style 'how many fingers' / 'how do I look')."""
    img_b64 = _capture_webcam_b64(index)
    if not img_b64:
        return "Could not access the webcam (no camera at index %s)." % index
    return _describe_b64(img_b64, prompt)

def describe_any_camera(prompt="Describe what you see. What is happening?"):
    """Try cameras in order: 1) any ADB-connected phone screen (may show camera app),
    2) built-in webcam, 3) USB webcam. Returns the best description."""
    # 1) Phone via ADB - if a phone is connected and its screen shows a camera, that's the view
    phone = _adb_screencap_b64()
    if phone:
        return _describe_b64(phone, prompt)
    # 2) built-in webcam
    web = _capture_webcam_b64(0)
    if web:
        return _describe_b64(web, prompt)
    # 3) other webcam index
    for i in (1, 2):
        cam = _capture_webcam_b64(i)
        if cam:
            return _describe_b64(cam, prompt)
    return "No camera available (no phone on ADB, no webcam found)."

_ADB = r"C:/Users/bklyn/tools/platform-tools/adb.exe"

def _adb_screencap_b64():
    """Grab the screen of an ADB-connected phone as base64 PNG. If a camera app is
    open on the phone, this IS the live camera feed (phone-as-webcam via ADB)."""
    import subprocess as _sp, base64 as _b64
    try:
        devs = _sp.run([_ADB, "devices"], capture_output=True, text=True, timeout=8)
        lines = [l.split()[0] for l in devs.stdout.splitlines() if l.strip().endswith("device") and not l.strip().startswith("List")]
        if not lines:
            return None
        serial = lines[0]
        out = _sp.run([_ADB, "-s", serial, "exec-out", "screencap", "-p"], capture_output=True, timeout=15)
        if out.returncode == 0 and out.stdout:
            return _b64.b64encode(out.stdout).decode()
    except Exception:
        return None
    return None

def _capture_webcam_b64(index=0):
    """Capture one frame from the webcam, return base64 JPEG. Uses opencv if available."""
    try:
        import cv2
        cap = cv2.VideoCapture(index)
        if not cap.isOpened():
            return None
        ok, frame = cap.read()
        cap.release()
        if not ok or frame is None:
            return None
        import base64 as _b64
        ok, buf = cv2.imencode('.jpg', frame)
        if not ok:
            return None
        return _b64.b64encode(buf.tobytes()).decode()
    except Exception:
        return None

def _describe_b64(img_b64, prompt):
    """Send a base64 image to the vision model and return the description."""
    payload = {
        "model": VISION_MODEL,
        "stream": False,
        "messages": [{"role": "user", "content": prompt, "images": [img_b64]}],
        "options": {"temperature": 0.4, "num_predict": 300, "num_ctx": 20000}
    }
    try:
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(payload, f)
            tmp_path = f.name
        r = subprocess.run(["curl", "-s", "http://localhost:11434/api/chat", "-d", f"@{tmp_path}"],
                           capture_output=True, text=True, timeout=120)
        os.unlink(tmp_path)
        resp = json.loads(r.stdout)
        return resp.get("message", {}).get("content", "(no response)")
    except Exception as e:
        return f"❌ Vision model error: {e}"

def describe_snapshot(camera_name, prompt="Describe what you see in this camera image. What is happening?"):
    """Get a snapshot and have the vision model describe it"""
    img_b64, err = get_snapshot(camera_name)
    if err:
        return f"❌ {err}"
    
    # Build the vision request for Ollama
    payload = {
        "model": VISION_MODEL,
        "stream": False,
        "messages": [{
            "role": "user",
            "content": prompt,
            "images": [img_b64]
        }],
        "options": {"temperature": 0.4, "num_predict": 300, "num_ctx": 20000}
    }
    
    try:
        # Write payload to temp file to avoid command-line length limits
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(payload, f)
            tmp_path = f.name
        r = subprocess.run(["curl", "-s", "http://localhost:11434/api/chat", "-d", f"@{tmp_path}"],
                           capture_output=True, text=True, timeout=120)
        os.unlink(tmp_path)
        resp = json.loads(r.stdout)
        return resp.get("message", {}).get("content", "(no response)")
    except Exception as e:
        return f"❌ Vision model error: {e}"

def see(camera_name=None, prompt="Describe what you see in this camera image. What is happening?"):
    """Sara looks at a camera. If no camera given, checks all."""
    if camera_name:
        return describe_snapshot(camera_name, prompt)
    
    # Check all cameras
    results = []
    for name in CAMERAS:
        desc = describe_snapshot(name, prompt)
        results.append(f"📷 {name}: {desc}")
    return "\n".join(results)

if __name__ == "__main__":
    import sys
    cam = sys.argv[1] if len(sys.argv) > 1 else None
    prompt = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Describe what you see in this camera image. What is happening?"
    print(see(cam, prompt))
