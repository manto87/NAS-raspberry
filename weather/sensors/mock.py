import random
from datetime import datetime

from ..base_sensor import BaseSensor, WeatherReading


class MockSensor(BaseSensor):
    """Simulated sensor for development — produces a realistic random walk."""

    def __init__(self, base_temp: float = 20.0, base_humidity: float = 60.0):
        self._temp = base_temp
        self._humidity = base_humidity

    @property
    def name(self) -> str:
        return "mock"

    def read(self) -> WeatherReading:
        self._temp += random.uniform(-0.3, 0.3)
        self._humidity = max(10.0, min(99.0, self._humidity + random.uniform(-0.5, 0.5)))
        return WeatherReading(
            timestamp=datetime.now(),
            temperature=round(self._temp, 1),
            humidity=round(self._humidity, 1),
            pressure=round(1013.25 + random.uniform(-2, 2), 1),
        )
