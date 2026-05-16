# NAS-raspberry

Raspberry Pi 4 home server: NAS (Samba), weather station, and irrigation controller.

## Project layout

```
nas/          Samba setup script and system monitor
weather/      Sensor abstraction + SQLite collector
  sensors/    Mock, DHT22, and BME280 implementations
irrigation/   GPIO zone controller (scaffolded, enable in config.yaml)
web/          Flask dashboard served on port 5000
systemd/      Service unit files
scripts/      install.sh for first-time setup
data/         Runtime SQLite DB (git-ignored)
config.yaml   Single source of truth for all settings
```

## Development

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python web/app.py          # dashboard at http://localhost:5000
python -m weather.collector  # background data collector
```

## First-time Pi setup

```bash
sudo bash scripts/install.sh
sudo python3 nas/setup.py           # writes /etc/samba/smb.conf
sudo python3 nas/users.py add alice  # adds a Samba user
```

## Adding a new sensor

1. Create `weather/sensors/myname.py` subclassing `BaseSensor`
2. Register it in `SENSOR_MAP` in `weather/collector.py`
3. Set `sensor: myname` in `config.yaml`
