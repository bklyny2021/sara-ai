#!/usr/bin/env python3
"""
🎓 SARA LEARNING LOG - Tracks what she learns and how
Every 30 minutes she learns something new!
"""

import json
import os
from datetime import datetime
from typing import Dict, List

class SaraLearningLog:
    """Tracks SARA's continuous learning journey"""
    
    def __init__(self, log_dir: str = None):
        if log_dir is None:
            log_dir = "C:/Users/bklyn/SARA3-2026/learning_logs"
        self.log_dir = log_dir
        self.daily_log = os.path.join(log_dir, f"learned_{datetime.now().strftime('%Y-%m-%d')}.json")
        
        # Ensure directory exists
        os.makedirs(log_dir, exist_ok=True)
        
        # Load or create today's log
        self.load_log()
    
    def load_log(self):
        """Load today's learning log"""
        if os.path.exists(self.daily_log):
            with open(self.daily_log, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {
                "date": datetime.now().isoformat(),
                "total_lessons": 0,
                "lessons": [],
                "skills_gained": [],
                "capabilities_count": 0
            }
    
    def save_log(self):
        """Save learning log"""
        with open(self.daily_log, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def record_lesson(self, lesson_name: str, how_learned: str, 
                      what_learned: str, proof_of_working: str,
                      code_changes: List[str] = None):
        """
        Record a new lesson
        
        Args:
            lesson_name: Name of what was taught
            how_learned: The method/process of learning
            what_learned: Detailed description of the knowledge/skill
            proof_of_working: Test output or evidence it works
            code_changes: List of files modified/created
        """
        lesson = {
            "timestamp": datetime.now().isoformat(),
            "lesson_number": self.data["total_lessons"] + 1,
            "lesson_name": lesson_name,
            "how_learned": how_learned,
            "what_learned": what_learned,
            "proof_of_working": proof_of_working,
            "code_changes": code_changes or [],
            "verified": True
        }
        
        self.data["lessons"].append(lesson)
        self.data["total_lessons"] += 1
        
        # Add to skills list if new
        if lesson_name not in self.data["skills_gained"]:
            self.data["skills_gained"].append(lesson_name)
        
        self.data["capabilities_count"] = len(self.data["skills_gained"])
        
        self.save_log()
        
        return lesson
    
    def get_progress_summary(self) -> str:
        """Get a summary of what SARA has learned today"""
        summary = f"""
╔══════════════════════════════════════════════════════════╗
║  📚 SARA'S LEARNING LOG - {datetime.now().strftime('%B %d, %Y')}      ║
╠══════════════════════════════════════════════════════════╣
║  Total Lessons Today: {self.data['total_lessons']:2d}                            ║
║  Unique Skills: {self.data['capabilities_count']:2d}                               ║
╠══════════════════════════════════════════════════════════╣
"""
        
        if self.data["skills_gained"]:
            summary += "║  SKILLS GAINED:                                          ║\n"
            for skill in self.data["skills_gained"][-5:]:  # Last 5
                summary += f"║    • {skill[:45]:45s}          ║\n"
        
        summary += "╚══════════════════════════════════════════════════════════╝\n"
        
        return summary
    
    def get_latest_lesson(self) -> Dict:
        """Get the most recent lesson"""
        if self.data["lessons"]:
            return self.data["lessons"][-1]
        return None
    
    def format_lesson_detail(self, lesson: Dict) -> str:
        """Format a lesson for display"""
        return f"""
🎓 LESSON #{lesson['lesson_number']}: {lesson['lesson_name']}
⏰ Learned at: {lesson['timestamp']}

📖 HOW I LEARNED IT:
{lesson['how_learned']}

🧠 WHAT I LEARNED:
{lesson['what_learned']}

✅ PROOF IT'S WORKING:
{lesson['proof_of_working']}

💻 FILES CHANGED:
{chr(10).join(['  • ' + f for f in lesson['code_changes']]) if lesson['code_changes'] else '  None'}
"""

def main():
    """Test the learning log"""
    print("🧪 Testing SaraLearningLog...")
    
    log = SaraLearningLog()
    
    # Record a sample lesson
    lesson = log.record_lesson(
        lesson_name="Network IP Pool Detection",
        how_learned="MAX built network_tool.py with get_ip_pool() method, then wired it into my brain by importing in sara_brain.py and adding detection pattern",
        what_learned="I can now detect network queries like 'ip pool', 'my ip', 'ping host', 'check port'. I use NetworkTool class to get local IP (10.211.144.110), external IP (107.13.106.21), and all interfaces. I can format this into pretty output with emojis.",
        proof_of_working="Test output: 🌐 **IP POOL INFORMATION**\n📍 Hostname: DESKTOP-19SGUQU\n🏠 Local IP (Primary): 10.211.144.110\n🌍 External IP: 107.13.106.21",
        code_changes=["network_tool.py", "sara_brain.py"]
    )
    
    print("\n" + log.get_progress_summary())
    print("\n" + log.format_lesson_detail(lesson))
    
    print(f"\n💾 Log saved to: {log.daily_log}")

if __name__ == "__main__":
    main()