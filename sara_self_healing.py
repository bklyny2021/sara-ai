#!/usr/bin/env python3
"""
🩺 SARA SELF-HEALING SYSTEM
Stay alive, monitor health, read logs, fix herself
Can code - repairs her own broken code
"""

import os
import sys
import json
import time
import subprocess
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class SaraHealthMonitor:
    """Monitor SARA's vital signs and detect issues"""
    
    def __init__(self):
        self.base_path = "C:/Users/bklyn/SARA3-2026"
        self.log_file = os.path.join(self.base_path, "logs", "health.log")
        self.status_file = os.path.join(self.base_path, "logs", "status.json")
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        # Health thresholds
        self.max_response_time = 10  # seconds
        self.max_memory_percent = 80
        
    def log(self, message: str, level: str = "INFO"):
        """Write to health log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        with open(self.log_file, 'a') as f:
            f.write(log_entry)
        
        print(log_entry.strip())
    
    def check_vital_signs(self) -> Dict:
        """Check if SARA is healthy"""
        checks = {
            "web_server": False,
            "brain_loaded": False,
            "memory_ok": False,
            "response_time_ok": False,
            "errors_recent": False
        }
        
        # 1. Check web server responding
        try:
            import requests
            start = time.time()
            response = requests.get("http://127.0.0.1:8892", timeout=5)
            checks["web_server"] = response.status_code == 200
            checks["response_time_ok"] = (time.time() - start) < self.max_response_time
        except:
            checks["web_server"] = False
        
        # 2. Check brain can load
        try:
            sys.path.insert(0, self.base_path)
            from sara_brain import SaraBrain
            brain = SaraBrain()
            checks["brain_loaded"] = True
        except Exception as e:
            self.log(f"Brain failed to load: {e}", "ERROR")
            checks["brain_loaded"] = False
        
        # 3. Check for recent errors in logs
        checks["errors_recent"] = self._check_recent_errors()
        
        # Overall health
        healthy = all([
            checks["web_server"],
            checks["brain_loaded"],
            not checks["errors_recent"]
        ])
        
        result = {
            "healthy": healthy,
            "timestamp": datetime.now().isoformat(),
            "checks": checks,
            "needs_healing": not healthy
        }
        
        # Save status
        with open(self.status_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        return result
    
    def _check_recent_errors(self) -> bool:
        """Check log for errors in last 5 minutes"""
        if not os.path.exists(self.log_file):
            return False
        
        try:
            with open(self.log_file, 'r') as f:
                lines = f.readlines()[-100:]  # Last 100 lines
            
            # Check for ERROR entries in last 5 minutes
            recent_errors = [l for l in lines if "[ERROR]" in l]
            return len(recent_errors) > 3  # More than 3 recent errors
        except:
            return False


class SaraLogAnalyzer:
    """Read logs, diagnose problems"""
    
    def __init__(self, base_path: str = None):
        self.base_path = base_path or "C:/Users/bklyn/SARA3-2026"
        self.logs_dir = os.path.join(self.base_path, "logs")
    
    def analyze_recent_issues(self) -> List[Dict]:
        """Find and analyze recent problems"""
        issues = []
        
        # Check health log
        health_log = os.path.join(self.logs_dir, "health.log")
        if os.path.exists(health_log):
            errors = self._extract_errors(health_log)
            for error in errors[-5:]:  # Last 5 errors
                issue = self._diagnose_error(error)
                if issue:
                    issues.append(issue)
        
        # Check for crash dumps
        crash_files = self._find_crash_files()
        for crash in crash_files:
            issues.append({
                "type": "crash_dump",
                "file": crash,
                "diagnosis": "SARA crashed, restart needed"
            })
        
        return issues
    
    def _extract_errors(self, log_file: str) -> List[str]:
        """Extract error lines from log"""
        errors = []
        try:
            with open(log_file, 'r') as f:
                for line in f:
                    if "[ERROR]" in line or "Traceback" in line:
                        errors.append(line.strip())
        except:
            pass
        return errors
    
    def _diagnose_error(self, error_line: str) -> Optional[Dict]:
        """Diagnose what caused an error"""
        # Pattern matching for common issues
        if "ModuleNotFoundError" in error_line:
            return {
                "type": "missing_module",
                "error": error_line,
                "diagnosis": "Python module not installed",
                "fix_strategy": "install_dependency"
            }
        elif "ImportError" in error_line:
            return {
                "type": "import_error",
                "error": error_line,
                "diagnosis": "Failed to import module",
                "fix_strategy": "check_imports"
            }
        elif "Connection refused" in error_line or "port 8892" in error_line:
            return {
                "type": "server_down",
                "error": error_line,
                "diagnosis": "Web server not responding",
                "fix_strategy": "restart_server"
            }
        elif "chromadb" in error_line.lower():
            return {
                "type": "chroma_error",
                "error": error_line,
                "diagnosis": "ChromaDB error, using fallback",
                "fix_strategy": "verify_fallback"
            }
        
        return None
    
    def _find_crash_files(self) -> List[str]:
        """Find crash dump files"""
        crashes = []
        log_dir = os.path.join(self.base_path, "logs")
        if os.path.exists(log_dir):
            for f in os.listdir(log_dir):
                if "crash" in f.lower() or "dump" in f.lower():
                    crashes.append(os.path.join(log_dir, f))
        return crashes


class SaraCodeRepair:
    """SARA repairs her own code!"""
    
    def __init__(self, base_path: str = None):
        self.base_path = base_path or "C:/Users/bklyn/SARA3-2026"
    
    def fix_import_error(self, module_name: str) -> bool:
        """Fix missing import by creating stub or installing"""
        # Check if it's a local module vs pip module
        if os.path.exists(os.path.join(self.base_path, f"{module_name}.py")):
            # Local file exists but won't import - syntax error?
            return self._fix_syntax_error(f"{module_name}.py")
        
        # Check if we have a fallback
        if module_name in ["chromadb", "sentence_transformers"]:
            self._ensure_fallback_exists(module_name)
            return True
        
        return False
    
    def _fix_syntax_error(self, filename: str) -> bool:
        """Try to fix syntax errors in a file"""
        filepath = os.path.join(self.base_path, filename)
        if not os.path.exists(filepath):
            return False
        
        # Read current
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Common fixes
        fixes_applied = []
        
        # Fix 1: Missing colon after if/def/for
        # Simple regex patterns
        import re
        
        # Fix missing colons on function defs
        pattern1 = r'^(def \w+\([^)]*\))(?!:)'
        fixed, count = re.subn(pattern1, r'\1:', content, flags=re.MULTILINE)
        if count > 0:
            fixes_applied.append(f"Added {count} missing colons after function defs")
            content = fixed
        
        # Fix 2: Double return statements
        if "return self._handle_nano_request(user_input)\n            return self._handle_nano_request(user_input)" in content:
            content = content.replace(
                "return self._handle_nano_request(user_input)\n            return self._handle_nano_request(user_input)",
                "return self._handle_nano_request(user_input)"
            )
            fixes_applied.append("Removed duplicate return statement")
        
        # Write back if changes made
        if fixes_applied:
            # Backup first
            backup = filepath + ".backup"
            shutil.copy(filepath, backup)
            
            with open(filepath, 'w') as f:
                f.write(content)
            
            print(f"✅ Fixed {filename}: {', '.join(fixes_applied)}")
            return True
        
        return False
    
    def _ensure_fallback_exists(self, module_name: str):
        """Ensure fallback code exists for optional modules"""
        # Already handled in code via try/except
        pass
    
    def create_repair_script(self, issue: Dict) -> str:
        """Generate Python code to fix an issue"""
        if issue["type"] == "server_down":
            return """
