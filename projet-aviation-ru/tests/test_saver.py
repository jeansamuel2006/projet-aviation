import json
import pytest
from src.aeroplane import Aeroplane
from src.saver import BaseSaver, JSONSaver


@pytest.fixture
def saver(tmp_path):
    return JSONSaver(tmp_path / "sub" / "p.json")


def test_abstract():
    with pytest.raises(TypeError):
        BaseSaver()


def test_add_get_delete(saver):
    a, b = Aeroplane("A", "France", 1, 2), Aeroplane("B", "Spain", 3, 4)
    saver.add_aeroplane(a)
    saver.add_aeroplanes([a, b])
    assert len(saver.get_aeroplanes()) == 2
    assert saver.get_aeroplanes(country="france") == [a]
    saver.delete_aeroplane(a)
    assert saver.get_aeroplanes() == [b]
    saver.clear()
    assert saver.get_aeroplanes() == []


def test_json_valid_and_corrupted(saver):
    saver.add_aeroplane(Aeroplane("A", "X", 1, 2))
    assert json.loads(saver._path.read_text(encoding="utf-8"))[0]["callsign"] == "A"
    saver._path.write_text("{oops", encoding="utf-8")
    assert saver.get_aeroplanes() == []
    saver._path.write_text('{"a": 1}', encoding="utf-8")
    assert saver.get_aeroplanes() == []
    saver._path.write_text('[{"callsign": "A"}]', encoding="utf-8")
    assert saver.get_aeroplanes() == []
