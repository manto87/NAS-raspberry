"""Timed irrigation runner — turns a zone on, then off after `duration` seconds."""
import logging
import threading

from .controller import ZoneController

logger = logging.getLogger(__name__)


class Scheduler:
    def __init__(self, controller: ZoneController):
        self._ctrl = controller
        self._timers: dict[int, threading.Timer] = {}

    def run_zone(self, zone_id: int, duration: int):
        """Turn zone on; schedule automatic shutoff after `duration` seconds."""
        if zone_id in self._timers:
            self._timers[zone_id].cancel()

        self._ctrl.turn_on(zone_id)
        logger.info("Zone %d scheduled for %ds", zone_id, duration)

        t = threading.Timer(duration, self._stop, args=[zone_id])
        t.daemon = True
        t.start()
        self._timers[zone_id] = t

    def _stop(self, zone_id: int):
        self._ctrl.turn_off(zone_id)
        self._timers.pop(zone_id, None)

    def cancel(self, zone_id: int):
        if zone_id in self._timers:
            self._timers[zone_id].cancel()
        self._stop(zone_id)
