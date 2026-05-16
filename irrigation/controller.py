"""GPIO-based irrigation zone controller.

Runs in simulation mode when RPi.GPIO is not available (e.g. dev laptop).
Active-low relay wiring assumed: LOW = valve open, HIGH = valve closed.
"""
import logging

logger = logging.getLogger(__name__)

_gpio_available = False
try:
    import RPi.GPIO as GPIO  # type: ignore
    GPIO.setmode(GPIO.BCM)
    _gpio_available = True
except (ImportError, RuntimeError):
    logger.warning("RPi.GPIO not available — running in simulation mode")


class ZoneController:
    def __init__(self, zones: list[dict]):
        self._zones = {z["id"]: z for z in zones}
        self._active: dict[int, bool] = {z["id"]: False for z in zones}

        if _gpio_available:
            for zone in zones:
                GPIO.setup(zone["gpio_pin"], GPIO.OUT, initial=GPIO.HIGH)

    def turn_on(self, zone_id: int):
        zone = self._zones[zone_id]
        if _gpio_available:
            GPIO.output(zone["gpio_pin"], GPIO.LOW)
        self._active[zone_id] = True
        logger.info("Zone %d (%s) ON", zone_id, zone["name"])

    def turn_off(self, zone_id: int):
        zone = self._zones[zone_id]
        if _gpio_available:
            GPIO.output(zone["gpio_pin"], GPIO.HIGH)
        self._active[zone_id] = False
        logger.info("Zone %d (%s) OFF", zone_id, zone["name"])

    def status(self) -> list[dict]:
        return [
            {
                "id": z["id"],
                "name": z["name"],
                "active": self._active[z["id"]],
                "gpio_pin": z["gpio_pin"],
            }
            for z in self._zones.values()
        ]

    def cleanup(self):
        for zone_id in list(self._active):
            if self._active[zone_id]:
                self.turn_off(zone_id)
        if _gpio_available:
            GPIO.cleanup()
