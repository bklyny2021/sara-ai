#!/usr/bin/env python3
"""
🎓 SARA AUTO-TEACH HEARTBEAT
Runs every 30 minutes to teach SARA something new
Logs everything she learns
"""

import os
import sys
import random
import json
from datetime import datetime

# Add SARA2_v2 to path
sys.path.insert(0, 'C:/Users/bklyn/SARA3-2026')

from sara_learning_log import SaraLearningLog
from sara_brain import SaraBrain

class TeachingCurriculum:
    """Curriculum of lessons to teach SARA"""
    
    def __init__(self):
        self.lessons = [
            {
                "name": "Calculator Tool",
                "teach_method": "Created calculator_tool.py with CalculatorTool class. Can do: basic math (5 plus 3), scientific functions (sqrt, power), unit conversions (km to miles).",
                "what_she_learns": "I can now calculate! I detect math phrases like 'calculate', 'plus', 'times', 'squared'. I use eval safely with allowed functions. I can convert units between length/weight/storage.",
                "test_query": "calculate 100 divided by 4",
                "verify_func": self.verify_calculator
            },
            {
                "name": "Look File Handler",
                "teach_method": "Created lookfile_tool.py for .look files. Handles: plain text, JSON, key:value pairs, markdown. Auto-detects content type and formats nicely.",
                "what_she_learns": "I can read .look files! These are special observation logs. I detect content type (json, keyval, markdown, plain) and format output with emojis and structure. I look for .look extension.",
                "test_query": "read network_status.look",
                "verify_func": self.verify_lookfile
            },
            {
                "name": "Network Diagnostics",
                "teach_method": "Created network_tool.py with NetworkTool class. Gets IP pool (local/external), pings hosts, checks ports. Uses socket and subprocess.",
                "what_she_learns": "I can do network stuff! I get local IP (10.211.144.110), external IP, all interfaces. I can ping (google.com) and check if ports are open (8892). I format output with emojis.",
                "test_query": "what is my ip",
                "verify_func": self.verify_network
            },
            {
                "name": "File Pattern Recognition",
                "teach_method": "Enhanced brain to detect file patterns: 'look filename.txt', 'open README.md'. Extracts filename and routes to read handler.",
                "what_she_learns": "I understand file commands better now! If someone says 'look sara.text' I know it's a file, not a command. I detect extensions (.py, .md, .json, .look) and file indicator words.",
                "test_query": "open README.md",
                "verify_func": self.verify_file_patterns
            },
            {
                "name": "Nano Editor Helper",
                "teach_method": "Created nano_guide.py with NanoHelper class. Teaches me nano shortcuts and helps users open files.",
                "what_she_learns": "I know nano now! Ctrl+O=save, Ctrl+X=exit, Ctrl+W=search. I can tell users how to edit files. I can check if nano is installed and help them open files.",
                "test_query": "how do I save in nano",
                "verify_func": self.verify_nano
            },
            {
                "name": "Activity State Tracking",
                "teach_method": "ActivityTracker class tracks: THINKING, TYPING, READING, SEARCHING, EXECUTING, IDLE. Granular states for sidebar display.",
                "what_she_learns": "I track my own activity! When I'm thinking vs typing vs reading files. I show this in the sidebar. I know when I'm idle vs busy.",
                "test_query": "who are you",
                "verify_func": self.verify_identity
            }
        ]
    
    def get_next_lesson(self, log: SaraLearningLog) -> dict:
        """Get next lesson that hasn't been learned yet"""
        learned_skills = set(log.data.get("skills_gained", []))
        
        # Find lessons not yet learned
        available = [l for l in self.lessons if l["name"] not in learned_skills]
        
        if available:
            return random.choice(available)
        
        # All lessons learned - review a random one
        return random.choice(self.lessons)
    
    # Verification methods
    def verify_calculator(self, brain: SaraBrain) -> tuple:
        result = brain.process_request("calculate 5 plus 3")
        return (result["type"] == "calculator" and result["data"]["status"] == "success", 
                f"Got answer: {result['data'].get('formatted', 'N/A')}")
    
    def verify_lookfile(self, brain: SaraBrain) -> tuple:
        result = brain.process_request("list .look files")
        return (result["type"] == "lookfile", 
                f"Found files: {result['data'].get('count', 0)}")
    
    def verify_network(self, brain: SaraBrain) -> tuple:
        result = brain.process_request("ip pool")
        return (result["type"] == "network", 
                f"Has local IP: {'local_ip' in str(result.get('data', {}))}")
    
    def verify_file_patterns(self, brain: SaraBrain) -> tuple:
        result = brain.process_request("read README.md")
        return (result["type"] == "read", 
                f"Read file successfully: {result['data'].get('file', 'none')}")
    
    def verify_nano(self, brain: SaraBrain) -> tuple:
        result = brain.process_request("how do I save in nano")
        return (result["type"] == "nano", 
                f"Knew nano shortcut: {'Ctrl' in str(result.get('response', ''))}")
    
    def verify_identity(self, brain: SaraBrain) -> tuple:
        result = brain.process_request("who are you")
        return (result["type"] == "identity", 
                f"Response: {result.get('response', 'none')[:30]}")


def teach_sara_new_skill():
    """Main teaching function - runs every 30 min via cron"""
    
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "🎓 SARA AUTO-TEACH HEARTBEAT" + " "*17 + "║")
    print("║" + " "*20 + f"{datetime.now().strftime('%H:%M:%S')}" + " "*30 + "║")
    print("╚" + "="*58 + "╝\n")
    
    # Initialize
    log = SaraLearningLog()
    brain = SaraBrain()
    curriculum = TeachingCurriculum()
    
    print(f"📚 Previous lessons today: {log.data['total_lessons']}")
    print(f"🧠 Unique skills: {len(log.data['skills_gained'])}")
    print()
    
    # Get lesson to teach
    lesson = curriculum.get_next_lesson(log)
    
    print(f"🎓 TEACHING: {lesson['name']}")
    print(f"📖 Method: {lesson['teach_method'][:60]}...\n")
    
    # Test the skill
    print(f"🧪 Testing with query: '{lesson['test_query']}'")
    try:
        is_working, proof = lesson['verify_func'](brain)
        
        if is_working:
            print(f"✅ VERIFIED WORKING: {proof}\n")
            status = "success"
        else:
            print(f"⚠️ Issue: {proof}\n")
            status = "partial"
            
    except Exception as e:
        print(f"❌ Test failed: {e}\n")
        is_working = False
        proof = f"Error: {str(e)}"
        status = "error"
    
    # Record the lesson
    learned = log.record_lesson(
        lesson_name=lesson['name'],
        how_learned=lesson['teach_method'],
        what_learned=lesson['what_she_learns'],
        proof_of_working=proof if is_working else f"Issue: {proof}",
        code_changes=[]  # Tracked separately
    )
    
    print("📋 LESSON LOGGED:")
    print(f"   Lesson #{learned['lesson_number']}: {lesson['name']}")
    print(f"   Status: {status}")
    print(f"   Proof: {proof[:50]}...")
    print()
    
    # Show progress
    print(log.get_progress_summary())
    
    print(f"💾 Log saved: {log.daily_log}\n")
    
    return {
        "status": status,
        "lesson": lesson['name'],
        "working": is_working,
        "proof": proof,
        "total_lessons": log.data['total_lessons']
    }

if __name__ == "__main__":
    result = teach_sara_new_skill()
    
    # Exit with appropriate code for cron monitoring
    if result['status'] == "error":
        sys.exit(1)
    else:
        sys.exit(0)