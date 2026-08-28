#!/usr/bin/env python3
"""
SARA NETWORK SECURITY - protect Boo's network.
Scans for threats, checks open ports, monitors for suspicious activity,
and reports findings. Uses netstat, ping, and network scanning.

Commands:
- scan_network() - find all live hosts on the LAN
- check_open_ports() - list open ports and listening services
- check_connections() - show active connections
- security_audit() - full security check
"""
import subprocess
import re
import socket
import platform
import json
import os
from datetime import datetime

class SaraNetworkSecurity:
    """Network protection and monitoring for Boo's PC"""

    def __init__(self):
        self.log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "network_security_log.json")
        self.known_devices = self._load_known_devices()

    def _load_known_devices(self):
        """Load known devices from log if exists"""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, "r", encoding="utf-8") as f:
                    return json.load(f).get("known_devices", {})
            except:
                pass
        return {}

    def _save(self, data):
        """Save to log"""
        try:
            with open(self.log_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except:
            pass

    def _run(self, cmd, timeout=20):
        """Run a command and return output"""
        try:
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
            return r.stdout or r.stderr
        except Exception as e:
            return f"ERROR: {e}"

    def get_local_ip(self):
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    def scan_network(self):
        """Find live hosts on the LAN"""
        ip = self.get_local_ip()
        subnet = ".".join(ip.split(".")[:3])
        print(f"Scanning {subnet}.0/24...")
        hosts = []
        for i in range(1, 255):
            target = f"{subnet}.{i}"
            r = self._run(f"ping -n 1 -w 500 {target}", timeout=3)
            if "TTL=" in r or "Reply from" in r:
                hosts.append(target)
        return hosts

    def check_open_ports(self):
        """List open ports and listening services"""
        out = self._run("netstat -ano")
        listening = []
        for line in out.splitlines():
            if "LISTENING" in line:
                parts = line.split()
                if len(parts) >= 2:
                    addr = parts[1]
                    port = addr.split(":")[-1]
                    listening.append({"address": addr, "port": port})
        return listening

    def check_connections(self):
        """Show active connections"""
        out = self._run("netstat -ano")
        connections = []
        for line in out.splitlines():
            if "ESTABLISHED" in line:
                parts = line.split()
                if len(parts) >= 3:
                    connections.append({
                        "local": parts[1],
                        "remote": parts[2],
                        "state": parts[3]
                    })
        return connections

    def check_firewall(self):
        """Check Windows firewall status"""
        out = self._run("netsh advfirewall show allprofiles state")
        return out

    def port_scan(self, host=None, ports=None):
        """Scan a host for open ports. Default: common ports on localhost."""
        if not host:
            host = self.get_local_ip()
        if not ports:
            ports = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 993, 995, 1433, 1521, 3306, 3389, 5432, 5900, 6379, 8080, 8443, 8888, 8892, 9090, 27017]
        open_ports = []
        for port in ports:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1)
                result = s.connect_ex((host, port))
                if result == 0:
                    open_ports.append(port)
                s.close()
            except:
                pass
        return open_ports

    def packet_loss(self, host="8.8.8.8", count=4):
        """Check packet loss to a host using ping"""
        out = self._run(f"ping -n {count} {host}", timeout=30)
        # Parse packet loss percentage
        loss = "unknown"
        m = re.search(r"\((\d+)% loss\)", out)
        if m:
            loss = m.group(1) + "%"
        # Parse avg latency
        avg = "unknown"
        m2 = re.search(r"Average = (\d+)ms", out)
        if m2:
            avg = m2.group(1) + "ms"
        return {"host": host, "packet_loss": loss, "avg_latency": avg, "raw": out[:300]}

    def trace_route(self, host="8.8.8.8"):
        """Trace the route to a host"""
        out = self._run(f"tracert -d {host}", timeout=30)
        return out[:500]

    def security_audit(self):
        """Full security check"""
        report = []
        report.append("🔒 SARA Network Security Audit")
        report.append(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Local IP: {self.get_local_ip()}")
        report.append("")
        
        # Open ports
        report.append("📡 Open ports (listening):")
        ports = self.check_open_ports()
        if ports:
            for p in ports[:20]:
                report.append(f"  • Port {p['port']} on {p['address']}")
        else:
            report.append("  None found")
        report.append("")
        
        # Active connections
        report.append("🔗 Active connections:")
        conns = self.check_connections()
        if conns:
            for c in conns[:15]:
                report.append(f"  • {c['local']} → {c['remote']}")
        else:
            report.append("  None")
        report.append("")
        
        # Firewall
        report.append("🛡️ Firewall status:")
        fw = self.check_firewall()
        report.append(f"  {fw[:200]}")
        
        return "\n".join(report)

    def monitor(self):
        """Monitor for new/suspicious connections"""
        conns = self.check_connections()
        new = []
        for c in conns:
            remote = c.get("remote", "")
            if remote and remote not in self.known_devices:
                new.append(remote)
        if new:
            self.known_devices.update({r: datetime.now().isoformat() for r in new})
            self._save({"known_devices": self.known_devices})
        return new

if __name__ == "__main__":
    sec = SaraNetworkSecurity()
    print(sec.security_audit())
