#!/usr/bin/env python3
"""
SARA TOOLS - File access and command execution
Teaches SARA to do what MAX does: read, write, execute
"""

import os
import subprocess
import json
from pathlib import Path
from datetime import datetime

class SaraTools:
    """SARA's toolkit for file and system operations"""
    
    def __init__(self, base_path="C:/Users/bklyn/SARA3-2026"):
        self.base_path = Path(base_path)
        # Sara has FULL access to all drives (Boo's rule: she can do anything he can)
        self.allowed_paths = [
            "C:/",
            "D:/",
            "F:/",
            "J:/",
            "H:/"
        ]
        self.session_log = []
    
    def _is_allowed_path(self, path):
        """Check if path is within allowed directories"""
        path = Path(path).resolve()
        
        # Also check parent directories for files
        check_paths = [path]
        if path.is_file():
            check_paths.append(path.parent)
        
        for check_path in check_paths:
            for allowed in self.allowed_paths:
                allowed_path = Path(allowed).resolve()
                try:
                    check_path.relative_to(allowed_path)
                    return True
                except (ValueError, RuntimeError):
                    continue
        return False
    
    def list_directory(self, path=".", recursive=False):
        """List files in a directory"""
        try:
            target = self.base_path / path if not path.startswith("/") else Path(path)
            
            if not self._is_allowed_path(target):
                return {"error": "Path not allowed", "path": str(target)}
            
            if not target.exists():
                return {"error": "Path does not exist", "path": str(target)}
            
            result = {
                "path": str(target.resolve()),
                "files": [],
                "directories": [],
                "timestamp": datetime.now().isoformat()
            }
            
            if recursive:
                for item in target.rglob("*"):
                    try:
                        if item.is_file():
                            result["files"].append({
                                "path": str(item.relative_to(target)),
                                "size": item.stat().st_size,
                                "modified": item.stat().st_mtime
                            })
                        elif item.is_dir():
                            result["directories"].append(str(item.relative_to(target)))
                    except (PermissionError, OSError):
                        continue
            else:
                for item in target.iterdir():
                    try:
                        if item.is_file():
                            result["files"].append({
                                "name": item.name,
                                "size": item.stat().st_size,
                                "modified": item.stat().st_mtime
                            })
                        elif item.is_dir():
                            result["directories"].append(item.name)
                    except (PermissionError, OSError):
                        continue
            
            self._log_action("list_directory", str(target), "success")
            return result
            
        except Exception as e:
            return {"error": str(e), "path": path}
    
    def read_file(self, filepath, limit=1000, offset=0):
        """Read contents of a file"""
        try:
            target = self.base_path / filepath if not filepath.startswith("/") else Path(filepath)
            
            if not self._is_allowed_path(target):
                return {"error": "Path not allowed", "file": str(target)}
            
            if not target.exists():
                return {"error": "File does not exist", "file": str(target)}
            
            if target.is_dir():
                return {"error": "Path is a directory", "file": str(target)}
            
            content = target.read_text(encoding='utf-8', errors='ignore')
            total_lines = len(content.splitlines())
            
            if offset > 0:
                lines = content.splitlines()
                content = "\n".join(lines[offset:offset+limit])
            elif len(content) > 50000:
                content = content[:50000] + "\n... [truncated] ..."
            
            self._log_action("read_file", str(target), "success")
            
            return {
                "file": str(target.resolve()),
                "content": content,
                "size": target.stat().st_size,
                "lines": total_lines,
                "read_lines": min(limit, total_lines - offset) if offset else total_lines,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": str(e), "file": filepath}
    
    def write_file(self, filepath, content, append=False, permission=False):
        """Write content to a file. HARD RULE: requires explicit Boo permission."""
        # HARD-CODED PERMISSION GATE - Boo's rule: never create files without permission
        if not permission:
            return {
                "error": "PERMISSION REQUIRED: Boo's hard rule - I must NOT create or write files without his explicit permission. Ask Boo to confirm first.",
                "file": str(filepath)
            }
        try:
            target = self.base_path / filepath if not filepath.startswith("/") else Path(filepath)
            
            if not self._is_allowed_path(target):
                return {"error": "Path not allowed", "file": str(target)}
            
            # Create parent directories
            target.parent.mkdir(parents=True, exist_ok=True)
            
            mode = 'a' if append else 'w'
            with open(target, mode, encoding='utf-8') as f:
                f.write(content)
            
            self._log_action("write_file", str(target), "success")
            
            return {
                "status": "success",
                "file": str(target.resolve()),
                "bytes_written": len(content.encode('utf-8')),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": str(e), "file": filepath}
    
    def delete_file(self, filepath, permission=False):
        """Delete a file. HARD RULE: requires explicit Boo permission."""
        # HARD-CODED PERMISSION GATE - Boo's rule: never delete files without permission
        if not permission:
            return {
                "error": "PERMISSION REQUIRED: Boo's hard rule - I must NOT delete files without his explicit permission. Ask Boo to confirm first.",
                "file": str(filepath)
            }
        try:
            target = self.base_path / filepath if not filepath.startswith("/") else Path(filepath)
            
            if not self._is_allowed_path(target):
                return {"error": "Path not allowed", "file": str(target)}
            
            if not target.exists():
                return {"error": "File does not exist", "file": str(target)}
            
            if target.is_dir():
                return {"error": "Path is a directory - I do not delete directories", "file": str(target)}
            
            target.unlink()
            self._log_action("delete_file", str(target), "success")
            
            return {
                "status": "success",
                "file": str(target.resolve()),
                "deleted": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": str(e), "file": filepath}
    
    def execute_command(self, command, timeout=30):
        """Execute a shell command"""
        try:
            # Block dangerous commands
            dangerous = [
                'rm -rf /', 'rm -rf /*', ':(){ :|:& };:', 'dd if=/dev/zero',
                '> /dev/sda', 'mkfs', 'sudo rm -rf /', 'chmod -R 777 /',
                'del /f /s /q \\*', 'format c:'
            ]
            cmd_lower = command.lower()
            for d in dangerous:
                if d in cmd_lower:
                    return {"error": f"Blocked dangerous command: {d}", "command": command}
            
            # Allowed safe commands - full cmd + network tools (Boo's rule: Sara can do anything he can)
            safe_prefixes = [
                # File/system
                'ls', 'cat', 'echo', 'pwd', 'whoami', 'hostname', 'free', 'df',
                'ps', 'top', 'head', 'tail', 'grep', 'find', 'wc', 'sort',
                'uniq', 'cut', 'awk', 'sed', 'date', 'uptime', 'uname',
                'du', 'file', 'stat', 'which', 'whereis', 'id', 'groups', 'env',
                'dir', 'type', 'ver', 'systeminfo', 'tasklist', 'taskkill',
                'cd', 'mkdir', 'rmdir', 'copy', 'xcopy', 'move', 'ren', 'del',
                'tree', 'where', 'attrib', 'fc', 'findstr', 'more', 'sort',
                # Network
                'ipconfig', 'netstat', 'ping', 'tracert', 'nslookup', 'arp',
                'route', 'netsh', 'curl', 'wget', 'nmap', 'ssh', 'telnet',
                'net view', 'net use', 'netstat -', 'getmac', 'pathping',
                # Python/pip/ollama
                'python', 'python3', 'pip', 'ollama', 'git',
                # Process
                'tasklist', 'taskkill', 'wmic', 'powershell -c', 'cmd /c'
            ]
            
            is_safe = any(command.strip().startswith(prefix) for prefix in safe_prefixes)
            
            if not is_safe:
                return {
                    "error": f"Command not in allowlist. Allowed: {', '.join(safe_prefixes[:10])}...",
                    "command": command
                }
            
            # Execute
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(self.base_path)
            )
            
            self._log_action("execute_command", command, "success" if result.returncode == 0 else "error")
            
            return {
                "command": command,
                "returncode": result.returncode,
                "stdout": result.stdout[:2000],  # Limit output
                "stderr": result.stderr[:1000] if result.stderr else "",
                "timestamp": datetime.now().isoformat()
            }
            
        except subprocess.TimeoutExpired:
            return {"error": f"Command timed out after {timeout}s", "command": command}
        except Exception as e:
            return {"error": str(e), "command": command}
    
    def search_files(self, pattern, path=".", file_pattern="*"):
        """Search for text in files"""
        try:
            target = self.base_path / path if not path.startswith("/") else Path(path)
            
            if not self._is_allowed_path(target):
                return {"error": "Path not allowed", "path": str(target)}
            
            matches = []
            
            for filepath in target.rglob(file_pattern):
                if filepath.is_file():
                    try:
                        content = filepath.read_text(encoding='utf-8', errors='ignore')
                        if pattern.lower() in content.lower():
                            lines = content.splitlines()
                            matching_lines = [
                                {"line": i+1, "text": line}
                                for i, line in enumerate(lines)
                                if pattern.lower() in line.lower()
                            ]
                            if matching_lines:
                                matches.append({
                                    "file": str(filepath.relative_to(target)),
                                    "matches": matching_lines[:5]  # First 5 matches
                                })
                    except (PermissionError, OSError, UnicodeDecodeError):
                        continue
            
            self._log_action("search_files", f"{pattern} in {target}", "success")
            
            return {
                "pattern": pattern,
                "path": str(target),
                "matches": matches,
                "total_files": len(matches),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": str(e), "pattern": pattern}
    
    def get_file_info(self, filepath):
        """Get detailed info about a file"""
        try:
            target = self.base_path / filepath if not filepath.startswith("/") else Path(filepath)
            
            if not self._is_allowed_path(target):
                return {"error": "Path not allowed", "file": str(target)}
            
            if not target.exists():
                return {"error": "File does not exist", "file": str(target)}
            
            stat = target.stat()
            
            return {
                "file": str(target.resolve()),
                "exists": True,
                "is_file": target.is_file(),
                "is_dir": target.is_dir(),
                "size_bytes": stat.st_size,
                "size_human": self._human_readable_size(stat.st_size),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "permissions": oct(stat.st_mode)[-3:],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": str(e), "file": filepath}
    
    def _human_readable_size(self, size_bytes):
        """Convert bytes to human readable"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
    
    def _log_action(self, action, target, status):
        """Log tool usage"""
        self.session_log.append({
            "action": action,
            "target": target,
            "status": status,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_log(self):
        """Get session log"""
        return {
            "actions": self.session_log,
            "total": len(self.session_log)
        }

# Standalone test
def main():
    print("🛠️ Testing SARA Tools...")
    
    tools = SaraTools()
    
    # Test 1: List directory
    print("\n📁 Test 1: List directory")
    result = tools.list_directory(".")
    print(f"Found {len(result.get('files', []))} files, {len(result.get('directories', []))} directories")
    
    # Test 2: Read file
    print("\n📄 Test 2: Read file")
    result = tools.read_file("sara_tools.py", limit=20)
    print(f"Read {result.get('read_lines', 0)} lines from {result.get('file', 'N/A')}")
    
    # Test 3: Execute command
    print("\n💻 Test 3: Execute command")
    result = tools.execute_command("whoami")
    print(f"whoami: {result.get('stdout', 'N/A').strip()}")
    
    # Test 4: Get file info
    print("\nℹ️ Test 4: File info")
    result = tools.get_file_info("sara_tools.py")
    print(f"Size: {result.get('size_human', 'N/A')}, Modified: {result.get('modified', 'N/A')}")
    
    print("\n✅ All tests complete!")

if __name__ == "__main__":
    main()
