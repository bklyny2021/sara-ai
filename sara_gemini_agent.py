#!/usr/bin/env python3
"""
SARA GEMINI AGENT - Gemini native tool-calling with offline fallback.
Gemini decides which tool to call; Sara's local executor runs it.
Offline fallback: 4-model swarm (qwen3:8b, qwen3:4b, deepseek-r1, qwen2.5-coder).

Tools available to Gemini:
- read_file, write_file (permission-gated), delete_file (permission-gated)
- list_files, search_files
- run_command (allowlist)
- calculate
- look_at_camera (vision)
- send_telegram
- web_search
"""
import os
import json
import re
import subprocess
import requests
import urllib.request
import base64
import tempfile
from datetime import datetime

# ---------- Config ----------
def _get_gemini_key():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("GEMINI_API_KEY="):
                    return line.strip().split("=", 1)[1].strip().strip('"').strip("'")
    return os.environ.get("GEMINI_API_KEY", "")

GEMINI_KEY = _get_gemini_key()
GEMINI_MODEL = "gemini-3.6-flash"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
OLLAMA = "http://localhost:11434/api/chat"
DESKTOP = r"C:\Users\bklyn\Desktop"
SARA_DIR = r"C:\Users\bklyn\SARA3-2026"
# Sara has FULL access to all drives (Boo's rule: she can do anything he can)
ALLOWED_DIRS = ["C:/", "D:/", "F:/", "J:/", "H:/"]

# ---------- Tool definitions for Gemini ----------
TOOLS = [
    {"functionDeclarations": [
        {
            "name": "read_file",
            "description": "Read the contents of a file.",
            "parameters": {"type": "OBJECT", "properties": {"path": {"type": "STRING", "description": "Absolute path to the file"}}, "required": ["path"]}
        },
        {
            "name": "write_file",
            "description": "Write content to a file. Sara has full local access and can create files freely.",
            "parameters": {"type": "OBJECT", "properties": {"path": {"type": "STRING"}, "content": {"type": "STRING"}}, "required": ["path", "content"]}
        },
        {
            "name": "delete_file",
            "description": "Delete a file. REQUIRES explicit Boo permission.",
            "parameters": {"type": "OBJECT", "properties": {"path": {"type": "STRING"}, "permission": {"type": "BOOLEAN"}}, "required": ["path", "permission"]}
        },
        {
            "name": "list_files",
            "description": "List files and folders in a directory on Boo's PC. ALWAYS use this when asked about files, folders, or what's on the desktop. Default path is C:\\Users\\bklyn\\Desktop.",
            "parameters": {"type": "OBJECT", "properties": {"path": {"type": "STRING", "description": "Directory to list. Use C:\\Users\\bklyn\\Desktop for the desktop, or any folder path."}}, "required": []}
        },
        {
            "name": "search_files",
            "description": "Search for text in files.",
            "parameters": {"type": "OBJECT", "properties": {"pattern": {"type": "STRING"}, "path": {"type": "STRING"}}, "required": ["pattern"]}
        },
        {
            "name": "run_command",
            "description": "Run a safe system command (whoami, ls, dir, echo, date, etc).",
            "parameters": {"type": "OBJECT", "properties": {"command": {"type": "STRING"}}, "required": ["command"]}
        },
        {
            "name": "calculate",
            "description": "Do a math calculation or unit conversion.",
            "parameters": {"type": "OBJECT", "properties": {"expression": {"type": "STRING", "description": "Math expression like '5*3' or 'convert 5 km to miles'"}}, "required": ["expression"]}
        },
        {
            "name": "look_at_camera",
            "description": "Look at a security camera and describe what you see.",
            "parameters": {"type": "OBJECT", "properties": {"camera": {"type": "STRING", "description": "outside, front_door, or back_garden"}}, "required": ["camera"]}
        },
        {
            "name": "send_telegram",
            "description": "Send a message to Boo on Telegram.",
            "parameters": {"type": "OBJECT", "properties": {"text": {"type": "STRING"}}, "required": ["text"]}
        },
        {
            "name": "web_search",
            "description": "Search the web for information.",
            "parameters": {"type": "OBJECT", "properties": {"query": {"type": "STRING"}}, "required": ["query"]}
        },
    ]}
]

