# NAS-raspberry

Raspberry Pi 4 home server with three subsystems managed from a single Flask dashboard.

| Module | Status | Description |
|---|---|---|
| NAS | Ready | Samba shares + system monitoring |
| Weather station | Ready (mock sensor) | Pluggable sensor interface — add DHT22 or BME280 |
| Irrigation | Scaffolded | GPIO zone controller, enable when hardware is connected |

## Quick start (Pi)

```bash
# 1. Clone and install
git clone https://github.com/manto87/NAS-raspberry.git
cd NAS-raspberry
sudo SERVICE_USER=pi bash scripts/install.sh

# 2. Configure Samba (edit config.yaml first)
sudo .venv/bin/python nas/setup.py
sudo .venv/bin/python nas/users.py add alice

# 3. Open the dashboard
# http://<pi-ip>:5000
```

## Development (laptop)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Terminal 1 — weather data collector (uses mock sensor by default)
python -m weather.collector

# Terminal 2 — web dashboard
python web/app.py
# → http://localhost:5000
```

## Configuration

All settings live in `config.yaml`:

- `nas.shares` — list of Samba shares (path, name, permissions)
- `weather.sensor` — `mock` | `dht22` | `bme280`
- `irrigation.enabled` — set `true` and wire up GPIO pins when hardware arrives
- `web.port` — default `5000`

## Adding a sensor

1. Subclass `BaseSensor` in `weather/sensors/myname.py`
2. Register it in `SENSOR_MAP` in `weather/collector.py`
3. Set `sensor: myname` in `config.yaml`
