#!/usr/bin/env python3
"""
🔍 SARA NETWORK SCANNER
Find real devices on the local network
No fake team members - actual network discovery
"""

import subprocess
import socket
import re
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

class NetworkScanner:
    """Scan local network for real connected devices"""
    
    def __init__(self):
        self.timeout = 2
        
    def get_local_subnet(self) -> Optional[str]:
        """Get local IP and determine subnet (Windows + Linux compatible)"""
        try:
            import platform
            is_win = platform.system() == "Windows"
            local_ip = self._windows_local_ip() if is_win else None
            if not local_ip:
                # fallback: grab from an outbound UDP socket
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                try:
                    s.connect(("8.8.8.8", 80))
                    local_ip = s.getsockname()[0]
                finally:
                    s.close()
            if not local_ip:
                return None
            parts = local_ip.split(".")
            if len(parts) == 4:
                return f"{parts[0]}.{parts[1]}.{parts[2]}."
        except Exception:
            pass
        return None

    def _get_local_ip(self) -> Optional[str]:
        """Get primary local IP address (Windows/Linux compatible)"""
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
            finally:
                s.close()
        except Exception:
            return None

    def _windows_local_ip(self) -> Optional[str]:
        """Windows: get local IPv4 via ipconfig"""
        try:
            out = subprocess.run(["ipconfig"], capture_output=True, text=True, timeout=10).stdout
            for line in out.splitlines():
                if "IPv4" in line:
                    ip = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                    if ip:
                        return ip.group(1)
        except Exception:
            pass
        return None

    def scan_host(self, ip: str) -> Optional[Dict]:
        """Ping a single host to see if it's up (Windows + Linux compatible)"""
        import platform
        try:
            if platform.system() == "Windows":
                result = subprocess.run(
                    ["ping", "-n", "1", "-w", "1500", ip],
                    capture_output=True, text=True, timeout=5
                )
                up = result.returncode == 0
            else:
                result = subprocess.run(
                    ["ping", "-c", "1", "-W", "2", ip],
                    capture_output=True, text=True, timeout=5
                )
                up = result.returncode == 0
            if up:
                hostname = self._get_hostname(ip)
                return {
                    "ip": ip,
                    "status": "up",
                    "hostname": hostname or "unknown",
                    "ports_open": []
                }
        except Exception:
            pass
        return None
    
    def _get_hostname(self, ip: str) -> Optional[str]:
        """Try to resolve hostname from IP"""
        try:
            result = subprocess.run(
                ["host", ip],
                capture_output=True,
                text=True,
                timeout=3
            )
            if result.returncode == 0 and "domain name pointer" in result.stdout:
                # Extract hostname
                match = re.search(r'pointer\s+(.+)\.?$', result.stdout)
                if match:
                    return match.group(1).rstrip('.')
        except:
            pass
        return None
    
    def scan_port(self, ip: str, port: int) -> bool:
        """Check if a specific port is open on a host"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except:
            return False
    
    def get_arp_table(self) -> List[Dict]:
        """Get ARP table - shows MAC addresses of connected devices"""
        devices = []
        try:
            result = subprocess.run(
                ["ip", "neigh", "show"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    # Parse: 10.211.144.1 dev eth0 lladdr ab:cd:ef:12:34:56 REACHABLE
                    match = re.match(r'(\S+)\s+.*lladdr\s+([a-f0-9:]{17}).*REACHABLE', line, re.I)
                    if match:
                        ip = match.group(1)
                        mac = match.group(2)
                        devices.append({
                            "ip": ip,
                            "mac": mac,
                            "vendor": self._lookup_vendor(mac),
                            "status": "active"
                        })
        except:
            pass
        return devices
    
    def _lookup_vendor(self, mac: str) -> str:
        """Simple MAC vendor lookup (could use API, but keeping it local)"""
        # Common prefixes
        vendors = {
            "00:50:56": "VMware",
            "00:0c:29": "VMware",
            "08:00:27": "VirtualBox",
            "52:54:00": "KVM/QEMU",
            "b8:27:eb": "Raspberry Pi",
            "dc:a6:32": "Raspberry Pi",
            "00:1b:21": "Intel",
            "00:1c:c4": "Dell",
            "00:25:64": "Hewlett-Packard",
            "00:26:73": "Hewlett-Packard",
            "00:4e:35": "Google",
            "ac:de:48": "Apple",
        }
        
        # Check first 3 octets
        prefix = ':'.join(mac.split(':')[:3]).upper()
        prefix_lower = prefix.lower()
        
        for p, v in vendors.items():
            if prefix_lower == p.lower():
                return v
        
        return "Unknown"
    
    def find_local_devices(self) -> str:
        """Scan and return formatted list of local devices"""
        subnet = self.get_local_subnet()
        
        if not subnet:
            return "❌ Could not determine local network"
        
        output = [
            "🔍 SCANNING LOCAL NETWORK",
            f"Subnet: {subnet}0/24",
            "",
            "📍 ACTIVE DEVICES:",
        ]
        
        # Quick scan of common IPs (x.x.x.1 to x.x.x.20 is usually enough)
        active = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(self.scan_host, f"{subnet}{i}"): i for i in range(1, 21)}
            
            for future in as_completed(futures):
                result = future.result()
                if result:
                    active.append(result)
        
        # Sort by IP
        active.sort(key=lambda x: [int(n) for n in x['ip'].split('.')])
        
        if active:
            for device in active:
                hostname = device.get('hostname', 'unknown')
                if hostname == "unknown":
                    hostname = ""
                else:
                    hostname = f" ({hostname})"
                output.append(f"  🖥️  {device['ip']}{hostname}")
        else:
            output.append("  None found in quick scan")
        
        # ARP table
        output.append("")
        output.append("📋 KNOWN DEVICES (from ARP table):")
        
        arp_devices = self.get_arp_table()
        if arp_devices:
            for device in arp_devices:
                vendor = device.get('vendor', 'Unknown')
                output.append(f"  📡 {device['ip']} - {device['mac']} [{vendor}]")
        else:
            output.append("  No ARP entries found")
        
        # This local machine info
        output.append("")
        output.append("💻 THIS MACHINE:")
        try:
            hostname = subprocess.run(["hostname"], capture_output=True, text=True).stdout.strip()
            output.append(f"  Name: {hostname}")
            output.append(f"  IPs: {self.get_local_subnet() or 'N/A'}")
        except:
            output.append("  Could not get local info")
        
        output.append("")
        output.append("📝 Note: This is a LOCAL network scan only (10.x.x.x or 192.168.x.x)")
        output.append("    No internet/external connections shown")
        
        return '\n'.join(output)


if __name__ == "__main__":
    scanner = NetworkScanner()
    print(scanner.find_local_devices())