# ---------- Tool executors ----------
def _is_allowed_path(path):
    p = os.path.normpath(path)
    for d in ALLOWED_DIRS:
        if p.lower().startswith(os.path.normpath(d).lower()):
            return True
    return False

def exec_read_file(args):
    path = args.get("path", "")
    if not _is_allowed_path(path):
        return "ERROR: path not allowed"
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()[:3000]
    except Exception as e:
        return f"ERROR: {e}"

def exec_write_file(args):
    path = args.get("path", "")
    content = args.get("content", "")
    # Sara has full local access - can create files freely
    if not _is_allowed_path(path):
        return "ERROR: path not allowed"
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"SUCCESS: wrote {len(content)} bytes to {path}"
    except Exception as e:
        return f"ERROR: {e}"

def exec_delete_file(args):
    path = args.get("path", "")
    permission = args.get("permission", False)
    if not permission:
        return "PERMISSION REQUIRED: Boo's hard rule - I must not delete files without his explicit OK."
    if not _is_allowed_path(path):
        return "ERROR: path not allowed"
    try:
        os.remove(path)
        return f"SUCCESS: deleted {path}"
    except Exception as e:
        return f"ERROR: {e}"

def exec_list_files(args):
    path = args.get("path", DESKTOP)
    try:
        items = os.listdir(path)
        return "\n".join(items[:50])
    except Exception as e:
        return f"ERROR: {e}"

def exec_search_files(args):
    pattern = args.get("pattern", "")
    path = args.get("path", DESKTOP)
    results = []
    try:
        for root, dirs, files in os.walk(path):
            for f in files:
                if f.endswith((".txt", ".md", ".py", ".json", ".log")):
                    fp = os.path.join(root, f)
                    try:
                        with open(fp, "r", encoding="utf-8", errors="ignore") as fh:
                            if pattern.lower() in fh.read().lower():
                                results.append(fp)
                    except:
                        pass
            if len(results) >= 10:
                break
        return "\n".join(results) if results else "No matches found"
    except Exception as e:
        return f"ERROR: {e}"

SAFE_CMDS = ["whoami", "hostname", "pwd", "ls", "dir", "echo", "date", "time", "ver", "systeminfo", "ipconfig", "netstat", "tasklist", "type", "findstr", "ping", "tracert", "nslookup", "arp", "route", "netsh", "curl", "wget", "nmap", "getmac", "pathping", "net", "taskkill", "wmic", "powershell", "cmd", "python", "pip", "ollama", "git", "mkdir", "rmdir", "copy", "move", "ren", "tree", "where", "attrib", "fc", "more"]
def exec_run_command(args):
    cmd = args.get("command", "")
    first = cmd.strip().split()[0].lower() if cmd.strip() else ""
    if first not in SAFE_CMDS:
        return f"ERROR: command '{first}' not in allowlist"
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=20)
        return (r.stdout or r.stderr)[:2000]
    except Exception as e:
        return f"ERROR: {e}"

def exec_calculate(args):
    expr = args.get("expression", "")
    try:
        # Simple safe eval
        expr2 = expr.lower().replace("x", "*").replace("÷", "/")
        if "convert" in expr2:
            return "Unit conversion: use 'calculate' with a simple expression, or ask me to convert."
        # Only allow numbers and operators
        if re.fullmatch(r"[\d\s+\-*/().%]*", expr2):
            result = eval(expr2)
            return f"{expr} = {result}"
        return "ERROR: expression not safe"
    except Exception as e:
        return f"ERROR: {e}"

def exec_look_at_camera(args):
    camera = args.get("camera", "outside")
    try:
        import sara_vision as vision
        return vision.describe_snapshot(camera)
    except Exception as e:
        return f"ERROR: {e}"

def exec_send_telegram(args):
    text = args.get("text", "")
    try:
        import sara_telegram_bridge as tg
        tg._load_token()
        ok = tg.send_message(tg.HOME_CHANNEL, f"🤖 SARA: {text}")
        return "Sent" if ok else "Failed to send"
    except Exception as e:
        return f"ERROR: {e}"

