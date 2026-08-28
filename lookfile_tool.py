#!/usr/bin/env python3
"""
👁️ .LOOK FILE TOOL - Special viewer for .look files
Teaches SARA how to handle and display .look files
A .look file is a human-readable log/view format
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional

class LookFileTool:
    """
    Tool for handling .look files
    
    .look files are:
    - Human-readable observation logs
    - Time-stamped view records  
    - Status/monitoring snapshots
    - Visual data representations
    """
    
    def __init__(self, look_dir: str = None):
        if look_dir is None:
            look_dir = "C:/Users/bklyn/SARA3-2026/look_files"
        self.look_dir = look_dir
        os.makedirs(look_dir, exist_ok=True)
    
    def read_look_file(self, filepath: str) -> Dict:
        """
        Read and parse a .look file
        
        .look files can be:
        - Plain text logs with timestamps
        - JSON structured data
        - Markdown formatted observations
        - Simple key:value pair logs
        """
        result = {
            "status": "error",
            "file": filepath,
            "content_type": None,
            "content": None,
            "formatted": None,
            "error": None
        }
        
        try:
            # Resolve path
            if not os.path.isabs(filepath):
                filepath = os.path.join(self.look_dir, filepath)
            
            if not os.path.exists(filepath):
                result["error"] = f".look file not found: {filepath}"
                return result
            
            # Check extension
            if not filepath.endswith('.look'):
                result["warning"] = "File doesn't have .look extension, but attempting to read anyway"
            
            # Read the file
            with open(filepath, 'r', encoding='utf-8') as f:
                raw_content = f.read()
            
            result["raw_content"] = raw_content
            
            # Determine content type and parse
            content_type = self._detect_content_type(raw_content)
            result["content_type"] = content_type
            
            # Parse based on type
            if content_type == "json":
                parsed = self._parse_json_look(raw_content)
                result["content"] = parsed
                result["formatted"] = self._format_json_look(parsed)
                
            elif content_type == "markdown":
                result["content"] = raw_content
                result["formatted"] = self._format_markdown_look(raw_content)
                
            elif content_type == "keyvalue":
                parsed = self._parse_keyvalue_look(raw_content)
                result["content"] = parsed
                result["formatted"] = self._format_keyvalue_look(parsed)
                
            else:  # plain text
                result["content"] = raw_content
                result["formatted"] = self._format_plain_look(raw_content)
            
            result["status"] = "success"
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def create_look_file(self, name: str, content: str, 
                         look_type: str = "plain") -> Dict:
        """
        Create a new .look file
        
        Args:
            name: Filename (will add .look if missing)
            content: Content to write
            look_type: Type of .look file (plain, json, markdown, keyvalue)
        """
        result = {
            "status": "error",
            "file": None,
            "error": None
        }
        
        try:
            # Ensure .look extension
            if not name.endswith('.look'):
                name += '.look'
            
            filepath = os.path.join(self.look_dir, name)
            
            # Add header based on type
            if look_type == "json":
                header = f'{{"look_file": "{name}", "created": "{datetime.now().isoformat()}", "type": "observation"}}\n'
            elif look_type == "markdown":
                header = f"# {name.replace('.look', '')}\n\n**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n---\n\n"
            elif look_type == "keyvalue":
                header = f"# Look File: {name}\n# Created: {datetime.now().isoformat()}\n\n"
            else:
                header = f"# Look File: {name}\n# Created: {datetime.now().isoformat()}\n\n"
            
            full_content = header + content
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(full_content)
            
            result["status"] = "success"
            result["file"] = filepath
            result["message"] = f"✅ Created .look file: {filepath}"
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def list_look_files(self) -> Dict:
        """List all .look files"""
        result = {
            "status": "error",
            "files": [],
            "count": 0,
            "error": None
        }
        
        try:
            files = []
            for item in os.listdir(self.look_dir):
                if item.endswith('.look'):
                    filepath = os.path.join(self.look_dir, item)
                    stat = os.stat(filepath)
                    files.append({
                        "name": item,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "path": filepath
                    })
            
            result["status"] = "success"
            result["files"] = files
            result["count"] = len(files)
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def _detect_content_type(self, content: str) -> str:
        """Detect if content is JSON, markdown, key:value, or plain text"""
        content = content.strip()
        
        # Check for JSON
        if content.startswith('{') or content.startswith('['):
            try:
                json.loads(content)
                return "json"
            except:
                pass
        
        # Check for key:value pairs
        lines = content.split('\n')
        kv_count = 0
        for line in lines:
            if ':' in line and not line.startswith('#'):
                kv_count += 1
        if kv_count > 2:
            return "keyvalue"
        
        # Check for markdown markers
        if any(marker in content for marker in ['# ', '## ', '**', '__', '- ', '* ']):
            return "markdown"
        
        return "plain"
    
    def _parse_json_look(self, content: str) -> Dict:
        """Parse JSON .look files"""
        try:
            return json.loads(content)
        except:
            return {"error": "Invalid JSON", "raw": content[:200]}
    
    def _parse_keyvalue_look(self, content: str) -> Dict:
        """Parse key:value pair .look files"""
        result = {}
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    result[key.strip()] = value.strip()
        return result
    
    def _format_json_look(self, data: Dict) -> str:
        """Format JSON data for display"""
        return f"""👁️ JSON .LOOK FILE

