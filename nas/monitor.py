import subprocess
from pathlib import Path

import psutil


def get_disk_usage(paths: list[str] | None = None) -> list[dict]:
    if paths:
        results = []
        for path in paths:
            p = Path(path)
            if p.exists():
                usage = psutil.disk_usage(path)
                results.append({
                    "path": path,
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent": usage.percent,
                })
        return results

    results = []
    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
            results.append({
                "path": part.mountpoint,
                "device": part.device,
                "fstype": part.fstype,
                "total": usage.total,
                "used": usage.used,
                "free": usage.free,
                "percent": usage.percent,
            })
        except PermissionError:
            continue
    return results


def get_samba_status() -> dict:
    try:
        result = subprocess.run(
            ["systemctl", "is-active", "smbd"],
            capture_output=True, text=True, timeout=5,
        )
        running = result.stdout.strip() == "active"
    except (subprocess.TimeoutExpired, FileNotFoundError):
        running = False

    users: list[str] = []
    try:
        result = subprocess.run(
            ["smbstatus", "--brief"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            for line in result.stdout.strip().splitlines()[2:]:
                if line.strip():
                    users.append(line.split()[0])
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return {"running": running, "connected_users": users}


def get_system_stats() -> dict:
    stats: dict = {
        "cpu_percent": psutil.cpu_percent(interval=0.5),
        "memory": {
            "total": psutil.virtual_memory().total,
            "used": psutil.virtual_memory().used,
            "percent": psutil.virtual_memory().percent,
        },
        "temperature": None,
    }
    temp_path = Path("/sys/class/thermal/thermal_zone0/temp")
    if temp_path.exists():
        stats["temperature"] = round(int(temp_path.read_text()) / 1000, 1)
    return stats
