#!/usr/bin/env python3
"""
SARA NANO GUIDE - Text Editing Assistant
Teaches SARA how to use nano and helps Boo edit files
"""

NANO_GUIDE = """
╔══════════════════════════════════════════════════════════════════╗
║  📝 NANO TEXT EDITOR - QUICK REFERENCE GUIDE                     ║
╚══════════════════════════════════════════════════════════════════╝

Nano is a simple, user-friendly command-line text editor.

🚀 BASIC COMMANDS (Ctrl = ^)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OPEN FILE:
  nano filename.txt          - Open or create file
  nano +10 filename.txt      - Open at line 10
  nano -i filename.txt       - Auto-indent mode

SAVE & EXIT:
  Ctrl + O (^O)              - Save (Write Out)
  Enter                      - Confirm filename
  Ctrl + X (^X)              - Exit nano

NAVIGATION:
  Arrow Keys                 - Move cursor
  Ctrl + V (^V)              - Page Down
  Ctrl + Y (^Y)              - Page Up
  Ctrl + A (^A)              - Start of line
  Ctrl + E (^E)              - End of line
  Ctrl + W (^W)              - Search (Where Is)
  Ctrl + _   (^_ or ^/)      - Go to line number

EDITING:
  Ctrl + K (^K)              - Cut entire line
  Ctrl + U (^U)              - Uncut (paste) line
  Ctrl + 6 (^6)              - Mark text (start selection)
    → Move cursor            - Select text
    → Ctrl + K               - Cut selected text
    → Ctrl + U               - Paste
  Ctrl + D (^D)              - Delete character under cursor
  Backspace                  - Delete character before cursor

SEARCH & REPLACE:
  Ctrl + W (^W)              - Search
  Alt + W  (M-W)             - Find next match
  Ctrl + \\  (^\\)            - Search & Replace

UNDO/REDO:
  Alt + U  (M-U)             - Undo
  Alt + E  (M-E)             - Redo

OTHER USEFUL:
  Ctrl + G (^G)              - Help (show all commands)
  Ctrl + C (^C)              - Cursor position
  Alt + #  (M-#)             - Line numbers ON/OFF
  Ctrl + T (^T)              - Spell check (if installed)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

NANO_SHORTCUTS = {
    'save': 'Ctrl + O',
    'exit': 'Ctrl + X', 
    'quit': 'Ctrl + X',
    'search': 'Ctrl + W',
    'find': 'Ctrl + W',
    'cut': 'Ctrl + K',
    'copy': 'Alt + 6',
    'paste': 'Ctrl + U',
    'undo': 'Alt + U',
    'redo': 'Alt + E',
    'gotoline': 'Ctrl + _',
}

import subprocess
import os

class NanoHelper:
    """Helps SARA use nano effectively"""
    
    def __init__(self):
        self.nano_installed = self._check_nano()
    
    def _check_nano(self):
        """Check if nano is installed"""
        try:
            result = subprocess.run(['which', 'nano'], capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def install_nano(self):
        """Install nano if not present"""
        if self.nano_installed:
            return {"status": "already_installed", "message": "Nano is already installed! 👍"}
        
        try:
            # Try dnf (Fedora)
            result = subprocess.run(['sudo', 'dnf', 'install', '-y', 'nano'], 
                                   capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                self.nano_installed = True
                return {"status": "installed", "message": "✅ Nano installed successfully via dnf!"}
            
            # Try apt (Debian/Ubuntu)
            result = subprocess.run(['sudo', 'apt', 'install', '-y', 'nano'],
                                   capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                self.nano_installed = True
                return {"status": "installed", "message": "✅ Nano installed successfully via apt!"}
            
            return {"status": "error", "message": "Could not install nano. Check package manager."}
            
        except Exception as e:
            return {"status": "error", "message": f"Installation failed: {str(e)}"}
    
    def edit_file(self, filepath, line=None):
        """Open file in nano - use this when Boo wants to edit"""
        if not self.nano_installed:
            return {"status": "error", "message": "Nano not installed. Use 'install nano' first."}
        
        try:
            # Check if file exists
            if not os.path.exists(filepath):
                # Create empty file
                open(filepath, 'a').close()
            
            cmd = ['nano']
            if line:
                cmd.extend(['+', str(line)])
            cmd.append(filepath)
            
            # Note: This will block until nano exits
            # In web interface, we can't do this directly
            return {
                "status": "info", 
                "message": f"📝 To edit '{filepath}', run in terminal:\n\n   nano {filepath}\n\nOr use these commands:\n• Ctrl+O to save\n• Ctrl+X to exit",
                "command": f"nano {filepath}"
            }
            
        except Exception as e:
            return {"status": "error", "message": f"Error: {str(e)}"}
    
    def get_help(self, topic=None):
        """Get nano help info"""
        if topic:
            topic_lower = topic.lower()
            for key, shortcut in NANO_SHORTCUTS.items():
                if key in topic_lower:
                    return f"📝 {key.upper()}: {shortcut}"
            return f"❓ Unknown command '{topic}'. Ask about: save, exit, search, cut, paste, undo, etc."
        
        return NANO_GUIDE
    
    def quick_guide(self):
        """Quick reference card"""
        return """
╔══════════════════════════════════════╗
║     📝 NANO - QUICK REFERENCE       ║
╠══════════════════════════════════════╣
║ OPEN:  nano filename.txt            ║
║ SAVE:  Ctrl + O                     ║
║ EXIT:  Ctrl + X                     ║
║ FIND:  Ctrl + W                     ║
║ CUT:   Ctrl + K   PASTE: Ctrl + U   ║
║ GOTO:  Ctrl + _ (line number)       ║
║ UNDO:  Alt + U    REDO:  Alt + E    ║
╚══════════════════════════════════════╝
"""

def main():
    """Test nano helper"""
    print("📝 Testing NANO Helper...")
    
    helper = NanoHelper()
    
    if helper.nano_installed:
        print("✅ Nano is installed!")
        print(f"{helper.quick_guide()}")
        
        print("\nExample help requests:")
        print(helper.get_help("save"))
        print(helper.get_help("search"))
    else:
        print("⚠️ Nano not found!")
        print("Would install nano here...")
        # result = helper.install_nano()
        # print(result['message'])

if __name__ == "__main__":
    main()