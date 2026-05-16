#!/usr/bin/env python3
"""Configure Samba shares from config.yaml. Run as root."""
import sys
import subprocess
from pathlib import Path

import yaml

_GLOBAL = """\
[global]
    workgroup = {workgroup}
    server string = {server_name}
    netbios name = {server_name}
    security = user
    map to guest = Bad User
    dns proxy = no
    log file = /var/log/samba/log.%m
    max log size = 50

"""

_SHARE = """\
[{name}]
    path = {path}
    browsable = yes
    writable = {writable}
    valid users = {valid_users}
    create mask = 0664
    directory mask = 0775

"""


def setup(config_path: str = "config.yaml"):
    with open(config_path) as f:
        cfg = yaml.safe_load(f)["nas"]

    conf = _GLOBAL.format(
        workgroup=cfg.get("workgroup", "WORKGROUP"),
        server_name=cfg.get("server_name", "raspberrypi"),
    )

    for share in cfg.get("shares", []):
        Path(share["path"]).mkdir(parents=True, exist_ok=True)
        conf += _SHARE.format(
            name=share["name"],
            path=share["path"],
            writable="yes" if share.get("writable", True) else "no",
            valid_users=share.get("valid_users", "@nasusers"),
        )

    dest = Path("/etc/samba/smb.conf")
    dest.write_text(conf)
    print(f"Written: {dest}")

    subprocess.run(["systemctl", "restart", "smbd", "nmbd"], check=True)
    print("Samba restarted.")


if __name__ == "__main__":
    if sys.geteuid() != 0:
        sys.exit("Run as root: sudo python3 nas/setup.py")
    setup()
