from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class WeatherReading:
    timestamp: datetime
    temperature: float    # Celsius
    humidity: float       # percent
    pressure: float | None = None  # hPa
    extra: dict = field(default_factory=dict)


class BaseSensor(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def read(self) -> WeatherReading: ...
