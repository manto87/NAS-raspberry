from datetime import datetime

from ..base_sensor import BaseSensor, WeatherReading


class BME280Sensor(BaseSensor):
    """BME280 (temperature + humidity + pressure) over I2C."""

    def __init__(self, i2c_address: int = 0x76):
        try:
            import board  # type: ignore
            import busio  # type: ignore
            import adafruit_bme280.basic as adafruit_bme280  # type: ignore
        except ImportError as exc:
            raise ImportError("pip install adafruit-circuitpython-bme280") from exc

        i2c = busio.I2C(board.SCL, board.SDA)
        self._bme = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=i2c_address)

    @property
    def name(self) -> str:
        return "bme280"

    def read(self) -> WeatherReading:
        return WeatherReading(
            timestamp=datetime.now(),
            temperature=round(self._bme.temperature, 1),
            humidity=round(self._bme.humidity, 1),
            pressure=round(self._bme.pressure, 1),
        )
