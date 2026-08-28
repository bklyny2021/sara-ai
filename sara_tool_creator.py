#!/usr/bin/env python3
r"""
SARA TOOL CREATOR - lets Sara create and register her own tools on the fly.
Like Sarah (the main agent), Sara can define new tools, save them, and use them.

Tools are stored as Python files in the tools/ directory. Each tool is a
function that Sara can call. New tools can be created at runtime.

Structure:
  C:\Users\bklyn\SARA3-2026\tools\
    <tool_name>.py   - each tool is a Python module with a run() function
    registry.json    - tool registry (name, description, created)
"""
import os
import json
import importlib
import sys
from datetime import datetime

TOOLS_DIR = os.path.join("C:", os.sep, "Users", "bklyn", "SARA3-2026", "tools")
REGISTRY_FILE = os.path.join(TOOLS_DIR, "registry.json")

def ensure_dirs():
    os.makedirs(TOOLS_DIR, exist_ok=True)

def _load_registry():
    ensure_dirs()
    if os.path.exists(REGISTRY_FILE):
        try:
            with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def _save_registry(reg):
    ensure_dirs()
    with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
        json.dump(reg, f, indent=2)

def create_tool(name, description, code, update=False):
    """
    Create a new tool. The code must define a run(*args) function.
    Saves it to tools/<name>.py and registers it.
    If update=True and the tool exists, it updates the existing tool.
    """
    ensure_dirs()
    # Validate name
    if not name or not name.replace("_", "").isalnum():
        return {"ok": False, "error": "Invalid tool name. Use letters, numbers, underscores."}
    
    # Check if tool exists
    reg = _load_registry()
    exists = name in reg
    if exists and not update:
        return {"ok": False, "error": f"Tool '{name}' already exists. Use update=True to update it."}
    
    # Write the tool file
    tool_path = os.path.join(TOOLS_DIR, f"{name}.py")
    with open(tool_path, "w", encoding="utf-8") as f:
        f.write(code)
    
    # Register it
    reg[name] = {
        "description": description,
        "created": reg.get(name, {}).get("created", datetime.now().isoformat()),
        "updated": datetime.now().isoformat() if exists else None,
        "file": tool_path,
        "uses": reg.get(name, {}).get("uses", 0)
    }
    _save_registry(reg)
    
    return {"ok": True, "name": name, "file": tool_path, "updated": exists}

def update_tool(name, description=None, code=None):
    """Update an existing tool's code and/or description"""
    reg = _load_registry()
    if name not in reg:
        return {"ok": False, "error": f"Tool '{name}' not found"}
    
    tool_path = reg[name]["file"]
    if code is not None:
        with open(tool_path, "w", encoding="utf-8") as f:
            f.write(code)
    if description is not None:
        reg[name]["description"] = description
    reg[name]["updated"] = datetime.now().isoformat()
    _save_registry(reg)
    return {"ok": True, "name": name, "updated": True}

def record_use(name):
    """Record that a tool was used (for learning)"""
    reg = _load_registry()
    if name in reg:
        reg[name]["uses"] = reg[name].get("uses", 0) + 1
        reg[name]["last_used"] = datetime.now().isoformat()
        _save_registry(reg)
        return True
    return False

def run_tool(name, *args):
    """Run a registered tool by name"""
    reg = _load_registry()
    if name not in reg:
        return {"ok": False, "error": f"Tool '{name}' not found. Available: {list(reg.keys())}"}
    
    tool_path = reg[name]["file"]
    if not os.path.exists(tool_path):
        return {"ok": False, "error": f"Tool file missing: {tool_path}"}
    
    # Import the tool module
    try:
        spec = importlib.util.spec_from_file_location(f"sara_tool_{name}", tool_path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[f"sara_tool_{name}"] = mod
        spec.loader.exec_module(mod)
        
        if not hasattr(mod, "run"):
            return {"ok": False, "error": f"Tool '{name}' has no run() function"}
        
        result = mod.run(*args)
        # Record usage for learning
        try:
            record_use(name)
        except Exception:
            pass
        return {"ok": True, "result": result}
    except Exception as e:
        return {"ok": False, "error": f"Tool execution failed: {e}"}

def list_tools():
    """List all registered tools"""
    reg = _load_registry()
    return [{"name": n, "description": v.get("description", ""), "created": v.get("created", "")} 
            for n, v in reg.items()]

def delete_tool(name):
    """Delete a tool (requires permission - handled by caller)"""
    reg = _load_registry()
    if name not in reg:
        return {"ok": False, "error": f"Tool '{name}' not found"}
    tool_path = reg[name]["file"]
    if os.path.exists(tool_path):
        os.remove(tool_path)
    del reg[name]
    _save_registry(reg)
    return {"ok": True, "deleted": name}

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "list":
        for t in list_tools():
            print(f"  {t['name']}: {t['description']}")
    else:
        print("Usage: python sara_tool_creator.py list")
