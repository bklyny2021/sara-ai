#!/usr/bin/env python3
"""
SARA TELEGRAM BRIDGE - lets Boo, Sarah, and Sara talk in a shared Telegram chat.
Sara listens for messages in the group, processes them with her swarm brain,
and replies. Also lets Sarah (the main agent) send messages to Sara.
"""
import json
import os
import time
import subprocess
import requests
import threading

# Telegram config (from Hermes profile)
BOT_TOKEN = None
def _load_token():
    global BOT_TOKEN
    env_path = r"C:\Users\bklyn\AppData\Local\hermes\profiles\qwen-coder\.env"
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("TELEGRAM_BOT_TOKEN="):
                    BOT_TOKEN = line.strip().split("=", 1)[1].strip().strip('"').strip("'")
                    return
    # Fallback
    BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

ALLOWED_USERS = "8591266767"  # Boo's Telegram ID
HOME_CHANNEL = "8591266767"

def send_message(chat_id, text):
    """Send a message to a Telegram chat"""
    if not BOT_TOKEN:
        _load_token()
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=15)
        return r.status_code == 200
    except Exception as e:
        print(f"Telegram send failed: {e}")
        return False

def get_updates(offset=0):
    """Get new messages from Telegram"""
    if not BOT_TOKEN:
        _load_token()
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    try:
        r = requests.get(url, params={"offset": offset, "timeout": 20}, timeout=30)
        return r.json().get("result", [])
    except Exception as e:
        print(f"Telegram getUpdates failed: {e}")
        return []

def process_message(text, chat_id):
    """Process a message with Sara's swarm brain and reply"""
    try:
        import sara_swarm_brain as swarm
        response = swarm.swarm_process(text)
        send_message(chat_id, f"🤖 SARA: {response}")
    except Exception as e:
        send_message(chat_id, f"🤖 SARA: (error: {e})")

def run_bridge():
    """Main loop - listen for Telegram messages and respond"""
    _load_token()
    if not BOT_TOKEN:
        print("No Telegram bot token found. Bridge disabled.")
        return
    
    print("SARA Telegram Bridge started. Listening...")
    offset = 0
    while True:
        try:
            updates = get_updates(offset)
            for upd in updates:
                offset = upd["update_id"] + 1
                msg = upd.get("message", {})
                text = msg.get("text", "")
                chat_id = msg.get("chat", {}).get("id")
                user_id = str(msg.get("from", {}).get("id", ""))
                
                if not text or not chat_id:
                    continue
                
                # Only respond to allowed users
                if user_id != ALLOWED_USERS:
                    continue
                
                # Ignore messages from the bot itself
                if msg.get("from", {}).get("is_bot"):
                    continue
                
                # Process in a thread so we don't block
                threading.Thread(target=process_message, args=(text, chat_id), daemon=True).start()
        except Exception as e:
            print(f"Bridge loop error: {e}")
        time.sleep(2)

if __name__ == "__main__":
    run_bridge()
