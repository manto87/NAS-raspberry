from datetime import datetime

from ..base_sensor import BaseSensor, WeatherReading


class DHT22Sensor(BaseSensor):
    """DHT22 or DHT11 via the Adafruit_DHT library (GPIO, no I2C)."""

    def __init__(self, gpio_pin: int, sensor_type: str = "DHT22"):
        try:
            import Adafruit_DHT  # type: ignore
        except ImportError as exc:
            raise ImportError("pip install Adafruit-DHT") from exc

        self._lib = Adafruit_DHT
        self._sensor = Adafruit_DHT.DHT22 if sensor_type == "DHT22" else Adafruit_DHT.DHT11
        self._pin = gpio_pin

    @property
    def name(self) -> str:
        return "dht22"

    def read(self) -> WeatherReading:
        humidity, temperature = self._lib.read_retry(self._sensor, self._pin)
        if humidity is None or temperature is None:
            raise RuntimeError("Failed to read from DHT sensor")
        return WeatherReading(
            timestamp=datetime.now(),
            temperature=round(temperature, 1),
            humidity=round(humidity, 1),
        )
