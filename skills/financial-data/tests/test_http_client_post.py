from financial_data.adapters.base import HttpClient


class Response:
    status_code = 200
    text = '{"data":[1]}'
    content = b"zip-bytes"

    def json(self):
        return {"data": [1]}


class Session:
    def __init__(self):
        self.calls = []

    def get(self, url, timeout=None, **kwargs):
        self.calls.append(("GET", url, kwargs))
        return Response()

    def post(self, url, timeout=None, **kwargs):
        self.calls.append(("POST", url, kwargs))
        return Response()


def test_post_json_uses_post_transport_and_preserves_payload():
    session = Session()
    client = HttpClient(session=session, max_retries=0)
    assert client.post_json("https://example.test", json={"a": 1}) == {"data": [1]}
    assert session.calls == [("POST", "https://example.test", {"json": {"a": 1}})]


def test_get_response_exposes_binary_content_after_status_classification():
    session = Session()
    client = HttpClient(session=session, max_retries=0)
    assert client.get_response("https://example.test/archive.zip").content == b"zip-bytes"
    assert session.calls[0][0] == "GET"


def test_post_response_exposes_binary_content_and_preserves_payload():
    session = Session()
    client = HttpClient(session=session, max_retries=0)
    response = client.post_response("https://example.test/archive.zip", json={"tradeDate": "20260814"})
    assert response.content == b"zip-bytes"
    assert session.calls == [("POST", "https://example.test/archive.zip", {"json": {"tradeDate": "20260814"}})]
