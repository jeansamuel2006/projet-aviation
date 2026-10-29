"""Хранение самолётов: абстрактный контракт + реализация JSON."""
import json
from abc import ABC, abstractmethod
from pathlib import Path

from src.aeroplane import Aeroplane


class BaseSaver(ABC):
    """Контракт хранилища (файл, база данных, ...)."""

    @abstractmethod
    def add_aeroplane(self, aeroplane: Aeroplane) -> None:
        """Добавляет самолёт."""

    @abstractmethod
    def add_aeroplanes(self, aeroplanes: list[Aeroplane]) -> None:
        """Добавляет несколько самолётов."""

    @abstractmethod
    def get_aeroplanes(self, **criteria) -> list[Aeroplane]:
        """Возвращает самолёты по критериям (country, callsign...)."""

    @abstractmethod
    def delete_aeroplane(self, aeroplane: Aeroplane) -> None:
        """Удаляет самолёт."""

    @abstractmethod
    def clear(self) -> None:
        """Очищает хранилище."""


class JSONSaver(BaseSaver):
    """Сохраняет самолёты в JSON-файл."""

    def __init__(self, path: str | Path = "data/aeroplanes.json"):
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if not self._path.exists():
            self._write([])

    def _read(self) -> list[dict]:
        try:
            with self._path.open(encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            return []
        return data if isinstance(data, list) else []

    def _write(self, data: list[dict]) -> None:
        with self._path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def add_aeroplane(self, aeroplane: Aeroplane) -> None:
        self.add_aeroplanes([aeroplane])

    def add_aeroplanes(self, aeroplanes: list[Aeroplane]) -> None:
        data = self._read()
        for plane in aeroplanes:
            item = plane.to_dict()
            if item not in data:
                data.append(item)
        self._write(data)

    def get_aeroplanes(self, **criteria) -> list[Aeroplane]:
        result = []
        for item in self._read():
            if all(
                str(item.get(k, "")).lower() == str(v).lower()
                for k, v in criteria.items()
            ):
                try:
                    result.append(Aeroplane.from_dict(item))
                except (KeyError, TypeError, ValueError):
                    continue
        return result

    def delete_aeroplane(self, aeroplane: Aeroplane) -> None:
        target = aeroplane.to_dict()
        self._write([item for item in self._read() if item != target])

    def clear(self) -> None:
        self._write([])
