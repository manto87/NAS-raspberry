import logging
import sys
from pathlib import Path

# Ensure project root is on the path regardless of how this script is invoked
sys.path.insert(0, str(Path(__file__).parent.parent))

import yaml
from flask import Flask, abort, jsonify, render_template, request

app = Flask(__name__)
logger = logging.getLogger(__name__)

_cfg: dict | None = None
_zone_controller = None


def get_config(path: str = "config.yaml") -> dict:
    global _cfg
    if _cfg is None:
        with open(path) as f:
            _cfg = yaml.safe_load(f)
    return _cfg


def get_zone_controller():
    global _zone_controller
    if _zone_controller is None:
        cfg = get_config()
        if cfg["irrigation"].get("enabled"):
            from irrigation.controller import ZoneController
            _zone_controller = ZoneController(cfg["irrigation"]["zones"])
    return _zone_controller


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/nas/status")
def nas_status():
    from nas.monitor import get_disk_usage, get_samba_status, get_system_stats
    cfg = get_config()
    share_paths = [s["path"] for s in cfg["nas"]["shares"]]
    return jsonify({
        "disks": get_disk_usage(share_paths),
        "samba": get_samba_status(),
        "system": get_system_stats(),
    })


@app.route("/api/weather/current")
def weather_current():
    from weather import store
    cfg = get_config()
    return jsonify(store.get_latest(cfg["weather"]["db_path"]) or {})


@app.route("/api/weather/history")
def weather_history():
    from weather import store
    cfg = get_config()
    hours = request.args.get("hours", 24, type=int)
    return jsonify(store.get_history(cfg["weather"]["db_path"], hours))


@app.route("/api/irrigation/status")
def irrigation_status():
    cfg = get_config()
    if not cfg["irrigation"].get("enabled"):
        return jsonify({"enabled": False, "zones": []})
    return jsonify({"enabled": True, "zones": get_zone_controller().status()})


@app.route("/api/irrigation/zone/<int:zone_id>/on", methods=["POST"])
def zone_on(zone_id: int):
    cfg = get_config()
    if not cfg["irrigation"].get("enabled"):
        abort(503, "Irrigation is disabled in config.yaml")
    zone_cfg = next((z for z in cfg["irrigation"]["zones"] if z["id"] == zone_id), None)
    if not zone_cfg:
        abort(404, f"Zone {zone_id} not found")
    body = request.get_json(silent=True) or {}
    duration = body.get("duration", zone_cfg["duration"])
    get_zone_controller().turn_on(zone_id)
    return jsonify({"status": "on", "zone_id": zone_id, "duration": duration})


@app.route("/api/irrigation/zone/<int:zone_id>/off", methods=["POST"])
def zone_off(zone_id: int):
    cfg = get_config()
    if not cfg["irrigation"].get("enabled"):
        abort(503, "Irrigation is disabled in config.yaml")
    if not any(z["id"] == zone_id for z in cfg["irrigation"]["zones"]):
        abort(404, f"Zone {zone_id} not found")
    get_zone_controller().turn_off(zone_id)
    return jsonify({"status": "off", "zone_id": zone_id})


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    cfg = get_config()
    web = cfg.get("web", {})
    app.run(host=web.get("host", "0.0.0.0"), port=web.get("port", 5000), debug=web.get("debug", False))
