#!/usr/bin/env python3
"""
🌐 NETWORK TOOL - SARA's Network Diagnostics
Teaches SARA how to get IP information, check connectivity, scan ports
"""

import subprocess
import socket
import re
from typing import Dict, List, Optional

class NetworkTool:
    """
    Network diagnostics and information tool
    
    This tool gives SARA the ability to:
    - Get IP addresses (local, external, all interfaces)
    - Check network connectivity
    - Scan ports
    - Get network interface info
    - Ping hosts
    """
    
    def __init__(self):
        # No caching - fetch fresh every time for privacy
        pass
    
    def get_ip_pool(self) -> Dict:
        """
        Get all IP addresses on the system (the "IP pool")
        
        Returns:
            Dict with local IP, external IP, and all interface IPs
        """
        result = {
            "status": "success",
            "local_ip": None,
            "external_ip": None,
            "interfaces": [],
            "hostname": socket.gethostname(),
            "timestamp": None
        }
        
        try:
            # Get local IP (default route)
            result["local_ip"] = self._get_local_ip()
            
            # Get all interface IPs
            result["interfaces"] = self._get_all_interfaces()
            
            # Try to get external IP (requires internet)
            result["external_ip"] = self._get_external_ip()
            
            from datetime import datetime
            result["timestamp"] = datetime.now().isoformat()
            
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
        
        return result
    
    def _get_local_ip(self) -> Optional[str]:
        """Get the primary local IP address"""
        try:
            # Connect to a remote address to determine local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(2)
            s.connect(("8.8.8.8", 80))  # Google's DNS
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return "127.0.0.1"
    
    def _get_all_interfaces(self) -> List[Dict]:
        """Get all network interfaces and their IPs"""
        interfaces = []
        
        try:
            # Using ip command (modern Linux)
            cmd = ["ip", "-j", "addr", "show"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                import json
                ip_data = json.loads(result.stdout)
                
                for iface in ip_data:
                    iface_info = {
                        "name": iface.get("ifname", "unknown"),
                        "state": iface.get("operstate", "unknown"),
                        "type": iface.get("link_type", "unknown"),
                        "ips": []
                    }
                    
                    # Get IP addresses from interface
                    for addr_info in iface.get("addr_info", []):
                        if addr_info.get("family") == "inet":  # IPv4
                            ip_entry = {
                                "ip": addr_info.get("local"),
                                "prefix": addr_info.get("prefixlen"),
                                "scope": addr_info.get("scope", "unknown")
                            }
                            iface_info["ips"].append(ip_entry)
                    
                    if iface_info["ips"]:
                        interfaces.append(iface_info)
                        
        except Exception as e:
            # Fallback to ifconfig or hostname
            try:
                result = subprocess.run(["hostname", "-I"], capture_output=True, text=True, timeout=2)
                if result.returncode == 0:
                    ips = result.stdout.strip().split()
                    if ips:
                        interfaces.append({
                            "name": "default",
                            "state": "up",
                            "type": "ethernet",
                            "ips": [{"ip": ip, "prefix": 24, "scope": "global"} for ip in ips]
                        })
            except:
                pass
        
        return interfaces
    
    def _get_external_ip(self) -> Optional[str]:
        """Get external/public IP address (requires internet)"""
        try:
            # Try multiple services
            services = [
                ["curl", "-s", "https://ipinfo.io/ip"],
                ["curl", "-s", "https://api.ipify.org"],
                ["curl", "-s", "https://ifconfig.me"]
            ]
            
            for service in services:
                result = subprocess.run(service, capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    ip = result.stdout.strip()
                    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip):
                        return ip
        except:
            pass
        
        return None  # No internet or all services failed
    
    def ping(self, host: str, count: int = 4) -> Dict:
        """
        Ping a host to check connectivity
        
        Args:
            host: Hostname or IP to ping
            count: Number of ping attempts
        
        Returns:
            Dict with ping results
        """
        result = {
            "status": "error",
            "host": host,
            "sent": count,
            "received": 0,
            "loss_percent": 100,
            "time_ms": None,
            "output": ""
        }
        
        try:
            cmd = ["ping", "-c", str(count), host]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=count*2 + 5)
            
            result["output"] = proc.stdout + proc.stderr
            
            if proc.returncode == 0:
                result["status"] = "success"
                
                # Parse ping statistics
                # Look for: 4 packets transmitted, 4 received, 0% packet loss
                match = re.search(r'(\d+) packets transmitted, (\d+) received.*?(\d+)% packet loss', result["output"])
                if match:
                    result["sent"] = int(match.group(1))
                    result["received"] = int(match.group(2))
                    result["loss_percent"] = int(match.group(3))
                
                # Look for: time 23.4ms
                match = re.search(r'time[<=]([\d\.]+)\s*ms', result["output"])
                if match:
                    result["time_ms"] = float(match.group(1))
            
        except subprocess.TimeoutExpired:
            result["error"] = "Ping timed out"
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def check_port(self, host: str, port: int, timeout: int = 3) -> Dict:
        """
        Check if a port is open on a host
        
        Args:
            host: Hostname or IP
            port: Port number to check
            timeout: Connection timeout in seconds
        
        Returns:
            Dict with port status
        """
        result = {
            "status": "error",
            "host": host,
            "port": port,
            "is_open": False,
            "service": None
        }
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result_code = sock.connect_ex((host, port))
            sock.close()
            
            if result_code == 0:
                result["status"] = "success"
                result["is_open"] = True
                result["service"] = self._get_service_name(port)
            else:
                result["status"] = "success"
                result["is_open"] = False
                result["error_code"] = result_code
                
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def _get_service_name(self, port: int) -> Optional[str]:
        """Get common service name for a port"""
        common_ports = {
            22: "SSH",
            80: "HTTP",
            443: "HTTPS",
            21: "FTP",
            25: "SMTP",
            53: "DNS",
            110: "POP3",
            143: "IMAP",
            3306: "MySQL",
            5432: "PostgreSQL",
            6379: "Redis",
            8080: "HTTP-Alt",
            8443: "HTTPS-Alt",
            3000: "Dev-Server",
            5000: "Flask",
            8000: "Django",
            8892: "SARA-Web"
        }
        return common_ports.get(port)
    
    def get_network_stats(self) -> Dict:
        """Get network interface statistics"""
        result = {
            "status": "error",
            "stats": []
        }
        
        try:
            # Get interface stats from /proc/net/dev or ip command
            cmd = ["ip", "-s", "link"]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            
            if proc.returncode == 0:
                result["status"] = "success"
                result["raw_output"] = proc.stdout
                
                # Parse the output (simplified)
                lines = proc.stdout.strip().split('\n')
                current_iface = None
                
                for line in lines:
                    if ':' in line and not line.startswith(' '):
                        parts = line.split(':')
                        current_iface = parts[0].strip()
                    elif current_iface and 'RX:' in line:
                        # RX stats line
                        pass
                    elif current_iface and line.strip() and 'bytes' not in line.lower():
                        # TX/RX data
                        pass
                        
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def format_ip_pool(self, ip_data: Dict) -> str:
        """
        Format IP pool data into a nice readable string
        Use this when responding to users!
        """
        if ip_data.get("status") != "success":
            return f"❌ Error getting IP info: {ip_data.get('error', 'Unknown error')}"
        
        output = []
        output.append("🌐 **IP POOL INFORMATION**")
        output.append(f"📍 Hostname: {ip_data.get('hostname', 'Unknown')}")
        output.append("")
        
        # Primary local IP
        local_ip = ip_data.get("local_ip")
        if local_ip:
            output.append(f"🏠 Local IP (Primary): {local_ip}")
        
        # External IP
        external_ip = ip_data.get("external_ip")
        if external_ip:
            output.append(f"🌍 External IP: {external_ip}")
        else:
            output.append("🌍 External IP: Not available (no internet)")
        
        output.append("")
        output.append("📡 Network Interfaces:")
        
        # All interfaces
        interfaces = ip_data.get("interfaces", [])
        if interfaces:
            for iface in interfaces:
                name = iface.get("name", "unknown")
                state = iface.get("state", "unknown")
                icon = "🟢" if state == "UP" else "🔴"
                output.append(f"  {icon} {name} ({state})")
                
                for ip_info in iface.get("ips", []):
                    ip = ip_info.get("ip", "N/A")
                    prefix = ip_info.get("prefix", "?")
                    scope = ip_info.get("scope", "unknown")
                    output.append(f"     └─ IP: {ip}/{prefix} ({scope})")
        else:
            output.append("  No interfaces found")
        
        return "\n".join(output)

