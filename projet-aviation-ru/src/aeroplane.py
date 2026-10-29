"""Модель самолёта (инкапсуляция + сравнение)."""
from functools import total_ordering


@total_ordering
class Aeroplane:
    """Самолёт. Сравнение по высоте, затем по скорости (==, <, >, ...)."""

    __slots__ = ("_callsign", "_country", "_velocity", "_altitude")

    def __init__(self, callsign: str, country: str, velocity: float, altitude: float):
        self._callsign = self._validate_text(callsign, "callsign", allow_empty=True)
        self._country = self._validate_text(country, "country")
        self._velocity = self._validate_number(velocity, "velocity")
        self._altitude = self._validate_number(altitude, "altitude")

    # --- валидация -------------------------------------------------
    @staticmethod
    def _validate_text(value, name: str, allow_empty: bool = False) -> str:
        if not isinstance(value, str):
            raise TypeError(f"{name} должен быть строкой.")
        value = value.strip()
        if not value and not allow_empty:
            raise ValueError(f"{name} не может быть пустым.")
        return value or "N/A"

    @staticmethod
    def _validate_number(value, name: str) -> float:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"{name} должен быть числом.")
        if value < 0:
            raise ValueError(f"{name} не может быть отрицательным.")
        return float(value)

    # --- чтение атрибутов ------------------------------------------
    @property
    def callsign(self) -> str:
        return self._callsign

    @property
    def country(self) -> str:
        return self._country

    @property
    def velocity(self) -> float:
        return self._velocity

    @property
    def altitude(self) -> float:
        return self._altitude

    # --- сравнение -----------------------------------------------
    def compare_by_velocity(self, other: "Aeroplane") -> int:
        """Возвращает -1, 0 или 1 по скорости."""
        return (self._velocity > other._velocity) - (self._velocity < other._velocity)

    def compare_by_altitude(self, other: "Aeroplane") -> int:
        """Возвращает -1, 0 или 1 по высоте."""
        return (self._altitude > other._altitude) - (self._altitude < other._altitude)

    def _key(self) -> tuple[float, float]:
        return self._altitude, self._velocity

    def __eq__(self, other):
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return self._key() == other._key()

    def __lt__(self, other):
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return self._key() < other._key()

    def __hash__(self):
        return hash((self._callsign, self._country, self._velocity, self._altitude))

    # --- преобразование ------------------------------------------------
    def to_dict(self) -> dict:
        return {
            "callsign": self._callsign,
            "country": self._country,
            "velocity": self._velocity,
            "altitude": self._altitude,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Aeroplane":
        return cls(data["callsign"], data["country"], data["velocity"], data["altitude"])

    @classmethod
    def cast_to_object_list(cls, states: list[list]) -> list["Aeroplane"]:
        """Преобразует «states» OpenSky в объекты; некорректные строки пропускаются.

        Индексы OpenSky: 1 позывной, 2 страна, 7 барометрическая высота, 9 скорость, 13 геометрическая высота.
        """
        result = []
        for state in states or []:
            try:
                altitude = state[7] if state[7] is not None else state[13]
                result.append(
                    cls(state[1] or "", state[2], state[9] or 0, altitude or 0)
                )
            except (IndexError, TypeError, ValueError):
                continue
        return result

    def __str__(self) -> str:
        return (
            f"{self._callsign:<9} | {self._country:<25} | "
            f"скорость: {self._velocity:8.2f} м/с | высота: {self._altitude:9.2f} м"
        )

    def __repr__(self) -> str:
        return (
            f"Aeroplane({self._callsign!r}, {self._country!r}, "
            f"{self._velocity}, {self._altitude})"
        )
