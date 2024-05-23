import pytest

from fastapi.testclient import TestClient

from obugs.backend import app
from obugs.database.database import Database
from obugs.settings import Settings


@pytest.fixture()
def mock_app():
    """Prepare a mock application to run REST tests"""
    settings = Settings()
    settings.database_uri = "sqlite+pysqlite:///sqlite.db"
    Database(uri=settings.database_uri, check_migrations=True)
    yield TestClient(app)


def test_rest_hello_world(mock_app):
    """Example of a test on the /hello endpoint"""
    response = mock_app.get('/hello')
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


def test_query_softwares(mock_app):
    """Example of a graphql query softwares"""
    query = """
    {
        softwares(search: null){
            id
        }
    }
    """
    response = mock_app.post("/graphql", json={"query": query})
    print(response)
    assert response.status_code == 200
    json = response.json()
    print(json)
    assert "data" in json
    assert "softwares" in json["data"]
    assert len(json["data"]["softwares"]) >= 0
