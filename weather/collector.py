import importlib
import logging
import time

import yaml

from .base_sensor import BaseSensor
from . import store

logger = logging.getLogger(__name__)

SENSOR_MAP = {
    "mock":      ("weather.sensors.mock",      "MockSensor"),
    "dht22":     ("weather.sensors.dht22",     "DHT22Sensor"),
    "bme280":    ("weather.sensors.bme280",    "BME280Sensor"),
    "openmeteo": ("weather.sensors.openmeteo", "OpenMeteoSensor"),
}


def _load_sensor(cfg: dict) -> BaseSensor:
    sensor_type = cfg.get("sensor", "mock")
    if sensor_type not in SENSOR_MAP:
        raise ValueError(f"Unknown sensor type '{sensor_type}'. Choose: {list(SENSOR_MAP)}")

    module_path, class_name = SENSOR_MAP[sensor_type]
    cls = getattr(importlib.import_module(module_path), class_name)

    if sensor_type == "dht22":
        return cls(gpio_pin=cfg.get("dht_gpio_pin", 4))
    if sensor_type == "bme280":
        return cls(i2c_address=int(cfg.get("bme280_i2c_address", "0x76"), 16))
    if sensor_type == "openmeteo":
        return cls(latitude=cfg["latitude"], longitude=cfg["longitude"])
    return cls()


def run(config_path: str = "config.yaml"):
    with open(config_path) as f:
        cfg = yaml.safe_load(f)

    weather_cfg = cfg["weather"]
    interval = weather_cfg.get("interval", 60)
    db_path = weather_cfg.get("db_path", "data/weather.db")

    sensor = _load_sensor(weather_cfg)
    logger.info("Collector started — sensor: %s, interval: %ds", sensor.name, interval)

    while True:
        try:
            reading = sensor.read()
            store.save(reading, db_path)
            logger.debug("Saved: %s", reading)
        except Exception as exc:
            logger.error("Sensor read failed: %s", exc)
        time.sleep(interval)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    run()
