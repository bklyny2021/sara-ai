#!/usr/bin/env python3
"""SARA SYSTEM INFO - real GPU (nvidia-smi) + RAM + CPU + disk breakdown.
Gives an honest, real readout instead of a guessed 'no GPU'."""
import subprocess
import psutil
import platform

def _gpu_info():
    """Real NVIDIA GPU info via nvidia-smi (Boo has 4060 Ti + 1660 Ti)."""
    lines = []
    try:
        r = subprocess.run(
            ["nvidia-smi", "--query-gpu=index,name,memory.total,memory.used,memory.free,utilization.gpu,temperature.gpu",
             "--format=csv,noheader"],
            capture_output=True, text=True, timeout=12)
        if r.returncode == 0 and r.stdout.strip():
            for ln in r.stdout.strip().splitlines():
                parts = [p.strip() for p in ln.split(",")]
                if len(parts) >= 6:
                    lines.append(
                        f"  GPU {parts[0]}: {parts[1]} | VRAM {parts[3]} used / {parts[2]} total "
                        f"({parts[4]} free) | {parts[5]} load | {parts[6]}C"
                    )
        else:
            lines.append("  nvidia-smi returned nothing (check driver)")
    except Exception as e:
        lines.append(f"  nvidia-smi unavailable: {e}")
    return "\n".join(lines) if lines else "  no GPU info"

def get_system_info():
    vm = psutil.virtual_memory()
    cpu = psutil.cpu_percent(interval=0.5)
    cores = psutil.cpu_count(logical=True)
    disk = psutil.disk_usage("C:/")
    out = (
        "🧮 SYSTEM BREAKDOWN\n"
        f"• RAM: {vm.used/1e9:.1f} GB used / {vm.total/1e9:.1f} GB total | {vm.available/1e9:.1f} GB free ({vm.percent:.0f}%)\n"
        f"• CPU: {cpu}% load | {cores} logical cores\n"
        f"• Disk C:: {disk.used/1e9:.0f} GB used / {disk.total/1e9:.0f} GB total | {disk.free/1e9:.0f} GB free\n"
        f"• GPU(s):\n{_gpu_info()}"
    )
    return out

if __name__ == "__main__":
    print(get_system_info())
