import pytest
from src.aeroplane import Aeroplane


def test_attributes_and_str():
    a = Aeroplane("UAL1", "United States", 268.79, 10203.18)
    assert (a.callsign, a.country, a.velocity, a.altitude) == ("UAL1", "United States", 268.79, 10203.18)
    assert "UAL1" in str(a) and "UAL1" in repr(a)


@pytest.mark.parametrize("args,exc", [
    ((1, "X", 1, 1), TypeError),
    (("A", "", 1, 1), ValueError),
    (("A", "X", "fast", 1), TypeError),
    (("A", "X", -1, 1), ValueError),
    (("A", "X", 1, True), TypeError),
])
def test_validation(args, exc):
    with pytest.raises(exc):
        Aeroplane(*args)


def test_empty_callsign_allowed():
    assert Aeroplane("  ", "France", 1, 1).callsign == "N/A"


def test_comparisons():
    low, high = Aeroplane("A", "X", 100, 1000), Aeroplane("B", "X", 50, 2000)
    assert high > low and low < high and low <= high and high >= low
    assert low.compare_by_velocity(high) == 1
    assert low.compare_by_altitude(high) == -1
    assert low.compare_by_altitude(Aeroplane("C", "X", 1, 1000)) == 0
    assert low == Aeroplane("Z", "Y", 100, 1000)
    assert low != "x"
    with pytest.raises(TypeError):
        low < 5
    assert len({low, Aeroplane("A", "X", 100, 1000)}) == 1


def test_dict_roundtrip():
    a = Aeroplane("A", "X", 1, 2)
    assert Aeroplane.from_dict(a.to_dict()) == a


def test_cast_to_object_list():
    good = [None, "AFR1", "France", None, None, 0, 0, 5000.0, False, 200.0, 0, 0, None, None]
    geo = [None, "", "Spain", None, None, 0, 0, None, False, None, 0, 0, None, 3000.0]
    bad = [None, "X"]
    planes = Aeroplane.cast_to_object_list([good, geo, bad])
    assert len(planes) == 2
    assert planes[0].altitude == 5000.0 and planes[1].altitude == 3000.0
    assert Aeroplane.cast_to_object_list(None) == []
