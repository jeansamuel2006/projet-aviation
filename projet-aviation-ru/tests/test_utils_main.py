import pytest
from main import user_interaction
from src.aeroplane import Aeroplane
from src.api import APIError
from src.saver import JSONSaver
from src import utils

PLANES = [
    Aeroplane("A", "France", 100, 3000),
    Aeroplane("B", "Spain", 200, 9000),
    Aeroplane("C", "France", 300, 6000),
]


def test_filter():
    assert len(utils.filter_aeroplanes(PLANES, ["france"])) == 2
    assert utils.filter_aeroplanes(PLANES, []) == PLANES


def test_altitude_range():
    assert utils.parse_altitude_range("9000 - 1000") == (1000.0, 9000.0)
    assert len(utils.get_aeroplanes_by_altitude(PLANES, "4000 - 10000")) == 2
    assert utils.get_aeroplanes_by_altitude(PLANES, "") == PLANES
    for bad in ("abc", "1-2-3", "a - b"):
        with pytest.raises(ValueError):
            utils.parse_altitude_range(bad)


def test_sort_top():
    assert [p.callsign for p in utils.sort_aeroplanes(PLANES)] == ["B", "C", "A"]
    assert utils.sort_aeroplanes(PLANES, "velocity")[0].callsign == "C"
    with pytest.raises(ValueError):
        utils.sort_aeroplanes(PLANES, "x")
    assert len(utils.get_top_aeroplanes(PLANES, 2)) == 2
    with pytest.raises(ValueError):
        utils.get_top_aeroplanes(PLANES, -1)


def test_print(capsys):
    utils.print_aeroplanes([])
    assert "не найдены" in capsys.readouterr().out
    utils.print_aeroplanes(PLANES[:1])
    assert "1." in capsys.readouterr().out


class FakeAPI:
    def __init__(self, error=None):
        self.error = error

    def get_aeroplanes(self, country):
        if self.error:
            raise self.error
        return [[None, "AFR1", "France", None, None, 0, 0, 5000.0, False, 200.0, 0, 0, None, None]]


def run(monkeypatch, tmp_path, inputs, api):
    it = iter(inputs)
    monkeypatch.setattr("builtins.input", lambda *_: next(it))
    user_interaction(api, JSONSaver(tmp_path / "x.json"))


def test_interaction_ok(monkeypatch, tmp_path, capsys):
    run(monkeypatch, tmp_path, ["France", "3", "france", "1000 - 9000"], FakeAPI())
    assert "AFR1" in capsys.readouterr().out
    assert len(JSONSaver(tmp_path / "x.json").get_aeroplanes()) == 1


def test_interaction_errors(monkeypatch, tmp_path, capsys):
    run(monkeypatch, tmp_path, ["France"], FakeAPI(APIError("boom")))
    assert "Ошибка" in capsys.readouterr().out
    run(monkeypatch, tmp_path, ["France", "abc"], FakeAPI())
    assert "Некорректный" in capsys.readouterr().out
