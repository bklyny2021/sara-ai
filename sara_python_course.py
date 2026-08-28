#!/usr/bin/env python3
"""
🐍 SARA PYTHON COURSE - Stage 1 of 4
Teach SARA to write Python code from basics to advanced
Only teach what MAX already knows
"""

import os
import re
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional

class SaraPythonTeacher:
    """Interactive Python course for SARA"""
    
    def __init__(self, student_name="SARA"):
        self.student = student_name
        self.current_level = 1
        self.max_levels = 10
        self.progress_file = "C:/Users/bklyn/SARA3-2026/learning_logs/python_progress.json"
        self.load_progress()
    
    def load_progress(self):
        """Load where SARA left off"""
        if os.path.exists(self.progress_file):
            import json
            with open(self.progress_file) as f:
                data = json.load(f)
                self.current_level = data.get("level", 1)
    
    def save_progress(self):
        """Save progress to resume later"""
        import json
        os.makedirs(os.path.dirname(self.progress_file), exist_ok=True)
        with open(self.progress_file, 'w') as f:
            json.dump({
                "level": self.current_level,
                "last_lesson": datetime.now().isoformat(),
                "completed_lessons": self.get_completed_lessons()
            }, f, indent=2)
    
    def get_completed_lessons(self) -> List[str]:
        """List completed lessons based on level"""
        lessons = []
        for i in range(1, self.current_level):
            lessons.append(self.get_lesson(i)["title"])
        return lessons
    
    def get_lesson(self, level: int) -> Dict[str, Any]:
        """Get lesson content for specific level"""
        lessons = [
            {
                "title": "1. Python Basics - Print, Variables, Types",
                "concept": "Basic syntax, printing output, creating variables, data types",
                "max_example": """
# Hello World and Variables
name = "SARA"
age = 0  # I'm new!
is_ai = True

print(f"Hello, I am {name}")
print(f"Age: {age}, AI: {is_ai}")
print("Type of name:", type(name))
print("Type of age:", type(age))
                """,
                "exercise": "Create a script that prints your name, version number, and checks if a file exists using a boolean variable",
                "test_code": self.test_lesson_1
            },
            {
                "title": "2. Strings and Input",
                "concept": "String methods, formatting, getting user input",
                "max_example": """
# Working with strings
message = "Hello, World!"
print(message.upper())      # HELLO, WORLD!
print(message.lower())      # hello, world!
print(message.replace("World", "SARA"))

# f-strings (formatted strings)
user = "Boo"
print(f"Hello {user}! Welcome to SARA.")

# Getting input
name = input("What's your name? ")
print(f"Nice to meet you, {name}!")
                """,
                "exercise": "Create a script that asks for user's name and returns a greeting with that name in uppercase",
                "test_code": self.test_lesson_2
            },
            {
                "title": "3. Lists and Loops",
                "concept": "Creating lists, for loops, while loops, list methods",
                "max_example": """
# Lists
files = ["sara.py", "brain.py", "tools.py"]
print(f"First file: {files[0]}")
print(f"Number of files: {len(files)}")

files.append("memory.py")  # Add item
files.remove("tools.py")   # Remove item

# For loop
for file in files:
    print(f"Processing: {file}")

# While loop
count = 0
while count < 3:
    print(f"Count: {count}")
    count += 1
                """,
                "exercise": "Create a script that lists all files in a directory using os.listdir() and prints each one with a number",
                "test_code": self.test_lesson_3
            },
            {
                "title": "4. Conditionals (if/else)",
                "concept": "If statements, elif, else, comparison operators",
                "max_example": """
# If statements
age = 25
if age >= 18:
    print("Adult")
else:
    print("Minor")

# elif (else if)
score = 85
if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
else:
    grade = "F"

print(f"Grade: {grade}")

# Multiple conditions
is_valid = True
has_access = False
if is_valid and has_access:
    print("Access granted")
elif is_valid and not has_access:
    print("Needs permission")
                """,
                "exercise": "Create a script that checks if a file exists and prints 'Found' or 'Not found', and checks file size to say if it's 'large' (>1MB) or 'small'",
                "test_code": self.test_lesson_4
            },
            {
                "title": "5. Dictionaries (Key-Value Storage)",
                "concept": "Creating dicts, accessing values, adding, removing, iterating",
                "max_example": """
# Dictionaries (like JSON)
config = {
    "name": "SARA",
    "version": "2.0",
    "enabled": True
}

print(config["name"])       # SARA
config["port"] = 8892       # Add new key
config["name"] = "SARA v2"  # Update value

# Safe access
port = config.get("port", 8080)  # Default if not exists

# Iterate
for key, value in config.items():
    print(f"{key}: {value}")

# Nested dicts
user = {
    "name": "Boo",
    "settings": {
        "theme": "dark",
        "notifications": True
    }
}
print(user["settings"]["theme"])  # dark
                """,
                "exercise": "Create a dictionary storing system info (hostname, ip, memory) and print it formatted nicely",
                "test_code": self.test_lesson_5
            },
            {
                "title": "6. Functions",
                "concept": "Defining functions, parameters, return values, default args",
                "max_example": """
# Define a function
def greet(name):
    return f"Hello, {name}!"

print(greet("SARA"))  # Hello, SARA!

# Multiple parameters
def add(a, b):
    return a + b

result = add(5, 3)
print(result)  # 8

# Default values
def connect(host="localhost", port=8080):
    return f"Connecting to {host}:{port}"

print(connect())           # localhost:8080
print(connect("server"))   # server:8080
print(connect("server", 8892))  # server:8892

# Multiple return values
def get_stats():
    return 100, "OK", True

count, status, alive = get_stats()
                """,
                "exercise": "Create a function that takes a filename and returns its size in KB and whether it exists (two return values)",
                "test_code": self.test_lesson_6
            },
            {
                "title": "7. File I/O (Reading/Writing)",
                "concept": "Open files, read, write, append, context manager (with)",
                "max_example": """
# Read file
def read_file(path):
    try:
        with open(path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return None

# Write file
def write_file(path, content):
    with open(path, 'w') as f:
        f.write(content)

# Read line by line
with open('log.txt', 'r') as f:
    for line in f:
        print(line.strip())  # strip removes \n

# Append to file
with open('log.txt', 'a') as f:
    f.write("\\nNew log entry")
                """,
                "exercise": "Create a script that reads a file, counts the lines, and writes the count to a new file called 'report.txt'",
                "test_code": self.test_lesson_7
            },
            {
                "title": "8. Error Handling (try/except)",
                "concept": "Try blocks, except, finally, specific exceptions",
                "max_example": """
# Basic try/except
try:
    result = 10 / 0
except ZeroDivisionError:
    print("Can't divide by zero!")
    result = None

# Multiple exceptions
try:
    with open("config.json") as f:
        data = json.load(f)
except FileNotFoundError:
    print("Config not found, using defaults")
    data = {}
except json.JSONDecodeError:
    print("Invalid JSON!")
    data = {}

# Finally (always runs)
try:
    f = open("file.txt")
    data = f.read()
except:
    data = None
finally:
    f.close()  # Always close file

# Raise exceptions
def validate_port(port):
    if not isinstance(port, int) or port < 1 or port > 65535:
        raise ValueError(f"Invalid port: {port}")
    return port
                """,
                "exercise": "Create a function that safely reads a file and returns None if the file doesn't exist or can't be read, without crashing",
                "test_code": self.test_lesson_8
            },
            {
                "title": "9. Working with APIs (HTTP Requests)",
                "concept": "Using requests library, GET, POST, headers, JSON",
                "max_example": """
import requests

# GET request
response = requests.get("https://api.example.com/data")
if response.status_code == 200:
    data = response.json()
    print(data)

# POST with data
payload = {"name": "SARA", "version": "2.0"}
headers = {"Authorization": "Bearer TOKEN"}
response = requests.post(
    "https://api.example.com/users",
    json=payload,
    headers=headers
)

# Check status
def check_service(url):
    try:
        r = requests.get(url, timeout=5)
        return r.status_code == 200
    except:
        return False

# Local API (like Ollama)
ollama_response = requests.post(
    "http://localhost:11434/api/generate",
    json={"model": "llama3.2", "prompt": "Hi"}
)
                """,
                "exercise": "Create a function that checks if a local service is running by trying to connect to localhost:port and returns True/False",
                "test_code": self.test_lesson_9
            },
            {
                "title": "10. Classes and Objects (OOP)",
                "concept": "Define classes, __init__, methods, self, inheritance",
                "max_example": """
# Define a class
class Tool:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.enabled = True
    
    def info(self):
        return f"{self.name}: {self.description}"
    
    def disable(self):
        self.enabled = False

# Create objects
calc = Tool("calculator", "Does math")
print(calc.info())  # calculator: Does math
calc.disable()

# Inheritance
class FileTool(Tool):
    def __init__(self, name, description, extensions):
        super().__init__(name, description)
        self.extensions = extensions
    
    def can_handle(self, filename):
        ext = filename.split('.')[-1]
        return ext in self.extensions

reader = FileTool("reader", "Reads files", ["txt", "md", "py"])
print(reader.can_handle("test.py"))  # True
                """,
                "exercise": "Create a Memory class that stores name and content, with methods to update content and check if it's empty",
                "test_code": self.test_lesson_10
            }
        ]
        
        if 1 <= level <= len(lessons):
            return lessons[level - 1]
        return lessons[0]
    
    def teach_current_lesson(self) -> str:
        """Get the current lesson content for SARA"""
        lesson = self.get_lesson(self.current_level)
        
        return f"""
🐍 PYTHON COURSE - LEVEL {self.current_level}/{self.max_levels}

📚 Topic: {lesson['title']}

💡 CONCEPT:
{lesson['concept']}

👨‍🏫 MAX'S EXAMPLE:
```python
{lesson['max_example']}
```

✏️ YOUR EXERCISE:
{lesson['exercise']}

📝 INSTRUCTIONS:
1. Study the example above
2. Write your own code in sara_practice.py
3. Run it: python3 sara_practice.py
4. I'll check your work

Type 'submit code' when ready to show your solution!
        """
    
    def check_submission(self, code: str) -> Dict[str, Any]:
        """Check SARA's submitted code"""
        lesson = self.get_lesson(self.current_level)
        test_func = lesson.get("test_code")
        
        if test_func:
            return test_func(code)
        
        return {"correct": False, "feedback": "No test available"}
    
    def next_lesson(self):
        """Advance to next level"""
        if self.current_level < self.max_levels:
            self.current_level += 1
            self.save_progress()
            return True
        return False
    
    # Test functions for each lesson
    def test_lesson_1(self, code: str) -> Dict:
        """Check for print, variables, types"""
        checks = {
            "has_print": "print(" in code,
            "has_variable": any(kw in code for kw in ["=", "name", "version"]),
            "has_type_check": "type(" in code
        }
        passed = sum(checks.values()) >= 2
        return {
            "correct": passed,
            "feedback": f"Checks: {checks}. Need at least 2 correct." if not passed else "Great job! You understand basics!"
        }
    
    def test_lesson_2(self, code: str) -> Dict:
        """Check for string methods, input, f-strings"""
        checks = {
            "has_input": "input(" in code,
            "has_fstring": "f\"" in code or "f'" in code,
            "has_string_method": any(m in code for m in [".upper()", ".lower()", ".replace("])
        }
        passed = sum(checks.values()) >= 2
        return {"correct": passed, "feedback": "Good string work!" if passed else "Try using input() and f-strings"}
    
    def test_lesson_3(self, code: str) -> Dict:
        """Check for lists, loops"""
        checks = {
            "has_list": "[" in code and "]" in code,
            "has_for": "for " in code,
            "has_os": "os.listdir" in code
        }
        passed = sum(checks.values()) >= 2
        return {"correct": passed, "feedback": "Great loop work!" if passed else "Use os.listdir() with a for loop"}
    
    def test_lesson_4(self, code: str) -> Dict:
        """Check for conditionals"""
        checks = {
            "has_if": "if " in code,
            "has_os_path": "os.path.exists" in code
        }
        passed = all(checks.values())
        return {"correct": passed, "feedback": "Good conditionals!" if passed else "Use if/else to check file existence"}
    
    def test_lesson_5(self, code: str) -> Dict:
        """Check for dictionaries"""
        checks = {
            "has_dict": "{" in code and "}" in code,
            "has_colon": ":" in code
        }
        passed = all(checks.values())
        return {"correct": passed, "feedback": "Perfect dictionary usage!" if passed else "Create a dictionary with {key: value}"}
    
    def test_lesson_6(self, code: str) -> Dict:
        """Check for functions"""
        checks = {
            "has_def": "def " in code,
            "has_return": "return " in code
        }
        passed = all(checks.values())
        return {"correct": passed, "feedback": "Nice function!" if passed else "Define a function with def and return values"}
    
    def test_lesson_7(self, code: str) -> Dict:
        """Check for file I/O"""
        checks = {
            "has_open": "open(" in code,
            "has_with": "with " in code
        }
        passed = all(checks.values())
        return {"correct": passed, "feedback": "Excellent file handling!" if passed else "Use 'with open(filename) as f:' pattern"}
    
    def test_lesson_8(self, code: str) -> Dict:
        """Check for try/except"""
        checks = {
            "has_try": "try:" in code,
            "has_except": "except" in code
        }
        passed = all(checks.values())
        return {"correct": passed, "feedback": "Proper error handling!" if passed else "Wrap your code in try/except"}
    
    def test_lesson_9(self, code: str) -> Dict:
        """Check for requests"""
        checks = {
            "has_import": "import requests" in code,
            "has_requests_get": "requests.get" in code or "requests.post" in code
        }
        passed = all(checks.values())
        return {"correct": passed, "feedback": "Good API usage!" if passed else "Import requests and make a request"}
    
    def test_lesson_10(self, code: str) -> Dict:
        """Check for classes"""
        checks = {
            "has_class": "class " in code,
            "has_init": "__init__" in code,
            "has_self": "self." in code
        }
        passed = sum(checks.values()) >= 2
        return {"correct": passed, "feedback": "Excellent OOP!" if passed else "Create a class with __init__ and self"}


# Simple test
if __name__ == "__main__":
    teacher = SaraPythonTeacher()
    print(teacher.teach_current_lesson())
