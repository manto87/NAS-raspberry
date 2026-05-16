#!/usr/bin/env bash
# First-time setup for the Pi home system.
# Run as root: sudo bash scripts/install.sh
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SERVICE_USER="${SERVICE_USER:-pi}"

echo "=== Pi Home System — Installer ==="
echo "Repo : $REPO_DIR"
echo "User : $SERVICE_USER"
echo ""

[ "$EUID" -eq 0 ] || { echo "Run as root: sudo bash $0"; exit 1; }

echo "[1/5] Installing system packages..."
apt-get update -qq
apt-get install -y -qq samba samba-common-bin python3 python3-pip python3-venv python3-dev

echo "[2/5] Creating Python virtual environment..."
python3 -m venv "$REPO_DIR/.venv"
"$REPO_DIR/.venv/bin/pip" install --quiet --upgrade pip
"$REPO_DIR/.venv/bin/pip" install --quiet -r "$REPO_DIR/requirements.txt"

echo "[3/5] Creating data directory..."
mkdir -p "$REPO_DIR/data"
chown "$SERVICE_USER:$SERVICE_USER" "$REPO_DIR/data"

echo "[4/5] Installing systemd services..."
for SVC in rpi-weather rpi-web; do
  sed \
    -e "s|/home/pi/NAS-raspberry|$REPO_DIR|g" \
    -e "s|User=pi|User=$SERVICE_USER|g" \
    "$REPO_DIR/systemd/$SVC.service" \
    > "/etc/systemd/system/$SVC.service"
  echo "  Installed /etc/systemd/system/$SVC.service"
done

systemctl daemon-reload
systemctl enable --now rpi-weather rpi-web

echo ""
echo "[5/5] Done!"
echo ""
echo "  Configure shares : edit config.yaml, then:"
echo "    sudo .venv/bin/python nas/setup.py"
echo "  Add a NAS user   : sudo .venv/bin/python nas/users.py add <username>"
echo "  Dashboard        : http://$(hostname -I | awk '{print $1}'):5000"
echo ""
systemctl status rpi-weather rpi-web --no-pager -l || true
