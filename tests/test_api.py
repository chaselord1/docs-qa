import importlib

from fastapi.testclient import TestClient


def _fresh_app():
    import app.main as main_module
    importlib.reload(main_module)
    return main_module


def test_upload_endpoint_accepts_txt():
    main_module = _fresh_app()
    with TestClient(main_module.app) as client:
        files = {"file": ("note.txt", b"Northwind bikes close at 7pm on weekdays.", "text/plain")}
        res = client.post("/api/upload", files=files)
        assert res.status_code == 200
        body = res.json()
        assert body["filename"] == "note.txt"
        assert body["chunks"] >= 1


def test_ask_endpoint_returns_citations():
    main_module = _fresh_app()
    with TestClient(main_module.app) as client:
        res = client.post("/api/ask", json={"question": "how do I get a refund"})
        assert res.status_code == 200
        body = res.json()
        assert body["citations"]
        assert any("returns" in c["source"] for c in body["citations"])


def test_ask_not_covered():
    main_module = _fresh_app()
    with TestClient(main_module.app) as client:
        res = client.post("/api/ask", json={"question": "what is the capital of France"})
        assert res.status_code == 200
        body = res.json()
        assert body["citations"] == []
        assert "isn't covered" in body["answer"]
