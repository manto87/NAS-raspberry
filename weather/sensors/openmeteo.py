from datetime import datetime

import requests

from ..base_sensor import BaseSensor, WeatherReading


class OpenMeteoSensor(BaseSensor):
    """Real weather data from the Open-Meteo public API — no API key required."""

    _URL = "https://api.open-meteo.com/v1/forecast"

    def __init__(self, latitude: float, longitude: float):
        self._lat = latitude
        self._lon = longitude

    @property
    def name(self) -> str:
        return "openmeteo"

    def read(self) -> WeatherReading:
        resp = requests.get(
            self._URL,
            params={
                "latitude": self._lat,
                "longitude": self._lon,
                "current": "temperature_2m,relative_humidity_2m,pressure_msl",
                "timezone": "auto",
            },
            timeout=10,
        )
        resp.raise_for_status()
        c = resp.json()["current"]
        return WeatherReading(
            timestamp=datetime.now(),
            temperature=round(c["temperature_2m"], 1),
            humidity=round(float(c["relative_humidity_2m"]), 1),
            pressure=round(c["pressure_msl"], 1),
        )
