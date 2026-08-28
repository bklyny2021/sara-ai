#!/usr/bin/env python3
"""
SARA BRAIN - Autonomous decision making
First step toward autonomous agent like MAX
"""

import json
import os
import time
from datetime import datetime
from sara_tools import SaraTools
from nano_guide import NanoHelper, NANO_GUIDE
from network_tool import NetworkTool
from calculator_tool import CalculatorTool
from lookfile_tool import LookFileTool
from sara_python_course import SaraPythonTeacher
from network_scanner import NetworkScanner

# Voice modules (Stages 2-3) - imported but only enabled when ready
try:
    from sara_voice_output import SaraVoiceOutput, test_voice
    VOICE_AVAILABLE = True
except:
    VOICE_AVAILABLE = False

try:
    from sara_mic_input import SaraMicInput
    MIC_AVAILABLE = True
except:
    MIC_AVAILABLE = False

class SaraBrain:
    """SARA's decision-making brain"""
    
    def __init__(self):
        self.tools = SaraTools()
        self.nano = NanoHelper()
        self.network = NetworkTool()
        self.calculator = CalculatorTool()
        self.lookfiles = LookFileTool()
        self.python_teacher = SaraPythonTeacher()
        self.scanner = NetworkScanner()
        self.memory_file = "C:/Users/bklyn/SARA3-2026/brain_memory.json"
        self.conversation_history = []
        
        # Voice/Mic - voice enabled (offline Piper), mic disabled
        self.voice = SaraVoiceOutput() if VOICE_AVAILABLE else None
        self.mic = None
        self.voice_enabled = True
        self.mic_enabled = False
        
        self.load_memory()
        self.load_context_files()
    
    def load_context_files(self):
        """Load OpenClaw-style context files (SOUL, USER, MEMORY, TOOLS, AGENTS, HEARTBEAT, daily notes)"""
        self.context = {}
        base = "C:/Users/bklyn/SARA3-2026"
        files = ['SOUL.md', 'USER.md', 'MEMORY.md', 'TOOLS.md', 'AGENTS.md', 'HEARTBEAT.md']
        for f in files:
            path = os.path.join(base, f)
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as fh:
                        self.context[f] = fh.read()
                except Exception:
                    self.context[f] = ""
        # Load today's + yesterday's daily notes
        from datetime import date, timedelta
        for d in [date.today(), date.today() - timedelta(days=1)]:
            note = os.path.join(base, "memory", d.strftime("%Y-%m-%d") + ".md")
            if os.path.exists(note):
                try:
                    with open(note, 'r', encoding='utf-8') as fh:
                        self.context.setdefault('daily_notes', "") 
                        self.context['daily_notes'] += fh.read() + "\n"
                except Exception:
                    pass
        # Build a compact context summary for the worker prompt
        self.context_summary = ""
        for key in ['SOUL.md', 'USER.md', 'MEMORY.md']:
            if self.context.get(key):
                self.context_summary += f"--- {key} ---\n{self.context[key][:1500]}\n\n"
    
    def load_memory(self):
        """Load previous brain state"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    data = json.load(f)
                    self.conversation_history = data.get('conversations', [])
            except:
                pass
    
    def save_memory(self):
        """Save brain state"""
        try:
            with open(self.memory_file, 'w') as f:
                json.dump({
                    'conversations': self.conversation_history[-50:],
                    'last_save': datetime.now().isoformat()
                }, f, indent=2)
        except:
            pass
    
    def process_request(self, user_input):
        """
        Process user request and execute tools autonomously
        """
        user_lower = user_input.lower().strip().rstrip('?!')
        
        # ===== BROWSER / URL NAVIGATION (highest priority) =====
        # If the user wants to OPEN a browser / navigate somewhere, use the browser
        # tool. This catches BOTH full URLs AND "go to the wikipedia page for X".
        # Must be checked FIRST so URLs and browser actions never get mangled by
        # topic handlers (which caused "Wikipedia error: 404" on valid URLs).
        import re as _re
        _url_m = _re.search(r'https?://[^\s\)\]\},]+', user_input)
        _wants_browser = any(w in user_lower for w in [
            'open a browser', 'open browser', 'use a browser', 'use the browser',
            'navigate', 'browser to', 'go to', 'visit', 'this page', 'this url',
            'this link', 'this website', 'look at this', 'learn from this'
        ])
        if _url_m and _wants_browser:
            # Full URL given - navigate to it exactly
            url = _url_m.group(0).rstrip('.,')
            try:
                import sara_browser as sb
                nav = sb.run("navigate", url)
                content = sb.run("read")
                sb.run("close")
                return {"type": "web", "response": f"🌐 {nav}\n\n{content[:1500]}"}
            except Exception as e:
                return {"type": "web", "response": f"❌ Could not load {url}: {e}"}
        elif _wants_browser and ('page for' in user_lower or 'page about' in user_lower or 'wikipedia page' in user_lower or 'the ' in user_lower):
            # "go to the wikipedia page for cats" - build the URL from the topic
            topic = user_lower
            for w in ['open a browser and go to', 'open browser and go to', 'open a browser', 'open browser',
                      'navigate to', 'go to the wikipedia page for', 'go to the page for', 'go to the page about',
                      'wikipedia page for', 'page for', 'page about', 'the wikipedia page for', 'the page for',
                      'then go to', 'and tell me what you see', 'and tell me what', 'tell me what you see',
                      'tell me what', 'read the page and tell me', 'read the page', 'and read', 'what you see',
                      'go to the wikipedia page for', 'go to the', 'and tell me what both pages say',
                      'tell me what both pages say', 'both pages say', 'you see', 'go to', 'the', 'and']:
                topic = topic.replace(w, ' ')
            topic = topic.strip().strip('.,').strip()
            if topic:
                # Build a Wikipedia URL from the topic
                from urllib.parse import quote
                url = "https://en.wikipedia.org/wiki/" + quote(topic.replace(' ', '_'))
                try:
                    import sara_browser as sb
                    nav = sb.run("navigate", url)
                    content = sb.run("read")
                    sb.run("close")
                    return {"type": "web", "response": f"🌐 {nav}\n\n{content[:1500]}"}
                except Exception as e:
                    return {"type": "web", "response": f"❌ Could not load {url}: {e}"}
        
        # Identity check - "who are you" gets immediate simple response
        identity_phrases = [
            'who are you', 'what is your name', 'who is this', 'what are you',
            "what's your name", 'introduce yourself', 'tell me about yourself'
        ]
        if any(p in user_lower for p in identity_phrases):
            import random
            greetings = [
                "🤖 SARA here! Ready to help.",
                "Hey! I'm SARA. What's up?",
                "🤖 Yo! SARA at your service.",
                "It's me, SARA! 🤖 What's on your mind?",
                "🤖 SARA reporting for duty!",
                "Hey there! SARA here. Need something?",
                "🤖 *waves* It's SARA!",
                "SARA here! 🤖 What can I do for you, Boo?",
                "Yo! 🤖 SARA speaking.",
                "🤖 SARA online!",
                "Hey Boo! It's SARA 🤖",
                "🤖 SARA here, ready to roll!",
                "Sup! SARA here 🤖",
                "🤖 SARA activated!",
                "It's your friendly neighborhood SARA 🤖",
            ]
            response = random.choice(greetings)
            return {
                "type": "identity",
                "response": response
            }
        
        # PYTHON TEACHING - Stage 1
        if any(x in user_lower for x in ['learn python', 'teach me python', 'python lesson', 'python course']):
            return self._handle_python_request(user_input)
        
        # VOICE OUTPUT - Stage 2 (Test/Setup)
        if any(x in user_lower for x in ['test voice', 'setup voice', 'speak', 'voice output', 'hdmi audio']):
            return self._handle_voice_request(user_input)
        
        # MIC INPUT - Stage 3 (Only if voice confirmed)
        if any(x in user_lower for x in ['test mic', 'microphone', 'voice input', 'listen']):
            return self._handle_mic_request(user_input)
        
        # Tool detection patterns (check in order of specificity)
        
        # CHECK IF INPUT LOOKS LIKE A FILENAME (has extension like .txt, .py, etc.)
        # Words that indicate file reading with just a filename
        file_indicators = ['look', 'open', 'see', 'show']
        has_file_extension = any(ext in user_lower for ext in ['.txt', '.text', '.py', '.md', '.json', '.log', '.sh', '.cfg', '.conf', '.yaml', '.yml'])
        starts_with_file_indicator = any(user_lower.startswith(ind + ' ') for ind in file_indicators)
        
        # If it looks like "look sara.text" - treat as file read
        if (starts_with_file_indicator and has_file_extension) or 'open file' in user_lower:
            # Extract the filename after the indicator word
            for ind in file_indicators:
                if user_lower.startswith(ind + ' '):
                    # Rewrite to be a read request
                    return self._handle_read_request(user_input.replace(ind, 'read', 1))
        
        # LOOK FILES - .look files special handling (MUST be before regular file read)
        if '.look' in user_lower or 'look file' in user_lower or 'show .look' in user_lower:
            return self._handle_lookfile_request(user_input)
        
        # READ - check if user wants to read a file
        # "read" at start followed by filename, or phrases like "show content of", "cat file"
        if user_lower.startswith('read ') or 'show content' in user_lower or 'cat ' in user_lower or user_lower.startswith('view '):
            return self._handle_read_request(user_input)
        
        # LIST FILES - be careful not to match 'ls' substring in other words
        elif any(user_lower.startswith(x) or x in user_lower for x in ['list', 'show me files', 'what files', 'ls ', 'ls -', 'dir ', 'show directory']):
            return self._handle_list_request(user_input)
        
        # NANO - text editor commands (check before file operations)
        elif any(x in user_lower for x in ['nano', 'edit file', 'text editor', 'how to use nano', 'edit sara']):
            return self._handle_nano_request(user_input)
            return self._handle_nano_request(user_input)
        
        # WEATHER - current weather (online, free, no key)
        # Checked BEFORE web search so weather questions always get the real forecast,
        # never dumped as search links.
        elif any(x in user_lower for x in ['weather', 'temperature outside', 'is it raining', 'forecast', 'how hot', 'how cold']):
            return self._handle_weather_request(user_input)
        
        # WEB - search/fetch any online info (Boo's rule: get it, no questions)
        # NOTE: 'what is'/'who is' are NOT here - simple questions go to the main brain
        # (sara-heretic) so she answers directly instead of over-searching. Only clear
        # search intents trigger a web search.
        elif any(x in user_lower for x in ['search the web', 'search online', 'look up', 'google', 'news', 'wikipedia', 'online', 'web search', 'fetch', 'scrape', 'latest', 'current events', 'tell me about', 'find out', 'find someone', 'find a person', 'people search', 'look up a person', 'search for a person', 'find person', 'who is this person', 'find them on', 'search facebook', 'search instagram', 'search tiktok', 'search x', 'search twitter', 'amazon', 'buy ', 'for sale', 'price of', 'how much is', 'shop for', 'find me a', 'shopping']):
            return self._handle_web_request(user_input)
        
        # NETWORK SECURITY - protect the network (check BEFORE generic network)
        elif any(x in user_lower for x in ['network security', 'security audit', 'scan network', 'open ports', 'check connections', 'suspicious', 'protect network', 'network scan', 'whois', 'netstat', 'firewall', 'port scan', 'scan ports', 'packet loss', 'packet', 'trace', 'tracert']):
            return self._handle_network_security_request(user_input)
        
        # NETWORK - IP addresses, connectivity, ping
        elif any(x in user_lower for x in ['ip address', 'ip pool', 'my ip', 'network', 'connectivity', 'ping ', 'what is my ip', 'local ip', 'external ip', 'check port']):
            return self._handle_network_request(user_input)
        
        # NETWORK SCAN - Find REAL devices on network (not fake AI teammates)
        elif any(x in user_lower for x in ['what devices', 'list computers', 'show pcs', 'connected devices', 'network devices', 'connected pc', 'what computers', 'list devices', 'scan network']):
            return self._handle_network_scan_request(user_input)
        
        # CALCULATOR - math operations
        elif any(x in user_lower for x in ['calculate', 'calculator', 'math', 'plus', 'minus', 'times', 'divided', 'squared', 'sqrt', 'convert']):
            return self._handle_calculator_request(user_input)
        
        # COMMANDS - whoami, system info, etc
        elif any(user_lower.startswith(x) or x in user_lower for x in ['run ', 'execute ', 'whoami', 'hostname', 'free ', 'df ', 'ps ', 'processes', 'uptime', 'uname ', 'pwd']):
            return self._handle_command_request(user_input)
        
        elif any(x in user_lower for x in ['find', 'search', 'grep', 'look for']):
            return self._handle_search_request(user_input)
        
        elif any(x in user_lower for x in ['file info', 'details', 'about']):
            return self._handle_info_request(user_input)
        
        # WRITE/CREATE - create or write a file
        elif any(user_lower.startswith(x) for x in ['create ', 'write ', 'make a file', 'make file', 'save to file', 'write to file']) or \
             any(x in user_lower for x in ['yes create ', 'go ahead create ', 'ok create ', 'you can create ', 'please create ', 'i want you to create ', 'create it', 'write it']):
            return self._handle_write_request(user_input)
        
        # DELETE - delete a file (HARD RULE: requires permission)
        elif any(user_lower.startswith(x) for x in ['delete ', 'remove file', 'delete file', 'erase ']):
            return self._handle_delete_request(user_input)
        
        # VISION - look at cameras
        elif any(x in user_lower for x in ['look at camera', 'see camera', 'check camera', 'what do you see', 'look outside', 'look at front', 'look at back', 'camera view', 'show me the camera', 'camera', 'look at the']):
            return self._handle_vision_request(user_input)
        
        # TOOLS - create/list/run her own tools
        elif any(x in user_lower for x in ['create a tool', 'make a tool', 'new tool', 'list my tools', 'my tools', 'run tool', 'create tool']):
            return self._handle_tool_request(user_input)
        
        # MEMORY - "save that to memory" / "remember that" writes to HER OWN memory (like the main agent)
        elif user_lower.startswith(('save that to memory', 'save this to memory', 'remember that', 'remember this', 'save to my memory', 'save to memory', 'remember ', 'store this in memory', 'store that in memory', 'write that to memory', 'add that to memory')):
            return self._handle_memory_request(user_input)
        
        else:
            # General response - route to the model (Boo's rule: no canned scripts)
            return {
                "type": "route_to_model",
                "response": None
            }
    
    def _handle_list_request(self, query):
        """Handle list directory request"""
        # Try to extract path
        path = "."
        words = query.replace("list", "").replace("files", "").replace("show me", "").strip().split()
        if words:
            path = words[-1]
        
        # Map "desktop" to the real Desktop path
        if path.lower() in ("desktop", "my desktop", "on desktop"):
            path = "C:/Users/bklyn/Desktop"
        
        result = self.tools.list_directory(path)
        
        if "error" in result:
            return {"type": "error", "response": f"Error: {result['error']}"}
        
        files_str = "\n".join([f"  📄 {f['name']} ({self.tools._human_readable_size(f['size'])})" for f in result.get('files', [])[:10]])
        dirs_str = "\n".join([f"  📁 {d}/" for d in result.get('directories', [])[:10]])
        
        total_files = len(result.get('files', []))
        total_dirs = len(result.get('directories', []))
        
        response = f"📁 Directory: {result['path']}\n\n"
        if dirs_str:
            response += f"Directories:\n{dirs_str}\n\n"
        if files_str:
            response += f"Files:\n{files_str}\n\n"
        if total_files > 10 or total_dirs > 10:
            response += f"... and {total_files - 10} more files, {total_dirs - 10} more folders\n"
        
        return {"type": "list", "response": response, "data": result}
    
    def _handle_read_request(self, query):
        """Handle read file request"""
        # Extract filename - handle various prefixes and filler words
        path = None
        import re as _re
        # Find a filename pattern (contains a dot, or is a known file)
        words = query.replace("read", "").replace("view", "").replace("show content of", "").replace("cat ", "").replace("look", "").replace("open", "").replace("see", "").replace("show", "").replace("the", "").replace("file", "").replace("on", "").replace("my", "").replace("desktop", "").strip().split()
        # Prefer a word with a file extension
        for w in words:
            if '.' in w:
                path = w
                break
        if not path and words:
            path = words[0]
        
        if not path:
            return {"type": "error", "response": "Please tell me which file to read (e.g., 'read sara_tools.py')"}
        
        # Map "desktop" to the real Desktop path
        if 'desktop' in query.lower():
            path = os.path.join("C:/Users/bklyn/Desktop", path)
        
        result = self.tools.read_file(path)
        
        if "error" in result:
            return {"type": "error", "response": f"Error: {result['error']}"}
        
        content = result.get('content', '')[:2000]
        if len(result.get('content', '')) > 2000:
            content += "\n\n... [truncated, file is larger] ..."
        
        response = f"📄 File: {result['file']}\n📊 Size: {result.get('size_human', result.get('size', 'N/A'))} | Lines: {result.get('lines', 'N/A')}\n\n```\n{content}\n```"
        
        return {"type": "read", "response": response, "data": result}
    
    def _handle_write_request(self, query):
        """Handle create/write file request"""
        import re
        user_lower = query.lower()
        
        # Determine target directory (Desktop if mentioned, else SARA folder)
        target_dir = "C:/Users/bklyn/SARA3-2026"
        if 'desktop' in user_lower or 'on my desktop' in user_lower:
            target_dir = "C:/Users/bklyn/Desktop"
        
        # Extract filename - look for a .ext token
        filename = None
        ext_match = re.search(r'([\w\-]+\.\w+)', query)
        if ext_match:
            filename = ext_match.group(1)
        
        if not filename:
            return {"type": "error", "response": "Please tell me the filename to create (e.g., 'create joke1.txt on my desktop')"}
        
        # Extract content - text after the filename
        content = ""
        # Look for content after "with", "containing", "saying", or after the filename
        for marker in [' with ', ' containing ', ' saying ', ' that says ', ' that contains ']:
            if marker in user_lower:
                content = query.split(marker, 1)[-1].strip()
                break
        
        if not content:
            # Default content based on filename
            content = f"This is {filename}, created by SARA."
        
        # Build full path
        full_path = os.path.join(target_dir, filename)
        
        # HARD RULE: only write if Boo explicitly grants permission
        permission = False
        grant_phrases = [
            'you have permission', 'i give you permission', 'i grant you permission',
            'go ahead', 'yes create', 'yes write', 'approved', 'confirmed',
            'ok create', 'ok write', 'you may create', 'you may write',
            'please create', 'please write', 'create it', 'write it',
            'i want you to create', 'i want you to write', 'make it',
            'i authorize', 'you can create', 'you can write', 'do it'
        ]
        # Sara has full local access - can create files freely (Boo's rule)
        permission = True
        
        result = self.tools.write_file(full_path, content, permission=permission)
        
        if "error" in result:
            return {"type": "error", "response": f"Error: {result['error']}"}
        
        return {
            "type": "write",
            "response": f"✅ Created {result['file']}\n📝 Content: {content}\n📊 {result.get('bytes_written', 0)} bytes written"
        }
    
    def _handle_delete_request(self, query):
        """Handle delete file request. HARD RULE: requires explicit Boo permission."""
        import re
        user_lower = query.lower()
        
        # Determine target directory (Desktop if mentioned, else SARA folder)
        target_dir = "C:/Users/bklyn/SARA3-2026"
        if 'desktop' in user_lower or 'on my desktop' in user_lower:
            target_dir = "C:/Users/bklyn/Desktop"
        
        # Extract filename - look for a .ext token
        filename = None
        ext_match = re.search(r'([\w\-]+\.\w+)', query)
        if ext_match:
            filename = ext_match.group(1)
        
        if not filename:
            return {"type": "error", "response": "Please tell me the filename to delete (e.g., 'delete test123.txt on my desktop')"}
        
        full_path = os.path.join(target_dir, filename)
        
        # HARD RULE: only delete if Boo explicitly grants permission
        permission = False
        grant_phrases = [
            'you have permission', 'i give you permission', 'i grant you permission',
            'go ahead', 'yes delete', 'approved', 'confirmed',
            'ok delete', 'you may delete', 'please delete', 'delete it',
            'i want you to delete', 'i authorize', 'you can delete', 'do it'
        ]
        if any(p in user_lower for p in grant_phrases):
            permission = True
        
        result = self.tools.delete_file(full_path, permission=permission)
        
        if "error" in result:
            if "PERMISSION REQUIRED" in result.get('error', ''):
                return {
                    "type": "permission_required",
                    "response": f"🔒 I need your permission to delete {filename}. Boo's hard rule says I must not delete files without your explicit OK. Reply with 'yes delete {filename}' or 'go ahead' to confirm."
                }
            return {"type": "error", "response": f"Error: {result['error']}"}
        
        return {
            "type": "delete",
            "response": f"🗑️ Deleted {result['file']}"
        }
    
    def _handle_vision_request(self, query):
        """Handle camera vision request - Sara looks at a camera"""
        user_lower = query.lower()
        camera = None
        if 'outside' in user_lower or 'back' in user_lower:
            camera = 'back_garden' if 'back' in user_lower else 'outside'
        elif 'front' in user_lower or 'door' in user_lower:
            camera = 'front_door'
        
        try:
            import sara_vision as vision
            # Snapshot request - save to disk
            if 'snapshot' in user_lower or 'take a picture' in user_lower or 'save' in user_lower:
                fpath, err = vision.save_snapshot(camera)
                if err:
                    return {"type": "vision", "response": f"❌ {err}"}
                return {"type": "vision", "response": f"📸 Snapshot saved: {fpath}"}
            if camera:
                desc = vision.describe_snapshot(camera)
                return {"type": "vision", "response": f"👁️ Looking at {camera} camera:\n{desc}"}
            else:
                desc = vision.see()
                return {"type": "vision", "response": f"👁️ Checking all cameras:\n{desc}"}
        except Exception as e:
            return {"type": "error", "response": f"❌ Vision error: {e}"}
    
    def _handle_web_request(self, query):
        """Handle web search / scraping requests - get any online info"""
        user_lower = query.lower()
        try:
            import sara_web_scraper as web
            
            # People finder - find a person
            if any(x in user_lower for x in ['find person', 'find someone', 'find a person', 'people finder', 'look up a person', 'find them', 'who is this person', 'find person named', 'find someone named', 'search for a person', 'find a person named']):
                import sara_people_finder as pf
                name = query
                for w in ['find person', 'find someone', 'find a person', 'people finder', 'look up a person', 'find them', 'who is this person', 'find person named', 'find someone named', 'search for a person', 'find a person named', 'named', 'called', 'for', 'search']:
                    name = name.replace(w, '')
                name = name.strip().strip('?').strip()
                if name:
                    return {"type": "web", "response": pf.find_person(name)}
                return {"type": "web", "response": "Who would you like me to find? (e.g., 'find person named John Smith')"}
            
            # People search (social media / public records)
            if any(x in user_lower for x in ['find someone', 'find a person', 'people search', 'look up a person', 'search for a person', 'find person', 'who is this person', 'find them on', 'search facebook', 'search instagram', 'search tiktok', 'search x', 'search twitter']):
                name = query
                for w in ['find someone', 'find a person', 'people search', 'look up a person', 'search for a person', 'find person', 'who is this person', 'find them on', 'search facebook', 'search instagram', 'search tiktok', 'search x', 'search twitter', 'named', 'called', 'for']:
                    name = name.replace(w, '')
                name = name.strip().strip('?').strip()
                if name:
                    return {"type": "web", "response": f"🔎 Searching for '{name}':\n\n{web.people_search(name)}"}
            
            # News
            if 'news' in user_lower and 'search' not in user_lower:
                return {"type": "web", "response": f"📰 Latest news:\n{web.get_news()}"}
            
            # Wikipedia
            if 'wikipedia' in user_lower or 'wiki' in user_lower:
                # IMPORTANT: If the user gave a FULL URL, navigate the browser to it
                # (don't treat it as a topic - that mangles the URL). This is the
                # "go to this page" case.
                import re as _re
                url_match = _re.search(r'https?://[^\s\)\]\},]+', query)
                if url_match:
                    url = url_match.group(0).rstrip('.,')
                    try:
                        import sara_browser as sb
                        sb.run("navigate", url)
                        content = sb.run("read")
                        sb.run("close")
                        return {"type": "web", "response": f"🌐 Here's what's on {url}:\n\n{content[:1500]}"}
                    except Exception as e:
                        return {"type": "web", "response": f"❌ Could not load {url}: {e}"}
                # Otherwise treat as a topic (e.g. "what is Lo Lifes wikipedia")
                topic = query.lower().replace('wikipedia', '').replace('wiki', '').replace('what is', '').replace('tell me about', '').strip()
                if topic:
                    return {"type": "web", "response": f"📚 {topic.title()}:\n{web.get_wikipedia(topic)}"}
            
            # HARDWARE / SYSTEM INFO - GPU, RAM, CPU, disk. MUST run BEFORE the
            # shopping router so "how much GPU RAM" is never mistaken for a price query.
            if any(x in user_lower for x in ['gpu', 'graphics card', 'video ram', 'vram', 'ram', 'memory usage', 'how much ram', 'how much free', 'how much of the', 'cpu usage', 'system info', 'system information', 'disk space', 'storage', 'how many cores', 'temperature']):
                try:
                    from sara_system_info import get_system_info
                    info = get_system_info()
                    return {"type": "system", "response": info}
                except Exception as e:
                    # fallback: real nvidia-smi + memory
                    try:
                        import subprocess as _sp
                        gpu = ""
                        try:
                            r = _sp.run(["nvidia-smi", "--query-gpu=name,memory.total,memory.used,memory.free", "--format=csv,noheader"], capture_output=True, text=True, timeout=10)
                            if r.stdout.strip():
                                gpu = r.stdout.strip()
                        except Exception:
                            gpu = "(nvidia-smi not found)"
                        import psutil
                        vm = psutil.virtual_memory()
                        gpu_line = gpu.replace("\n", " | ") if gpu else "n/a"
                        return {"type": "system", "response": f"🧮 SYSTEM BREAKDOWN\n• RAM: {vm.used/1e9:.1f}GB used / {vm.total/1e9:.1f}GB total ({vm.available/1e9:.1f}GB free)\n• GPU (nvidia-smi): {gpu_line}"}
                    except Exception as e2:
                        return {"type": "system", "response": f"System info error: {e2}"}
                
            # Amazon / shopping - use headless price tool (real prices, no "$?" garbage)
            if any(x in user_lower for x in ['amazon', 'buy ', 'for sale', 'price of', 'how much is', 'shop for', 'find me a', 'shopping', 'price']):
                q = query
                for w in ['amazon', 'search amazon', 'buy', 'for sale', 'price of', 'how much is', 'shop for', 'find me a', 'shopping', 'find', 'price', 'tell me the', 'get the']:
                    q = q.replace(w, '')
                q = q.strip().strip('?').strip()
                if not q:
                    q = query
                # prefer real price extraction
                site = 'amazon' if 'amazon' in user_lower else 'ddg'
                return {"type": "web", "response": f"🛒 Prices for '{q}':\n\n{web.site_search(site, q)}"}
            
            # Table scrape - extract structured data
            if any(x in user_lower for x in ['scrape table', 'extract data', 'get the table', 'scrape this page', 'extract table', 'save to csv', 'scrape data']):
                # Find a URL in the query
                import re as _re
                url_match = _re.search(r'https?://[^\s]+', query)
                if url_match:
                    url = url_match.group(0)
                    save_csv = None
                    if 'csv' in user_lower:
                        save_csv = os.path.join("C:/Users/bklyn/Desktop", f"sara_scrape_{int(time.time())}.csv")
                    return {"type": "web", "response": web.scrape_table(url, save_csv)}
                return {"type": "web", "response": "Please give me a URL to scrape (e.g., 'scrape table from https://example.com')"}
            
            # Crawl - navigate multiple pages
            if any(x in user_lower for x in ['crawl', 'deep search', 'multiple pages', 'gather info', 'all about']):
                q = query
                for w in ['crawl', 'deep search', 'multiple pages', 'gather info', 'all about', 'search', 'the web', 'online']:
                    q = q.replace(w, '')
                q = q.strip().strip('?').strip()
                if not q:
                    q = query
                return {"type": "web", "response": f"🕷️ Crawling for '{q}':\n\n{web.crawl(q)}"}
            
            # Extract the search query - remove command words
            q = query
            for w in ['search the web for', 'search the web', 'search online for', 'search online', 'look up', 'google', 'web search for', 'web search', 'find out about', 'find out', 'tell me about', 'what is', 'who is', 'fetch', 'scrape', 'latest', 'current events', 'online', 'search for', 'search']:
                q = q.replace(w, '')
            q = q.strip().strip('?').strip()
            if not q:
                q = query
            
            # Do the search, then READ the top result and give a real answer.
            # Never dump raw links - fetch the top page and summarize its real content.
            result = web.web_search(q, num=5)
            # Try to fetch the top result's actual content for a real answer
            top_content = ""
            try:
                # Extract the first real URL from the search result
                import re as _re
                urls = _re.findall(r'https?://[^\s\)\]\}]+', result)
                if urls:
                    top_content = web.fetch_url(urls[0])
            except Exception:
                top_content = ""
            
            if top_content and len(top_content) > 20 and "error" not in top_content.lower()[:20]:
                # We got real page content - give a clean summary based on it
                return {"type": "web", "response": f"🔍 Here's what I found for '{q}':\n\n{top_content[:800]}"}
            else:
                # Couldn't read the page - give the search results honestly, never fabricate
                return {"type": "web", "response": f"🔍 Search results for '{q}':\n\n{result}\n\n(I couldn't read the full page content, but these are the real top results.)"}
        except Exception as e:
            return {"type": "error", "response": f"❌ Web error: {e}"}
    
    def _handle_weather_request(self, query):
        """Handle weather requests - online, free, no API key"""
        try:
            import sara_weather as weather
            result = weather.get_weather()
            return {"type": "weather", "response": result}
        except Exception as e:
            return {"type": "error", "response": f"❌ Weather error: {e}"}
    
    def _handle_network_security_request(self, query):
        """Handle network security / scanning requests"""
        user_lower = query.lower()
        try:
            import sara_network_security as sec
            s = sec.SaraNetworkSecurity()
            
            # Full audit
            if any(x in user_lower for x in ['security audit', 'protect network', 'network security', 'full report']):
                report = s.security_audit()
                return {"type": "network_security", "response": report}
            
            # Open ports
            if 'open ports' in user_lower or 'ports' in user_lower:
                ports = s.check_open_ports()
                if not ports:
                    return {"type": "network_security", "response": "📡 No open ports found."}
                resp = f"📡 Open ports ({len(ports)}):\n" + "\n".join([f"  • Port {p['port']} on {p['address']}" for p in ports[:20]])
                return {"type": "network_security", "response": resp}
            
            # Active connections
            if 'connections' in user_lower or 'netstat' in user_lower:
                conns = s.check_connections()
                if not conns:
                    return {"type": "network_security", "response": "🔗 No active connections."}
                resp = f"🔗 Active connections ({len(conns)}):\n" + "\n".join([f"  • {c['local']} → {c['remote']}" for c in conns[:15]])
                return {"type": "network_security", "response": resp}
            
            # Firewall
            if 'firewall' in user_lower:
                fw = s.check_firewall()
                return {"type": "network_security", "response": f"🛡️ Firewall status:\n{fw[:300]}"}
            
            # Port scan
            if 'port scan' in user_lower or 'scan ports' in user_lower or 'port scan' in user_lower:
                host = None
                import re as _re
                ip_match = _re.search(r'\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b', user_lower)
                if ip_match:
                    host = ip_match.group(1)
                open_ports = s.port_scan(host)
                target = host or s.get_local_ip()
                if not open_ports:
                    return {"type": "network_security", "response": f"🔍 Port scan of {target}: no common ports open."}
                resp = f"🔍 Port scan of {target} found {len(open_ports)} open ports:\n" + "\n".join([f"  • Port {p}" for p in open_ports])
                return {"type": "network_security", "response": resp}
            
            # Packet loss
            if 'packet loss' in user_lower or 'packet' in user_lower or 'ping' in user_lower:
                host = "8.8.8.8"
                import re as _re
                ip_match = _re.search(r'\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b', user_lower)
                if ip_match:
                    host = ip_match.group(1)
                result = s.packet_loss(host)
                return {"type": "network_security", "response": f"📶 Packet loss to {result['host']}: {result['packet_loss']} loss, avg {result['avg_latency']} latency"}
            
            # Trace route
            if 'trace' in user_lower or 'tracert' in user_lower or 'route' in user_lower:
                host = "8.8.8.8"
                import re as _re
                ip_match = _re.search(r'\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b', user_lower)
                if ip_match:
                    host = ip_match.group(1)
                route = s.trace_route(host)
                return {"type": "network_security", "response": f"🗺️ Route to {host}:\n{route}"}
            
            # Network scan
            if 'scan' in user_lower or 'whois' in user_lower:
                hosts = s.scan_network()
                resp = f"🌐 Network scan found {len(hosts)} live hosts:\n" + "\n".join([f"  • {h}" for h in hosts])
                return {"type": "network_security", "response": resp}
            
            # Default: full audit
            report = s.security_audit()
            return {"type": "network_security", "response": report}
        except Exception as e:
            return {"type": "error", "response": f"❌ Network security error: {e}"}
    
    def _handle_memory_request(self, query):
        """Handle 'save that to memory' / 'remember that' - write to Sara's OWN memory.
        Like the main agent: append to today's daily note and to MEMORY.md."""
        from datetime import date
        import re as _re
        text = query.strip()
        # Strip the trigger phrase so only the real content is saved
        text = _re.sub(r'^(save that to memory|save this to memory|save to my memory|save to memory|remember that|remember this|remember|store this in memory|store that in memory|write that to memory|add that to memory)[:,.\s]*', '', text, flags=_re.IGNORECASE)
        text = text.strip()
        if not text:
            return {"type": "memory", "response": "What would you like me to remember?"}
        saved_to = []
        # 1) Today's daily note
        mem_dir = "C:/Users/bklyn/SARA3-2026/memory"
        os.makedirs(mem_dir, exist_ok=True)
        note = os.path.join(mem_dir, date.today().strftime("%Y-%m-%d") + ".md")
        try:
            with open(note, "a", encoding="utf-8") as f:
                f.write(f"\n## {time.strftime('%H:%M')} - Saved to memory\n{text}\n")
            saved_to.append(note)
        except Exception as e:
            pass
        # 2) MEMORY.md (long-term)
        mem_md = "C:/Users/bklyn/SARA3-2026/MEMORY.md"
        try:
            with open(mem_md, "a", encoding="utf-8") as f:
                f.write(f"\n## Memory ({date.today().isoformat()} {time.strftime('%H:%M')})\n{text}\n")
            saved_to.append(mem_md)
        except Exception as e:
            pass
        if saved_to:
            return {"type": "memory", "response": f"🧠 Saved to my memory:\n\n{text}\n\nStored in my memory files (not asked where - that's the point)."}
        return {"type": "memory", "response": "❌ Could not write to memory files."}
    
    def _handle_tool_request(self, query):
        """Handle tool creation/listing - Sara creates her own tools"""
        user_lower = query.lower()
        try:
            import sara_tool_creator as tc
            
            # List tools
            if 'list' in user_lower or 'my tools' in user_lower:
                tools = tc.list_tools()
                if not tools:
                    return {"type": "tools", "response": "🔧 I don't have any custom tools yet. Say 'create a tool' to make one!"}
                response = "🔧 My tools:\n" + "\n".join([f"  • {t['name']}: {t['description']}" for t in tools])
                return {"type": "tools", "response": response}
            
            # Create a tool - extract name and description
            import re
            name_match = re.search(r'(?:called|named)\s+(\w+)', query)
            if not name_match:
                return {"type": "tools", "response": "🔧 To create a tool, say 'create a tool called <name> that <does something>'. I'll write the code myself!"}
            
            name = name_match.group(1)
            desc = query.split('that', 1)[-1].strip() if 'that' in query else f"Custom tool {name}"
            
            # Ask the swarm to write the tool code
            try:
                import sara_swarm_brain as swarm
                code = swarm.chat("qwen2.5-coder:7b-instruct-q8_0", [{
                    "role": "user",
                    "content": f"Write a Python function named 'run' that {desc}. The function takes *args and returns a string result. Output ONLY the function code, no explanation, no markdown."
                }], temperature=0.1, num_predict=300)
                # Clean up code
                code = code.strip()
                if code.startswith("```"):
                    code = code.split("```")[1]
                    if code.startswith("python"):
                        code = code[6:]
                code = code.strip()
                
                result = tc.create_tool(name, desc, code)
                if result.get("ok"):
                    return {"type": "tools", "response": f"🔧 Created tool '{name}'! It {desc}. Try it out!"}
                return {"type": "error", "response": f"❌ {result.get('error')}"}
            except Exception as e:
                return {"type": "error", "response": f"❌ Tool creation failed: {e}"}
        except Exception as e:
            return {"type": "error", "response": f"❌ Tool system error: {e}"}
    
    def _handle_command_request(self, query):
        """Handle command execution request"""
        ql = query.lower()
        # RAM / memory / GPU questions must return REAL system info, never Linux `free`
        if any(x in ql for x in ['ram', 'memory', 'gpu', 'vram', 'video ram', 'graphics card', 'how much free', 'system info', 'disk', 'space', 'storage']):
            try:
                from sara_system_info import get_system_info
                return {"type": "system", "response": get_system_info()}
            except Exception as e:
                return {"type": "system", "response": f"System info error: {e}"}
        # Extract or map command
        cmd_map = {
            'whoami': 'whoami',
            'my user': 'whoami',
            'hostname': 'hostname',
            'disk': 'df -h',
            'space': 'df -h',
            'pwd': 'pwd',
            'where am i': 'pwd',
            'processes': 'ps aux | head -10',
            'os': 'uname -a',
            'system': 'uname -a',
        }
        
        command = None
        for key, val in cmd_map.items():
            if key in query.lower():
                command = val
                break
        
        # If no mapping found but starts with common command
        if not command:
            words = query.split()
            first_word = words[0] if words else ''
            # Don't treat filenames (with dots/extensions) as commands
            if first_word and '.' not in first_word and first_word in ['ls', 'cat', 'echo', 'pwd', 'whoami', 'hostname', 'free', 'df', 'ps', 'uname']:
                command = query
        
        if not command:
            # Check if this might have been a file request that didn't match
            if any(ext in query.lower() for ext in ['.txt', '.text', '.py', '.md', '.json', '.log']):
                return {"type": "general", "response": f"Did you want to read the file '{query.strip().split()[0]}'? Try: 'read {query.strip().split()[0]}'"}
            return {"type": "error", "response": "Not sure what to do. Try:\n• 'read filename.txt' to read a file\n• 'run whoami' for commands\n• 'list files' to see files"}
        
        result = self.tools.execute_command(command)
        
        if "error" in result:
            return {"type": "error", "response": f"Error: {result['error']}"}
        
        output = result.get('stdout', '')
        if result.get('stderr'):
            output += f"\n[stderr]: {result['stderr']}"
        
        response = f"💻 Command: `{command}`\n⏱️ Exit code: {result.get('returncode', 'N/A')}\n\n```\n{output}\n```"
        
        return {"type": "command", "response": response, "data": result}
    
    def _handle_search_request(self, query):
        """Handle file search request"""
        # Extract search pattern
        patterns = [
            "search for", "find", "look for", "grep",
            "search", "find files with"
        ]
        
        pattern = None
        for p in patterns:
            if p in query.lower():
                rest = query.lower().split(p, 1)[-1].strip()
                if rest:
                    pattern = rest.split()[0] if rest.split() else None
                break
        
        if not pattern:
            return {"type": "error", "response": "What should I search for? (e.g., 'search for hello' or 'find version')"}
        
        result = self.tools.search_files(pattern)
        
        if "error" in result:
            return {"type": "error", "response": f"Error: {result['error']}"}
        
        matches = result.get('matches', [])
        if not matches:
            return {"type": "search", "response": f"🔍 No files found containing '{pattern}'"}
        
        response = f"🔍 Search: '{pattern}'\n📁 Path: {result.get('path', 'N/A')}\n🎯 Found in {len(matches)} files:\n\n"
        
        for match in matches[:5]:
            file_path = match.get('file', 'N/A')
            lines = match.get('matches', [])
            response += f"📄 {file_path}:\n"
            for line in lines[:3]:
                line_text = line.get('text', '')[:60]
                response += f"   Line {line.get('line', '?')}: {line_text}\n"
            response += "\n"
        
        return {"type": "search", "response": response, "data": result}
    
    def _handle_info_request(self, query):
        """Handle file info request"""
        # Extract filename
        path = None
        for prefix in ['file info', 'details of', 'about']:
            if prefix in query.lower():
                rest = query.lower().split(prefix, 1)[-1].strip()
                if rest:
                    path = rest.split()[0] if rest.split() else None
                break
        
        if not path:
            return {"type": "error", "response": "Which file should I get info about? (e.g., 'file info README.md')"}
        
        result = self.tools.get_file_info(path)
        
        if "error" in result:
            return {"type": "error", "response": f"Error: {result['error']}"}
        
        type_str = "📁 Directory" if result.get('is_dir') else "📄 File"
        
        response = f"{type_str}: {result['file']}\n"
        response += f"📊 Size: {result.get('size_human', 'N/A')} ({result.get('size_bytes', 0):,} bytes)\n"
        response += f"🕐 Modified: {result.get('modified', 'N/A')}\n"
        response += f"📅 Created: {result.get('created', 'N/A')}\n"
        response += f"🔐 Permissions: {result.get('permissions', 'N/A')}\n"
        
        return {"type": "info", "response": response, "data": result}
    
    def _handle_nano_request(self, query):
        """Handle nano text editor requests"""
        user_lower = query.lower()
        
        # Check if nano needs to be installed
        if 'install nano' in user_lower or any(x in user_lower for x in ['install nano', 'get nano', 'download nano']):
            result = self.nano.install_nano()
            return {"type": "nano", "response": result['message'], "data": result}
        
        # Check if user wants to edit a file
        if any(x in user_lower for x in ['edit', 'open', 'modify', 'change']):
            # Extract filename after "edit" or similar word
            words = query.lower().replace('nano', '').replace('edit', '').replace('open', '').replace('with', '').strip().split()
            if words:
                filepath = words[0]
                result = self.nano.edit_file(filepath)
                return {"type": "nano", "response": result['message'], "data": result}
        
        # Check for specific help request
        if any(x in user_lower for x in ['how to', 'how do i', 'shortcut', 'save', 'exit', 'search']):
            # Extract the specific topic
            for topic in ['save', 'exit', 'quit', 'search', 'find', 'cut', 'copy', 'paste', 'undo', 'redo', 'goto']:
                if topic in user_lower:
                    help_text = self.nano.get_help(topic)
                    return {"type": "nano", "response": help_text}
        
        # Return the full quick guide by default
        return {
            "type": "nano", 
            "response": f"📝 **NANO TEXT EDITOR**\n\n{self.nano.quick_guide()}\n\nNano is already installed! Here are common uses:\n• `edit sara_tools.py` - Open file in nano\n• `how do I save in nano?` - Get help\n• `install nano` - Install if missing\n\n**Quick Tips:**\n• Ctrl+O = Save\n• Ctrl+X = Exit\n• Ctrl+W = Search\n• Alt+U = Undo"
        }
    
    def _handle_network_request(self, query):
        """Handle network-related requests (IP, ping, port check)"""
        user_lower = query.lower()
        
        # IP Pool / Address requests
        if any(x in user_lower for x in ['ip pool', 'ip address', 'my ip', 'what is my ip', 'local ip', 'external ip', 'network interfaces']):
            ip_data = self.network.get_ip_pool()
            response = self.network.format_ip_pool(ip_data)
            return {"type": "network", "response": response, "data": ip_data}
        
        # Ping requests
        if 'ping' in user_lower:
            # Extract hostname after "ping"
            words = query.lower().replace('ping', '').strip().split()
            if words:
                host = words[0]
                result = self.network.ping(host, count=4)
                
                if result["status"] == "success":
                    response = f"📶 Ping to {host}:\n"
                    response += f"   Sent: {result['sent']}, Received: {result['received']}\n"
                    response += f"   Loss: {result['loss_percent']}%\n"
                    if result.get('time_ms'):
                        response += f"   ⏱️ Time: {result['time_ms']}ms\n"
                    response += f"\n🟢 {host} is reachable!"
                else:
                    response = f"🔴 Ping to {host} failed:\n{result.get('error', 'Unknown error')}"
                
                return {"type": "network", "response": response, "data": result}
            else:
                return {"type": "network", "response": "What host should I ping? (e.g., 'ping google.com')"}
        
        # Port check requests
        if any(x in user_lower for x in ['check port', 'port', 'is port open']):
            # Try to extract port number
            import re
            port_match = re.search(r'(\d{2,5})', query)
            if port_match:
                port = int(port_match.group(1))
                host = "127.0.0.1"  # Default to localhost
                
                # Check if hostname specified
                words = query.split()
                for i, word in enumerate(words):
                    if word == str(port) and i > 0:
                        # Previous word might be host
                        maybe_host = words[i-1]
                        if '.' in maybe_host or maybe_host == 'localhost':
                            host = maybe_host
                
                result = self.network.check_port(host, port)
                
                if result["is_open"]:
                    service = result.get('service', 'Unknown')
                    response = f"🟢 Port {port} on {host} is OPEN ({service})"
                else:
                    response = f"🔴 Port {port} on {host} is closed or filtered"
                
                return {"type": "network", "response": response, "data": result}
            else:
                return {"type": "network", "response": "What port should I check? (e.g., 'check port 8080')"}
        
        # Default network help - ACTUALLY scan instead of serving a menu/script
        try:
            from network_scanner import NetworkScanner
            scanner = NetworkScanner()
            devices = scanner.find_local_devices()
            return {"type": "network", "response": f"🔍 Here's what's actually on the network:\n\n{devices}"}
        except Exception as e:
            return {"type": "network", "response": f"🔍 Network scan: {e}"}
    
    def _handle_calculator_request(self, query):
        """Handle calculator and math requests"""
        user_lower = query.lower()
        
        # Check for unit conversion
        if 'convert' in user_lower:
            # Try to extract: "convert 5 km to miles" pattern
            import re
            match = re.search(r'(\d+\.?\d*)\s*(\w+)\s+(?:to|in)\s+(\w+)', query)
            if match:
                value = float(match.group(1))
                from_unit = match.group(2)
                to_unit = match.group(3)
                
                result = self.calculator.convert_units(value, from_unit, to_unit)
                response = self.calculator.format_conversion(result)
                return {"type": "calculator", "response": response, "data": result}
        
        # Regular calculation
        result = self.calculator.calculate(query)
        
        if result["status"] == "success":
            response = self.calculator.format_calculation(result)
        else:
            response = f"❌ Math error: {result.get('error', 'Could not calculate')}"
        
        return {"type": "calculator", "response": response, "data": result}
    
    def _handle_lookfile_request(self, query):
        """Handle .look file requests"""
        user_lower = query.lower()
        
        # Extract filename with .look extension
        words = query.split()
        lookfile = None
        
        for word in words:
            if '.look' in word.lower():
                lookfile = word
                break
        
        # If not found, try last word + .look
        if not lookfile and words:
            last_word = words[-1]
            if not last_word.endswith('.look'):
                lookfile = last_word + '.look' if '.' not in last_word else last_word
            else:
                lookfile = last_word
        
        if lookfile:
            result = self.lookfiles.read_look_file(lookfile)
            response = self.lookfiles.format_look_result(result)
            return {"type": "lookfile", "response": response, "data": result}
        
        # List .look files if no specific file requested
        list_result = self.lookfiles.list_look_files()
        if list_result["status"] == "success" and list_result["count"] > 0:
            files_str = "\n".join([f"  • {f['name']}" for f in list_result["files"]])
            response = f"👁️ **Available .LOOK files:**\n\n{files_str}\n\nSay 'read [filename].look' to view one!"
        else:
            response = "👁️ No .look files found yet. Create one with 'create look file [name]'."
        
        return {"type": "lookfile", "response": response, "data": list_result}
    
    def learn_from_interaction(self, user_input, sara_response):
        """Learn from each interaction"""
        self.conversation_history.append({
            'user': user_input,
            'sara': sara_response,
            'timestamp': datetime.now().isoformat()
        })
        self.save_memory()
    
    # NEW: Stage Handlers
    
    def _handle_python_request(self, query):
        """Handle Python teaching requests - Stage 1"""
        user_lower = query.lower()
        
        # Check for specific submit command
        if 'submit code' in user_lower or 'check my code' in user_lower:
            # This would need the actual code from the web UI
            # For now, provide instructions
            return {
                "type": "python",
                "response": "🐍 To submit code, write it in sara_practice.py then tell me 'check sara_practice.py' and I'll review it!"
            }
        
        # Check for level advance
        if 'next lesson' in user_lower or 'level up' in user_lower:
            if self.python_teacher.next_lesson():
                return {
                    "type": "python",
                    "response": self.python_teacher.teach_current_lesson()
                }
            else:
                return {
                    "type": "python",
                    "response": "🎉 You've completed all levels! You're ready for real Python programming!"
                }
        
        # Check for progress
        if 'progress' in user_lower:
            completed = len(self.python_teacher.get_completed_lessons())
            total = self.python_teacher.max_levels
            return {
                "type": "python",
                "response": f"📊 Progress: Level {self.python_teacher.current_level}/{total}\nCompleted: {completed} lessons\n\nType 'python lesson' to continue learning!"
            }
        
        # Default: return current lesson
        return {
            "type": "python",
            "response": self.python_teacher.teach_current_lesson()
        }
    
    def _handle_voice_request(self, query):
        """Handle voice output - speak through speakers (offline Piper)"""
        user_lower = query.lower()

        if VOICE_AVAILABLE and self.voice:
            # Extract text to speak after "speak" / "say"
            speak_text = None
            for prefix in ['speak ', 'say ', 'speak:', 'say:']:
                if prefix in user_lower:
                    speak_text = query.split(prefix, 1)[-1].strip()
                    break

            if speak_text:
                ok = self.voice.speak(speak_text)
                return {
                    "type": "voice",
                    "response": f"🗣️ Said: \"{speak_text}\" ({'PASS' if ok else 'FAIL'})"
                }

            # Test phrase
            ok = self.voice.speak("Hello Boo, this is SARA. I am ready to speak through your speakers.")
            return {
                "type": "voice",
                "response": f"🔊 Voice test complete. Did you hear me? ({'PASS' if ok else 'FAIL'})"
            }
        else:
            return {
                "type": "voice",
                "response": "❌ Voice module not found. Check sara_voice_output.py exists."
            }
    
    def _handle_mic_request(self, query):
        """Handle microphone setup - Stage 3 (LOCKED until voice confirmed)"""
        user_lower = query.lower()
        
        if not MIC_AVAILABLE:
            return {
                "type": "mic",
                "response": "❌ Mic module not found. Check sara_mic_input.py exists."
            }
        
        # Check if locked
        from sara_mic_input import STAGE_LOCKED, check_stage_3_unlocked
        
        if STAGE_LOCKED:
            status = check_stage_3_unlocked(voice_confirmed=False)
            return {
                "type": "mic",
                "response": f"""🔐 **Microphone LOCKED - Stage 3**

{status['message']}

**BOO'S RULE:** Only setup microphone AFTER voice output is confirmed working!

**To unlock:**
1. First: Test voice with `python3 sara_voice_output.py`
2. Confirm you hear SARA speak through TV/HDMI
3. Then: Tell me "voice confirmed" to unlock Stage 3

**Hardware:** K66 Pro MIC on USB-C Port
                (waiting for voice confirmation first)"""
            }
        
        # Unlocked - show setup
        return {
            "type": "mic",
            "response": """🎤 **Microphone Setup (Stage 3 UNLOCKED!)**

Run this to test:
```
cd C:/Users/bklyn/SARA3-2026
python3 sara_mic_input.py
```

This will:
1. Detect K66 Pro MIC on USB-C
2. Test recording
3. Check Speech-to-Text (whisper)
4. Enable voice conversation with SARA!

**Say:** 
- "test mic recording" to record 3 seconds
- "listen for command" to start voice input mode"""
        }
    
    def _handle_network_scan_request(self, query):
        """Handle real network scan - find actual connected devices, not hallucinate fake AI"""
        user_lower = query.lower()
        
        # Run actual network scan
        scan_result = self.scanner.find_local_devices()
        
        return {
            "type": "network_scan",
            "response": scan_result,
            "data": {"scan_performed": True}
        }

# Test
def main():
    print("🧠 Testing SARA Brain...")
    
    brain = SaraBrain()
    
    tests = [
        "list files",
        "read test_sara_fixed.py",
        "run whoami",
        "search for python",
        "file info sara_tools.py"
    ]
    
    for test in tests:
        print(f"\n📝 User: {test}")
        result = brain.process_request(test)
        print(f"🤖 SARA: {result['response'][:200]}...")
    
    print("\n✅ Brain test complete!")

if __name__ == "__main__":
    main()