def main():
    """Test the NetworkTool"""
    print("🌐 Testing NetworkTool...")
    
    tool = NetworkTool()
    
    # Test 1: Get IP Pool
    print("\n1️⃣ Getting IP Pool:")
    ip_data = tool.get_ip_pool()
    print(tool.format_ip_pool(ip_data))
    
    # Test 2: Ping
    print("\n2️⃣ Pinging Google (8.8.8.8):")
    ping_result = tool.ping("8.8.8.8", count=2)
    if ping_result["status"] == "success":
        print(f"   📶 {ping_result['received']}/{ping_result['sent']} replies, {ping_result['loss_percent']}% loss")
        if ping_result.get("time_ms"):
            print(f"   ⏱️  Time: {ping_result['time_ms']}ms")
    else:
        print(f"   ❌ Ping failed: {ping_result.get('error', 'Unknown')}")
    
    # Test 3: Check port
    print("\n3️⃣ Checking port 8892 (SARA web):")
    port_result = tool.check_port("127.0.0.1", 8892)
    if port_result["is_open"]:
        print(f"   🟢 Port 8892 is OPEN ({port_result.get('service', 'Unknown')})")
    else:
        print(f"   🔴 Port 8892 is closed")
    
    print("\n✅ NetworkTool test complete!")

if __name__ == "__main__":
    main()