import pytest
import requests
from src.api import AeroplanesAPI, APIError, BaseAPI


class FakeResp:
    def __init__(self, data, fail=False, bad_json=False):
        self.data, self.fail, self.bad_json = data, fail, bad_json

    def raise_for_status(self):
        if self.fail:
            raise requests.HTTPError("500")

    def json(self):
        if self.bad_json:
            raise ValueError
        return self.data


def test_abstract():
    with pytest.raises(TypeError):
        BaseAPI()


def test_connect_ok(monkeypatch):
    monkeypatch.setattr(requests, "get", lambda *a, **k: FakeResp({"a": 1}))
    assert AeroplanesAPI().connect("http://x") == {"a": 1}


@pytest.mark.parametrize("resp", [FakeResp({}, fail=True), FakeResp({}, bad_json=True)])
def test_connect_errors(monkeypatch, resp):
    monkeypatch.setattr(requests, "get", lambda *a, **k: resp)
    with pytest.raises(APIError):
        AeroplanesAPI().connect("http://x")


def test_connect_network_error(monkeypatch):
    def boom(*a, **k):
        raise requests.ConnectionError("down")
    monkeypatch.setattr(requests, "get", boom)
    with pytest.raises(APIError):
        AeroplanesAPI().connect("http://x")


def test_bbox(monkeypatch):
    api = AeroplanesAPI()
    monkeypatch.setattr(api, "connect", lambda *a, **k: [{"boundingbox": ["1", "2", "3", "4"]}])
    assert api.get_country_bbox("Spain") == (1.0, 2.0, 3.0, 4.0)


def test_bbox_errors(monkeypatch):
    api = AeroplanesAPI()
    with pytest.raises(ValueError):
        api.get_country_bbox("  ")
    monkeypatch.setattr(api, "connect", lambda *a, **k: [])
    with pytest.raises(APIError):
        api.get_country_bbox("Nowhere")
    monkeypatch.setattr(api, "connect", lambda *a, **k: [{"boundingbox": ["a"]}])
    with pytest.raises(APIError):
        api.get_country_bbox("Bad")


def test_get_aeroplanes(monkeypatch):
    api = AeroplanesAPI()
    monkeypatch.setattr(api, "get_country_bbox", lambda c: (1, 2, 3, 4))
    monkeypatch.setattr(api, "connect", lambda *a, **k: {"states": [[1]]})
    assert api.get_aeroplanes("Spain") == [[1]]
    monkeypatch.setattr(api, "connect", lambda *a, **k: {"states": None})
    assert api.get_aeroplanes("Spain") == []