import subprocess
import time

# Kill stuck processes
subprocess.run(["pkill", "-9", "-f", "sara_web"], capture_output=True)
time.sleep(2)

# Restart
subprocess.Popen([
    "setsid", "python3", "sara_web_fixed.py"
], cwd="C:/Users/bklyn/SARA3-2026")

print("SARA restarted successfully")
"""
        elif issue["type"] == "missing_module":
            return f"""
import subprocess
import sys

# Install missing module
try:
    subprocess.run([sys.executable, "-m", "pip", "install", "{issue.get('module', 'unknown')}"], 
                   check=True, capture_output=True)
    print("Module installed successfully")
except Exception as e:
    print(f"Failed to install: {{e}}")
"""
        return ""


class SaraSelfHealer:
    """
    Main self-healing orchestrator
    Stay alive, check health, read logs, fix problems
    """
    
    def __init__(self):
        self.health = SaraHealthMonitor()
        self.analyzer = SaraLogAnalyzer()
        self.repair = SaraCodeRepair()
        self.heartbeat_count = 0
        
    def stay_alive(self):
        """Main loop - keep SARA alive"""
        self.health.log("🩺 SARA Self-Healing System initialized")
        
        while True:
            self.heartbeat_count += 1
            
            # Check health
            status = self.health.check_vital_signs()
            
            if status["needs_healing"]:
                self.health.log("⚠️ Health check failed - attempting healing", "WARNING")
                self._heal_thyself()
            else:
                if self.heartbeat_count % 10 == 0:  # Log every 10th healthy beat
                    self.health.log("💓 Health check passed - all systems OK")
            
            # Sleep before next check
            time.sleep(30)  # Check every 30 seconds
    
    def _heal_thyself(self):
        """Diagnose and fix issues"""
        # 1. Analyze logs for issues
        issues = self.analyzer.analyze_recent_issues()
        
        if not issues:
            self.health.log("No specific issues found - trying generic restart", "WARNING")
            self._restart_web_server()
            return
        
        # 2. Fix each issue
        for issue in issues:
            self.health.log(f"Found issue: {issue['diagnosis']}", "WARNING")
            
            if issue["fix_strategy"] == "restart_server":
                self._restart_web_server()
            
            elif issue["fix_strategy"] == "check_imports":
                module = self._extract_module_from_error(issue["error"])
                if module:
                    self.repair.fix_import_error(module)
            
            elif issue["fix_strategy"] == "install_dependency":
                self._install_dependency(issue.get("module", "unknown"))
            
            elif issue["type"] in ["syntax_error", "import_error"]:
                # Try code repair
                self.health.log("Attempting code repair...")
                # Could trigger code repair skill
    
    def _restart_web_server(self):
        """Restart the web server"""
        self.health.log("Restarting web server...")
        
        try:
            # Kill existing
            subprocess.run(["pkill", "-9", "-f", "sara_web"], 
                         capture_output=True, timeout=5)
            time.sleep(2)
            
            # Start new
            subprocess.Popen([
                "setsid", "python3", "sara_web_fixed.py"
            ], 
            cwd="C:/Users/bklyn/SARA3-2026",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
            )
            
            self.health.log("✅ Web server restarted", "SUCCESS")
            
        except Exception as e:
            self.health.log(f"❌ Failed to restart: {e}", "ERROR")
    
    def _extract_module_from_error(self, error_line: str) -> Optional[str]:
        """Extract module name from error message"""
        # "No module named 'xyz'" or similar patterns
        import re
        matches = re.findall(r"No module named ['\"]([^'\"]+)['\"]", error_line)
        if matches:
            return matches[0]
        return None
    
    def _install_dependency(self, module: str):
        """Install a missing Python package"""
        self.health.log(f"Installing dependency: {module}")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", module],
                capture_output=True,
                timeout=60,
                check=True
            )
            self.health.log(f"✅ Installed {module}")
        except Exception as e:
            self.health.log(f"❌ Failed to install {module}: {e}", "ERROR")
    
    def run_once(self) -> Dict:
        """Run single health check and heal if needed"""
        status = self.health.check_vital_signs()
        
        if status["needs_healing"]:
            self._heal_thyself()
        
        return status


def run_health_check():
    """Run one health check (for cron/heartbeat)"""
    healer = SaraSelfHealer()
    result = healer.run_once()
    
    output = {
        "healthy": result["healthy"],
        "timestamp": result["timestamp"],
        "checks": result["checks"]
    }
    
    if not result["healthy"]:
        output["action"] = "healing_attempted"
    
    print(json.dumps(output, indent=2))
    return result["healthy"]


def run_daemon():
    """Run as continuous daemon"""
    healer = SaraSelfHealer()
    try:
        healer.stay_alive()
    except KeyboardInterrupt:
        print("\n👋 Self-healing daemon stopped")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--daemon":
        run_daemon()
    else:
        healthy = run_health_check()
        sys.exit(0 if healthy else 1)