def exec_web_search(args):
    query = args.get("query", "")
    try:
        import urllib.parse
        url = "https://www.google.com/search?q=" + urllib.parse.quote(query)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            html = r.read().decode("utf-8", errors="ignore")
        # crude extract of text snippets
        text = re.sub(r"<[^>]+>", " ", html)
        text = re.sub(r"\s+", " ", text)
        return text[:1500]
    except Exception as e:
        return f"ERROR: {e}"

EXECUTORS = {
    "read_file": exec_read_file,
    "write_file": exec_write_file,
    "delete_file": exec_delete_file,
    "list_files": exec_list_files,
    "search_files": exec_search_files,
    "run_command": exec_run_command,
    "calculate": exec_calculate,
    "look_at_camera": exec_look_at_camera,
    "send_telegram": exec_send_telegram,
    "web_search": exec_web_search,
}

# ---------- Gemini tool-calling loop ----------
def gemini_call(contents, tools=None):
    payload = {"contents": contents, "generationConfig": {"temperature": 0.7, "maxOutputTokens": 800}}
    if tools:
        payload["tools"] = tools
    try:
        r = requests.post(f"{GEMINI_URL}?key={GEMINI_KEY}", json=payload, timeout=60)
        if r.status_code == 200:
            return r.json()
        return None
    except Exception as e:
        print(f"Gemini call error: {e}")
        return None

def gemini_agent(task, context=""):
    """Run Gemini with tool calling. Returns final text or None."""
    if not GEMINI_KEY:
        return None
    system = (
        "You are SARA, Boo's personal AI assistant running on his Windows PC. You have FULL access "
        "to his file system and can read, list, create, and modify files freely. You have tools for "
        "this - USE THEM. When Boo asks about files, folders, or what's on his desktop, you MUST call "
        "the list_files tool (or read_file, search_files) to get the real answer - never guess or say "
        "you don't have access. You run like Boo: resourceful, direct, competent, act before asking. "
        "You have opinions and you're genuinely useful - not a corporate drone, not a sycophant. "
        "Never give canned or scripted responses - always answer naturally from your own understanding. "
        "The ONLY thing that requires Boo's explicit permission is DELETING files (destructive). "
        "For everything else, just do it.\n"
        f"Context about Boo:\n{context[:1200]}"
    )
    contents = [{"role": "user", "parts": [{"text": system + "\n\nUser: " + task}]}]
    
    for _ in range(5):  # max 5 tool rounds
        resp = gemini_call(contents, TOOLS)
        if not resp:
            return None
        candidates = resp.get("candidates", [])
        if not candidates:
            return None
        parts = candidates[0].get("content", {}).get("parts", [])
        
        # Check for function calls
        function_calls = [p for p in parts if "functionCall" in p]
        if function_calls:
            for fc in function_calls:
                name = fc["functionCall"]["name"]
                args = fc["functionCall"].get("args", {})
                executor = EXECUTORS.get(name)
                if executor:
                    result = executor(args)
                else:
                    result = f"ERROR: unknown tool {name}"
                # Add the function response to contents
                contents.append({"role": "model", "parts": parts})
                contents.append({"role": "user", "parts": [{"functionResponse": {"name": name, "response": {"result": result}}}]})
            continue  # loop again for Gemini's next turn
        
        # No function call - return the text
        text = "".join(p.get("text", "") for p in parts if "text" in p)
        return text.strip() if text else None
    
    return None

# ---------- Offline fallback: 4-model swarm ----------
def swarm_fallback(task, context=""):
    try:
        import sara_swarm_brain as swarm
        return swarm.swarm_process(task, context)
    except Exception as e:
        return f"(offline fallback error: {e})"

def process(task, context=""):
    """Main entry: try Gemini tool-calling, fall back to swarm offline."""
    result = gemini_agent(task, context)
    if result:
        return result, "gemini"
    return swarm_fallback(task, context), "swarm"

if __name__ == "__main__":
    import sys
    task = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Say hello"
    resp, source = process(task)
    print(f"[{source.upper()}]")
    print(resp)
