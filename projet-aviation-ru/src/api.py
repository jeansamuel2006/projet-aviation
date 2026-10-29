"""Классы для работы с внешними API (Nominatim и OpenSky)."""
from abc import ABC, abstractmethod
from typing import Any

import requests


class APIError(Exception):
    """Ошибка при обращении к внешнему API."""


class BaseAPI(ABC):
    """Общий контракт для классов, работающих с API."""

    @abstractmethod
    def connect(self, url: str, params: dict | None = None) -> Any:
        """Отправляет запрос и возвращает декодированный ответ."""

    @abstractmethod
    def get_country_bbox(self, country: str) -> tuple[float, float, float, float]:
        """Возвращает (lat_min, lat_max, lon_min, lon_max) страны."""

    @abstractmethod
    def get_aeroplanes(self, country: str) -> list[list]:
        """Возвращает «сырые» данные о самолётах над страной."""


class AeroplanesAPI(BaseAPI):
    """Запрашивает nominatim.openstreetmap.org, затем opensky-network.org."""

    NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
    OPENSKY_URL = "https://opensky-network.org/api/states/all"
    HEADERS = {"User-Agent": "projet-aviation-coursework/1.0"}
    TIMEOUT = 15

    def connect(self, url: str, params: dict | None = None) -> Any:
        try:
            response = requests.get(
                url, params=params, headers=self.HEADERS, timeout=self.TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            raise APIError(f"Не удалось выполнить запрос к {url}: {exc}") from exc
        except ValueError as exc:
            raise APIError(f"Ответ {url} не является JSON") from exc

    def get_country_bbox(self, country: str) -> tuple[float, float, float, float]:
        if not country or not country.strip():
            raise ValueError("Название страны не может быть пустым.")
        data = self.connect(
            self.NOMINATIM_URL,
            {"q": country.strip(), "format": "json", "limit": 1},
        )
        if not data:
            raise APIError(f"Страна не найдена: {country}")
        try:
            south, north, west, east = (float(v) for v in data[0]["boundingbox"])
        except (KeyError, TypeError, ValueError) as exc:
            raise APIError("Boundingbox отсутствует или некорректен.") from exc
        return south, north, west, east

    def get_aeroplanes(self, country: str) -> list[list]:
        south, north, west, east = self.get_country_bbox(country)
        data = self.connect(
            self.OPENSKY_URL,
            {"lamin": south, "lamax": north, "lomin": west, "lomax": east},
        )
        states = (data or {}).get("states")
        return states or []