```json
{json.dumps(data, indent=2)}
```

📊 Parsed: {len(data)} top-level keys"""
    
    def _format_markdown_look(self, content: str) -> str:
        """Format markdown for display"""
        return f"""👁️ MARKDOWN .LOOK FILE

{content}

📄 Formatted view above"""
    
    def _format_keyvalue_look(self, data: Dict) -> str:
        """Format key:value pairs"""
        formatted_lines = []
        for key, value in data.items():
            formatted_lines.append(f"  {key}: {value}")
        
        return f"""👁️ KEY:VALUE .LOOK FILE

{chr(10).join(formatted_lines)}

📊 {len(data)} entries found"""
    
    def _format_plain_look(self, content: str) -> str:
        """Format plain text"""
        lines = content.split('\n')
        preview = '\n'.join(lines[:20])  # First 20 lines
        
        if len(lines) > 20:
            preview += f"\n\n... ({len(lines) - 20} more lines)"
        
        return f"""👁️ PLAIN TEXT .LOOK FILE

```
{preview}
```

📄 {len(lines)} lines total"""
    
    def format_look_result(self, result: Dict) -> str:
        """Format a look file result for display"""
        if result["status"] != "success":
            return f"❌ Error reading .look file: {result.get('error', 'Unknown error')}"
        
        formatted = result.get("formatted", "No formatted output available")
        file_path = result.get("file", "Unknown file")
        content_type = result.get("content_type", "unknown")
        
        return f"""{formatted}

💾 File: {file_path}
📋 Type: {content_type}
✅ Successfully read"""

def main():
    """Test the LookFileTool"""
    print("👁️ Testing LookFileTool...\n")
    
    tool = LookFileTool()
    
    # Create sample .look files
    print("Creating sample .look files...")
    
    # Plain text
    tool.create_look_file("system_status", 
        "Time: 2026-02-12 10:00:00\nCPU: 45%\nRAM: 60%\nDisk: 30%\nStatus: Healthy",
        "plain")
    
    # Key:value
    tool.create_look_file("network_status",
        "local_ip: 10.211.144.110\nexternal_ip: 107.13.106.21\nhostname: DESKTOP-19SGUQU\nport_8892: open",
        "keyvalue")
    
    # List them
    print("\n📂 .look files created:")
    files = tool.list_look_files()
    for f in files.get("files", []):
        print(f"  • {f['name']} ({f['size']} bytes)")
    
    # Read one
    print("\n👁️ Reading network_status.look:")
    result = tool.read_look_file("network_status.look")
    print(tool.format_look_result(result))

if __name__ == "__main__":
    main()