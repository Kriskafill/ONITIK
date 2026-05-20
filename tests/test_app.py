import os
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest
import app as application
from app import Dynasty, engine, Base, seed

@pytest.fixture
def client():
    application.app.config["TESTING"] = True
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    seed()
    with application.app.test_client() as c:
        yield c

# iuhkjhk
def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"

def test_index_loads(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "Хань".encode() in r.data

def test_add_dynasty(client):
    r = client.post("/add", data={
        "name": "Юань", "ruler": "Хубилай-хан",
        "year_start": "1271", "year_end": "1368",
        "capital": "Ханбалык", "description": "Монгольская династия",
    }, follow_redirects=True)
    assert r.status_code == 200
    assert "Юань".encode() in r.data

def test_update_dynasty(client):
    r = client.post("/edit/1", data={
        "name": "Хань (ред.)", "ruler": "Лю Бан",
        "year_start": "-206", "year_end": "220",
        "capital": "Лоян", "description": "обновлено",
    }, follow_redirects=True)
    assert r.status_code == 200
    assert "Хань (ред.)".encode() in r.data

def test_delete_dynasty(client):
    r = client.post("/delete/1", follow_redirects=True)
    assert r.status_code == 200
    assert "удалена".encode() in r.data