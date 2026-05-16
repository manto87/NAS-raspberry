#!/usr/bin/env python3
"""Manage Samba users. Run as root."""
import getpass
import subprocess
import sys


def add_user(username: str, password: str):
    result = subprocess.run(["id", username], capture_output=True)
    if result.returncode != 0:
        subprocess.run(
            ["useradd", "-M", "-s", "/usr/sbin/nologin", username], check=True
        )

    subprocess.run(["groupadd", "-f", "nasusers"], check=True)
    subprocess.run(["usermod", "-aG", "nasusers", username], check=True)

    subprocess.run(
        ["smbpasswd", "-a", "-s", username],
        input=f"{password}\n{password}\n",
        text=True,
        check=True,
    )
    print(f"User '{username}' added.")


def remove_user(username: str):
    subprocess.run(["smbpasswd", "-x", username], check=True)
    print(f"User '{username}' removed from Samba.")


if __name__ == "__main__":
    if sys.geteuid() != 0:
        sys.exit("Run as root: sudo python3 nas/users.py")

    if len(sys.argv) < 3 or sys.argv[1] not in ("add", "remove"):
        print("Usage: users.py add <username> | users.py remove <username>")
        sys.exit(1)

    action, username = sys.argv[1], sys.argv[2]
    if action == "add":
        pw = getpass.getpass(f"Samba password for {username}: ")
        add_user(username, pw)
    else:
        remove_user(username)
