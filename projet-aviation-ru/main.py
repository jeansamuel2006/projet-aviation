"""Точка входа: консольное взаимодействие."""
from src.aeroplane import Aeroplane
from src.api import AeroplanesAPI, APIError
from src.saver import JSONSaver
from src.utils import (
    filter_aeroplanes,
    get_aeroplanes_by_altitude,
    get_top_aeroplanes,
    print_aeroplanes,
    sort_aeroplanes,
)


def user_interaction(api=None, saver=None) -> None:
    api = api or AeroplanesAPI()
    saver = saver or JSONSaver()

    country = input("Введите название страны (на английском, например Spain): ")
    try:
        aeroplanes = Aeroplane.cast_to_object_list(api.get_aeroplanes(country))
    except (APIError, ValueError) as exc:
        print(f"Ошибка: {exc}")
        return
    print(f"Найдено самолётов: {len(aeroplanes)}.")
    saver.add_aeroplanes(aeroplanes)

    try:
        top_n = int(input("Сколько самолётов вывести в топ N? "))
        words = input("Страны регистрации для фильтрации (через пробел, пусто = все): ").split()
        altitude_range = input("Диапазон высот в м (например, 1000 - 10000, пусто = все): ")
        filtered = filter_aeroplanes(aeroplanes, words)
        ranged = get_aeroplanes_by_altitude(filtered, altitude_range)
        top = get_top_aeroplanes(sort_aeroplanes(ranged), top_n)
    except ValueError as exc:
        print(f"Некорректный ввод: {exc}")
        return
    print_aeroplanes(top)


if __name__ == "__main__":
    user_interaction()
