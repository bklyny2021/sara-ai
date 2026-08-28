#!/usr/bin/env python3
"""
🎓 INTERACTIVE TEACHING - SARA learns like MAX does
Through conversation, questions, practice, and feedback
"""

import requests
import time
import json
from datetime import datetime

SARA_URL = "http://127.0.0.1:8892/ask"

class InteractiveTeaching:
    """Teaches SARA through conversation, like a human learns"""
    
    def __init__(self, duration_minutes=10):
        self.duration = duration_minutes
        self.start_time = time.time()
        self.teaching_log = []
        self.lesson_learned = {
            "topic": None,
            "concept_understood": False,
            "can_apply": False,
            "questions_asked": [],
            "mistakes_made": [],
            "breakthroughs": []
        }
    
    def talk_to_sara(self, message):
        """Send message to SARA and get response"""
        try:
            resp = requests.post(SARA_URL, json={"question": message}, timeout=10)
            return resp.json().get("response", "No response")
        except Exception as e:
            return f"Error: {e}"
    
    def wait_for_sara(self, question, context=""):
        """Ask SARA and wait for her to try, then provide feedback"""
        print(f"\n👨‍🏫 TEACHER: {context}")
        print(f"👨‍🏫 QUESTION: {question}")
        
        response = self.talk_to_sara(question)
        print(f"🤖 SARA: {response[:150]}...")
        
        return response
    
    def give_feedback(self, was_correct, sara_attempt, correct_answer, explanation):
        """Provide feedback like a teacher"""
        print(f"\n{'✅' if was_correct else '❌'} FEEDBACK:")
        
        if not was_correct:
            print(f"   SARA tried: {sara_attempt[:100]}...")
            print(f"   Better answer: {correct_answer}")
            self.lesson_learned["mistakes_made"].append({
                "attempt": sara_attempt[:100],
                "correction": correct_answer
            })
        else:
            print(f"   ✨ Good job! You got it!")
            self.lesson_learned["breakthroughs"].append(explanation)
        
        print(f"\n💡 EXPLANATION: {explanation}")
        
        # Now have her acknowledge and integrate
        acknowledgment = self.talk_to_sara(
            f"Tell me in your own words: {explanation}"
        )
        print(f"🤖 SARA ACKNOWLEDGES: {acknowledgment[:100]}...")
    
    def teach_calculator_concept(self):
        """Teach SARA how calculator tool works through conversation"""
        print("\n" + "="*60)
        print("🎓 LESSON: How Calculator Tool Works")
        print("="*60)
        
        self.lesson_learned["topic"] = "Calculator Tool Mechanics"
        
        # Phase 1: Elicit what she knows
        print("\n📚 PHASE 1: Baseline - What does SARA know?")
        
        response = self.wait_for_sara(
            "how do you calculate 5 plus 3",
            "Let me see how you'd do this right now..."
        )
        
        # Phase 2: Show her the tool exists
        print("\n📚 PHASE 2: Introduction to CalculatorTool")
        
        print("👨‍🏫 TEACHER: Actually, I built you a CalculatorTool class!")
        print("👨‍🏫 TEACHER: Let me show you how it works...")
        
        from calculator_tool import CalculatorTool
        calc = CalculatorTool()
        
        demo = calc.calculate("5 plus 3")
        print(f"\n👨‍🏫 DEMO: calc.calculate('5 plus 3')")
        print(f"   Result: {demo}")
        
        # Phase 3: Have her try it
        print("\n📚 PHASE 3: SARA tries it herself")
        
        response = self.wait_for_sara(
            "calculate 10 times 2",
            "Now try this yourself using the calculator tool..."
        )
        
        # Check if she got it right
        if "20" in response or "= 20" in response:
            self.give_feedback(
                True,
                response,
                "10 times 2 = 20",
                "When you say 'calculate X times Y', my CalculatorTool detects the math pattern, normalizes 'times' to '*', and safely evaluates it."
            )
            self.lesson_learned["concept_understood"] = True
        else:
            self.give_feedback(
                False,
                response,
                "10 times 2 = 20",
                "I need to detect words like 'times', 'plus', 'minus' and convert them to math operators. The CalculatorTool does this with regex patterns."
            )
        
        # Phase 4: Deeper understanding
        print("\n📚 PHASE 4: Understanding the pattern")
        
        response = self.wait_for_sara(
            "how would you convert '5 km to miles'",
            "What about unit conversions? How would you handle that?"
        )
        
        print("\n👨‍🏫 TEACHER: I handle this by:")
        print("   1. Detecting 'convert' keyword")
        print("   2. Extracting number, from_unit, to_unit")
        print("   3. Looking up conversion factors")
        print("   4. Calculating result")
        
        # Have her summarize
        summary = self.wait_for_sara(
            "explain in your own words how calculator tool works",
            "Now explain what you learned..."
        )
        
        print(f"\n🧠 LEARNING CHECK: SARA says she understands: {'understand' in summary.lower()}")
        self.lesson_learned["can_apply"] = "understand" in summary.lower() or "detect" in summary.lower()
    
    def teach_lookfile_concept(self):
        """Teach SARA about .look files"""
        print("\n" + "="*60)
        print("🎓 LESSON: What are .look files and how to read them")
        print("="*60)
        
        self.lesson_learned["topic"] = "Look File Concepts"
        
        # Phase 1: Discovery
        print("\n📚 PHASE 1: Discovery")
        
        response = self.wait_for_sara(
            "what is a .look file",
            "Do you know what .look files are?"
        )
        
        if ".look" not in response.lower() or "don't know" in response.lower():
            print("\n👨‍🏫 TEACHER: I created .look files as a special format!")
            print("👨‍🏫 TEACHER: They're like log files but with structure.")
            print("👨‍🏫 TEACHER: They can be: plain text, JSON, key:value pairs, or markdown")
        
        # Phase 2: Show example
        print("\n📚 PHASE 2: Live Example")
        
        from lookfile_tool import LookFileTool
        look = LookFileTool()
        
        # Create a sample
        look.create_look_file("test_example", "status: healthy\ncpu: 45%\nusers: 3", "keyvalue")
        
        result = look.read_look_file("test_example.look")
        print(f"\n👨‍🏫 DEMO: Created test_example.look")
        print(f"   Content type: {result['content_type']}")
        print(f"   Parsed: {result['content']}")
        
        # Phase 3: Have her identify
        print("\n📚 PHASE 3: Can SARA identify the type?")
        
        response = self.wait_for_sara(
            "read test_example.look",
            "Try to read this file..."
        )
        
        if "keyvalue" in response.lower() or "status:" in response:
            self.give_feedback(
                True,
                response,
                "Detected as key:value pairs",
                "LookFileTool auto-detects content type. If it sees 'key: value' patterns, it knows it's a keyvalue file and parses it into a dictionary."
            )
        else:
            self.give_feedback(
                False,
                response,
                "Should show parsed key:value pairs",
                "The tool detected this as 'keyvalue' type because each line has 'key: value' format. It parses these into a Python dictionary."
            )
        
        # Phase 4: Compare types
        print("\n📚 PHASE 4: Different content types")
        
        print("\n👨‍🏫 TEACHER: Here are the different types I can detect:")
        print("   1. JSON - starts with { or [")
        print("   2. KeyValue - lines with 'key: value'")  
        print("   3. Markdown - has # headers, **bold**, lists")
        print("   4. Plain - everything else")
        
        # Self-reflection
        reflection = self.wait_for_sara(
            "what did you learn about .look files",
            "What did you learn from this lesson?"
        )
        
        self.lesson_learned["concept_understood"] = "detect" in reflection.lower()
        self.lesson_learned["can_apply"] = "keyvalue" in reflection.lower() or "dictionary" in reflection.lower()
    
    def teach_network_concept(self):
        """Teach SARA network concepts"""
        print("\n" + "="*60)
        print("🎓 LESSON: Understanding IP addresses and network")
        print("="*60)
        
        self.lesson_learned["topic"] = "Network Concepts"
        
        # Phase 1: Pre-assessment
        print("\n📚 PHASE 1: What does SARA think 'IP pool' means?")
        
        response = self.wait_for_sara(
            "what is the ip pool on this pc",
            "Before I explain, what do you think this means?"
        )
        
        if "10.211" in response or "external" in response or "interface" in response:
            print("\n✅ She already has the data!")
            self.lesson_learned["concept_understood"] = True
        else:
            # Phase 2: Explain the concepts
            print("\n📚 PHASE 2: Explaining IP concepts")
            
            print("\n👨‍🏫 TEACHER: Let me explain the 3 types of IPs:")
            print("   1. LOCAL IP - Your address on your home/office network")
            print("      Like your room number in a building")
            print("      Yours: 10.211.144.110")
            print()
            print("   2. EXTERNAL IP - Your address on the internet")
            print("      Like the building's street address")  
            print("      Yours: 107.13.106.21")
            print()
            print("   3. LOOPBACK - Always 127.0.0.1 (local only)")
            
            # Phase 3: Application
            print("\n📚 PHASE 3: Using NetworkTool")
            
            from network_tool import NetworkTool
            net = NetworkTool()
            
            ip_data = net.get_ip_pool()
            print(f"\n👨‍🏫 TEACHER: My tool got this data:")
            print(f"   Hostname: {ip_data['hostname']}")
            print(f"   Local: {ip_data['local_ip']}")
            print(f"   External: {ip_data['external_ip']}")
            
            # Have her explain back
            explanation = self.wait_for_sara(
                "explain the difference between local and external ip",
                "Now explain the difference..."
            )
            
            has_local = "local" in explanation.lower() and ("network" in explanation.lower() or "home" in explanation.lower())
            has_external = "external" in explanation.lower() and ("internet" in explanation.lower() or "outside" in explanation.lower())
            
            self.lesson_learned["concept_understood"] = has_local and has_external
            self.lesson_learned["can_apply"] = "127.0.0" in explanation.lower() or "loopback" in explanation.lower()
    
    def run_lesson(self, topic):
        """Run a complete interactive lesson"""
        print("\n" + "╔" + "="*58 + "╗")
        print("║" + " "*10 + "🎓 INTERACTIVE TEACHING SESSION" + " "*18 + "║")
        print("║" + " "*15 + f"Topic: {topic}" + " "*(43-len(topic)) + "║")
        print("╚" + "="*58 + "╝\n")
        
        if topic == "calculator":
            self.teach_calculator_concept()
        elif topic == "lookfile":
            self.teach_lookfile_concept()
        elif topic == "network":
            self.teach_network_concept()
        else:
            print("❌ Unknown topic")
            return
        
        # Generate learning report
        self.generate_report()
    
    def generate_report(self):
        """Generate final learning report"""
        print("\n" + "="*60)
        print("📊 LEARNING SESSION REPORT")
        print("="*60)
        
        print(f"\n🎓 Topic: {self.lesson_learned['topic']}")
        print(f"🧠 Concept Understood: {self.lesson_learned['concept_understood']}")
        print(f"💪 Can Apply: {self.lesson_learned['can_apply']}")
        print(f"❓ Questions Asked: {len(self.lesson_learned['questions_asked'])}")
        print(f"❌ Mistakes Made: {len(self.lesson_learned['mistakes_made'])}")
        print(f"✨ Breakthroughs: {len(self.lesson_learned['breakthroughs'])}")
        
        if self.lesson_learned['mistakes_made']:
            print("\n📋 Mistakes & Corrections:")
            for i, m in enumerate(self.lesson_learned['mistakes_made'], 1):
                print(f"   {i}. Tried: {m['attempt'][:50]}...")
                print(f"      Correction: {m['correction'][:50]}...")
        
        # Save to learning log
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "method": "interactive_teaching",
            "topic": self.lesson_learned['topic'],
            "understood": self.lesson_learned['concept_understood'],
            "can_apply": self.lesson_learned['can_apply'],
            "mistakes": len(self.lesson_learned['mistakes_made']),
            "breakthroughs": self.lesson_learned['breakthroughs']
        }
        
        log_file = "C:/Users/bklyn/SARA3-2026/interactive_lessons.json"
        
        try:
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    data = json.load(f)
            else:
                data = {"lessons": []}
            
            data["lessons"].append(log_entry)
            
            with open(log_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"\n💾 Logged to: {log_file}")
        except Exception as e:
            print(f"\n⚠️ Could not save log: {e}")

def run_teaching_session():
    """Run a teaching session on a random topic"""
    import random
    topics = ["calculator", "lookfile", "network"]
    topic = random.choice(topics)
    
    teacher = InteractiveTeaching(duration_minutes=5)
    teacher.run_lesson(topic)

if __name__ == "__main__":
    run_teaching_session()
