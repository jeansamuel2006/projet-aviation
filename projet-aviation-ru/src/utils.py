"""Функции фильтрации, сортировки и вывода."""
from src.aeroplane import Aeroplane


def filter_aeroplanes(aeroplanes: list[Aeroplane], countries: list[str]) -> list[Aeroplane]:
    """Оставляет самолёты, страна регистрации которых содержит одно из слов."""
    words = [c.lower() for c in countries if c]
    if not words:
        return list(aeroplanes)
    return [a for a in aeroplanes if any(w in a.country.lower() for w in words)]


def parse_altitude_range(text: str) -> tuple[float, float]:
    """Преобразует «100 - 5000» в (100.0, 5000.0)."""
    parts = [p.strip() for p in text.replace("–", "-").split("-")]
    if len(parts) != 2 or not all(parts):
        raise ValueError("Ожидаемый формат: мин - макс (например, 1000 - 10000).")
    low, high = float(parts[0]), float(parts[1])
    if low > high:
        low, high = high, low
    return low, high


def get_aeroplanes_by_altitude(aeroplanes: list[Aeroplane], altitude_range: str) -> list[Aeroplane]:
    if not altitude_range or not altitude_range.strip():
        return list(aeroplanes)
    low, high = parse_altitude_range(altitude_range)
    return [a for a in aeroplanes if low <= a.altitude <= high]


def sort_aeroplanes(aeroplanes: list[Aeroplane], by: str = "altitude") -> list[Aeroplane]:
    """Сортировка по убыванию: 'altitude' или 'velocity'."""
    if by not in ("altitude", "velocity"):
        raise ValueError("Неизвестный критерий сортировки.")
    return sorted(aeroplanes, key=lambda a: getattr(a, by), reverse=True)


def get_top_aeroplanes(aeroplanes: list[Aeroplane], top_n: int) -> list[Aeroplane]:
    if top_n < 0:
        raise ValueError("N должно быть неотрицательным.")
    return aeroplanes[:top_n]


def print_aeroplanes(aeroplanes: list[Aeroplane]) -> None:
    if not aeroplanes:
        print("Самолёты не найдены.")
        return
    for i, plane in enumerate(aeroplanes, 1):
        print(f"{i:>2}. {plane}")
